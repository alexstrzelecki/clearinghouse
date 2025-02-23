from typing import List

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
)


def create_order_endpoints(schwab_service: SchwabService):
    order_router = APIRouter(prefix="/v1", tags=["orders"])

    @order_router.get(
        "/orders",
        status_code=status.HTTP_200_OK,
    )
    def get_orders() -> List[Order]:
        return []


    @order_router.post(
        "/orders",
        status_code=status.HTTP_201_CREATED,
    )
    def place_order(order: RequestOrder) -> Order:
        # TODO: add payload verification
        ...

    @order_router.get(
        "/orders/{orderId}",
        status_code=status.HTTP_200_OK,
    )
    def order_details(order_id: str) -> Order:
        pass

    @order_router.delete(
        "/orders/{orderId}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    def delete_order(order_id: str):
        # TODO: return the object being deleted? Check schwab api docs
        pass

    @order_router.get(
        "/transactions",
        status_code=status.HTTP_200_OK,
        response_model=List[Transaction],
    )
    def get_transactions():
        # TODO: add filtering parameters
        pass

    @order_router.get(
        "/quotes/{ticker}",
        status_code=status.HTTP_200_OK,
    )
    def get_quote(ticker: str) -> Quote:
        # TODO: add parameter for equity vs option
        return None


    @order_router.post(
        "/quotes/{ticker}",
        status_code=status.HTTP_200_OK,
    )
    def get_bulk_quotes(tickers: List[str]) -> List[Quote]:
        return []

    @order_router.post(
        "/orders/batch",
        status_code=status.HTTP_201_CREATED,
    )
    def place_batch_order(orders: List[RequestOrder]) -> List[Order]:
        """
        Can be used to % change a list of positions.
        """
        # TODO: query parameter for percentage vs. absolute.
        return []

    return order_router
