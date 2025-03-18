from typing import Dict, List, Optional, Any
import datetime
from requests import Response

import msgspec

from clearinghouse.dependencies import SchwabService
import clearinghouse.models.schwab_response as schwab_response
from clearinghouse.models.request import (
    Order,
    TransactionType,
    OrderStatus,
    AdjustmentOrder,
    PositionsFilter,
    OrdersFilter,
    TransactionsFilter,
)
from clearinghouse.models.response import (
    Quote,
    Transaction,
    SubmittedOrder,
    Position,
    PreviewOrder
)
from clearinghouse.exceptions import ForbiddenException, NullPositionException, FailedOrderException


# TODO: enforce symbol format - uppercase

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


def fetch_order_details(schwab_service: SchwabService, order_id: str) -> SubmittedOrder:
    resp = schwab_service.client.order_details(
        accountHash=schwab_service.account_hash,
        orderId=order_id,
    )
    decoded_resp = msgspec.json.decode(resp.content, type=schwab_response.Order)

    return schwab_to_ch_order(decoded_resp)


def fetch_positions(schwab_service: SchwabService, **kwargs) -> List[Position]:
    # 'positions' fields returns a flat list of positions.
    resp = schwab_service.client.account_details(accountHash=schwab_service.account_hash, fields='positions')
    decoded_resp: List[schwab_response.SchwabPosition] = (
        msgspec.json.decode(resp.text, type=List[schwab_response.SchwabPosition]))

    return [schwab_to_ch_position(p) for p in decoded_resp]


async def _place_order(schwab_service: SchwabService, order: Dict) -> Response:
    """
    Schwab API returns status 201 and empty response body if successful.
    """
    return schwab_service.client.order_place(
        accountHash=schwab_service.account_hash,
        order=order,
    )


async def place_orders(schwab_service: SchwabService, orders: List[Order]) -> (List[Order], List[Order]):
    if schwab_service.read_only_mode:
        raise ForbiddenException()

    successful_orders, failed_orders = [], []

    for order in orders:
        resp = await _place_order(schwab_service, order.model_dump())

        if resp.status_code != 201:
            failed_orders.append(order)
        else:
            successful_orders.append(order)

    return successful_orders, failed_orders


def cancel_order_request(schwab_service: SchwabService, order_id: str) -> int:
    if schwab_service.read_only_mode:
        raise ForbiddenException()

    resp = schwab_service.client.order_cancel(
        accountHash=schwab_service.account_hash,
        orderId=order_id,
    )
    return resp.status_code


def fetch_quotes(schwab_service: SchwabService, symbols: List[str]) -> List[Quote]:
    resp = schwab_service.client.quote(symbols)
    decoded_resp = msgspec.json.decode(resp.text, type=Dict[str, schwab_response.Asset])

    return [schwab_to_ch_quote(q) for q in decoded_resp.values()]


def fetch_transactions(
    schwab_service: SchwabService,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    types: Optional[List[TransactionType]] = None,
    # symbols: Optional[str] = None
) -> List[Transaction]:
    """
    Get a list of transactions for the given account using the parameters provided.

    :param schwab_service: Instantiated Schwab service
    :param start_date: Start date for filtering transactions
    :param end_date: End date for filtering transactions
    :param types: List of transaction types to filter by
    :return: List of transactions
    """
    now = datetime.datetime.now()
    start_date = start_date or (now - datetime.timedelta(days=5))
    end_date = end_date or now

    # Confirm suitability of provided transaction types
    type_strings = [t.value for t in types] if types else None

    resp = schwab_service.client.transactions(
        accountHash=schwab_service.account_hash,
        startDate=start_date,
        endDate=end_date,
        types=type_strings,
        # symbol=symbol
    )
    decoded_resp = msgspec.json.decode(resp.text, type=List[schwab_response.Transaction])

    return [schwab_to_ch_transaction(t) for t in decoded_resp]


def fetch_transaction_details(schwab_service: SchwabService, transaction_id: str) -> Transaction:
    resp = schwab_service.client.transaction_details(
        accountHash=schwab_service.account_hash,
        transactionId=transaction_id,
    )
    decoded_resp = msgspec.json.decode(resp.text, type=List[schwab_response.Transaction])

    return [schwab_to_ch_transaction(t) for t in decoded_resp][0]


async def adjust_position_fraction(
        schwab_service: SchwabService,
        symbol: str,
        fraction: float,
        round_down: bool = False,
        preview: bool = True
) -> SubmittedOrder | PreviewOrder | None:
    """
    Adjust the current holding of a security by a fraction / percentage. It will round down to the closest quantity to
    minimize buying and selling and will not open new positions by default. Use negatives for position reductions.
    TODO: address percentage reduction by lot / strategy - e.g. FIFO
    TODO: return value of stable/failed order to concrete obj
    """
    # Fetch current positions
    positions: List[Position] = fetch_positions(schwab_service)
    position = next((p for p in positions if p.symbol == symbol), None)

    if not position:
        raise NullPositionException(symbol=symbol)
    else:
        current_quantity = position.quantity

    target_quantity = current_quantity * (1 + fraction)

    if round_down:
        target_quantity = int(target_quantity)

    quantity_difference = target_quantity - current_quantity

    # Place order if there is a difference
    if quantity_difference != 0:
        order = Order(
            symbol=symbol,
            quantity=abs(quantity_difference),
            order_type="buy" if quantity_difference > 0 else "sell",
            price=position.market_value / position.quantity if position else 0  # Assuming market order
        )
        if not preview:
            successful_orders, failed_orders = await place_orders(schwab_service, [order])
            if successful_orders:
                return successful_orders[0]
            else:
                raise Exception("Order placement failed.")
        else:
            return PreviewOrder(
                symbol=symbol,
                quantity=abs(quantity_difference),
                order_type="buy" if quantity_difference > 0 else "sell",
                price=position.market_value / position.quantity if position else 0,  # Assuming market order
                duration="",
                adjustment=fraction,
            )

    return None


async def adjust_bulk_positions_fractions(
        schwab_service: SchwabService,
        orders: List[AdjustmentOrder],
        round_down: bool = False,
        preview: bool = True,
) -> Dict[str, Any]:
    """
    Adjust the current holding of many securities by the fractions specified. It will round down to the closest quantity
    to minimize buying and selling and will not open new positions by default. Use negatives for position reductions.

    """
    results = {"successful": [], "failed": [], "stable": [], "preview": []}

    for order in orders:
        try:
            processed_order = await adjust_position_fraction(
                schwab_service,
                symbol=order.symbol,
                fraction=order.adjustment,
                round_down=round_down,
                preview=preview,
            )
            print(processed_order)
            if processed_order and not preview:
                results["successful"].append(processed_order)
            elif processed_order and preview:
                results["preview"].append(processed_order)
            elif not processed_order:
                results["stable"].append(order.symbol)
        except Exception as e:
            results["failed"].append({order.symbol: e})

    return results


def filter_positions(data: List[Position], filter_request: PositionsFilter) -> List[Position]:
    """
    Filter positions by input parameters.
    """
    print(data)
    filters = [
        lambda p: p.assetType in filter_request.assetTypes if filter_request.assetTypes else True,
        lambda p: p.quantity >= 0 if not filter_request.shorts else True,
        lambda p: p.quantity <= 0 if not filter_request.longs else True,
        lambda p: p.market_value >= filter_request.minPositionSize if filter_request.minPositionSize is not None else True,
        lambda p: p.market_value <= filter_request.maxPositionSize if filter_request.maxPositionSize is not None else True,
        lambda p: p.symbol in filter_request.symbols if filter_request.symbols else True,
    ]

    filtered_data = [
        item for item in data
        if all(f(item) for f in filters)
    ]

    return filtered_data


def filter_transactions(data: List[Transaction], filter_request: TransactionsFilter) -> List[Transaction]:
    """
    Filter transactions by input parameters. Parameters not included here are done natively by the Schwab client.
    TODO: add symbol to transaction?
    """
    filters = [
        lambda t: t.type in filter_request.types if filter_request.types else True,
        # lambda t: t.symbol in filter_request.symbols if filter_request.symbols else True,
        lambda t: t.time >= filter_request.startDate if filter_request.startDate else True,
        lambda t: t.time <= filter_request.endDate if filter_request.endDate else True,
    ]

    filtered_data = [
        item for item in data
        if all(f(item) for f in filters)
    ]

    return filtered_data


def filter_orders(data: List[Order], filter_request: OrdersFilter) -> List[Order]:
    """
    Filter orders by input parameters. Parameters not included here are done natively by the Schwab client.
    """
    filters = [
        lambda o: o.symbol in filter_request.symbols if filter_request.symbols else True,
    ]

    filtered_data = [
        item for item in data
        if all(f(item) for f in filters)
    ]

    return filtered_data


"""
Mapping functions
"""

def schwab_to_ch_position(position: schwab_response.SchwabPosition) -> Position:
    # todo: helper for settling short or long position
    quantity = position.longQuantity or position.shortQuantity
    entry_value = position.averagePrice * quantity  # confirm this value

    return Position(
        symbol=position.instrument.symbol,
        asset_type=position.instrument.type,
        quantity=quantity,  # TODO: confirm how this resp is structured. see docs
        lots=[],  # TODO: confirm how this is structured in response. see docs
        market_value=position.marketValue,
        entry_value=entry_value,
        net_change=position.instrument.netChange,
        account_fraction=0,  # TODO: Add this as a calculated value
    )


def schwab_to_ch_transaction(transaction: schwab_response.Transaction) -> Transaction:
    # TODO: confirm that these are valid
    return Transaction(
        id=transaction.activityId,
        order_id=transaction.orderId,
        time=transaction.time,
        type=transaction.type,
        status=transaction.status,
        net_amount=transaction.netAmount,
        trade_date=transaction.tradeDate,
    )


def schwab_to_ch_quote(asset: schwab_response.Asset) -> Quote:
    return Quote(
        symbol=asset.symbol,
        price=asset.quote.openPrice,
        quote_time=datetime.datetime.fromtimestamp(asset.quote.quoteTime / 1000),  # epoch time
        total_volume=asset.quote.totalVolume,
        net_percentage_change=asset.quote.netPercentChange,
        bid_price=asset.quote.bidPrice,
        ask_price=asset.quote.askPrice,
    )


def schwab_to_ch_order(order: schwab_response.Order) -> SubmittedOrder:
    return SubmittedOrder(
        order_id=order.orderId,
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
