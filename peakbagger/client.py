"""HTTP client for PeakBagger.com with rate limiting and Cloudflare bypass."""

import time
from typing import TYPE_CHECKING, Any, cast

import cloudscraper
from loguru import logger

if TYPE_CHECKING:
    from requests import Response


class PeakBaggerClient:
    """HTTP client for accessing PeakBagger.com with respectful rate limiting.

    PeakBagger sits behind a Cloudflare *managed* challenge that ``cloudscraper``
    cannot solve. When a request is challenged (HTTP 403, ``cf-mitigated:
    challenge``), the client lazily drives a stealth browser to mint a
    ``cf_clearance`` cookie (see :mod:`peakbagger.browser_transport`), applies it
    to the session, and retries. The cookie is cached on disk and reused across
    runs until it expires, so the browser only runs occasionally.
    """

    BASE_URL: str = "https://www.peakbagger.com"

    def __init__(self, rate_limit_seconds: float = 2.0) -> None:
        """
        Initialize the client.

        Args:
            rate_limit_seconds: Minimum seconds between requests (default: 2.0)
        """
        self.rate_limit: float = rate_limit_seconds
        self._last_request_time: float | None = None

        # Create cloudscraper session to bypass Cloudflare
        self.session: Any = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )

        # Reuse a previously minted Cloudflare clearance cookie if available.
        self._load_cached_clearance()

    def _load_cached_clearance(self) -> None:
        """Apply a cached Cloudflare clearance (cookie + User-Agent) if present."""
        from peakbagger.browser_transport import load_clearance

        cached = load_clearance()
        if cached:
            self._apply_clearance(cached["user_agent"], cached["cookies"])

    # Cloudflare cookies that carry the challenge clearance; other site cookies
    # are not needed and would just pollute the session jar.
    _CLEARANCE_COOKIES = frozenset({"cf_clearance", "__cf_bm"})

    def _apply_clearance(self, user_agent: str, cookies: list[dict[str, Any]]) -> None:
        """Inject a solved User-Agent and Cloudflare cookies into the session.

        The User-Agent must match the browser that minted ``cf_clearance`` or
        Cloudflare rejects the cookie.
        """
        if user_agent:
            self.session.headers["User-Agent"] = user_agent
        for cookie in cookies:
            if cookie.get("name") not in self._CLEARANCE_COOKIES:
                continue
            value = cookie.get("value")
            if value is None:
                continue
            self.session.cookies.set(
                cookie["name"],
                value,
                domain=cookie.get("domain"),
                path=cookie.get("path", "/"),
            )

    @staticmethod
    def _is_cloudflare_challenge(response: "Response") -> bool:
        """Return True if the response is a Cloudflare managed challenge page."""
        if response.status_code != 403:
            return False
        if response.headers.get("cf-mitigated") == "challenge":
            return True
        return "Just a moment" in response.text[:2000]

    def _solve_challenge(self, url: str) -> None:
        """Mint a fresh Cloudflare clearance for ``url`` and apply + cache it."""
        from peakbagger.browser_transport import save_clearance, solve_challenge

        user_agent, cookies = solve_challenge(url)
        self._apply_clearance(user_agent, cookies)
        clearance = [c for c in cookies if c.get("name") in self._CLEARANCE_COOKIES]
        save_clearance(user_agent, clearance)

    def _wait_for_rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        if self._last_request_time is not None:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.rate_limit:
                wait_time = self.rate_limit - elapsed
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s before next request")
                time.sleep(wait_time)

    def _send(self, url: str, params: dict[str, str] | None) -> tuple[str, "Response", float]:
        """Issue one rate-limited GET; returns (resolved_url, response, start_time)."""
        self._wait_for_rate_limit()
        if not url.startswith("http"):
            url = f"{self.BASE_URL}/{url.lstrip('/')}"
        start_time = time.time()
        try:
            response = self.session.get(url, params=params)
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e!s}")
            raise Exception(f"Failed to fetch {url}: {e!s}") from e
        self._last_request_time = time.time()
        return url, response, start_time

    def get(
        self,
        url: str,
        params: dict[str, str] | None = None,
        *,
        _allow_solve: bool = True,
    ) -> str:
        """Make a rate-limited GET, solving a Cloudflare challenge once if needed.

        Args:
            url: Full URL or path (if path, will be joined with BASE_URL)
            params: Optional query parameters

        Returns:
            Response text (HTML)
        """
        url, response, start_time = self._send(url, params)

        if self._is_cloudflare_challenge(response):
            if _allow_solve:
                elapsed_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"GET {url} - 403 (cf-challenge) - {elapsed_ms:.0f}ms; solving via browser"
                )
                self._solve_challenge(url)
                return self.get(url, params=params, _allow_solve=False)
            logger.error(f"Cloudflare challenge persists after browser solve: {url}")
            raise Exception(
                f"Failed to fetch {url}: Cloudflare challenge not cleared by browser solve"
            )

        try:
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e!s}")
            raise Exception(f"Failed to fetch {url}: {e!s}") from e

        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(f"GET {url} - {response.status_code} - {elapsed_ms:.0f}ms")
        return cast("str", response.text)

    def close(self) -> None:
        """Close the session."""
        self.session.close()
