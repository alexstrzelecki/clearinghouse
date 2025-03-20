from typing import Optional, List, Self, Dict
import datetime
import logging

from pydantic import BaseModel, Field, model_validator

from clearinghouse.models.shared import (
    OrderInstruction,
    OrderDuration,
    OrderType,
    OrderStatus,
    TransactionType,
    AssetType,
    OrderSession,
    OrderStrategyType,
)

"""
Models to be used in clearinghouse requests
"""

def _to_upper(fields: List[str], data: Dict[str, str]) -> Dict[str, str]:
    """
    Validation util to force strings to upper case to match the literals
    """
    if isinstance(data, BaseModel):
        data = data.model_dump()

    if not isinstance(data, dict):
        logging.error("Input is not valid JSON", type(data))
        raise ValueError("Input is not JSON")

    for field in fields:
        if field in data.keys():
            data[field] = data[field].upper()

    return data

def _split_comma_sep_string(fields: List[str], data: Dict[str, str]) -> Dict[str, str]:
    """
    Validation util to force a comma-delimited string to a list.
    """
    for field in fields:
        items = []
        for item in data.get(field, []):
            items += item.split(",")
        data[field] = items
    return data


class BaseOrder(BaseModel):
    symbol: str
    price: float
    order_type: OrderType = Field(default="MARKET")
    duration: OrderDuration = Field(default="DAY")
    asset_type: AssetType = Field(default="EQUITY")
    session: OrderSession = Field(default="NORMAL")
    strategy_type: OrderStrategyType = Field(default="SINGLE")

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def to_upper(cls, data):
        return _to_upper(["symbol", "order_type", "duration", "asset_type"], data)

class Order(BaseOrder):
    instruction: OrderInstruction
    quantity: float

    @model_validator(mode="after")
    def check_entries(self) -> Self:
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        return self

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def to_upper(cls, data):
        return _to_upper(["instruction", "symbol", "order_type", "duration", "asset_type"], data)

class AdjustmentOrder(BaseOrder):
    """
    Model representing orders to adjust currently held securities.

    adjustment: Fraction increase/decrease in a position
        e.g. 0.5 for 50% increase.
    """
    adjustment: float

    @model_validator(mode="after")
    def check_entries(self) -> Self:
        if self.adjustment < -1:
            raise ValueError("Cannot sell more than entire position.")
        return self


class PositionsFilter(BaseModel):
    asset_types: Optional[List[str]] = None
    shorts: Optional[bool] = True
    longs: Optional[bool] = True
    min_position_size: Optional[float] = None
    max_position_size: Optional[float] = None
    symbols: Optional[List[str]] = None

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def split_comma_separated_string(cls, data):
        """FastAPI not splitting values on , by default"""
        return _split_comma_sep_string(["symbols"], data)


class OrdersFilter(BaseModel):
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    max_results: Optional[int] = None
    status: Optional[OrderStatus] = None
    symbols: Optional[List[str]] = None

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def split_comma_separated_string(cls, data):
        """FastAPI not splitting values on , by default"""
        return _split_comma_sep_string(["symbols"], data)


class TransactionsFilter(BaseModel):
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    types: Optional[List[TransactionType]] = None
    symbols: Optional[List[str]] = None

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def split_comma_separated_string(cls, data):
        """FastAPI not splitting values on , by default"""
        return _split_comma_sep_string(["symbols"], data)
