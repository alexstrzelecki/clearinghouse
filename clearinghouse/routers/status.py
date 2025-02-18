import schwabdev
from fastapi import APIRouter, Depends, HTTPException

from clearinghouse.dependencies import SchwabService


def create_account_status_endpoints(schwab_service: SchwabService):
    account_status_router = APIRouter()
