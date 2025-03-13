import datetime
from typing_extensions import Self
from typing import Optional, List

from pydantic import BaseModel, Field, model_validator
from enum import Enum


class TransactionType(Enum):
    """
    Transaction types. Pulled from Schwab API documentation.
    """
    TRADE = "TRADE"
    RECEIVE_AND_DELIVER = "RECEIVE_AND_DELIVER"
    DIVIDEND_OR_INTEREST = "DIVIDEND_OR_INTEREST"
    ACH_RECEIPT = "ACH_RECEIPT"
    ACH_DISBURSEMENT = "ACH_DISBURSEMENT"
    CASH_RECEIPT = "CASH_RECEIPT"
    CASH_DISBURSEMENT = "CASH_DISBURSEMENT"
    ELECTRONIC_FUND = "ELECTRONIC_FUND"
    WIRE_OUT = "WIRE_OUT"
    WIRE_IN = "WIRE_IN"
    JOURNAL = "JOURNAL"
    MEMORANDUM = "MEMORANDUM"
    MARGIN_CALL = "MARGIN_CALL"
    MONEY_MARKET = "MONEY_MARKET"
    SMA_ADJUSTMENT = "SMA_ADJUSTMENT"


class OrderStatus(Enum):
    """
    Status options. Pulled from Schwab API documentation.
    """
    AWAITING_PARENT_ORDER = "AWAITING_PARENT_ORDER"
    AWAITING_CONDITION = "AWAITING_CONDITION"
    AWAITING_STOP_CONDITION = "AWAITING_STOP_CONDITION"
    AWAITING_MANUAL_REVIEW = "AWAITING_MANUAL_REVIEW"
    ACCEPTED = "ACCEPTED"
    AWAITING_UR_OUT = "AWAITING_UR_OUT"
    PENDING_ACTIVATION = "PENDING_ACTIVATION"
    QUEUED = "QUEUED"
    WORKING = "WORKING"
    REJECTED = "REJECTED"
    PENDING_CANCEL = "PENDING_CANCEL"
    CANCELED = "CANCELED"
    PENDING_REPLACE = "PENDING_REPLACE"
    REPLACED = "REPLACED"
    FILLED = "FILLED"
    EXPIRED = "EXPIRED"
    NEW = "NEW"
    AWAITING_RELEASE_TIME = "AWAITING_RELEASE_TIME"
    PENDING_ACKNOWLEDGEMENT = "PENDING_ACKNOWLEDGEMENT"
    PENDING_RECALL = "PENDING_RECALL"
    UNKNOWN = "UNKNOWN"


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


class BaseOrder(BaseModel):
    # TODO: add docstring explaining opaque attr
    symbol: str = Field(..., alias="symbol")
    price: float = Field(..., alias="price")
    orderType: OrderType = Field(OrderType.market, alias="order_type")
    duration: OrderDuration = Field(OrderDuration.day, alias="duration")


class Order(BaseOrder):
    operation: OrderOperation = Field(..., alias="operation")
    quantity: int = Field(..., alias="quantity")

    @model_validator(mode="after")
    def check_entries(self) -> Self:
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        return self


class AdjustmentOrder(BaseOrder):
    """
    Model representing orders to adjust currently held securities.

    adjustment: Fraction increase/decrease in a position
        e.g. 0.5 for 50% increase.
    """
    adjustment: float = Field(..., alias="adjustment")

    @model_validator(mode="after")
    def check_entries(self) -> Self:
        if self.adjustment < -1:
            raise ValueError("Cannot sell more than entire position.")
        return self


class PositionsFilter(BaseModel):
    assetType: Optional[str]  = "" # TODO: make enum
    shorts: Optional[bool] = True
    longs: Optional[bool] = True
    minPositionSize: Optional[float] = None
    maxPositionSize: Optional[float] = None


class OrdersFilter(BaseModel):
    startDate: Optional[datetime.datetime] = None
    endDate: Optional[datetime.datetime] = None
    maxResults: Optional[int] = None
    status: Optional[OrderStatus] = None
    symbols: Optional[List[str]] = None


class TransactionsFilter(BaseModel):
    startDate: Optional[datetime.datetime] = None
    endDate: Optional[datetime.datetime] = None
    types: Optional[List[TransactionType]] = None
    symbols: Optional[List[str]] = None
