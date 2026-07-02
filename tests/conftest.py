"""Pytest configuration and fixtures for peakbagger-cli tests."""

import pytest


@pytest.fixture(autouse=True)
def isolate_cache_dir(tmp_path, monkeypatch):
    """Point the clearance cache at a temp dir so tests never touch ~/.cache."""
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))


@pytest.fixture(autouse=True)
def neutral_color_env(monkeypatch):
    """Strip color-forcing env vars so Rich emits plain text under capture."""
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    monkeypatch.delenv("CLICOLOR_FORCE", raising=False)


@pytest.fixture(scope="module")
def vcr_config():
    """
    Configure VCR for recording HTTP interactions.

    Returns:
        Dict with VCR configuration
    """
    return {
        # Store cassettes in tests/cassettes/
        "cassette_library_dir": "tests/cassettes",
        # Use YAML format (human-readable, easy to edit if needed)
        "record_mode": "once",
        # Match requests by method and URL
        "match_on": ["method", "scheme", "host", "port", "path", "query"],
        # Filter out sensitive headers
        "filter_headers": ["cookie", "authorization"],
        # Ignore localhost/test URLs in recording
        "ignore_hosts": [],
        # Decode compressed responses for readability
        "decode_compressed_response": True,
    }
