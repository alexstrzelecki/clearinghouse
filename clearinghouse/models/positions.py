from typing import List

from pydantic import BaseModel


class Position(BaseModel):
    """
    Model for current account position of an equity / derivative
    """
    symbol: str
    quantity: int  # TODO: no current use of fractional shares. Shorted shares will be negative
    current_price: float
    market_value: float
    original_price: float  # weighted average of price in case of multiple lots
    asset_type: str  # TODO: convert this to an enum


class Account(BaseModel):
    """
    Model to represent an active trading account.

    TODO: include more parameters - e.g. unrealized gains, lots, etc.
    """
    account_number: str
    hash_value: str
    positions: List[Position]
    total_account_value: float
