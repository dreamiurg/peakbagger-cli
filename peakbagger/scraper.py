"""HTML parsing and data extraction for PeakBagger.com."""

import re
from typing import TYPE_CHECKING, Any

from bs4 import BeautifulSoup

from peakbagger.models import Peak, SearchResult

if TYPE_CHECKING:
    from bs4.element import Tag


class PeakBaggerScraper:
    """Scraper for extracting peak data from PeakBagger.com HTML."""

    @staticmethod
    def parse_search_results(html: str) -> list[SearchResult]:
        """
        Parse search results from search.aspx page.

        Args:
            html: HTML content from search page

        Returns:
            List of SearchResult objects
        """
        soup: BeautifulSoup = BeautifulSoup(html, "lxml")
        results: list[SearchResult] = []

        # Find all links to peak pages
        peak_links: list[Tag] = soup.find_all("a", href=lambda x: x and "peak.aspx?pid=" in x)

        for link in peak_links:
            href: str = link["href"]  # type: ignore[assignment]
            name: str = link.get_text(strip=True)

            # Extract peak ID from URL
            match = re.search(r"pid=(-?\d+)", href)
            if match:
                pid = match.group(1)
                results.append(SearchResult(pid=pid, name=name, url=href))

        return results

    @staticmethod
    def parse_peak_detail(html: str, pid: str) -> Peak | None:
        """
        Parse detailed peak information from peak.aspx page.

        Args:
            html: HTML content from peak detail page
            pid: Peak ID

        Returns:
            Peak object with extracted data, or None if parsing fails
        """
        soup: BeautifulSoup = BeautifulSoup(html, "lxml")

        try:
            # Extract peak name and state from H1
            h1: Tag | None = soup.find("h1")  # type: ignore[assignment]
            if not h1:
                return None

            title_text: str = h1.get_text(strip=True)
            # Format is usually "Peak Name, State/Province"
            name_parts: list[str] = title_text.rsplit(", ", 1)
            name: str = name_parts[0]
            state: str | None = name_parts[1] if len(name_parts) > 1 else None

            # Initialize peak object
            peak: Peak = Peak(pid=pid, name=name, state=state)

            # Extract elevation from H2
            h2: Tag | None = soup.find("h2")  # type: ignore[assignment]
            if h2:
                elevation_text: str = h2.get_text(strip=True)
                # Format: "Elevation: 10,984 feet, 3348 meters"
                elev_match = re.search(r"([\d,]+)\s*feet,\s*([\d,]+)\s*meters", elevation_text)
                if elev_match:
                    peak.elevation_ft = int(elev_match.group(1).replace(",", ""))
                    peak.elevation_m = int(elev_match.group(2).replace(",", ""))

            # Extract prominence (appears in table near H2)
            text: str = soup.get_text()
            prom_match = re.search(r"Prominence:\s*([\d,]+)\s*ft,\s*([\d,]+)\s*m", text)
            if prom_match:
                peak.prominence_ft = int(prom_match.group(1).replace(",", ""))
                peak.prominence_m = int(prom_match.group(2).replace(",", ""))

            # Extract isolation
            iso_match = re.search(r"True Isolation:\s*([\d.]+)\s*mi,\s*([\d.]+)\s*km", text)
            if iso_match:
                peak.isolation_mi = float(iso_match.group(1))
                peak.isolation_km = float(iso_match.group(2))

            # Extract latitude/longitude
            # Format: "41.03313, -106.68432 (Dec Deg)"
            latlon_match = re.search(r"([-\d.]+),\s*([-\d.]+)\s*\(Dec Deg\)", text)
            if latlon_match:
                peak.latitude = float(latlon_match.group(1))
                peak.longitude = float(latlon_match.group(2))

            # Extract country from the gray table
            if "United States" in text:
                peak.country = "United States"
            elif "Canada" in text:
                peak.country = "Canada"
            elif "Mexico" in text:
                peak.country = "Mexico"

            county_match = re.search(
                r"County/Second Level Region([^\n]*?)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text
            )
            if county_match:
                peak.county = county_match.group(2).strip()

            # Extract peak lists with ranks
            peak.peak_lists = PeakBaggerScraper._extract_peak_lists(html)

            # Extract route information
            peak.routes = PeakBaggerScraper._extract_routes(html)

            return peak

        except Exception as e:
            # Log error but don't crash
            print(f"Error parsing peak detail: {e}")
            return None

    @staticmethod
    def _extract_peak_lists(html: str) -> list[dict[str, Any]]:
        """
        Extract peak lists and ranks from peak detail page.

        Args:
            html: HTML content from peak detail page

        Returns:
            List of dicts with list_name and rank
        """
        lists: list[dict[str, Any]] = []

        # Find the "Peak Lists" section
        # Format: <a href="list.aspx?lid=5030">List Name</a> (Rank #1)
        pattern = r'<a href="list\.aspx\?lid=\d+">([^<]+)</a>\s*\(Rank #(\d+)\)'

        for match in re.finditer(pattern, html):
            list_name: str = match.group(1)
            rank: int = int(match.group(2))
            lists.append({"list_name": list_name, "rank": rank})

        return lists

    @staticmethod
    def _extract_routes(html: str) -> list[dict[str, Any]]:
        """
        Extract route information from peak detail page.

        Args:
            html: HTML content from peak detail page

        Returns:
            List of dicts with route details
        """
        routes: list[dict[str, Any]] = []

        # Find route sections
        # Format: <tr><td valign=top>Route #1 </td><td>Glacier Climb: Disappointment Cleaver<br/>...
        route_pattern = r'<tr><td valign=top>Route #\d+\s*</td><td>([^<]+)<br/>(.*?)</td></tr>'

        for match in re.finditer(route_pattern, html, re.DOTALL):
            route_name: str = match.group(1).strip()
            route_details: str = match.group(2)

            route: dict[str, Any] = {"name": route_name}

            # Extract trailhead
            trailhead_match = re.search(r'Trailhead:\s*([^<(]+)\s*(?:\([^)]+\))?\s*([\d,]+)\s*ft', route_details)
            if trailhead_match:
                route["trailhead"] = trailhead_match.group(1).strip()
                route["trailhead_elevation_ft"] = int(trailhead_match.group(2).replace(",", ""))

            # Extract vertical gain
            gain_match = re.search(r'Vertical Gain:\s*([\d,]+)\s*ft', route_details)
            if gain_match:
                route["vertical_gain_ft"] = int(gain_match.group(1).replace(",", ""))

            # Extract distance
            distance_match = re.search(r'Distance \(one way\):\s*([\d.]+)\s*mi', route_details)
            if distance_match:
                route["distance_mi"] = float(distance_match.group(1))

            routes.append(route)

        return routes
