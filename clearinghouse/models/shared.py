from typing import Literal


OrderInstruction = Literal["BUY", "SELL", "SELL_SHORT", "BUY_TO_COVER"]
OrderType = Literal["MARKET", "LIMIT", "STOP"]
OrderDuration = Literal["DAY", "GOOD_TILL_CANCEL", "FILL_OR_KILL"]
AssetType = Literal["EQUITY", "OPTION", "MUTUAL_FUND", "FIXED_INCOME", "CASH_EQUIVALENT"]
OrderSession = Literal["NORMAL", "AM", "PM", "SEAMLESS"]
OrderStrategyType = Literal["SINGLE", "OCO", "TRIGGER"]

TransactionType = Literal[
    "TRADE",
    "RECEIVE_AND_DELIVER",
    "DIVIDEND_OR_INTEREST",
    "ACH_RECEIPT",
    "ACH_DISBURSEMENT",
    "CASH_RECEIPT",
    "CASH_DISBURSEMENT",
    "ELECTRONIC_FUND",
    "WIRE_OUT",
    "WIRE_IN",
    "JOURNAL",
    "MEMORANDUM",
    "MARGIN_CALL",
    "MONEY_MARKET",
    "SMA_ADJUSTMENT",
]

OrderStatus = Literal[
    "AWAITING_PARENT_ORDER",
    "AWAITING_CONDITION",
    "AWAITING_STOP_CONDITION",
    "AWAITING_MANUAL_REVIEW",
    "ACCEPTED",
    "AWAITING_UR_OUT",
    "PENDING_ACTIVATION",
    "QUEUED",
    "WORKING",
    "REJECTED",
    "PENDING_CANCEL",
    "CANCELED",
    "PENDING_REPLACE",
    "REPLACED",
    "FILLED",
    "EXPIRED",
    "NEW",
    "AWAITING_RELEASE_TIME",
    "PENDING_ACKNOWLEDGEMENT",
    "PENDING_RECALL",
    "UNKNOWN",
]
