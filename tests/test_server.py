import importlib
from unittest.mock import patch, MagicMock
from clearinghouse.dependencies import SchwabService, LocalSchwabService, EnvSettings


def test_schwab_service_in_production_mode(monkeypatch):
    with patch('clearinghouse.dependencies.EnvSettings') as MockEnvSettings:
        mock_env_settings = MagicMock()
        mock_env_settings.schwab_read_only_mode = False
        MockEnvSettings.return_value = mock_env_settings

        # Force re-init of main where local vs. non-local determined.
        from clearinghouse import main
        importlib.reload(main)

        assert isinstance(main.get_global_schwab_service(), SchwabService)


def test_schwab_service_in_local_mode(monkeypatch):
    with patch('clearinghouse.dependencies.EnvSettings') as MockEnvSettings:
        mock_env_settings = MagicMock()
        mock_env_settings.schwab_read_only_mode = True
        MockEnvSettings.return_value = mock_env_settings

        # Force re-init of main where local vs. non-local determined.
        from clearinghouse import main
        importlib.reload(main)

        assert isinstance(main.get_global_schwab_service(), LocalSchwabService)
