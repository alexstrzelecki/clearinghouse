from typing import List, Dict, Any

import schwabdev
from fastapi import APIRouter, Depends, HTTPException
import msgspec
from starlette import status

from clearinghouse.dependencies import SchwabService
from clearinghouse.models.request import Order as RequestOrder
from clearinghouse.models.response import (
    Order,
    Quote,
    Transaction,
    Lot,
    Position,
    GenericItemResponse,
    GenericCollectionResponse
)


def create_order_endpoints(schwab_service: SchwabService):
    order_router = APIRouter(prefix="/v1", tags=["orders"])

    @order_router.get(
        "/orders",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[Order]
    )
    def get_orders() -> Dict[str, Any]:
        return []


    @order_router.post(
        "/orders",
        status_code=status.HTTP_201_CREATED,
        response_model=GenericItemResponse[Order]
    )
    def place_order(order: RequestOrder) -> Dict[str, Any]:
        # TODO: add payload verification
        ...

    @order_router.get(
        "/orders/{orderId}",
        status_code=status.HTTP_200_OK,
        response_model=GenericItemResponse[Order]
    )
    def order_details(order_id: str) -> Dict[str, Any]:
        pass

    @order_router.delete(
        "/orders/{orderId}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    def delete_order(order_id: str) -> Dict[str, Any]:
        # TODO: return the object being deleted? Check schwab api docs
        pass

    @order_router.get(
        "/transactions",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[Transaction],
    )
    def get_transactions() -> Dict[str, Any]:
        # TODO: add filtering parameters
        pass

    @order_router.get(
        "/quotes/{ticker}",
        status_code=status.HTTP_200_OK,
        response_model=GenericItemResponse[Quote],
    )
    def get_quote(ticker: str) -> Dict[str, Any]:
        # TODO: add parameter for equity vs option
        return None


    @order_router.post(
        "/quotes/{ticker}",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[Quote],
    )
    def get_bulk_quotes(tickers: List[str]) -> Dict[str, Any]:
        return []

    @order_router.post(
        "/orders/batch",
        status_code=status.HTTP_201_CREATED,
        response_model=GenericCollectionResponse[Order]
    )
    def place_batch_order(orders: List[RequestOrder]) -> Dict[str, Any]:
        """
        Can be used to % change a list of positions.
        """
        # TODO: query parameter for percentage vs. absolute.
        return []

    return order_router
