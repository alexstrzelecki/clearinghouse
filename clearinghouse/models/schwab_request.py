from pydantic import BaseModel
from typing import List, Literal


class Instrument(BaseModel):
    symbol: str
    assetType: Literal["EQUITY", "OPTION", "MUTUAL_FUND", "FIXED_INCOME", "CASH_EQUIVALENT"]


class OrderLeg(BaseModel):
    instruction: Literal["BUY", "SELL", "BUY_TO_COVER", "SELL_SHORT"]
    quantity: int
    instrument: Instrument


class Order(BaseModel):
    orderType: Literal["MARKET", "LIMIT", "STOP", "STOP_LIMIT"]
    session: Literal["NORMAL", "AM", "PM", "SEAMLESS"]
    duration: Literal["DAY", "GOOD_TILL_CANCEL", "FILL_OR_KILL"]
    orderStrategyType: Literal["SINGLE", "OCO", "TRIGGER"]
    price: float = None  # Optional, only required for LIMIT or STOP_LIMIT orders
    orderLegCollection: List[OrderLeg]
