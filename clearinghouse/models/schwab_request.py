from pydantic import BaseModel
from typing import List, Literal

from clearinghouse.models.shared import (
    AssetType,
    OrderDuration,
    OrderInstruction,
    OrderType,
    OrderSession,
    OrderStrategyType,
)


class Instrument(BaseModel):
    symbol: str
    assetType: Literal[AssetType]


class OrderLeg(BaseModel):
    instruction: OrderInstruction
    quantity: float
    instrument: Instrument


class SchwabOrder(BaseModel):
    orderType: OrderType
    session: OrderSession
    duration: OrderDuration
    orderStrategyType: OrderStrategyType
    price: float = None  # Optional, only required for LIMIT or STOP_LIMIT orders.
    orderLegCollection: List[OrderLeg]
