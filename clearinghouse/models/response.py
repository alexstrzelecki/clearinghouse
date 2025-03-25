from typing import List, Generic, TypeVar, Literal, Optional
import datetime
from pydantic import BaseModel, Field

from clearinghouse.models.shared import (
    OrderInstruction,
    OrderType,
    OrderDuration,
    AssetType,
    OrderSession,
    OrderStrategyType,
)


T = TypeVar("T", bound=BaseModel)

InitialOrderStatus = Literal["IGNORED", "FAILED", "SUCCEEDED", "PREVIEW"]


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


class StandardOrder(BaseModel):
    """
    Simplified transaction model for the original Schwab API return model.
    """
    order_id: int
    is_filled: bool
    total: float
    duration: str
    order_type: str
    price: float
    quantity: float
    filled_quantity: float
    remaining_quantity: float
    status: str
    entered_time: datetime.datetime
    cancel_time: datetime.datetime
    session: str
    cancelable: bool

class OrderResult(BaseModel):
    """
    Model representing the return from a place order or similar request.
    Does not include the order ID and advanced values due to limitations from the Schwab API. Only returned on
    subsequent queries.
    """
    symbol: str
    order_type: OrderType = Field(default="MARKET")
    duration: OrderDuration = Field(default="DAY")
    asset_type: AssetType = Field(default="EQUITY")
    session: OrderSession = Field(default="NORMAL")
    strategy_type: OrderStrategyType = Field(default="SINGLE")
    instruction: OrderInstruction
    quantity: float
    price: Optional[float] = None
    status: InitialOrderStatus
    info: str = ""


class AdjustmentOrderResult(BaseModel):
    """
    Model representing the result of an adjustment order.
    """
    symbol: str
    order_type: OrderType = Field(default="MARKET")
    duration: OrderDuration = Field(default="DAY")
    asset_type: AssetType = Field(default="EQUITY")
    session: OrderSession = Field(default="NORMAL")
    strategy_type: OrderStrategyType = Field(default="SINGLE")
    adjustment: float
    quantity: float  # represents the delta
    total_position_size: float  # represents the new position size
    status: InitialOrderStatus
    info: str = ""


class Quote(BaseModel):
    """
    Current price model for equity/option.
    TODO: determine the extra attributes that may be needed.
    """
    symbol: str
    price: float
    quote_time: datetime.datetime
    total_volume: int
    net_percent_change: float
    bid_price: float
    ask_price: float


class Transaction(BaseModel):
    """
    Simplified transaction model for the original Schwab API return model.
    TODO: finish the attr collection for this
    """
    id: int
    order_id: int
    time: datetime.datetime
    type: str
    status: str
    net_amount: float
    trade_date: datetime.datetime


class Lot(BaseModel):
    acquisition_date: datetime.datetime
    quantity: float
    price: float


class Position(BaseModel):
    symbol: str
    asset_type: str
    quantity: float
    lots: List[Lot]
    market_value: float
    entry_value: float
    net_change: float
    account_fraction: float = 0
