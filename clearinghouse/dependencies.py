import datetime
from typing import Optional, List, Dict, Any
import json

import requests
import schwabdev
import schedule
from pydantic_settings import BaseSettings, SettingsConfigDict

import clearinghouse.data.sample_data as sample_data


class SafetySettings(BaseSettings):
    """
    Settings module that governs safety limits for an account and is user configurable.
    These ensure that trades do not go over exposure limits, account size, max trade size, etc.

    TODO: add settings around restricted tickers, exchanges, and currencies

    Attributes:
        max_dollar_trade_size (float): The maximum dollar amount allowed for a single trade.
        max_dollar_sell_size (float): The maximum dollar amount allowed for a single sell order.
            Will be ignored if greater than max_dollar_trade_size.
        max_dollar_buy_size (float): The maximum dollar amount allowed for a single buy order.
            Will be ignored if greater than max_dollar_trade_size.
        allow_short_sales (bool): Flag to allow short sales to be submitted.
        max_fee_per_trade (float): The maximum fee in dollars that can be charged for a single trade.
            Most commonly used for ADRs avoidance.
        minimum_trading_volume (int): The minimum average trading volume to allow a trade to proceed.
        restrict_position_fraction (bool):
            Flag indicating whether to restrict the fraction of the portfolio that any single position can represent.
        max_position_fraction (float):
            The maximum fraction of the portfolio that any single position can represent if restrictions are enabled.
        allowed_currencies (List[str]): Currencies that allowed to be used.
        restricted_securities (List[str]): Securities to be blocked from tradin
    """
    max_dollar_trade_size: float = None
    max_dollar_sell_size: float = None
    max_dollar_buy_size: float = None
    allow_short_sales: bool = True
    max_fee_per_trade: float = 1
    minimum_trading_volume: int = 0
    restrict_position_fraction: bool = False
    max_position_fraction: float = 1
    allowed_currencies: List[str] = ["USD"]  # TODO: use with enum
    restricted_securities: List[str] = []

    model_config = SettingsConfigDict(env_file="safety_settings.env")


class EnvSettings(BaseSettings):
    """
    Boilerplate settings file to get secrets from environmental variables or a dotenv file.
    Pydantic settings will ALWAYS use envvar values over values in the dotenv unless
    the envvar value is empty.
    """
    schwab_app_key: str = ""
    schwab_app_secret: str = ""
    schwab_use_default_trading_account: Optional[bool] = True
    schwab_account_number: Optional[str] = None
    schwab_local_mode: Optional[bool] = False
    schwab_read_only_mode: Optional[bool] = False

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


class SchwabService:
    """
    A service class for managing authentication and token renewal for Schwab accounts.

    This class initializes a Schwab client using credentials obtained from environment variables.
    It schedules automatic renewal of the refresh token every 6 days using the `schedule` library.

    Attributes:
        app_key (str): The Schwab app key.
        app_secret (str): The Schwab app secret.
        client (schwabdev.Client): The Schwab client initialized with app key and secret.

    Methods:
        refresh_token() -> str:
            Returns the current refresh token, which expires every 7 days.

        _renew_refresh_token() -> str:
            Forces the renewal of tokens, updating both access and refresh tokens.
    """

    def __init__(self, env_settings: EnvSettings):
        self.app_key = env_settings.schwab_app_key
        self.app_secret = env_settings.schwab_app_secret
        self.use_default_trading_account = env_settings.schwab_use_default_trading_account
        self.account_number = env_settings.schwab_account_number
        self.local_mode = env_settings.schwab_local_mode
        self.read_only_mode = env_settings.schwab_read_only_mode
        self.account_hash: str = ""

        self._cache = {}

        self.client = self._schwab_client()
        self.set_default_trading_account()

        schedule.every(6).days.do(self._renew_refresh_token)

    def _schwab_client(self) -> schwabdev.Client:
        # TODO: add a call_on_notify
        if not self._cache.get("schwab_client"):
            self._cache["schwab_client"] = schwabdev.Client(
                app_key=self.app_key,
                app_secret=self.app_secret,
            )
        return self._cache["schwab_client"]

    def set_default_trading_account(self, account_number: Optional[str] = None):
        """
        If no account ID provided, use the first that is returned from the Schwab API
        """
        account_info: List[Dict[str, str]] = self.client.account_linked().json()
        if self.use_default_trading_account:
            if not account_info:
                raise ValueError("No accounts linked. Check Schwab developer portal.")
            self.account_number = account_info[0]["accountNumber"]
            self.account_hash = account_info[0]["hashValue"]
        else:
            self.account_number = account_number or self.account_number
            if not self.account_number:
                raise ValueError("No account ID provided")

            matching_account_info = [acc for acc in account_info if acc["accountNumber"] == self.account_number]
            if not matching_account_info:
                raise ValueError("No linked account matches provided account number.")

            self.account_hash = matching_account_info[0]["accountHash"]

    def refresh_token(self) -> str:
        """
        Token that expires every 7 days. Renewing it requires manual action.
        Access token automatically renews if refresh token is valid.
        """
        return self.client.tokens.refresh_token

    def _renew_refresh_token(self) -> str:
        """
        Force renew the refresh token.
        """
        return self.client.tokens.update_tokens(force_refresh_token=True)


class LocalSchwabClient(schwabdev.Client):
    """
    A local-only client that aims to be used for integration testing and does
    not require an external connection or valid API keys.

    TODO: fill all methods with representative data.
    """
    def __init__(self):
        pass

    @staticmethod
    def _generate_response(data: Any, is_enc_json: bool = False, status_code: int = 200) -> requests.Response:
        resp = requests.models.Response()
        resp.status_code = status_code

        # if data:
        resp._content = json.dumps(data).encode("utf-8") if not is_enc_json else data
        return resp

    def account_linked(self) -> requests.Response:
        data = {
            "accountNumber": "1234",
            "hashValue": "abcde",
        }
        return self._generate_response(data)

    def account_details_all(self, fields: str = None) -> requests.Response:
        return self._generate_response(sample_data.ACCOUNT_DETAILS_ALL)

    def account_details(self, accountHash: str, fields: str = None) -> requests.Response:
        return self._generate_response(sample_data.ACCOUNT_DETAILS)

    def account_orders(self, accountHash: str, fromEnteredTime: datetime.datetime | str, toEnteredTime: datetime.datetime | str, maxResults: int = None, status: str = None) -> requests.Response:
        return self._generate_response(sample_data.ACCOUNT_ORDERS_ALL)

    def order_details(self, accountHash: str, orderId: int | str) -> requests.Response:
        return self._generate_response(sample_data.ACCOUNT_ORDERS_ALL[0])

    def order_place(self, accountHash: str, order: dict) -> requests.Response:
        # TODO: confirm what is returned
        return self._generate_response({}, status_code=201)

    def order_cancel(self, accountHash: str, orderId: int | str) -> requests.Response:
        # TODO: confirm status code
        return self._generate_response(None, status_code=204)

    def order_replace(self, accountHash: str, orderId: int | str, order: dict) -> requests.Response:
        data = None
        # TODO: confirm status code
        return self._generate_response(data, status_code=201)

    def account_orders_all(self, fromEnteredTime: datetime.datetime | str, toEnteredTime: datetime.datetime | str, maxResults: int = None, status: str = None) -> requests.Response:
        return self._generate_response(sample_data.ACCOUNT_ORDERS_ALL)

    def transactions(self, accountHash: str, startDate: datetime.datetime | str, endDate: datetime.datetime | str, types: str, symbol: str = None) -> requests.Response:
        return self._generate_response(sample_data.TRANSACTIONS)

    def quotes(self, symbols : list[str] | str, fields: str = None, indicative: bool = False) -> requests.Response:
        return self._generate_response(sample_data.QUOTES)

    def quote(self, symbol_id: str, fields: str = None) -> requests.Response:
        return self._generate_response({"AMD": sample_data.QUOTES.get("AMD")})

    def transaction_details(self, accountHash: str, transactionId: str | int) -> requests.Response:
        return self._generate_response(sample_data.TRANSACTION_DETAILS)


class LocalSchwabService(SchwabService):
    def __init__(self):
        super().__init__(EnvSettings())

    def _schwab_client(self) -> schwabdev.Client:
        return LocalSchwabClient()

    def set_default_trading_account(self, account_number: Optional[str] = None):
        ...

    def refresh_token(self) -> str:
        return ""

    def _renew_refresh_token(self) -> str:
        return ""
