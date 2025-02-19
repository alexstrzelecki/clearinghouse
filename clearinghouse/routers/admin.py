from typing import List, Dict, Any

from starlette import status
from fastapi import APIRouter, HTTPException

from clearinghouse.dependencies import SchwabService


def create_admin_endpoints(schwab_service: SchwabService):
    admin_router = APIRouter(prefix="/v1/admin", tags=["admin"])

    # account numbers
    @admin_router.get(
        "/accounts",
        status_code=status.HTTP_200_OK,
        response_model=List[Dict[str,str]]  # TODO: convert to typed response model
    )
    def get_linked_accounts():
        resp = schwab_service.client.account_linked()

        if not resp.ok:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve linked accounts from Schwab service."
            )

        return resp.json()

    # account details
    @admin_router.get(
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

    @admin_router.get(
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
