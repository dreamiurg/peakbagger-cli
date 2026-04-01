"""High-level Python API for PeakBagger.com data.

Example usage::

    from peakbagger import PeakBagger

    pb = PeakBagger()

    # Search for peaks
    results = pb.search("Mount Rainier")
    for r in results:
        print(r.name, r.elevation_ft)

    # Get peak details
    peak = pb.get_peak("2296")
    print(peak.name, peak.prominence_ft)

    # List ascents
    ascents = pb.get_ascents("2296")
    for a in ascents:
        print(a.date, a.climber_name)

    # Get ascent detail
    ascent = pb.get_ascent("12963")
    print(ascent.trip_report_text)
"""

from peakbagger.client import PeakBaggerClient
from peakbagger.models import Ascent, Peak, SearchResult
from peakbagger.scraper import PeakBaggerScraper


class PeakBagger:
    """High-level client for retrieving data from PeakBagger.com.

    Manages the HTTP client lifecycle and provides simple methods for
    common operations. Use as a context manager to ensure the session
    is properly closed::

        with PeakBagger() as pb:
            results = pb.search("Denali")

    Or manage the lifecycle manually::

        pb = PeakBagger()
        results = pb.search("Denali")
        pb.close()
    """

    def __init__(self, rate_limit_seconds: float = 2.0) -> None:
        """
        Initialize the PeakBagger client.

        Args:
            rate_limit_seconds: Minimum seconds between HTTP requests (default: 2.0).
                Reduce below 2.0 only for testing against saved HTML.
        """
        self._client = PeakBaggerClient(rate_limit_seconds=rate_limit_seconds)
        self._scraper = PeakBaggerScraper()

    def search(self, query: str) -> list[SearchResult]:
        """
        Search for peaks by name.

        Args:
            query: Search term (e.g., "Mount Rainier", "Denali")

        Returns:
            List of SearchResult objects matching the query.

        Raises:
            Exception: If the HTTP request fails.
        """
        html = self._client.get("/search.aspx", params={"ss": query, "tid": "M"})
        return self._scraper.parse_search_results(html)

    def get_peak(self, peak_id: str | int) -> Peak | None:
        """
        Get detailed information about a specific peak.

        Args:
            peak_id: The PeakBagger peak ID (e.g., "2296" or 2296 for Mount Rainier)

        Returns:
            Peak object with full details, or None if parsing fails.

        Raises:
            Exception: If the HTTP request fails.
        """
        pid = str(peak_id)
        html = self._client.get("/peak.aspx", params={"pid": pid})
        return self._scraper.parse_peak_detail(html, pid)

    def get_ascents(self, peak_id: str | int) -> list[Ascent]:
        """
        List all logged ascents for a specific peak.

        Args:
            peak_id: The PeakBagger peak ID (e.g., "2296" or 2296 for Mount Rainier)

        Returns:
            List of Ascent objects, sorted by date descending (most recent first).

        Raises:
            Exception: If the HTTP request fails.
        """
        pid = str(peak_id)
        html = self._client.get(
            "/climber/PeakAscents.aspx",
            params={"pid": pid, "sort": "ascentdate", "u": "ft", "y": "9999"},
        )
        return self._scraper.parse_peak_ascents(html)

    def get_ascent(self, ascent_id: str | int) -> Ascent | None:
        """
        Get detailed information about a specific ascent.

        Args:
            ascent_id: The PeakBagger ascent ID (e.g., "12963")

        Returns:
            Ascent object with full details including trip report, or None if parsing fails.

        Raises:
            Exception: If the HTTP request fails.
        """
        aid = str(ascent_id)
        html = self._client.get("/climber/ascent.aspx", params={"aid": aid})
        return self._scraper.parse_ascent_detail(html, aid)

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._client.close()

    def __enter__(self) -> "PeakBagger":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
