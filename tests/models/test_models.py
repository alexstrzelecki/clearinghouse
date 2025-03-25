"""
Testing data models and Schwab return types
"""

import pytest
from clearinghouse.models.request import BaseOrder, OrderType

def test_validate_price_with_market_order():
    """
    Test that a ValueError is raised if a price is set for a market order.
    """
    with pytest.raises(ValueError, match="Price cannot be set for market orders."):
        BaseOrder(symbol="AAPL", price=150.0, order_type="MARKET")

def test_validate_price_with_limit_order():
    """
    Test that no error is raised if a price is set for a limit order.
    """
    try:
        order = BaseOrder(symbol="AAPL", price=150.0, order_type="LIMIT")
        assert order.price == 150.0
    except ValueError:
        pytest.fail("Unexpected ValueError raised for limit order with price.")

def test_validate_price_without_price():
    """
    Test that no error is raised if no price is set for a market order.
    """
    try:
        order = BaseOrder(symbol="AAPL", order_type="MARKET")
        assert order.price is None
    except ValueError:
        pytest.fail("Unexpected ValueError raised for market order without price.")
