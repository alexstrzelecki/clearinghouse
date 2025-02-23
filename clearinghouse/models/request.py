from typing import Union

from pydantic import BaseModel, Field
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
    ticker: str = Field(..., alias="ticker")
    price: float = Field(..., alias="price")
    operation: OrderOperation = Field(..., alias="operation")
    orderType: OrderType = Field(OrderType.market, alias="order_type")
    amount: Union[int, float] = Field(..., alias="amount")
    amountType: OrderAmountType = Field(OrderAmountType.shares, alias="amount_type")
    duration: OrderDuration = Field(OrderDuration.day, alias="duration")
