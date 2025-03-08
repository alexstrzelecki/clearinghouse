import pytest
import importlib
from unittest.mock import patch, MagicMock
from clearinghouse import main
from clearinghouse.dependencies import SchwabService, LocalSchwabService, EnvSettings


@pytest.fixture
def mock_schwab_client():
    with patch('clearinghouse.dependencies.schwabdev.Client') as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        yield mock_client


@pytest.fixture(autouse=True)
def clean_imports():
    yield
    importlib.reload(main)


def test_schwab_service_in_production_mode(monkeypatch):
    monkeypatch.setenv("SCHWAB_RUN_MODE", "production")
    importlib.reload(main)
    assert isinstance(main.get_global_schwab_service(), SchwabService)


def test_schwab_service_in_local_mode(monkeypatch):
    monkeypatch.setenv("SCHWAB_RUN_MODE", "local")
    importlib.reload(main)
    assert isinstance(main.get_global_schwab_service(), LocalSchwabService)
