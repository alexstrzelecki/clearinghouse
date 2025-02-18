import os
import pytest
from unittest.mock import patch, MagicMock
from clearinghouse.dependencies import SchwabService


@pytest.fixture
def mock_schwab_client():
    with patch('clearinghouse.dependencies.schwabdev.Client') as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        yield mock_client

@patch.dict(os.environ, {"SCHWAB_APP_KEY": "test_key", "SCHWAB_APP_SECRET": "test_secret"})
def test_initialization(mock_schwab_client):
    service = SchwabService()
    assert service.app_key == "test_key"
    assert service.app_secret == "test_secret"

def test_refresh_token(mock_schwab_client):
    mock_schwab_client.tokens.refresh_token = "mock_refresh_token"
    service = SchwabService()
    assert service.refresh_token() == "mock_refresh_token"

def test_renew_refresh_token(mock_schwab_client):
    mock_schwab_client.tokens.update_tokens.return_value = "new_access_token"
    service = SchwabService()
    assert service._renew_refresh_token() == "new_access_token"
    mock_schwab_client.tokens.update_tokens.assert_called_once_with(force_refresh_token=True)
