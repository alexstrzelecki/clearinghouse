from typing import List

import schwabdev
from fastapi import APIRouter, Depends, HTTPException
import msgspec
from starlette import status

from clearinghouse.dependencies import SchwabService
from clearinghouse.models.request import Order
from clearinghouse.models.schwab import (
    EquityPosition,
    Transaction,
)


def create_order_endpoints(schwab_service: SchwabService):
    order_router = APIRouter()

    @order_router.get(
        "/orders",
        status_code=status.HTTP_200_OK,
        response_model=List[Transaction],
    )
    def get_orders(client: schwab_service):
        pass

    @order_router.post(
        "/orders",
        status_code=status.HTTP_201_CREATED,
        response_model=Transaction,
    )
    def place_order(order: Order, client: schwab_service):
        # TODO: add payload verification
        ...

    @order_router.get(
        "/orders/{orderId}",
        status_code=status.HTTP_200_OK,
        response_model=Transaction,
    )
    def order_details(order_id: str, client: schwab_service):
        pass

    @order_router.delete(
        "/orders/{orderId}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    def delete_order(order_id: str, client: schwab_service):
        pass

    @order_router.get(
        "/transactions",
        status_code=status.HTTP_200_OK,
        response_model=List[Transaction],
    )
    def get_transactions(client: schwab_service):
        pass

    @order_router.get(
        "/quotes/{ticker}",
        status_code=status.HTTP_200_OK,
        response_model=EquityPosition,
    )
    def get_quote(ticker: str, client: schwab_service):
        pass

    @order_router.post(
        "/orders/batch",
        status_code=status.HTTP_201_CREATED,
        response_model=List[Transaction],
    )
    def place_batch_order(orders: List[Order], client: schwab_service):
        """
        Can be used to % change a list of positions.
        """
        # TODO: query parameter for percentage vs. absolute.
        ...

    return order_router
