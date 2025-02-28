from typing import Dict, List
import datetime

import msgspec

from clearinghouse.dependencies import SchwabService
# import clearinghouse.models.schwab_request
import clearinghouse.models.schwab_response as schwab_response
from clearinghouse.models.request import (
    Order
)
from clearinghouse.models.response import (
    Quote,
    Transaction,
    SubmittedOrder,
    Position
)
# from clearinghouse.models.request import


# TODO: enforce ticker format - uppercase

def fetch_orders(schwab_service: SchwabService, **kwargs) -> List[SubmittedOrder]:
    # add filter flags
    now = datetime.datetime.now()
    resp = schwab_service.client.account_orders(
        accountHash=schwab_service.account_hash,
        fromEnteredTime=now - datetime.timedelta(days=5),
        toEnteredTime=now,
        # status=#submitted
   )
    # decoded_resp = msgspec.json.decode(resp.content, type=schwab_response.)

    # TODO: create a msgspec struct for Schwab Orders

    return []


def fetch_positions(schwab_service: SchwabService, **kwargs) -> List[Position]:
    # 'positions' fields returns a flat list of positions.
    resp = schwab_service.client.account_details(accountHash=schwab_service.account_hash, fields='positions')
    decoded_resp: List[schwab_response.SchwabPosition] = (
        msgspec.json.decode(resp.text, type=List[schwab_response.SchwabPosition]))

    return [schwab_to_ch_position(p) for p in decoded_resp]


def place_order(schwab_service: SchwabService, order: Order) -> SubmittedOrder:
    pass


def place_orders(schwab_service: SchwabService, orders: List[Order]) -> List[SubmittedOrder]:
    pass


def place_bulk_orders(schwab_service: SchwabService, orders: List[Order]) -> List[SubmittedOrder]:
    pass


def fetch_quote(schwab_service: SchwabService, ticker: str) -> Quote:
    # TODO: Add error handling
    resp = schwab_service.client.quote(ticker)
    decoded_resp = msgspec.json.decode(resp.text, type=Dict[str, schwab_response.Asset])

    return schwab_to_ch_quote(decoded_resp.get(ticker))


def fetch_quotes(schwab_service: SchwabService, tickers: List[str]) -> List[Quote]:
    resp = schwab_service.client.quote(tickers)
    decoded_resp = msgspec.json.decode(resp.text, type=Dict[str, schwab_response.Asset])

    return [schwab_to_ch_quote(q) for q in decoded_resp.values()]


def fetch_transactions() -> List[Transaction]:
    pass


def schwab_to_ch_position(position: schwab_response.SchwabPosition) -> Position:
    # todo: helper for settling short or long position
    quantity = position.longQuantity or position.shortQuantity
    entry_value = position.averagePrice * quantity  # confirm this value

    return Position(
        ticker=position.instrument.symbol,
        quantity=quantity,  # TODO: confirm how this resp is structured. see docs
        lots=[],  # TODO: confirm how this is structured in response. see docs
        market_value=position.marketValue,
        entry_value=entry_value,
        net_change=position.instrument.netChange,
        account_fraction=0,  # TODO: find if this is in the API response. Can see this in the UI as a calculated value.
    )


def schwab_to_ch_transaction(transaction: schwab_response.Transaction) -> Transaction:
    pass


def schwab_to_ch_quote(asset: schwab_response.Asset) -> Quote:
    return Quote(
        ticker=asset.symbol,
        price=asset.quote.openPrice,
        quote_time=datetime.datetime.fromtimestamp(asset.quote.quoteTime / 1000),  # epoch time
        total_volume=asset.quote.totalVolume,
        net_percentage_change=asset.quote.netPercentChange,  # TODO: confirm this in schwab docs
        bid_price=asset.quote.bidPrice,
        ask_price=asset.quote.askPrice,
    )
