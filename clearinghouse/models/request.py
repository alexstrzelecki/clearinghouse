from typing import Union

from pydantic import BaseModel, Field
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


class Order(BaseModel):
    # TODO: add docstring explaining opaque attr
    ticker: str = Field(..., alias="ticker")
    price: float = Field(..., alias="price")
    operation: OrderOperation = Field(..., alias="operation")
    orderType: OrderType = Field(OrderType.market, alias="order_type")
    amount: Union[int, float] = Field(..., alias="amount")
    amountType: OrderAmountType = Field(OrderAmountType.shares, alias="amount_type")
    duration: OrderDuration = Field(OrderDuration.day, alias="duration")
