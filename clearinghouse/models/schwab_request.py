from typing import List, Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from clearinghouse.models.shared import (
    AssetType,
    OrderDuration,
    OrderInstruction,
    OrderType,
    OrderSession,
    OrderStrategyType,
)


class Instrument(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    symbol: str
    asset_type: Literal[AssetType]


class OrderLeg(BaseModel):
    instruction: OrderInstruction
    quantity: float
    instrument: Instrument


class SchwabOrder(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    order_type: OrderType
    session: OrderSession
    duration: OrderDuration
    order_strategy_type: OrderStrategyType
    price: float = None  # Optional, only required for LIMIT or STOP_LIMIT orders.
    order_leg_collection: List[OrderLeg]
