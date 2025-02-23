from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException
from starlette import status

from clearinghouse.dependencies import SchwabService


def create_status_endpoints(schwab_service: SchwabService):
    status_router = APIRouter(prefix="/v1", tags=["status"])

    @status_router.get(
        "/accounts/accountNumbers",
        status_code=status.HTTP_200_OK,
        response_model=List[Dict[str,str]]  # TODO: convert to typed response model
    )
    def get_linked_accounts():
        """
        Mirrors the Schwab API endpoint for retrieving linked and authorized accounts.
        :return:
        """
        resp = schwab_service.client.account_linked()

        if not resp.ok:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve linked accounts from Schwab service."
            )

        return resp.json()

    # account details
    @status_router.get(
        "/accounts",
        status_code=status.HTTP_200_OK,
        response_model=List[Dict[str, Any]]
    )
    def get_account_details_all():
        # TODO: support all additional arguments for account details
        # TODO: fix the return type
        # resp = schwab_service.client.account_details_all()

        # if not resp.ok:
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="Failed to retrieve account details from Schwab service."
        #     )
        #
        # return resp.json()

        return []

    @status_router.get(
        "/accounts/{account_hash}",
        status_code=status.HTTP_200_OK,
        response_model=List[Dict[str, Any]]
    )
    def get_account_details(account_hash: str):
        # TODO: support all additional arguments for account details
        # TODO: fix the return type
        resp = schwab_service.client.account_details(accountHash=account_hash)
        if not resp.ok:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve account details from Schwab service."
            )

        return resp.json()

    return status_router
