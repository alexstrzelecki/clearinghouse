from pydantic import BaseModel
from enum import Enum


class OrderOperation(str, Enum):
    buy = "buy"
    sell = "sell"
    short = "short"
    close = "close"


class OrderType(str, Enum):
    market = "market"
    limit = "limit"
    stop = "stop"


class OrderAmountType(str, Enum):
    percentage = "percentage"
    shares = "shares"


class OrderDuration(str, Enum):
    """
    For how long to keep the order open
    TODO: add the remaining options
    """
    day = "day"
    gtc = "gtc"


class Order(BaseModel):
    ticker: str
    price: float
    operation: OrderOperation
    order_type: OrderType = OrderType.market
    amount: int | float
    amount_type: OrderAmountType = OrderAmountType.shares
    duration: OrderDuration = OrderDuration.day
