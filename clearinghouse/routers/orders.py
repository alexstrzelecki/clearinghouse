
import schwabdev
from fastapi import APIRouter, Depends, HTTPException

from clearinghouse.dependencies import SchwabService


def create_order_endpoints(schwab_service: SchwabService):
    order_router = APIRouter()
