import os
import pytest
from unittest.mock import patch, MagicMock
from clearinghouse.dependencies import SchwabService, EnvSettings, LocalSchwabService


@pytest.fixture
def mock_schwab_client():
    with patch('clearinghouse.dependencies.schwabdev.Client') as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        yield mock_client

@patch.dict(os.environ, {
    "SCHWAB_APP_KEY": "test_key",
    "SCHWAB_APP_SECRET": "test_secret",
    "SCHWAB_USE_DEFAULT_TRADING_ACCOUNT": "True",
    "SCHWAB_ACCOUNT_NUMBER": "12345678",
    "SCHWAB_READ_ONLY_MODE": "False",
    "SCHWAB_LOCAL_MODE": "True"
})
def test_env_settings_from_envvar():
    settings = EnvSettings()

    assert settings.schwab_app_key == "test_key"
    assert settings.schwab_app_secret == "test_secret"
    assert settings.schwab_use_default_trading_account is True
    assert settings.schwab_account_number == "12345678"
    assert settings.schwab_read_only_mode is False


@patch.dict(os.environ, {
    "SCHWAB_APP_KEY": "test_key",
    "SCHWAB_APP_SECRET": "test_secret",
    "SCHWAB_USE_DEFAULT_TRADING_ACCOUNT": "True",
    "SCHWAB_ACCOUNT_NUMBER": "12345678",
    "SCHWAB_READ_ONLY_MODE": "True",
    "SCHWAB_LOCAL_MODE": "True"
})
def test_envvar_schwab_client(mock_schwab_client):
    env_settings = EnvSettings()
    service = SchwabService(env_settings)
    assert service.app_key == "test_key"
    assert service.app_secret == "test_secret"
    assert service.use_default_trading_account is True
    assert service.read_only_mode is True

    # not testing account number and hash directly due to external dependency


@patch.dict(os.environ, {
    "SCHWAB_APP_KEY": "test_key",
    "SCHWAB_APP_SECRET": "test_secret",
    "SCHWAB_USE_DEFAULT_TRADING_ACCOUNT": "True",
    "SCHWAB_ACCOUNT_NUMBER": "12345678",
    "SCHWAB_READ_ONLY_MODE": "False",
    "SCHWAB_LOCAL_MODE": ""  # should revert to default value in BaseSettings
})
def test_envvar_empty_subset(mock_schwab_client):
    env_settings = EnvSettings()
    service = SchwabService(env_settings)
    assert service.app_key == "test_key"
    assert service.app_secret == "test_secret"
    assert service.use_default_trading_account is True
    assert service.read_only_mode is False


def test_refresh_token(mock_schwab_client):
    env_settings = EnvSettings()

    mock_schwab_client.tokens.refresh_token = "mock_refresh_token"
    service = SchwabService(env_settings)
    assert service.refresh_token() == "mock_refresh_token"

def test_renew_refresh_token(mock_schwab_client):
    env_settings = EnvSettings()

    mock_schwab_client.tokens.update_tokens.return_value = "new_access_token"
    service = SchwabService(env_settings)
    assert service._renew_refresh_token() == "new_access_token"
    mock_schwab_client.tokens.update_tokens.assert_called_once_with(force_refresh_token=True)
