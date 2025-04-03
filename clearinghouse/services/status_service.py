from typing import Dict

import msgspec
from cachetools import cached, TTLCache

from clearinghouse.dependencies import SchwabService
from clearinghouse.models.schwab_response import (
    SecuritiesAccount
)
from clearinghouse.models.response import (
    AccountDetails
)

@cached(cache=TTLCache(maxsize=1024, ttl=60))
def fetch_account_status(schwab_service: SchwabService) -> AccountDetails:
    resp = schwab_service.client.account_details(schwab_service.account_hash)
    decoded_resp: SecuritiesAccount = msgspec.json.decode(resp.content,
                                                          type=Dict[str, SecuritiesAccount]).get("securitiesAccount")
    return AccountDetails(
        current_balances=decoded_resp.current_balances,
        initial_balances=decoded_resp.initial_balances,
    )
