from typing import Dict, List, Optional
import datetime

import msgspec

from clearinghouse.dependencies import SchwabService
import clearinghouse.models.schwab_response as schwab_response
from clearinghouse.models.request import (
    Order,
    TransactionType,
    OrderStatus,
)
from clearinghouse.models.response import (
    Quote,
    Transaction,
    SubmittedOrder,
    Position
)
from clearinghouse.exceptions import ForbiddenException


# TODO: enforce ticker format - uppercase

def fetch_orders(
    schwab_service: SchwabService,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    max_results: Optional[int] = 3000,
    status: Optional[OrderStatus] = None
) -> List[SubmittedOrder]:
    """
    Get a list of orders for the given account using the parameters provided.

    :param schwab_service: Instantiated Schwab service
    :param start_date: Start date for filtering orders
    :param end_date: End date for filtering orders
    :param max_results: Maximum number of orders to retrieve
    :param status: Status of orders to filter by
    :return: List of submitted orders
    """
    now = datetime.datetime.now()
    start_date = start_date or (now - datetime.timedelta(days=5))
    end_date = end_date or now

    # Enforce status option via Enum
    status_arg = status.value if status else None

    resp = schwab_service.client.account_orders(
        accountHash=schwab_service.account_hash,
        fromEnteredTime=start_date.isoformat(),
        toEnteredTime=end_date.isoformat(),
        maxResults=max_results,
        status=status_arg,
    )
    decoded_resp = msgspec.json.decode(resp.content, type=List[schwab_response.Order])

    return [schwab_to_ch_order(k) for k in decoded_resp]


def fetch_positions(schwab_service: SchwabService, **kwargs) -> List[Position]:
    # 'positions' fields returns a flat list of positions.
    resp = schwab_service.client.account_details(accountHash=schwab_service.account_hash, fields='positions')
    decoded_resp: List[schwab_response.SchwabPosition] = (
        msgspec.json.decode(resp.text, type=List[schwab_response.SchwabPosition]))

    return [schwab_to_ch_position(p) for p in decoded_resp]


def place_order(schwab_service: SchwabService, order: Order) -> SubmittedOrder:
    if schwab_service.read_only_mode:
        raise ForbiddenException()

    return None

def place_orders(schwab_service: SchwabService, orders: List[Order]) -> List[SubmittedOrder]:
    if schwab_service.read_only_mode:
        raise ForbiddenException()

    return None


def place_bulk_orders(schwab_service: SchwabService, orders: List[Order]) -> List[SubmittedOrder]:
    if schwab_service.read_only_mode:
        raise ForbiddenException()

    return None


def fetch_quote(schwab_service: SchwabService, ticker: str) -> Quote:
    # TODO: Add error handling
    resp = schwab_service.client.quote(ticker)
    decoded_resp = msgspec.json.decode(resp.text, type=Dict[str, schwab_response.Asset])

    return schwab_to_ch_quote(decoded_resp.get(ticker))


def fetch_quotes(schwab_service: SchwabService, tickers: List[str]) -> List[Quote]:
    resp = schwab_service.client.quote(tickers)
    decoded_resp = msgspec.json.decode(resp.text, type=Dict[str, schwab_response.Asset])

    return [schwab_to_ch_quote(q) for q in decoded_resp.values()]


def fetch_transactions(
    schwab_service: SchwabService,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    types: Optional[List[TransactionType]] = None,
    ticker: Optional[str] = None
) -> List[Transaction]:
    """
    Get a list of transactions for the given account using the parameters provided.

    :param schwab_service: Instantiated Schwab service
    :param start_date: Start date for filtering transactions
    :param end_date: End date for filtering transactions
    :param types: List of transaction types to filter by
    :param ticker: Ticker symbol to filter transactions
    :return: List of transactions
    """
    now = datetime.datetime.now()
    start_date = start_date or (now - datetime.timedelta(days=5))
    end_date = end_date or now

    # Confirm suitability of provided transaction types
    type_strings = [t.value for t in types] if types else None

    resp = schwab_service.client.transactions(
        accountHash=schwab_service.account_hash,
        fromEnteredTime=start_date,
        toEnteredTime=end_date,
        types=type_strings,
        ticker=ticker
    )
    decoded_resp = msgspec.json.decode(resp.text, type=List[schwab_response.Transaction])

    return [schwab_to_ch_transaction(t) for t in decoded_resp]


def fetch_transaction_details(schwab_service: SchwabService, transaction_id: str) -> Transaction:
    raise NotImplementedError("Util function not implemented.")


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
    return Transaction(
        id=transaction.activityId,
        time=transaction.time,
        type=transaction.type,
        status=transaction.status,
        net_amount=transaction.netAmount,
        trade_date=transaction.tradeDate,
    )


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


def schwab_to_ch_order(order: schwab_response.Order) -> SubmittedOrder:
    return SubmittedOrder(
        order_id=str(order.orderId),  # TODO: Confirm if str or int
        is_filled=(order.filledQuantity == order.quantity),
        total=order.price * order.quantity,
        duration=order.duration,
        order_type=order.orderType,
        price=order.price,
        quantity=order.quantity,
        filled_quantity=order.filledQuantity,
        remaining_quantity=order.remainingQuantity,
        status=order.status,
        entered_time=datetime.datetime.strptime(order.enteredTime, "%Y-%m-%dT%H:%M:%S%z"),
        cancel_time=datetime.datetime.strptime(order.cancelTime, "%Y-%m-%dT%H:%M:%S%z"),
        session=order.session,
        cancelable=order.cancelable
    )
