"""Pytest configuration and fixtures for peakbagger-cli tests."""

import pytest


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
