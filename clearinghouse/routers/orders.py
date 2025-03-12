from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from clearinghouse.dependencies import SchwabService
from clearinghouse.models.request import (
    Order as RequestOrder,
    AdjustmentOrder,
)
from clearinghouse.models.response import (
    SubmittedOrder,
    Quote,
    Transaction,
    Lot,
    Position,
    GenericItemResponse,
    GenericCollectionResponse
)
from clearinghouse.services.response_generation import generate_generic_response
from clearinghouse.services.orders_service import (
    fetch_positions,
    fetch_orders,
    fetch_order_details,
    fetch_quotes,
    fetch_transactions,
    adjust_bulk_positions_fractions,
)
from clearinghouse.exceptions import ForbiddenException


def create_order_endpoints(schwab_service: SchwabService):
    order_router = APIRouter(prefix="/v1", tags=["orders"])

    @order_router.get(
        "/orders",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[SubmittedOrder]
    )
    def get_orders() -> Any:
        """
        TODO: add flags for order filtering / sorting
        """
        data = fetch_orders(schwab_service)
        return generate_generic_response("OrdersList", data)

    @order_router.get(
        "/orders/{orderID}",
        status_code=status.HTTP_200_OK,
        response_model=GenericItemResponse[SubmittedOrder]
    )
    def order_details(orderID: str) -> Any:
        data = fetch_order_details(schwab_service, order_id=orderID)

        return generate_generic_response("OrderDetails", data)

    @order_router.post(
        "/orders",
        status_code=status.HTTP_201_CREATED,
        response_model=GenericItemResponse[SubmittedOrder]
    )
    def place_order(order: RequestOrder) -> Any:
        # TODO: add payload verification
        data = None
        return generate_generic_response("SubmittedOrder", data)

    @order_router.post(
        "/orders/batch",
        status_code=status.HTTP_201_CREATED,
        response_model=GenericCollectionResponse[SubmittedOrder]
    )
    def place_batch_order(orders: List[RequestOrder]) -> Any:
        """
        Can be used to % change a list of positions.
        """
        # TODO: query parameter for percentage vs. absolute.
        data = []
        return generate_generic_response("SubmittedOrdersList", data)

    @order_router.delete(
        "/orders/{orderID}",  # Ensure the path parameter matches the function argument
        status_code=status.HTTP_204_NO_CONTENT,
    )
    def delete_order(orderID: str) -> None:
        # TODO: return the object being deleted? Check schwab api docs
        ...

    @order_router.get(
        "/transactions",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[Transaction],
    )
    def get_transactions() -> Any:
        # TODO: add filtering parameters
        data = []
        return generate_generic_response("TransactionsList", data)

    @order_router.get(
        "/quotes/{ticker}",
        status_code=status.HTTP_200_OK,
        response_model=GenericItemResponse[Quote],
    )
    def get_quote(ticker: str) -> GenericItemResponse[Quote]:
        # TODO: add parameter for equity vs option
        data = fetch_quotes(schwab_service, [ticker])[0]
        return generate_generic_response("Quote", data)


    @order_router.put(
        "/quotes",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[Quote],
    )
    def get_bulk_quotes(tickers: List[str]) -> Any:
        data = fetch_quotes(schwab_service, tickers)
        return generate_generic_response("QuotesList", data)


    @order_router.post(
        "/adjustments",
        status_code=status.HTTP_201_CREATED,
        response_model=GenericCollectionResponse[SubmittedOrder],
    )
    def adjust_position(
        ticker_to_fraction: List[AdjustmentOrder]
    ) -> GenericCollectionResponse[SubmittedOrder]:
        """
        Adjusts the amount, by percentage, of current holdings.
        Payload requests that include an un-held security will be ignored.
        Can be used to sell existing securities (e.g. -1).
        """
        data = adjust_bulk_positions_fractions(schwab_service, ticker_to_fraction)
        return generate_generic_response("SubmittedOrder", data)

    return order_router
