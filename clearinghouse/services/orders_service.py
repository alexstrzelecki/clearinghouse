from typing import Dict, List, Optional, get_args, Final, Set, overload
import datetime
from requests import Response
import logging

import msgspec
import cachetools

from clearinghouse.dependencies import SchwabService
import clearinghouse.models.schwab_response as schwab_response
from clearinghouse.models.shared import (
    TransactionType,
    OrderStatus,
)
from clearinghouse.models.request import (
    NumericalOrder,
    AdjustmentOrder,
    PositionsFilter,
    OrdersFilter,
    TransactionsFilter, FractionalOrder,
)
from clearinghouse.models.schwab_request import (
    SchwabOrder,
    Instrument,
    OrderLeg,
)
from clearinghouse.models.response import (
    Quote,
    Transaction,
    StandardOrder,
    Position,
    AdjustmentOrderResult,
    InitialOrderStatus,
    OrderResult,
)
from clearinghouse.services.status_service import fetch_account_status
from clearinghouse.exceptions import ForbiddenException, NullPositionException, FailedOrderException


def fetch_orders(
    schwab_service: SchwabService,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    max_results: Optional[int] = 3000,
    status: Optional[OrderStatus] = None
) -> List[StandardOrder]:
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


def fetch_order_details(schwab_service: SchwabService, order_id: str) -> StandardOrder:
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


def fetch_positions(schwab_service: SchwabService, symbols: Optional[Set[str]] = None, **kwargs) -> List[Position]:
    """
    Retrieve a list of positions for the given account.

    :param schwab_service: Instantiated Schwab service
    :param symbols: Optional list of symbols to filter positions by
    :return: List of positions

    TODO: kwargs to real filters
    """
    resp = schwab_service.client.account_details(accountHash=schwab_service.account_hash, fields='positions')
    decoded_resp: List[schwab_response.SchwabPosition] = (
        msgspec.json.decode(resp.text, type=List[schwab_response.SchwabPosition]))

    if symbols:
        decoded_resp = [p for p in decoded_resp if p.instrument.symbol in symbols]
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


def fetch_total_account_value(schwab_service: SchwabService, longs: bool = True, shorts: bool = True, **kwargs) -> float:
    """
    Get the total account value of the default trading account. Can filter by longs or shorts
    to get a narrowed version (e.g. liquidationValue, shortBalance, longStockValue)
    """
    account_status = fetch_account_status(schwab_service)
    account_value = 0

    # TODO: confirm the attr definitions from Schwab API
    if longs and shorts:
        account_value = account_status.current_balances.get("liquidationValue", 0)

    if longs:
        account_value = account_status.current_balances.get("longMarketValue", 0)

    if shorts:
        account_value = account_status.current_balances.get("shortMarketValue", 0)

    if account_value == 0:
        logging.warning("Account value appearing as 0 - confirm manually")

    return account_value

@overload
def calculate_account_fraction(schwab_service: SchwabService, *, position: Position) -> float:
    ...

@overload
def calculate_account_fraction(schwab_service: SchwabService, *, symbol: str) -> float:
    ...

def calculate_account_fraction(
    schwab_service: SchwabService,
    position: Optional[Position] = None,
    symbol: Optional[str] = None
) -> float:
    """
    Calculate the current account fraction of a symbol or position.
    Either 'position' or 'symbol' must be provided, but not both.
    """
    if position is None and symbol is None:
        raise ValueError("Either 'position' or 'symbol' must be provided.")

    if position is not None and symbol is not None:
        raise ValueError("Only one of 'position' or 'symbol' should be provided.")

    # Fetch positions if only symbol is provided
    if symbol is not None:
        positions = fetch_positions(schwab_service, symbols={symbol})
        position = positions[0] if positions else None

    if not position:
        return 0.0

    # Example calculation logic (replace with actual logic)
    total_account_value = 1000  # TODO: calculate this using a combination of longMarketValue, equity, etc.
    return position.market_value / total_account_value if total_account_value > 0 else 0.0


def _convert_fractional_to_numerical_order(schwab_service: SchwabService, order: FractionalOrder) -> NumericalOrder:
    """
    Realize a fractional portfolio request into an order that the Schwab API can accept.

    :param order: FractionalOrder object containing the desired fractional position
    :return: NumericalOrder object ready for submission to the Schwab API
    """
    # get current account value

    # get current positional value and determine if it needs to be a sell/buy order

    # get quote for the current price

    # convert the delta into an actual order


    # Get current positions
    positions = fetch_positions(schwab_service, {})
    position = next((p for p in positions if p.symbol == order.symbol), None)

    # If no current position, assume zero
    current_quantity = position.quantity if position else 0

    # Get the current quote for the symbol
    quotes = fetch_quotes(schwab_service, [order.symbol])
    current_price = quotes[0].price if quotes else 0

    # Calculate the target quantity based on the fractional order
    target_quantity = order.fraction * (current_quantity * current_price)

    # Determine the quantity difference
    quantity_difference = target_quantity - current_quantity

    # Determine the instruction (buy/sell) based on the quantity difference
    instruction: Final[str] = "BUY" if quantity_difference > 0 else "SELL"

    # Create a NumericalOrder based on the calculated values
    numerical_order = NumericalOrder(
        symbol=order.symbol,
        quantity=abs(quantity_difference),
        instruction=instruction,
        price=current_price,
        order_type="LIMIT",  # Assuming limit order; adjust as necessary
        duration="DAY",      # Assuming day order; adjust as necessary
        session="NORMAL"     # Assuming normal session; adjust as necessary
    )

    return numerical_order


# TODO: add overloading for adjustment, regular, and preview order
async def place_orders(schwab_service: SchwabService, orders: List[NumericalOrder]) -> (List[OrderResult], Dict[str, int]):
    """
    Place multiple orders and return lists of successful and failed orders.

    :param schwab_service: Instantiated Schwab service
    :param orders: List of orders to be placed
    :return: Tuple containing lists of successful and failed orders
    """
    if schwab_service.read_only_mode:
        raise ForbiddenException()

    results = []
    count = {k: 0 for k in get_args(InitialOrderStatus)}

    for order in orders:
        resp = await _place_order(schwab_service, order_to_schwab_order(order).model_dump())

        if resp.status_code == 201:
            results.append(OrderResult(**order.model_dump(), status="SUCCEEDED"))
            count["SUCCEEDED"] += 1
        else:
            results.append(OrderResult(**order.model_dump(), status="FAILED"))
            count["FAILED"] += 1

    return results, count


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
) -> AdjustmentOrderResult:
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
    positions: List[Position] = fetch_positions(schwab_service)
    position = next((p for p in positions if p.symbol == symbol), None)

    if not position:
        return AdjustmentOrderResult(
            symbol=symbol,
            adjustment=fraction,
            quantity=0,
            total_position_size=0,
            status="FAILED",
            info="No existing position"
        )
    else:
        current_quantity = position.quantity

    target_quantity = current_quantity * (1 + fraction)

    if round_down:
        target_quantity = int(target_quantity)

    quantity_difference = target_quantity - current_quantity

    # Place order if there is a difference
    # TODO: account for short positions -> translation back into Schwab orders
    # TODO: account for market vs. limit orders - default for setting the price
    #
    kwargs = {
        "symbol": symbol,
        "quantity": abs(quantity_difference),
        "instruction": "BUY" if quantity_difference > 0 else "SELL",
    }
    total_position_size = kwargs["quantity"] + current_quantity
    if quantity_difference != 0.0:
        if not preview:
            successful_orders: List[NumericalOrder]
            results, _ = await place_orders(schwab_service, [NumericalOrder(**kwargs)])
            if results[0].status == "FAILED":
                return AdjustmentOrderResult(
                    total_position_size=total_position_size,
                    status="FAILED",
                    info="Misc. failure"
                    **kwargs
                )

        return AdjustmentOrderResult(
            total_position_size=total_position_size,
            adjustment=fraction,
            status="PREVIEW" if preview else "SUCCEEDED",
            **kwargs
        )
    else:
        return AdjustmentOrderResult(
            total_position_size=total_position_size,
            adjustment=fraction,
            status="IGNORED",
            **kwargs
        )

async def adjust_bulk_positions_fractions(
        schwab_service: SchwabService,
        orders: List[AdjustmentOrder],
        round_down: bool = False,
        preview: bool = True,
) -> (List[AdjustmentOrderResult], Dict[str, int]):
    """
    Adjust the current holding of many securities by the fractions specified. It will round down to the closest quantity
    to minimize buying and selling and will not open new positions by default. Use negatives for position reductions.

    :param schwab_service: Instantiated Schwab service
    :param orders: List of adjustment orders specifying symbols and fractions
    :param round_down: Whether to round down the quantity
    :param preview: Whether to perform a preview of the adjustments
    :return: List containing of successful, failed, stable, and preview orders; Dict of the result counts
    """
    results = []
    count = {k: 0 for k in get_args(InitialOrderStatus)}

    for order in orders:
        processed_order = await adjust_position_fraction(
            schwab_service,
            symbol=order.symbol,
            fraction=order.adjustment,
            round_down=round_down,
            preview=preview,
        )
        results.append(processed_order)
        count[processed_order.status] += 1

    return results, count


def filter_positions(data: List[Position], filter_request: PositionsFilter) -> List[Position]:
    """
    Filter positions by input parameters.

    :param data: List of positions to filter
    :param filter_request: Filtering criteria
    :return: List of filtered positions
    """
    filters = [
        lambda p: p.asset_type in filter_request.asset_types if filter_request.asset_types else True,
        lambda p: p.quantity >= 0 if not filter_request.shorts else True,
        lambda p: p.quantity <= 0 if not filter_request.longs else True,
        lambda p: p.market_value >= filter_request.min_position_size if filter_request.min_position_size is not None else True,
        lambda p: p.market_value <= filter_request.max_position_size if filter_request.max_position_size is not None else True,
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
        lambda t: t.time >= filter_request.start_date if filter_request.start_date else True,
        lambda t: t.time <= filter_request.end_date if filter_request.end_date else True,
    ]

    filtered_data = [
        item for item in data
        if all(f(item) for f in filters)
    ]

    return filtered_data


def filter_orders(data: List[NumericalOrder], filter_request: OrdersFilter) -> List[NumericalOrder]:
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
    quantity = position.long_quantity or position.short_quantity
    entry_value = position.average_price * quantity  # confirm this value

    return Position(
        symbol=position.instrument.symbol,
        asset_type=position.instrument.type,
        quantity=quantity,  # TODO: confirm how this resp is structured. see docs
        lots=[],  # TODO: confirm how this is structured in response. see docs
        market_value=position.market_value,
        entry_value=entry_value,
        net_change=position.instrument.net_change,
        # account_fraction=calculate_account_fraction(schwab_service, position=position),
    )


def schwab_to_ch_transaction(transaction: schwab_response.Transaction) -> Transaction:
    """
    Convert a Schwab transaction response to a clearinghouse Transaction object.

    :param transaction: Schwab transaction response
    :return: Converted Transaction object
    """
    # TODO: confirm that these are valid
    return Transaction(
        id=transaction.activity_id,
        order_id=transaction.order_id,
        time=transaction.time,
        type=transaction.type,
        status=transaction.status,
        net_amount=transaction.net_amount,
        trade_date=transaction.trade_date,
    )


def schwab_to_ch_quote(asset: schwab_response.Asset) -> Quote:
    """
    Convert a Schwab asset response to a clearinghouse Quote object.

    :param asset: Schwab asset response
    :return: Converted Quote object
    """
    return Quote(
        symbol=asset.symbol,
        price=asset.quote.open_price,
        quote_time=datetime.datetime.fromtimestamp(asset.quote.quote_time / 1000),  # epoch time
        total_volume=asset.quote.total_volume,
        net_percent_change=asset.quote.net_percent_change,
        bid_price=asset.quote.bid_price,
        ask_price=asset.quote.ask_price,
    )


def schwab_to_ch_order(order: schwab_response.Order) -> StandardOrder:
    """
    Convert a Schwab order response to a clearinghouse SubmittedOrder object.

    :param order: Schwab order response
    :return: Converted SubmittedOrder object
    """
    return StandardOrder(
        order_id=order.order_id,
        is_filled=(order.filled_quantity == order.quantity),
        total=order.price * order.quantity,
        duration=order.duration,
        order_type=order.order_type,
        price=order.price,
        quantity=order.quantity,
        filled_quantity=order.filled_quantity,
        remaining_quantity=order.remaining_quantity,
        status=order.status,
        entered_time=datetime.datetime.strptime(order.entered_time, "%Y-%m-%dT%H:%M:%S%z"),
        cancel_time=datetime.datetime.strptime(order.cancel_time, "%Y-%m-%dT%H:%M:%S%z"),
        session=order.session,
        cancelable=order.cancelable
    )


def order_to_schwab_order(order: NumericalOrder) -> SchwabOrder:
    """
    Convert a simplified Order Request to a Schwab API-compliant SchwabOrder object.

    :param order: Simplified Order request
    :return: SchwabOrder object

    TODO: account for options requests.
    TODO: account for multiple order legs per order
    """
    instrument = Instrument(
        symbol=order.symbol,
        asset_type=order.asset_type,
    )
    order_leg = OrderLeg(
        instruction=order.instruction,
        quantity=order.quantity,
        instrument=instrument,
    )
    kwargs = {
        "order_type": order.order_type,
        "session": order.session,
        "duration": order.duration,
        "order_strategy_type": order.strategy_type,
        "order_leg_collection": [order_leg],
    }
    if order.price:
        kwargs["price"] = order.price

    return SchwabOrder(**kwargs)
