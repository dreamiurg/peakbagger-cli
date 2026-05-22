"""Tests for the Cloudflare clearance cache in browser_transport.

The headful browser solve itself is not unit-tested (it needs a real browser and
network); these cover the disk cache load/save/expiry logic that gates it.

The cache dir is isolated to a temp path by the autouse ``isolate_cache_dir``
fixture in conftest.py, so these tests never touch the real ~/.cache.
"""

import json
import time

import pytest

from peakbagger import browser_transport


def _write_cache(cookies):
    path = browser_transport._clearance_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"user_agent": "UA/1.0", "cookies": cookies}))
    return path


class TestLoadClearance:
    def test_returns_none_when_no_cache_file(self):
        assert browser_transport.load_clearance() is None

    def test_returns_none_when_cf_clearance_missing(self):
        _write_cache(cookies=[{"name": "__cf_bm", "value": "x"}])
        assert browser_transport.load_clearance() is None

    def test_returns_none_when_cf_clearance_expired(self):
        _write_cache(cookies=[{"name": "cf_clearance", "value": "x", "expires": time.time() - 10}])
        assert browser_transport.load_clearance() is None

    def test_returns_data_when_cf_clearance_valid(self):
        _write_cache(
            cookies=[{"name": "cf_clearance", "value": "x", "expires": time.time() + 3600}]
        )
        data = browser_transport.load_clearance()
        assert data is not None
        assert data["user_agent"] == "UA/1.0"

    def test_session_cookie_without_expiry_is_kept(self):
        # expires == -1 means a session cookie (no expiry); must not be discarded.
        _write_cache(cookies=[{"name": "cf_clearance", "value": "x", "expires": -1}])
        assert browser_transport.load_clearance() is not None

    def test_returns_none_on_corrupt_json(self):
        _write_cache(cookies=[])  # establishes the dir; overwrite with junk below
        browser_transport._clearance_path().write_text("{not valid json")
        assert browser_transport.load_clearance() is None


class TestSaveClearance:
    def test_round_trips_through_load(self):
        cookies = [{"name": "cf_clearance", "value": "abc", "expires": time.time() + 3600}]
        browser_transport.save_clearance("UA/2.0", cookies)

        data = browser_transport.load_clearance()
        assert data is not None
        assert data["user_agent"] == "UA/2.0"
        assert data["cookies"][0]["value"] == "abc"


class TestSolveChallenge:
    def test_raises_helpful_error_when_patchright_missing(self, monkeypatch):
        # Simulate patchright not installed: importing it raises ImportError.
        import builtins

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name.startswith("patchright"):
                raise ImportError("No module named 'patchright'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)

        with pytest.raises(browser_transport.BrowserTransportUnavailableError, match="patchright"):
            browser_transport.solve_challenge("https://www.peakbagger.com/")
