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
    activity_id: int | None = msgspec.field(default=None, name="activityId")
    time: datetime
    account_number: str = msgspec.field(name="accountNumber")
    type: str
    status: str
    sub_account: str = msgspec.field(name="subAccount")
    trade_date: datetime = msgspec.field(name="tradeDate")
    position_id: int = msgspec.field(name="positionId")
    order_id: int = msgspec.field(name="orderId")
    net_amount: float = msgspec.field(name="netAmount")
    transfer_items: List[InstrumentObj] | None = msgspec.field(default=None, name="transferItems")


class InstrumentObj(msgspec.Struct, kw_only=True):
    instrument: Instrument


class Instrument(msgspec.Struct, kw_only=True):
    asset_type: str | None = msgspec.field(default=None, name="assetType")
    status: str | None = None
    symbol: str | None = None
    instrument_id: int | None = msgspec.field(default=None, name="instrumentId")
    closing_price: float | None = msgspec.field(default=None, name="closingPrice")


class AccountPosition(msgspec.Struct):
    aggregated_balance: Dict[str, float] = msgspec.field(name="aggregatedBalance")
    securities_account: SecuritiesAccount = msgspec.field(name="securitiesAccount")


class SecuritiesAccount(msgspec.Struct):
    current_balances: Dict[str, float] = msgspec.field(name="currentBalances")
    initial_balances: Dict[str, Any] = msgspec.field(name="initialBalances")
    positions: list[SchwabPosition]
    type: str


class SchwabPosition(msgspec.Struct, kw_only=True):
    """
    Response object from the Schwab API for a position within an account
    """
    average_long_price: float | None = msgspec.field(default=None, name="averageLongPrice")
    average_price: float = msgspec.field(name="averagePrice")
    average_short_price: float | None = msgspec.field(default=None, name="averageShortPrice")
    current_day_cost: float = msgspec.field(name="currentDayCost")
    current_day_profit_loss: float = msgspec.field(name="currentDayProfitLoss")
    current_day_profit_loss_percentage: float = msgspec.field(name="currentDayProfitLossPercentage")
    instrument: SchwabInstrument
    long_quantity: float = msgspec.field(name="longQuantity")  # fractional shares?
    maintenance_requirement: float = msgspec.field(name="maintenanceRequirement")
    market_value: float = msgspec.field(name="marketValue")
    previous_session_short_quantity: float | None = msgspec.field(default=None, name="previousSessionShortQuantity")
    settled_long_quantity: float = msgspec.field(name="settledLongQuantity")
    settled_short_quantity: float = msgspec.field(name="settledShortQuantity")
    short_open_profit_loss: float | None = msgspec.field(default=None, name="shortOpenProfitLoss")
    short_quantity: float = msgspec.field(name="shortQuantity")
    tax_lot_average_short_price: float | None = msgspec.field(default=None, name="taxLotAverageShortPrice")

    def to_dict(self):
        return {f: getattr(self, f) for f in self.__struct_fields__}


class SchwabInstrument(msgspec.Struct, kw_only=True):
    cusip: str
    symbol: str
    description: str
    instrument_id: int = msgspec.field(name="instrumentId")
    net_change: float | None = msgspec.field(default=None, name="netChange")
    type: str  # TODO: determine the real response type - doc disagreement on assetType vs. type


"""
Quote Structs
"""


class Fundamental(msgspec.Struct):
    avg_10_days_volume: Optional[float] = msgspec.field(default=None, name="avg10DaysVolume")
    avg_1_year_volume: Optional[float] = msgspec.field(default=None, name="avg1YearVolume")
    declaration_date: Optional[str] = msgspec.field(default=None, name="declarationDate")
    div_amount: Optional[float] = msgspec.field(default=None, name="divAmount")
    div_ex_date: Optional[str] = msgspec.field(default=None, name="divExDate")
    div_freq: Optional[int] = msgspec.field(default=None, name="divFreq")
    div_pay_amount: Optional[float] = msgspec.field(default=None, name="divPayAmount")
    div_pay_date: Optional[str] = msgspec.field(default=None, name="divPayDate")
    div_yield: Optional[float] = msgspec.field(default=None, name="divYield")
    eps: Optional[float] = None
    fund_leverage_factor: Optional[float] = msgspec.field(default=None, name="fundLeverageFactor")
    last_earnings_date: Optional[str] = msgspec.field(default=None, name="lastEarningsDate")
    next_div_ex_date: Optional[str] = msgspec.field(default=None, name="nextDivExDate")
    next_div_pay_date: Optional[str] = msgspec.field(default=None, name="nextDivPayDate")
    pe_ratio: Optional[float] = msgspec.field(default=None, name="peRatio")


class Quote(msgspec.Struct):
    week_52_high: Optional[float] = msgspec.field(default=None, name="_52WeekHigh")
    week_52_low: Optional[float] = msgspec.field(default=None, name="_52WeekLow")
    ask_mic_id: Optional[str] = msgspec.field(default=None, name="askMICId")
    ask_price: Optional[float] = msgspec.field(default=None, name="askPrice")
    ask_size: Optional[int] = msgspec.field(default=None, name="askSize")
    ask_time: Optional[int] = msgspec.field(default=None, name="askTime")
    bid_mic_id: Optional[str] = msgspec.field(default=None, name="bidMICId")
    bid_price: Optional[float] = msgspec.field(default=None, name="bidPrice")
    bid_size: Optional[int] = msgspec.field(default=None, name="bidSize")
    bid_time: Optional[int] = msgspec.field(default=None, name="bidTime")
    close_price: Optional[float] = msgspec.field(default=None, name="closePrice")
    high_price: Optional[float] = msgspec.field(default=None, name="highPrice")
    last_mic_id: Optional[str] = msgspec.field(default=None, name="lastMICId")
    last_price: Optional[float] = msgspec.field(default=None, name="lastPrice")
    last_size: Optional[int] = msgspec.field(default=None, name="lastSize")
    low_price: Optional[float] = msgspec.field(default=None, name="lowPrice")
    mark: Optional[float] = None
    mark_change: Optional[float] = msgspec.field(default=None, name="markChange")
    mark_percent_change: Optional[float] = msgspec.field(default=None, name="markPercentChange")
    net_change: Optional[float] = msgspec.field(default=None, name="netChange")
    net_percent_change: Optional[float] = msgspec.field(default=None, name="netPercentChange")
    open_price: Optional[float] = msgspec.field(default=None, name="openPrice")
    post_market_change: Optional[float] = msgspec.field(default=None, name="postMarketChange")
    post_market_percent_change: Optional[float] = msgspec.field(default=None, name="postMarketPercentChange")
    quote_time: Optional[int] = msgspec.field(default=None, name="quoteTime")
    security_status: Optional[str] = msgspec.field(default=None, name="securityStatus")
    total_volume: Optional[int] = msgspec.field(default=None, name="totalVolume")
    trade_time: Optional[int] = msgspec.field(default=None, name="tradeTime")


class Reference(msgspec.Struct):
    cusip: Optional[str] = None
    description: Optional[str] = None
    exchange: Optional[str] = None
    exchange_name: Optional[str] = msgspec.field(default=None, name="exchangeName")
    htb_rate: Optional[float] = msgspec.field(default=None, name="htbRate")
    is_hard_to_borrow: Optional[bool] = msgspec.field(default=None, name="isHardToBorrow")
    is_shortable: Optional[bool] = msgspec.field(default=None, name="isShortable")


class Regular(msgspec.Struct):
    regular_market_last_price: Optional[float] = msgspec.field(default=None, name="regularMarketLastPrice")
    regular_market_last_size: Optional[int] = msgspec.field(default=None, name="regularMarketLastSize")
    regular_market_net_change: Optional[float] = msgspec.field(default=None, name="regularMarketNetChange")
    regular_market_percent_change: Optional[float] = msgspec.field(default=None, name="regularMarketPercentChange")
    regular_market_trade_time: Optional[int] = msgspec.field(default=None, name="regularMarketTradeTime")


class Asset(msgspec.Struct):
    asset_main_type: Optional[str] = msgspec.field(default=None, name="assetMainType")
    asset_sub_type: Optional[str] = msgspec.field(default=None, name="assetSubType")
    fundamental: Optional[Fundamental] = None
    quote: Optional[Quote] = None
    quote_type: Optional[str] = msgspec.field(default=None, name="quoteType")
    realtime: Optional[bool] = None
    reference: Optional[Reference] = None
    regular: Optional[Regular] = None
    ssid: Optional[int] = None
    symbol: Optional[str] = None


class OrderLeg(msgspec.Struct):
    order_leg_type: str = msgspec.field(name="orderLegType")
    leg_id: int = msgspec.field(name="legId")
    instrument: Instrument
    instruction: str
    position_effect: str = msgspec.field(name="positionEffect")
    quantity: float


class Order(msgspec.Struct):
    session: str
    duration: str
    order_type: str = msgspec.field(name="orderType")
    cancel_time: str = msgspec.field(name="cancelTime")
    complex_order_strategy_type: str = msgspec.field(name="complexOrderStrategyType")
    quantity: float
    filled_quantity: float = msgspec.field(name="filledQuantity")
    remaining_quantity: float = msgspec.field(name="remainingQuantity")
    requested_destination: str = msgspec.field(name="requestedDestination")
    destination_link_name: str = msgspec.field(name="destinationLinkName")
    price: float
    order_leg_collection: List[OrderLeg] = msgspec.field(name="orderLegCollection")
    order_strategy_type: str = msgspec.field(name="orderStrategyType")
    order_id: int = msgspec.field(name="orderId")
    cancelable: bool
    editable: bool
    status: str
    entered_time: str = msgspec.field(name="enteredTime")
    account_number: str = msgspec.field(name="accountNumber")
