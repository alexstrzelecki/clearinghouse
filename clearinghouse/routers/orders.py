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

    # place order


    # order details



    # cancel order



    # get all transactions



    # get single quote


    # bulk orders


    # percentage change


    # bulk percentage change

