from pathlib import Path

import pytest

from app.config import PROJECT_ROOT, Settings


def test_root_configuration_is_independent_of_working_directory(monkeypatch):
    monkeypatch.chdir(PROJECT_ROOT / "ai")
    assert Path(Settings.model_config["env_file"]) == PROJECT_ROOT / ".env"
    assert Settings().aethras_decision_provider == "cloudflare_clef_flash"


def test_environment_wins_over_dotenv(monkeypatch):
    monkeypatch.setenv("AETHRAS_DECISION_TIMEOUT_SECONDS", "7")
    assert Settings().aethras_decision_timeout_seconds == 7


def test_disabled_provider_does_not_require_credentials():
    settings = Settings(_env_file=None, aethras_decision_enabled=False, cloudflare_account_id="", cloudflare_auth_token="")
    assert not settings.decision_configured


def test_enabled_configuration_errors_hide_credentials():
    with pytest.raises(ValueError) as error:
        Settings(_env_file=None, aethras_decision_enabled=True, cloudflare_account_id="bad", cloudflare_auth_token="sensitive-token")
    assert "sensitive-token" not in str(error.value)


@pytest.mark.parametrize("provider", ["laya", "jev"])
def test_excluded_providers_cannot_be_selected(provider):
    with pytest.raises(ValueError):
        Settings(_env_file=None, aethras_decision_provider=provider)
