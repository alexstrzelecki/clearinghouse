import pytest
from clearinghouse.utils.math_utils import calculate_rmse
from clearinghouse.models.request import NumericalOrder
from clearinghouse.utils.orders_utils import sort_orders, find_order_minimum_error


def test_calculate_rmse_basic():
    pairs = [(100, 90), (200, 210), (300, 310)]
    expected_rmse = 10.0
    assert calculate_rmse(pairs) == pytest.approx(expected_rmse)

def test_calculate_rmse_zero_error():
    pairs = [(100, 100), (200, 200), (300, 300)]
    expected_rmse = 0.0
    assert calculate_rmse(pairs) == pytest.approx(expected_rmse)

def test_calculate_rmse_single_pair():
    pairs = [(100, 110)]
    expected_rmse = 10.0
    assert calculate_rmse(pairs) == pytest.approx(expected_rmse)

def test_calculate_rmse_empty_list():
    pairs = []
    with pytest.raises(ZeroDivisionError):
        calculate_rmse(pairs)

def test_calculate_rmse_negative_values():
    pairs = [(-100, -90), (-200, -210), (-300, -290)]
    expected_rmse = 10.0
    assert calculate_rmse(pairs) == pytest.approx(expected_rmse)

def test_sort_orders_default():
    orders = [
        NumericalOrder(symbol="AAPL", instruction="BUY", quantity=10),
        NumericalOrder(symbol="GOOGL", instruction="SELL", quantity=5),
        NumericalOrder(symbol="MSFT", instruction="SELL_SHORT", quantity=8),
        NumericalOrder(symbol="TSLA", instruction="BUY_TO_COVER", quantity=12)
    ]
    sorted_orders = sort_orders(orders)
    expected_order = ["SELL", "SELL_SHORT", "BUY_TO_COVER", "BUY"]
    assert [order.instruction for order in sorted_orders] == expected_order

def test_sort_orders_custom_order():
    custom_order = ["BUY", "SELL", "SELL_SHORT", "BUY_TO_COVER"]
    orders = [
        NumericalOrder(symbol="AAPL", instruction="BUY", quantity=10),
        NumericalOrder(symbol="GOOGL", instruction="SELL", quantity=5),
        NumericalOrder(symbol="MSFT", instruction="SELL_SHORT", quantity=8),
        NumericalOrder(symbol="TSLA", instruction="BUY_TO_COVER", quantity=12)
    ]
    sorted_orders = sort_orders(orders, sort_order=custom_order)
    expected_order = ["BUY", "SELL", "SELL_SHORT", "BUY_TO_COVER"]
    assert [order.instruction for order in sorted_orders] == expected_order

def test_sort_orders_empty_list():
    orders = []
    sorted_orders = sort_orders(orders)
    assert sorted_orders == []

def test_sort_orders_invalid_attr():
    orders = [
        NumericalOrder(symbol="AAPL", instruction="BUY", quantity=10)
    ]
    with pytest.raises(AttributeError):
        sort_orders(orders, attr="non_existent_attr")


def test_find_order_minimum_error_basic():
    order_options = {
        "A": (100, (80, 130)),
        "B": (100, (100,)),
        "C": (80, (79, 140))
    }
    expected_result = {"A": 0, "B": 0, "C": 0}
    assert find_order_minimum_error(order_options) == expected_result

def test_find_order_minimum_error_with_cap():
    order_options = {
        "A": (100, (80, 130)),
        "B": (100, (100,)),
        "C": (80, (79, 140))
    }
    capital_cap = 300
    expected_result = {"A": 0, "B": 0, "C": 0}
    assert find_order_minimum_error(order_options, capital_cap) == expected_result

def test_find_order_minimum_error_exceeding_cap():
    order_options = {
        "A": (100, (80, 130)),
        "B": (100, (100,)),
        "C": (80, (35, 100))
    }
    capital_cap = 270  # The ideal option exceeds the cap: (0,0,1)
    expected_result = {"A": 0, "B": 0, "C": 0}
    assert find_order_minimum_error(order_options, capital_cap) == expected_result

def test_find_order_minimum_error_empty_input():
    order_options = {}
    expected_result = {}
    assert find_order_minimum_error(order_options) == expected_result

def test_find_order_minimum_error_no_valid_permutation():
    order_options = {
        "A": (100, (150, 160)),
        "B": (100, (110,)),
        "C": (80, (90, 150))
    }
    capital_cap = 200
    expected_result = {}
    assert find_order_minimum_error(order_options, capital_cap) == expected_result
