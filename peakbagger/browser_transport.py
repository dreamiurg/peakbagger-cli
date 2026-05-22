"""Headful stealth-browser transport for minting Cloudflare clearance.

PeakBagger.com serves a Cloudflare *managed* challenge (the "Just a moment..."
Turnstile page) on its data endpoints (``peak.aspx``, ``search.aspx`` and
friends). ``cloudscraper`` only solves the legacy IUAM JS challenge and cannot
pass the modern managed challenge, so plain requests get ``403`` with the
``cf-mitigated: challenge`` header.

The reliable workaround is to drive a real, *visible* browser that passes the
challenge automatically, then harvest the resulting ``cf_clearance`` cookie and
matching ``User-Agent``. Those are handed back to the fast ``cloudscraper``
transport, which can then fetch normally until the cookie expires.

We use `patchright <https://github.com/Kaliiiiiiiiii-Vinyzu/patchright>`_, a
stealth-patched Playwright drop-in. Vanilla Playwright is detected by Cloudflare
(its CDP automation signals leak through); patchright hides them. ``headless``
mode is detected regardless of engine, so the solve runs headful by default.

The ``patchright`` package is an optional dependency
(``pip install peakbagger[browser]``); importing it is deferred so the rest of
the CLI works without it installed.
"""

import json
import os
import time
from pathlib import Path
from typing import Any, cast

from loguru import logger

# How long to wait for the Cloudflare challenge to clear before giving up.
_SOLVE_TIMEOUT_SECONDS = 45.0

# System Chrome gives the strongest stealth and needs no browser download.
# Overridable for environments where only bundled Chromium is available.
_BROWSER_CHANNEL = os.environ.get("PEAKBAGGER_BROWSER_CHANNEL", "chrome")


class BrowserTransportError(Exception):
    """Base error for the browser transport."""


class BrowserTransportUnavailableError(BrowserTransportError):
    """Raised when patchright (the optional browser dependency) is not installed."""


class ChallengeNotSolvedError(BrowserTransportError):
    """Raised when the Cloudflare challenge did not clear within the timeout."""


def _cache_dir() -> Path:
    """Return the peakbagger cache directory (not created; reads must not mkdir)."""
    base = os.environ.get("XDG_CACHE_HOME")
    root = Path(base) if base else Path.home() / ".cache"
    return root / "peakbagger"


def _clearance_path() -> Path:
    """Path to the cached Cloudflare clearance file."""
    return _cache_dir() / "cloudflare_clearance.json"


def _profile_dir() -> Path:
    """Persistent Chrome profile dir for the solver (separate from the user's).

    Chrome locks this directory, so only one solve may run at a time;
    concurrent CLI invocations that both hit a challenge will fail to launch.
    """
    return _cache_dir() / "chrome-profile"


def load_clearance() -> dict[str, Any] | None:
    """Load cached clearance (User-Agent + cookies), or None if missing/expired.

    The ``cf_clearance`` cookie is short-lived; if it has expired we discard the
    whole cache so the caller re-solves.
    """
    path = _clearance_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.debug(f"Ignoring unreadable clearance cache: {e}")
        return None

    cookies = data.get("cookies", [])
    cf_clearance = next((c for c in cookies if c.get("name") == "cf_clearance"), None)
    if cf_clearance is None:
        return None

    expires = cf_clearance.get("expires", -1)
    if 0 < expires <= time.time():
        logger.debug("Cached cf_clearance has expired; ignoring")
        return None

    logger.debug("Loaded cached Cloudflare clearance")
    return data


def save_clearance(user_agent: str, cookies: list[dict[str, Any]]) -> None:
    """Persist the User-Agent and cookies to the cache file."""
    path = _clearance_path()
    payload = {"user_agent": user_agent, "cookies": cookies, "saved_at": time.time()}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload))
        logger.debug(f"Saved Cloudflare clearance to {path}")
    except OSError as e:
        logger.warning(f"Could not write clearance cache: {e}")


def _navigate_until_cleared(page: Any, url: str, timeout: float) -> None:
    """Navigate to ``url`` and wait until the Cloudflare challenge clears."""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=int(timeout * 1000))
    except Exception as e:
        raise ChallengeNotSolvedError(f"Navigation to {url} failed: {e}") from e

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if "just a moment" not in page.title().lower():
            return
        time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))
    raise ChallengeNotSolvedError(
        f"Cloudflare challenge did not clear within {timeout:.0f}s. "
        "Try again; if the browser window did not appear, ensure Google "
        "Chrome is installed (or set PEAKBAGGER_BROWSER_CHANNEL)."
    )


def solve_challenge(
    url: str,
    *,
    timeout: float = _SOLVE_TIMEOUT_SECONDS,
    headless: bool = False,
) -> tuple[str, list[dict[str, Any]]]:
    """Drive a stealth browser through the Cloudflare challenge for ``url``.

    Returns a ``(user_agent, cookies)`` tuple, where ``cookies`` includes the
    ``cf_clearance`` cookie. ``headless`` is detected by Cloudflare, so the
    default (visible) is strongly recommended.

    Raises:
        BrowserTransportUnavailableError: patchright is not installed.
        ChallengeNotSolvedError: the challenge did not clear in time.
    """
    try:
        from patchright.sync_api import sync_playwright  # ty: ignore[unresolved-import]
    except ImportError as e:
        raise BrowserTransportUnavailableError(
            "patchright is required to bypass Cloudflare. Install it with: "
            "pip install 'peakbagger[browser]' (and ensure Google Chrome is installed)."
        ) from e

    mode = "headless" if headless else "headful"
    logger.info(f"Solving Cloudflare challenge via {mode} browser: {url}")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(_profile_dir()),
            channel=_BROWSER_CHANNEL,
            headless=headless,
            no_viewport=True,
        )
        try:
            # launch_persistent_context opens a default page; reuse it.
            page = context.pages[0] if context.pages else context.new_page()
            _navigate_until_cleared(page, url, timeout)
            user_agent = cast("str", page.evaluate("() => navigator.userAgent"))
            cookies = cast("list[dict[str, Any]]", context.cookies())
        finally:
            context.close()

    if not any(c.get("name") == "cf_clearance" for c in cookies):
        raise ChallengeNotSolvedError(
            "Browser left the challenge page but no cf_clearance cookie was set; "
            "the site may have shown an error or a non-managed challenge."
        )

    logger.info("Cloudflare challenge solved; harvested clearance cookie")
    return user_agent, cookies
