"""HTTP client for PeakBagger.com with rate limiting and Cloudflare bypass."""

import time

import cloudscraper

from peakbagger import __version__


class PeakBaggerClient:
    """HTTP client for accessing PeakBagger.com with respectful rate limiting."""

    BASE_URL = "https://www.peakbagger.com"

    def __init__(self, rate_limit_seconds: float = 2.0):
        """
        Initialize the client.

        Args:
            rate_limit_seconds: Minimum seconds between requests (default: 2.0)
        """
        self.rate_limit = rate_limit_seconds
        self._last_request_time: float | None = None

        # Create cloudscraper session to bypass Cloudflare
        self.session = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )

        # Set a clear user agent
        self.session.headers.update(
            {
                "User-Agent": f"peakbagger-cli/{__version__} (personal use; https://github.com/yourusername/peakbagger-cli)"
            }
        )

    def _wait_for_rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        if self._last_request_time is not None:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.rate_limit:
                time.sleep(self.rate_limit - elapsed)

    def get(self, url: str, params: dict | None = None) -> str:
        """
        Make a GET request with rate limiting.

        Args:
            url: Full URL or path (if path, will be joined with BASE_URL)
            params: Optional query parameters

        Returns:
            Response text (HTML)

        Raises:
            Exception: If request fails
        """
        # Wait for rate limit
        self._wait_for_rate_limit()

        # Build full URL if needed
        if not url.startswith("http"):
            url = f"{self.BASE_URL}/{url.lstrip('/')}"

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            self._last_request_time = time.time()
            return response.text
        except Exception as e:
            raise Exception(f"Failed to fetch {url}: {e!s}") from e

    def close(self) -> None:
        """Close the session."""
        self.session.close()
