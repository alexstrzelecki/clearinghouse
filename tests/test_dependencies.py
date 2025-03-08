import os
import pytest
from unittest.mock import patch, MagicMock
from clearinghouse.dependencies import SchwabService, EnvSettings, SafetySettings


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


def test_default_values():
    # this test will use values from safety_settings.env
    settings = SafetySettings()
    assert settings.max_dollar_trade_size == 10000.00
    assert settings.max_dollar_sell_size == 5000.00
    assert settings.max_dollar_buy_size == 5000.00
    assert settings.allow_short_sales is True
    assert settings.max_fee_per_trade == 5.00
    assert settings.minimum_trading_volume == 1000
    assert settings.restrict_position_fraction is True
    assert settings.max_position_fraction == 0.10
    assert settings.allowed_currencies == ["USD"]
    assert settings.restricted_securities == []


def test_custom_settings():
    custom_settings = SafetySettings(
        max_dollar_trade_size=10000,
        max_dollar_sell_size=5000,
        max_dollar_buy_size=5000,
        allow_short_sales=False,
        max_fee_per_trade=2,
        minimum_trading_volume=100,
        restrict_position_fraction=True,
        max_position_fraction=0.5,
        allowed_currencies=["USD", "EUR"],
        restricted_securities=["XYZ", "ABC"]
    )
    assert custom_settings.max_dollar_trade_size == 10000
    assert custom_settings.max_dollar_sell_size == 5000
    assert custom_settings.max_dollar_buy_size == 5000
    assert custom_settings.allow_short_sales is False
    assert custom_settings.max_fee_per_trade == 2
    assert custom_settings.minimum_trading_volume == 100
    assert custom_settings.restrict_position_fraction is True
    assert custom_settings.max_position_fraction == 0.5
    assert custom_settings.allowed_currencies == ["USD", "EUR"]
    assert custom_settings.restricted_securities == ["XYZ", "ABC"]
