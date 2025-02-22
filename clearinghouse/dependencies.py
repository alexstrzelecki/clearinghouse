import os

import schwabdev
import schedule
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    """
    Boilerplate settings file to get secrets from a dotenv
    """
    schwab_app_key: str = ""
    schwab_app_secret: str = ""

    model_config = SettingsConfigDict(env_file=".env")


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
        self.app_key = env_settings.schwab_app_key or os.environ.get("SCHWAB_APP_KEY")
        self.app_secret = env_settings.schwab_app_secret or os.environ.get("SCHWAB_APP_SECRET")
        self._cache = {}

        self.client = self._schwab_client()

        schedule.every(6).days.do(self._renew_refresh_token)

    def _schwab_client(self) -> schwabdev.Client:
        # TODO: add a call_on_notify
        if not self._cache.get("schwab_client"):
            self._cache["schwab_client"] = schwabdev.Client(
                app_key=self.app_key,
                app_secret=self.app_secret,
            )
        return self._cache["schwab_client"]

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
