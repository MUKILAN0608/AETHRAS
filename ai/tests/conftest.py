"""Unit tests must never append synthetic data to the real research stream."""
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory


@pytest.fixture(autouse=True)
def isolated_research_log(monkeypatch):
    from app import research_logger
    with TemporaryDirectory(prefix="aethras-unit-log-") as directory:
        path = Path(directory)
        monkeypatch.setattr(research_logger, "_LOG_DIR", path)
        monkeypatch.setattr(research_logger, "_LOG_FILE", path / "experiments.jsonl")
        yield
