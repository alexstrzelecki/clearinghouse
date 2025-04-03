from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from starlette import status

from clearinghouse.dependencies import SchwabService
from clearinghouse.models.response import (
    GenericCollectionResponse,
    GenericItemResponse,
    AccountDetails,
)
from clearinghouse.services.response_generation import generate_generic_response
from clearinghouse.services.status_service import (
    fetch_account_status,
)


def create_status_endpoints(schwab_service: SchwabService):
    status_router = APIRouter(prefix="/v1", tags=["status"])

    @status_router.get(
        "/accounts/accountNumbers",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[Dict[str, str]]
    )
    def get_linked_accounts() -> Any:
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

        return generate_generic_response("LinkedAccounts", resp.json())

    # account details
    @status_router.get(
        "/accounts",
        status_code=status.HTTP_200_OK,
        response_model=GenericCollectionResponse[Dict[str, Any]]  # TODO: clarify what the Schwab response is
    )
    def get_account_details_all() -> Dict[str, Any]:
        # TODO: support all additional arguments for account details
        # resp = schwab_service.client.account_details_all()

        # if not resp.ok:
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="Failed to retrieve account details from Schwab service."
        #     )
        #
        # return resp.json()

        return generate_generic_response("AccountDetailsList", [])

    @status_router.get(
        "/accounts/default",
        status_code=status.HTTP_200_OK,
        response_model=GenericItemResponse[AccountDetails]
    )
    def get_account_details() -> Any:
        data = fetch_account_status(schwab_service)
        return generate_generic_response("AccountDetails", data)

    return status_router
