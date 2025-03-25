from typing import Dict
from collections import Counter

import pytest
from fastapi.testclient import TestClient

from clearinghouse.main import app

VERSION = "v1"

"""
Tests for the orders router. Uses sample data in the repo to confirm orders.
"""

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('SCHWAB_LOCAL_MODE', 'true')
    return TestClient(app)


def assert_meta_structure(resp: Dict, expected_type_label: str):
    meta = resp["meta"]
    assert isinstance(meta, dict)
    assert meta["type"] == expected_type_label
    assert meta.keys() == {"type", "timestamp"}


def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_positions_no_filter(client):
    """
    Test for getting positions without any additional filtering
    """
    resp = client.get(f"/{VERSION}/positions")
    data = resp.json().get("data")

    assert_meta_structure(resp.json(), "PositionsList")
    assert resp.status_code == 200
    assert len(data) == 5

def test_get_positions_filter_positive(client):
    """
    Test for getting positions with a basic filter where the criteria
    do not remove anything.
    """
    resp = client.get(f"/{VERSION}/positions?symbols=AAPL")
    data = resp.json().get("data")

    assert_meta_structure(resp.json(), "PositionsList")
    assert resp.status_code == 200
    assert len(data) == 1

def test_get_positions_filter_negative(client):
    """
    Test for getting positions with a basic filter where the criteria
    remove all original data,
    """
    resp = client.get(f"/{VERSION}/positions?symbols=ASDF")
    data = resp.json().get("data")

    assert_meta_structure(resp.json(), "PositionsList")
    assert resp.status_code == 200
    assert len(data) == 0

def test_get_orders(client):
    """
    Test for GET /v1/orders
    """
    resp = client.get(f"/{VERSION}/orders")
    assert_meta_structure(resp.json(), "OrdersList")
    assert isinstance(resp.json()["data"], list)

def test_order_details(client):
    """
    Test for GET /v1/orders/{orderId}
    """
    orderId = "abcde1234"
    resp = client.get(f"/{VERSION}/orders/{orderId}")
    assert_meta_structure(resp.json(), "OrderDetails")

def test_cancel_order(client):
    """
    Test for DELETE /v1/orders/{orderId}
    """
    orderId = "testOrderId"  # Use a valid orderId for actual testing
    resp = client.delete(f"/{VERSION}/orders/{orderId}")
    assert resp.status_code == 204  # No content to check meta

def test_get_transactions(client):
    """
    Test for GET /v1/transactions
    """
    resp = client.get(f"/{VERSION}/transactions")
    assert_meta_structure(resp.json(), "TransactionsList")
    assert isinstance(resp.json()["data"], list)
    assert resp.status_code == 200

def test_get_transactions_details(client):
    """
    Test for GET /v1/transactions/{transactionId}
    """
    transactionId = "testTransactionId"  # Use a valid transactionId for actual testing
    resp = client.get(f"/{VERSION}/transactions/{transactionId}")
    assert_meta_structure(resp.json(), "Transaction")
    assert resp.status_code == 200

def test_get_quote(client):
    """
    Test for GET /v1/quotes/{symbol}
    """
    symbol = "AAPL"  # Example symbol
    resp = client.get(f"/{VERSION}/quotes/{symbol}")
    assert_meta_structure(resp.json(), "Quote")
    assert resp.status_code == 200

def test_get_bulk_quotes(client):
    """
    Test for POST /v1/quotes
    """
    symbols = ["AAPL", "GOOGL"]
    resp = client.post(f"/{VERSION}/quotes", json=symbols)
    assert_meta_structure(resp.json(), "QuotesList")
    assert resp.status_code == 200

def test_order_placement(client):
    """
    Test for POST /v1/orders
    """
    order_data = {
        "symbol": "AAPL",
        "quantity": "5",
        "price": 9.99,
        "order_type": "limit",
        "duration": "day",
        "instruction": "buy"
    }
    resp = client.post(f"/{VERSION}/orders", json=order_data)
    assert_meta_structure(resp.json(), "OrderResult")
    assert resp.status_code == 201

def test_order_placement_batch(client):
    """
    Test for POST /v1/orders/batch
    """
    orders_data = [
        {
        "symbol": "AAPL",
        "quantity": "5",
        "price": 9.99,
        "order_type": "limit",
        "duration": "day",
        "instruction": "buy"
        },
        {
        "symbol": "AMD",
        "quantity": "10",
        "price": 1234.40,
        "order_type": "limit",
        "duration": "day",
        "instruction": "sell"
        }
    ]
    resp = client.post(f"/{VERSION}/orders/batch", json=orders_data)
    assert_meta_structure(resp.json(), "OrderResultList")
    assert resp.status_code == 201

def test_adjust_position_base(client):
    """
    Test for POST /v1/adjustments.
    Basic test to ensure adjustments are processed correctly.
    """
    adjustments = [
        {
            "symbol": "AAPL",
            "price": 9.99,
            "order_type": "LIMIT",
            "duration": "DAY",
            "adjustment": 0.5
        }
    ]
    resp = client.post("/v1/adjustments?preview=False", json=adjustments)
    assert resp.status_code == 201
    data = resp.json()
    assert_meta_structure(data, "AdjustmentOrderList")

    count = Counter([d["status"] for d in data["data"]])
    assert count["SUCCEEDED"] == 1


def test_adjust_position_no_change(client):
    """
    Test for POST /v1/adjustments.
    The positions should match the requested adjustment and should return no orders.
    """
    # TODO: get the current position in the sample data
    adjustments = [
        {
            "symbol": "AAPL",
            "order_type": "MARKET",
            "duration": "DAY",
            "adjustment": 0.0  # No change
        }
    ]
    resp = client.post("/v1/adjustments", json=adjustments)
    assert resp.status_code == 207
    data = resp.json()
    assert_meta_structure(data, "AdjustmentOrderList")
    assert len(data["data"]) == 1
    item = data["data"][0]
    assert item["symbol"] == "AAPL"
    assert item["status"] == "IGNORED"


def test_adjust_position_total_sell(client):
    """
    Test for POST /v1/adjustments.
    Check whether a position can be completely sold to cash.
    """
    adjustments = [
        {
            "symbol": "AAPL",
            "order_type": "MARKET",
            "duration": "DAY",
            "adjustment": -1.0
        }
    ]
    resp = client.post("/v1/adjustments", json=adjustments)
    assert resp.status_code == 201
    data = resp.json()
    assert_meta_structure(data, "AdjustmentOrderList")
    assert len(data["data"]) == 1

    # TODO: assert that there are no shares remaining - not currently possible due to local client limitations

def test_adjust_position_open_new_position(client):
    """
    Test for POST /v1/adjustments.
    The request to open a new position by adjustment should be blocked.
    """
    adjustments = [
        {
            "symbol": "TSLA",
            "price": 700.0,
            "order_type": "LIMIT",
            "duration": "DAY",
            "adjustment": 1.0  # Attempt to open a new position
        }
    ]
    resp = client.post("/v1/adjustments", json=adjustments)
    assert resp.status_code == 207
    data = resp.json().get("data")
    assert data[0]["status"] == "FAILED"
    assert len(data) == 1

def test_adjust_position_preview_true(client):
    """
    Test for POST /v1/adjustments with preview set to False.
    Ensures that adjustments are actually processed.
    """
    adjustments = [
        {
            "symbol": "AAPL",
            "order_type": "MARKET",
            "duration": "DAY",
            "adjustment": 0.5
        }
    ]
    resp = client.post("/v1/adjustments?preview=True", json=adjustments)
    assert resp.status_code == 201
    data = resp.json()
    assert_meta_structure(data, "AdjustmentOrderList")
    assert len(data["data"]) == 1

    count = Counter([d["status"] for d in data["data"]])
    assert count["PREVIEW"] == 1


def test_adjust_position_multi_item_all_processed(client):
    """
    Test for POST /v1/adjustments with multiple items where all orders are processed successfully.
    """
    adjustments = [
        {
            "symbol": "AAPL",
            "order_type": "MARKET",
            "duration": "DAY",
            "adjustment": 0.5
        },
        {
            "symbol": "GOOGL",
            "price": 2800.0,
            "order_type": "LIMIT",
            "duration": "DAY",
            "adjustment": 0.3
        }
    ]
    resp = client.post("/v1/adjustments?preview=False", json=adjustments)
    assert resp.status_code == 201
    data = resp.json()
    assert_meta_structure(data, "AdjustmentOrderList")
    assert len(data["data"]) == 2

    count = Counter([d["status"] for d in data["data"]])
    assert count["SUCCEEDED"] == 2


def test_adjust_position_multi_item_some_processed(client):
    """
    Test for POST /v1/adjustments with multiple items where some orders are processed.
    """
    adjustments = [
        {
            "symbol": "AAPL",
            "order_type": "MARKET",
            "duration": "DAY",
            "adjustment": 0.5
        },
        {
            "symbol": "INVALID_SYMBOL",
            "price": 1000.0,
            "order_type": "LIMIT",
            "duration": "DAY",
            "adjustment": 0
        }
    ]
    resp = client.post("/v1/adjustments?preview=False", json=adjustments)
    assert resp.status_code == 207
    data = resp.json()
    assert_meta_structure(data, "AdjustmentOrderList")

    assert len(data["data"]) == 2
    count = Counter([d["status"] for d in data["data"]])
    assert count["FAILED"] == 1
    assert count["SUCCEEDED"] == 1



def test_adjust_position_multi_item_none_processed(client):
    """
    Test for POST /v1/adjustments with multiple items where no orders are processed due to 0 adjustment or
    invalid / non-existent symbols.
    """
    adjustments = [
        {
            "symbol": "AAPL",
            "price": 1000.0,
            "order_type": "LIMIT",
            "duration": "DAY",
            "adjustment": 0
        },
        {
            "symbol": "INVALID_SYMBOL_2",
            "price": 2000.0,
            "order_type": "LIMIT",
            "duration": "DAY",
            "adjustment": 0.3
        }
    ]
    resp = client.post("/v1/adjustments?preview=False", json=adjustments)
    assert resp.status_code == 207
    data = resp.json()
    assert_meta_structure(data, "AdjustmentOrderList")
    assert len(data["data"]) == 2

    count = Counter([d["status"] for d in data["data"]])
    assert count["IGNORED"] == 1
    assert count["FAILED"] == 1
