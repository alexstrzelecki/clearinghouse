from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from clearinghouse.dependencies import SchwabService
from clearinghouse.models.request import Order as RequestOrder
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
    fetch_quote,
    fetch_quotes,
    fetch_transactions,
)


def create_order_endpoints(schwab_service: SchwabService):
    order_router = APIRouter(prefix="/v1", tags=["orders"])

    @order_router.get(
        "/orders",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[SubmittedOrder]
    )
    def get_orders() -> Dict[str, Any]:
        """
        TODO: add flags for order filtering / sorting
        """
        data = fetch_orders(schwab_service)
        return generate_generic_response("OrdersList", data)

    @order_router.post(
        "/orders",
        status_code=status.HTTP_201_CREATED,
        response_model=GenericItemResponse[SubmittedOrder]
    )
    def place_order(order: RequestOrder) -> Dict[str, Any]:
        # TODO: add payload verification
        data = None
        return generate_generic_response("SubmittedOrder", data)

    @order_router.get(
        "/orders/{orderId}",
        status_code=status.HTTP_200_OK,
        response_model=GenericItemResponse[SubmittedOrder]
    )
    def order_details(order_id: str) -> Dict[str, Any]:
        data = None
        return generate_generic_response("OrderDetails", data)

    @order_router.delete(
        "/orders/{orderId}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    def delete_order(order_id: str) -> None:
        # TODO: return the object being deleted? Check schwab api docs
        pass

    @order_router.get(
        "/transactions",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[Transaction],
    )
    def get_transactions() -> Dict[str, Any]:
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
        data = fetch_quote(schwab_service, ticker)
        return generate_generic_response("Quote", data)


    @order_router.post(
        "/quotes/{ticker}",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[Quote],
    )
    def get_bulk_quotes(tickers: List[str]) -> Dict[str, Any]:
        data = []
        return generate_generic_response("QuotesList", data)

    @order_router.post(
        "/orders/batch",
        status_code=status.HTTP_201_CREATED,
        response_model=GenericCollectionResponse[SubmittedOrder]
    )
    def place_batch_order(orders: List[RequestOrder]) -> Dict[str, Any]:
        """
        Can be used to % change a list of positions.
        """
        # TODO: query parameter for percentage vs. absolute.
        data = []
        return generate_generic_response("SubmittedOrdersList", data)

    return order_router
