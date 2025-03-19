from typing import Optional, List, Self, Dict
import datetime
import logging

from pydantic import BaseModel, Field, model_validator, field_validator

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
    symbol: str = Field(..., alias="symbol")
    price: float = Field(..., alias="price")
    orderType: OrderType = Field(default="MARKET")
    duration: OrderDuration = Field(default="DAY", alias="duration")
    assetType: AssetType = Field(default="EQUITY")
    session: OrderSession = Field(default="NORMAL")
    strategyType: OrderStrategyType = Field(default="SINGLE")

    @model_validator(mode="before")
    def to_upper(cls, data):
        return _to_upper(["symbol", "orderType", "duration", "assetType"], data)

class Order(BaseOrder):
    instruction: OrderInstruction = Field(..., alias="instruction")
    quantity: float = Field(..., alias="quantity")

    @model_validator(mode="after")
    def check_entries(self) -> Self:
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        return self

    @model_validator(mode="before")
    def to_upper(cls, data):
        return _to_upper(["instruction", "symbol", "orderType", "duration", "assetType"], data)

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
    assetTypes: Optional[List[str]] = None
    shorts: Optional[bool] = True
    longs: Optional[bool] = True
    minPositionSize: Optional[float] = None
    maxPositionSize: Optional[float] = None
    symbols: Optional[List[str]] = None

    @model_validator(mode='before')
    def split_comma_separated_string(cls, data):
        """FastAPI not splitting values on , by default"""
        return _split_comma_sep_string(["symbols"], data)


class OrdersFilter(BaseModel):
    startDate: Optional[datetime.datetime] = None
    endDate: Optional[datetime.datetime] = None
    maxResults: Optional[int] = None
    status: Optional[OrderStatus] = None
    symbols: Optional[List[str]] = None

    @model_validator(mode='before')
    def split_comma_separated_string(cls, data):
        """FastAPI not splitting values on , by default"""
        return _split_comma_sep_string(["symbols"], data)


class TransactionsFilter(BaseModel):
    startDate: Optional[datetime.datetime] = None
    endDate: Optional[datetime.datetime] = None
    types: Optional[List[TransactionType]] = None
    symbols: Optional[List[str]] = None

    @model_validator(mode='before')
    def split_comma_separated_string(cls, data):
        """FastAPI not splitting values on , by default"""
        return _split_comma_sep_string(["symbols"], data)
