
import schwabdev
from fastapi import APIRouter, Depends, HTTPException

from clearinghouse.dependencies import SchwabService


def create_admin_endpoints(schwab_service: SchwabService):
    admin_router = APIRouter()
