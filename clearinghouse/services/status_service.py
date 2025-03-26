import msgspec
from cachetools import cached, TTLCache

from clearinghouse.dependencies import SchwabService
from clearinghouse.models.schwab_response import (
    SecuritiesAccount
)

@cached(cache=TTLCache(maxsize=1024, ttl=60))
def fetch_account_status(schwab_service: SchwabService) -> SecuritiesAccount:
    resp = schwab_service.client.account_details(schwab_service.account_hash)
    decoded_resp = msgspec.json.decode(resp.content, type=SecuritiesAccount)

    return decoded_resp
