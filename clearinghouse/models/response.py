from typing import List
import datetime

from pydantic import Field

from typing import Generic, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel


T = TypeVar("T", bound=BaseModel)


class Meta(BaseModel):
    type: str
    timestamp: datetime.datetime
    request_duration: datetime.timedelta


class BaseResponse(GenericModel):
    meta: Meta


class GenericItemResponse(BaseResponse, Generic[T]):
    data: T


class GenericCollectionResponse(BaseResponse, Generic[T]):
    data: List[T]


class SubmittedOrder(BaseModel):
    """
    Simplified transaction model for the original Schwab API return model.
    """
    orderId: str = Field(..., alias="order_id")
    isFilled: bool = Field(..., alias="is_filled")
    total: float


class Quote(BaseModel):
    """
    Current price model for equity/option.
    TODO: determine the extra attributes that may be needed.
    """
    ticker: str
    price: float
    quoteTime: datetime.datetime = Field(..., alias="quote_time")
    totalVolume: int = Field(..., alias="total_volume")
    netPercentageChange: float = Field(..., alias="net_percentage_change")
    bidPrice: float = Field(..., alias="bid_price")
    askPrice: float = Field(..., alias="ask_price")


class Transaction(BaseModel):
    """
    Simplified transaction model for the original Schwab API return model.
    TODO: finish the attr collection for this
    """
    orderId: str = Field(..., alias="order_id")


class Lot(BaseModel):
    acquisitionDate: datetime.datetime = Field(..., alias="acquisition_date")
    quantity: int
    price: float


class Position(BaseModel):
    ticker: str
    quantity: int  # assume no fractional shares
    lots: List[Lot]
    currentValue: float = Field(..., alias="current_value")
    entryValue: float = Field(..., alias="entry_value")
    percentageChange: float = Field(..., alias="percentage_change")
    accountFraction: float = Field(..., alias="account_fraction")
