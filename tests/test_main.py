import importlib
from unittest.mock import patch, MagicMock
from clearinghouse.dependencies import LocalSchwabService


def test_schwab_service_in_production_mode(monkeypatch):
    with patch('clearinghouse.dependencies.EnvSettings') as MockEnvSettings:
        mock_env_settings = MagicMock()
        mock_env_settings.schwab_local_mode = False
        MockEnvSettings.return_value = mock_env_settings

        # Mock SchwabService to avoid issues of missing API keys
        with patch('clearinghouse.dependencies.SchwabService') as MockSchwabService:
            from clearinghouse import main
            importlib.reload(main)
            main.initialize_services()

            assert main.schwab_service is not None
            MockSchwabService.assert_called_once()

def test_schwab_service_in_local_mode(monkeypatch):
    with patch('clearinghouse.dependencies.EnvSettings') as MockEnvSettings:
        mock_env_settings = MagicMock()
        mock_env_settings.schwab_local_mode = True
        MockEnvSettings.return_value = mock_env_settings

        with patch('clearinghouse.dependencies.LocalSchwabService') as MockLocalSchwabService:
            from clearinghouse import main
            importlib.reload(main)
            main.initialize_services()

            assert main.schwab_service is not None
            MockLocalSchwabService.assert_called_once()
