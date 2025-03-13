from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

import msgspec

"""
Empirically derived data models from the Schwab API.
"""


@dataclass
class EquityPosition:
    # TODO: remove?
    symbol: str
    quantity: int
    current_price: float
    cost_basis: float  # averaged over all lots, if applicable
    is_long: bool
    lot_details: Optional[List[Dict]] = field(default_factory=list)


class Transaction(msgspec.Struct, kw_only=True):
    activityId: int | None = None
    time: datetime
    accountNumber: str
    type: str
    status: str
    subAccount: str
    tradeDate: datetime
    positionId: int
    orderId: int
    netAmount: float
    transferItems: List[InstrumentObj] | None = None


class InstrumentObj(msgspec.Struct, kw_only=True):
    instrument: Instrument


class Instrument(msgspec.Struct, kw_only=True):
    assetType: str | None = None
    status: str | None = None
    symbol: str | None = None
    instrumentId: int | None = None
    closingPrice: float | None = None


class AccountPosition(msgspec.Struct):
    aggregatedBalance: Dict[str, float]
    securitiesAccount: SecuritiesAccount


class SecuritiesAccount(msgspec.Struct):
    currentBalances: Dict[str, float]
    initialBalances: Dict[str, Any]
    positions: list[SchwabPosition]
    type: str


class SchwabPosition(msgspec.Struct, kw_only=True):
    """
    Response object from the Schwab API for a position within an account
    """
    averageLongPrice: float | None = None
    averagePrice: float
    averageShortPrice: float | None = None
    currentDayCost: float
    currentDayProfitLoss: float
    currentDayProfitLossPercentage: float
    instrument: SchwabInstrument
    longQuantity: float  # fractional shares?
    maintenanceRequirement: float
    marketValue: float
    previousSessionShortQuantity: float | None = None
    settledLongQuantity: float
    settledShortQuantity: float
    shortOpenProfitLoss: float | None = None
    shortQuantity: float
    taxLotAverageShortPrice: float | None = None

    def to_dict(self):
        return {f: getattr(self, f) for f in self.__struct_fields__}


class SchwabInstrument(msgspec.Struct, kw_only=True):
    cusip: str
    symbol: str
    description: str
    instrumentId: int
    netChange: float | None = None
    type: str


"""
Quote Structs
"""


class Fundamental(msgspec.Struct):
    avg10DaysVolume: Optional[float] = None
    avg1YearVolume: Optional[float] = None
    declarationDate: Optional[str] = None
    divAmount: Optional[float] = None
    divExDate: Optional[str] = None
    divFreq: Optional[int] = None
    divPayAmount: Optional[float] = None
    divPayDate: Optional[str] = None
    divYield: Optional[float] = None
    eps: Optional[float] = None
    fundLeverageFactor: Optional[float] = None
    lastEarningsDate: Optional[str] = None
    nextDivExDate: Optional[str] = None
    nextDivPayDate: Optional[str] = None
    peRatio: Optional[float] = None


class Quote(msgspec.Struct):
    _52WeekHigh: Optional[float] = None
    _52WeekLow: Optional[float] = None
    askMICId: Optional[str] = None
    askPrice: Optional[float] = None
    askSize: Optional[int] = None
    askTime: Optional[int] = None
    bidMICId: Optional[str] = None
    bidPrice: Optional[float] = None
    bidSize: Optional[int] = None
    bidTime: Optional[int] = None
    closePrice: Optional[float] = None
    highPrice: Optional[float] = None
    lastMICId: Optional[str] = None
    lastPrice: Optional[float] = None
    lastSize: Optional[int] = None
    lowPrice: Optional[float] = None
    mark: Optional[float] = None
    markChange: Optional[float] = None
    markPercentChange: Optional[float] = None
    netChange: Optional[float] = None
    netPercentChange: Optional[float] = None
    openPrice: Optional[float] = None
    postMarketChange: Optional[float] = None
    postMarketPercentChange: Optional[float] = None
    quoteTime: Optional[int] = None
    securityStatus: Optional[str] = None
    totalVolume: Optional[int] = None
    tradeTime: Optional[int] = None


class Reference(msgspec.Struct):
    cusip: Optional[str] = None
    description: Optional[str] = None
    exchange: Optional[str] = None
    exchangeName: Optional[str] = None
    htbRate: Optional[float] = None
    isHardToBorrow: Optional[bool] = None
    isShortable: Optional[bool] = None


class Regular(msgspec.Struct):
    regularMarketLastPrice: Optional[float] = None
    regularMarketLastSize: Optional[int] = None
    regularMarketNetChange: Optional[float] = None
    regularMarketPercentChange: Optional[float] = None
    regularMarketTradeTime: Optional[int] = None


class Asset(msgspec.Struct):
    assetMainType: Optional[str] = None
    assetSubType: Optional[str] = None
    fundamental: Optional[Fundamental] = None
    quote: Optional[Quote] = None
    quoteType: Optional[str] = None
    realtime: Optional[bool] = None
    reference: Optional[Reference] = None
    regular: Optional[Regular] = None
    ssid: Optional[int] = None
    symbol: Optional[str] = None


class OrderLeg(msgspec.Struct):
    orderLegType: str
    legId: int
    instrument: Instrument
    instruction: str
    positionEffect: str
    quantity: float


class Order(msgspec.Struct):
    session: str
    duration: str
    orderType: str
    cancelTime: str
    complexOrderStrategyType: str
    quantity: float
    filledQuantity: float
    remainingQuantity: float
    requestedDestination: str
    destinationLinkName: str
    price: float
    orderLegCollection: List[OrderLeg]
    orderStrategyType: str
    orderId: int
    cancelable: bool
    editable: bool
    status: str
    enteredTime: str
    accountNumber: str
