from typing import Dict

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
    assert len(data) == 1

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
        "orderType": "limit",
        "duration": "day",
        "instruction": "buy"
    }
    resp = client.post(f"/{VERSION}/orders", json=order_data)
    assert_meta_structure(resp.json(), "SubmittedOrder")
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
        "orderType": "limit",
        "duration": "day",
        "instruction": "buy"
        },
        {
        "symbol": "AMD",
        "quantity": "10",
        "price": 1234.40,
        "orderType": "limit",
        "duration": "day",
        "instruction": "sell"
        }
    ]
    resp = client.post(f"/{VERSION}/orders/batch", json=orders_data)
    assert_meta_structure(resp.json(), "SubmittedOrdersList")
    assert resp.status_code == 201

def test_adjust_position(client):
    """
    Test for POST /v1/adjustments
    """
    adjustments = [
          {
            "symbol": "AAPL",
            "price": 9.99,
            "orderType": "limit",
            "duration": "day",
            "adjustment": 0.5
          }
    ]
    resp = client.post(f"/{VERSION}/adjustments", json=adjustments)
    assert_meta_structure(resp.json(), "AdjustmentOrder")
