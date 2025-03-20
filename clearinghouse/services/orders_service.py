from typing import Dict, List, Optional, Any
import datetime
from requests import Response
import logging

import msgspec

from clearinghouse.dependencies import SchwabService
import clearinghouse.models.schwab_response as schwab_response
from clearinghouse.models.shared import (
    TransactionType,
    OrderStatus,
)
from clearinghouse.models.request import (
    Order,
    AdjustmentOrder,
    PositionsFilter,
    OrdersFilter,
    TransactionsFilter,
)
from clearinghouse.models.schwab_request import (
    SchwabOrder,
    Instrument,
    OrderLeg,
)
from clearinghouse.models.response import (
    Quote,
    Transaction,
    SubmittedOrder,
    Position,
    PreviewOrder
)
from clearinghouse.exceptions import ForbiddenException, NullPositionException, FailedOrderException


def fetch_orders(
    schwab_service: SchwabService,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    max_results: Optional[int] = 3000,
    status: Optional[OrderStatus] = None
) -> List[SubmittedOrder]:
    """
    Retrieve a list of orders for the given account using the provided parameters.

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
    status_arg = status if status else None

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
    """
    Retrieve details of a specific order by its ID.

    :param schwab_service: Instantiated Schwab service
    :param order_id: ID of the order to fetch details for
    :return: Details of the submitted order
    """
    resp = schwab_service.client.order_details(
        accountHash=schwab_service.account_hash,
        orderId=order_id,
    )
    decoded_resp = msgspec.json.decode(resp.content, type=schwab_response.Order)

    return schwab_to_ch_order(decoded_resp)


def fetch_positions(schwab_service: SchwabService, **kwargs) -> List[Position]:
    """
    Retrieve a list of positions for the given account.

    :param schwab_service: Instantiated Schwab service
    :return: List of positions

    TODO: kwargs to real filters
    """
    resp = schwab_service.client.account_details(accountHash=schwab_service.account_hash, fields='positions')
    decoded_resp: List[schwab_response.SchwabPosition] = (
        msgspec.json.decode(resp.text, type=List[schwab_response.SchwabPosition]))

    return [schwab_to_ch_position(p) for p in decoded_resp]


async def _place_order(schwab_service: SchwabService, order: Dict) -> Response:
    """
    Place an order using the Schwab API.
    Client returns status 201 and empty response body if successful.

    :param schwab_service: Instantiated Schwab service
    :param order: Order data to be placed
    :return: Response from the Schwab API
    """
    return schwab_service.client.order_place(
        accountHash=schwab_service.account_hash,
        order=order,
    )

# TODO: add overloading for adjustment, regular, and preview order
async def place_orders(schwab_service: SchwabService, orders: List[Order | AdjustmentOrder]) -> (List[Order], List[Order]):
    """
    Place multiple orders and return lists of successful and failed orders.

    :param schwab_service: Instantiated Schwab service
    :param orders: List of orders to be placed
    :return: Tuple containing lists of successful and failed orders
    """
    if schwab_service.read_only_mode:
        raise ForbiddenException()

    successful_orders, failed_orders = [], []

    for order in orders:
        resp = await _place_order(schwab_service, order_to_schwab_order(order).model_dump())

        if resp.status_code != 201:
            failed_orders.append(order)
        else:
            successful_orders.append(order)

    return successful_orders, failed_orders


def cancel_order_request(schwab_service: SchwabService, order_id: str) -> int:
    """
    Cancel an order by its ID.

    :param schwab_service: Instantiated Schwab service
    :param order_id: ID of the order to be canceled
    :return: Status code of the cancellation request
    """
    if schwab_service.read_only_mode:
        raise ForbiddenException()

    resp = schwab_service.client.order_cancel(
        accountHash=schwab_service.account_hash,
        orderId=order_id,
    )
    return resp.status_code


def fetch_quotes(schwab_service: SchwabService, symbols: List[str]) -> List[Quote]:
    """
    Retrieve quotes for a list of symbols.

    :param schwab_service: Instantiated Schwab service
    :param symbols: List of symbols to fetch quotes for
    :return: List of quotes
    """
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

    resp = schwab_service.client.transactions(
        accountHash=schwab_service.account_hash,
        startDate=start_date,
        endDate=end_date,
        types=types,
        # symbol=symbol
    )
    decoded_resp = msgspec.json.decode(resp.text, type=List[schwab_response.Transaction])

    return [schwab_to_ch_transaction(t) for t in decoded_resp]


def fetch_transaction_details(schwab_service: SchwabService, transaction_id: str) -> Transaction:
    """
    Retrieve details of a specific transaction by its ID.

    :param schwab_service: Instantiated Schwab service
    :param transaction_id: ID of the transaction to fetch details for
    :return: Details of the transaction
    """
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
    Adjust the current holding of a security by a fraction. It will round down to the closest quantity to
    minimize buying and selling and will not open new positions by default. Use negatives for position reductions.
    TODO: address percentage reduction by lot / strategy - e.g. FIFO
    TODO: return value of stable/failed order to concrete obj

    :param schwab_service: Instantiated Schwab service
    :param symbol: Symbol of the security to adjust
    :param fraction: Fraction/percentage to adjust the position by
    :param round_down: Whether to round down the quantity
    :param preview: Whether to perform a preview of the adjustment
    :return: Submitted or preview order, or None if no adjustment is needed
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
    # TODO: account for short positions -> translation back into Schwab orders
    if quantity_difference != 0.0:
        order = Order(
            symbol=symbol,
            quantity=abs(quantity_difference),
            instruction="BUY" if quantity_difference > 0 else "SELL",
            price=position.marketValue / position.quantity if position else 0  # Assuming market order
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
                price=position.marketValue / position.quantity if position else 0,  # Assuming market order
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

    :param schwab_service: Instantiated Schwab service
    :param orders: List of adjustment orders specifying symbols and fractions
    :param round_down: Whether to round down the quantity
    :param preview: Whether to perform a preview of the adjustments
    :return: Dictionary containing lists of successful, failed, stable, and preview orders
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
            if processed_order and not preview:
                results["successful"].append(processed_order)
            elif processed_order and preview:
                results["preview"].append(processed_order)
            elif not processed_order:
                results["stable"].append(order.symbol)
        except Exception as e:
            logging.warning(f"{order.model_dump()} {e}")
            results["failed"].append({order.symbol: e})

    return results


def filter_positions(data: List[Position], filter_request: PositionsFilter) -> List[Position]:
    """
    Filter positions by input parameters.

    :param data: List of positions to filter
    :param filter_request: Filtering criteria
    :return: List of filtered positions
    """
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

    :param data: List of transactions to filter
    :param filter_request: Filtering criteria
    :return: List of filtered transactions
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

    :param data: List of orders to filter
    :param filter_request: Filtering criteria
    :return: List of filtered orders
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
    """
    Convert a Schwab position response to a clearinghouse Position object.

    :param position: Schwab position response
    :return: Converted Position object
    """

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
    """
    Convert a Schwab transaction response to a clearinghouse Transaction object.

    :param transaction: Schwab transaction response
    :return: Converted Transaction object
    """
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
    """
    Convert a Schwab asset response to a clearinghouse Quote object.

    :param asset: Schwab asset response
    :return: Converted Quote object
    """
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
    """
    Convert a Schwab order response to a clearinghouse SubmittedOrder object.

    :param order: Schwab order response
    :return: Converted SubmittedOrder object
    """
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


def order_to_schwab_order(order: Order) -> SchwabOrder:
    """
    Convert a simplified Order Request to a Schwab API-compliant SchwabOrder object.

    :param order: Simplified Order request
    :return: SchwabOrder object

    TODO: account for options requests.
    TODO: account for multiple order legs per order
    """
    instrument = Instrument(
        symbol=order.symbol,
        assetType=order.assetType,
    )
    order_leg = OrderLeg(
        instruction=order.instruction,
        quantity=order.quantity,
        instrument=instrument,
    )
    return SchwabOrder(
        orderType=order.orderType,
        session=order.session,
        duration=order.duration,
        orderStrategyType=order.strategyType,
        price=order.price,
        orderLegCollection=[order_leg],
    )
