from typing import List, Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from starlette import status

from clearinghouse.dependencies import SchwabService
from clearinghouse.models.request import (
    Order as RequestOrder,
    AdjustmentOrder,
    PositionsFilter,
    OrdersFilter,
    TransactionsFilter,
)
from clearinghouse.models.response import (
    SubmittedOrder,
    Quote,
    Transaction,
    Position,
    GenericItemResponse,
    GenericCollectionResponse
)
from clearinghouse.services.response_generation import generate_generic_response
from clearinghouse.services.orders_service import (
    fetch_positions,
    fetch_orders,
    fetch_order_details,
    place_orders,
    cancel_order_request,
    fetch_quotes,
    fetch_transactions,
    adjust_bulk_positions_fractions,
    fetch_transaction_details,
    filter_orders,
    filter_positions,
    filter_transactions,
)
from clearinghouse.exceptions import ForbiddenException


def create_order_endpoints(schwab_service: SchwabService):
    order_router = APIRouter(prefix="/v1", tags=["orders"])

    @order_router.get(
        "/positions",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[Position]
    )
    def get_positions(position_filter: Annotated[PositionsFilter, Query()]) -> Any:
        # All current filtering is done by clearinghouse and not by the schwab client
        data = fetch_positions(schwab_service)
        filtered_data = filter_positions(data, position_filter)

        return generate_generic_response("PositionsList", filtered_data)

    @order_router.get(
        "/orders",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[SubmittedOrder]
    )
    def get_orders(orders_filter: Annotated[OrdersFilter, Query()]) -> Any:
        # TODO: settle submittedorder vs order
        data = fetch_orders(schwab_service,
                            start_date=orders_filter.startDate,
                            end_date=orders_filter.endDate,
                            max_results=orders_filter.maxResults,
                            status=orders_filter.status)
        filtered_data = filter_orders(data, orders_filter)
        return generate_generic_response("OrdersList", filtered_data)

    @order_router.get(
        "/orders/{orderId}",
        status_code=status.HTTP_200_OK,
        response_model=GenericItemResponse[SubmittedOrder]
    )
    def order_details(orderId: str) -> Any:
        data = fetch_order_details(schwab_service, order_id=orderId)

        return generate_generic_response("OrderDetails", data)

    @order_router.post(
        "/orders",
        status_code=status.HTTP_201_CREATED,
        response_model=GenericItemResponse[RequestOrder]
    )
    async def order_placement(order: RequestOrder) -> Any:
        successful, failed = await place_orders(schwab_service, [order])

        if any(failed):
            # TODO: handle partial failures
            pass

        return generate_generic_response("SubmittedOrder", successful[0])

    @order_router.post(
        "/orders/batch",
        status_code=status.HTTP_201_CREATED,
        response_model=GenericCollectionResponse[RequestOrder]
    )
    async def order_placement_batch(orders: List[RequestOrder]) -> Any:
        """
        """
        successful, failed = await place_orders(schwab_service, orders)

        if any(failed):
            # TODO: handle partial failures
            pass

        return generate_generic_response("SubmittedOrdersList", successful)

    @order_router.delete(
        "/orders/{orderId}",  # Ensure the path parameter matches the function argument
        status_code=status.HTTP_204_NO_CONTENT,
    )
    def cancel_order(orderId: str) -> None:
        status_code = cancel_order_request(schwab_service, orderId)
        if status_code != 200:
            raise HTTPException(
                status_code=status_code,
                detail=f"Failed to cancel order {orderId}",
            )

    @order_router.get(
        "/transactions",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[Transaction],
    )
    def get_transactions(transaction_filter: Annotated[TransactionsFilter, Query(...)]) -> Any:
        data = fetch_transactions(schwab_service,
                                  start_date=transaction_filter.startDate,
                                  end_date=transaction_filter.endDate,
                                  types=transaction_filter.types)

        filtered_data = filter_transactions(data, transaction_filter)
        return generate_generic_response("TransactionsList", filtered_data)

    @order_router.get(
        "/transactions/{transactionId}",
        status_code=status.HTTP_200_OK,
        response_model=GenericItemResponse[Transaction],
    )
    def get_transactions_details(transactionId: str) -> Any:
        data = fetch_transaction_details(schwab_service, transactionId)
        return generate_generic_response("Transaction", data)


    @order_router.get(
        "/quotes/{symbol}",
        status_code=status.HTTP_200_OK,
        response_model=GenericItemResponse[Quote],
    )
    def get_quote(symbol: str) -> GenericItemResponse[Quote]:
        # TODO: add parameter for equity vs option
        # TODO: consolidate quotes into query parameter
        data = fetch_quotes(schwab_service, [symbol])[0]
        return generate_generic_response("Quote", data)


    @order_router.post(
        "/quotes",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[Quote],
    )
    def get_bulk_quotes(symbols: List[str]) -> Any:
        data = fetch_quotes(schwab_service, symbols)
        return generate_generic_response("QuotesList", data)


    @order_router.post(
        "/adjustments",
        status_code=status.HTTP_201_CREATED,
        response_model=GenericCollectionResponse[SubmittedOrder],
    )
    def adjust_position(
        symbol_to_fraction: List[AdjustmentOrder]
    ) -> GenericCollectionResponse[SubmittedOrder]:
        """
        Adjusts the amount, by percentage, of current holdings.
        Payload requests that include an un-held security will be ignored.
        Can be used to sell existing securities (e.g. -1).
        """
        data = adjust_bulk_positions_fractions(schwab_service, symbol_to_fraction)
        return generate_generic_response("SubmittedOrder", data)

    return order_router
