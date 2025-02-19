from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException
from starlette import status

from clearinghouse.dependencies import SchwabService


def create_status_endpoints(schwab_service: SchwabService):
    status_router = APIRouter(prefix="/v1/status", tags=["status"])

    # account details
    @status_router.get(
        "/accounts/details",
        status_code=status.HTTP_200_OK,
        response_model=List[Dict[str, Any]]
    )
    def get_account_details_all():
        # TODO: support all additional arguments for account details
        resp = schwab_service.client.account_details_all()

        if not resp.ok:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve account details from Schwab service."
            )

        return resp.json()

    @status_router.get(
        "/accounts/details/{accountHash}",
        status_code=status.HTTP_200_OK,
        response_model=List[Dict[str, Any]]
    )
    def get_account_details(account_hash: str):
        # TODO: support all additional arguments for account details
        resp = schwab_service.client.account_details(account_hash)
        if not resp.ok:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve account details from Schwab service."
            )

        return resp.json()
