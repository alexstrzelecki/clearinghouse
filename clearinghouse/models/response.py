from typing import List
import datetime

from pydantic import Field

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class Meta(BaseModel):
    type: str
    timestamp: datetime.datetime
    # request_duration: Optional[datetime.timedelta]  # TODO: implement this via middleware


class BaseResponse(BaseModel, Generic[T]):
    meta: Meta


class GenericItemResponse(BaseResponse[T]):
    """
    Allow data to be a dict in case of empty data to prevent returning null
    """
    data: T | dict


class GenericCollectionResponse(BaseResponse[T]):
    data: List[T]


class SubmittedOrder(BaseModel):
    """
    Simplified transaction model for the original Schwab API return model.
    """
    orderId: str = Field(..., alias="order_id")
    isFilled: bool = Field(..., alias="is_filled")
    total: float = Field(..., alias="total")
    duration: str = Field(..., alias="duration")
    orderType: str = Field(..., alias="order_type")
    price: float = Field(..., alias="price")
    quantity: float = Field(..., alias="quantity")
    filledQuantity: float = Field(..., alias="filled_quantity")
    remainingQuantity: float = Field(..., alias="remaining_quantity")
    status: str = Field(..., alias="status")
    enteredTime: datetime.datetime = Field(..., alias="entered_time")
    cancelTime: datetime.datetime = Field(..., alias="cancel_time")
    session: str = Field(..., alias="session")
    cancelable: bool = Field(..., alias="cancelable")


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
    id: str = Field(..., alias="id")
    orderId: str = Field(..., alias="order_id")
    time: datetime.datetime = Field(..., alias="time")
    type: str = Field(..., alias="type")
    status: str = Field(..., alias="status")
    netAmount: str = Field(..., alias="net_amount")
    trade_date: datetime.datetime = Field(..., alias="trade_date")


class Lot(BaseModel):
    acquisitionDate: datetime.datetime = Field(..., alias="acquisition_date")
    quantity: float
    price: float


class Position(BaseModel):
    ticker: str
    quantity: float
    lots: List[Lot]
    marketValue: float = Field(..., alias="market_value")
    entryValue: float = Field(..., alias="entry_value")
    netChange: float = Field(..., alias="net_change")
    accountFraction: float = Field(..., alias="account_fraction")
