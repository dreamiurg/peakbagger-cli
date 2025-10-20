"""HTML parsing and data extraction for PeakBagger.com."""

import re
from typing import TYPE_CHECKING, Any

from bs4 import BeautifulSoup

from peakbagger.models import Ascent, Peak, SearchResult

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

        # Find the search results table (has "Peak Search Results" header before it)
        # Format: <h2>Peak Search Results</h2><table class="gray">...
        search_header: Tag | None = soup.find("h2", string="Peak Search Results")  # type: ignore[assignment]
        if not search_header:
            return results

        # Find the next table after the header
        table: Tag | None = search_header.find_next("table", class_="gray")  # type: ignore[assignment]
        if not table:
            return results

        # Skip header row, process data rows
        rows: list[Tag] = table.find_all("tr")[1:]  # type: ignore[assignment]

        for row in rows:
            cells: list[Tag] = row.find_all("td")  # type: ignore[assignment]
            if len(cells) < 5:  # Need at least: Type, Name, Location, Range, Elevation
                continue

            # Extract peak link (2nd column)
            link: Tag | None = cells[1].find("a", href=lambda x: x and "peak.aspx?pid=" in x)  # type: ignore[assignment]
            if not link:
                continue

            href: str = link["href"]  # type: ignore[assignment]
            name: str = link.get_text(strip=True)

            # Extract peak ID from URL
            match = re.search(r"pid=(-?\d+)", href)
            if not match:
                continue

            pid: str = match.group(1)

            # Extract location (3rd column)
            location: str = cells[2].get_text(strip=True)

            # Extract range (4th column)
            range_name: str = cells[3].get_text(strip=True)

            # Extract elevation in feet (5th column)
            elevation_ft_str: str = cells[4].get_text(strip=True)
            elevation_ft: int | None = None
            if elevation_ft_str and elevation_ft_str.isdigit():
                elevation_ft = int(elevation_ft_str)

            # Convert to meters (approximate: 1 ft = 0.3048 m)
            elevation_m: int | None = None
            if elevation_ft:
                elevation_m = int(elevation_ft * 0.3048)

            results.append(
                SearchResult(
                    pid=pid,
                    name=name,
                    url=href,
                    location=location if location else None,
                    range=range_name if range_name else None,
                    elevation_ft=elevation_ft,
                    elevation_m=elevation_m,
                )
            )

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
            List of dicts with list_name, rank, and url
        """
        lists: list[dict[str, Any]] = []

        # Find the "Peak Lists" section
        # Format: <a href="list.aspx?lid=5030">List Name</a> (Rank #1)
        pattern = r'<a href="(list\.aspx\?lid=\d+)">([^<]+)</a>\s*\(Rank #(\d+)\)'

        for match in re.finditer(pattern, html):
            url: str = match.group(1)
            list_name: str = match.group(2)
            rank: int = int(match.group(3))
            lists.append(
                {"list_name": list_name, "rank": rank, "url": f"https://www.peakbagger.com/{url}"}
            )

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
        route_pattern = r"<tr><td valign=top>Route #\d+\s*</td><td>([^<]+)<br/>(.*?)</td></tr>"

        for match in re.finditer(route_pattern, html, re.DOTALL):
            route_name: str = match.group(1).strip()
            route_details: str = match.group(2)

            route: dict[str, Any] = {"name": route_name}

            # Extract trailhead
            trailhead_match = re.search(
                r"Trailhead:\s*([^<(]+)\s*(?:\([^)]+\))?\s*([\d,]+)\s*ft", route_details
            )
            if trailhead_match:
                route["trailhead"] = trailhead_match.group(1).strip()
                route["trailhead_elevation_ft"] = int(trailhead_match.group(2).replace(",", ""))

            # Extract vertical gain
            gain_match = re.search(r"Vertical Gain:\s*([\d,]+)\s*ft", route_details)
            if gain_match:
                route["vertical_gain_ft"] = int(gain_match.group(1).replace(",", ""))

            # Extract distance
            distance_match = re.search(r"Distance \(one way\):\s*([\d.]+)\s*mi", route_details)
            if distance_match:
                route["distance_mi"] = float(distance_match.group(1))

            routes.append(route)

        return routes

    @staticmethod
    def parse_peak_ascents(html: str) -> list[Ascent]:
        """
        Parse ascent list from PeakAscents.aspx page.

        Args:
            html: HTML content from peak ascents page

        Returns:
            List of Ascent objects
        """
        soup: BeautifulSoup = BeautifulSoup(html, "lxml")
        ascents: list[Ascent] = []

        # Find all tables
        tables: list[Tag] = soup.find_all("table")  # type: ignore[assignment]

        # Look for the data table (has specific header structure)
        data_table: Tag | None = None
        for table in tables:
            rows: list[Tag] = table.find_all("tr")  # type: ignore[assignment]
            if len(rows) < 10:
                continue

            # Check if second row has expected headers
            if len(rows) > 1:
                header_row: Tag = rows[1]
                headers: list[Tag] = header_row.find_all(["th", "td"])  # type: ignore[assignment]
                if len(headers) == 14:
                    header_texts: list[str] = [h.get_text(strip=True) for h in headers]
                    # Check for "Climber" and "Ascent Date" (may have non-breaking spaces)
                    if (
                        "Climber" in header_texts
                        and "Ascent" in header_texts[1]
                        and "Date" in header_texts[1]
                    ):
                        data_table = table
                        break

        if not data_table:
            return ascents

        rows = data_table.find_all("tr")

        # Process data rows (skip first 2 rows: separator and header)
        for row in rows[2:]:
            cells: list[Tag] = row.find_all(["td", "th"])  # type: ignore[assignment]
            if len(cells) != 14:
                continue

            # Extract climber name and ID (column 0)
            climber_cell: Tag = cells[0]
            climber_link: Tag | None = climber_cell.find(
                "a", href=lambda x: x and "climber.aspx?cid=" in x
            )  # type: ignore[assignment]
            if not climber_link:
                continue

            climber_name: str = climber_link.get_text(strip=True)
            climber_href: str = climber_link["href"]  # type: ignore[assignment]
            climber_id_match = re.search(r"cid=(\d+)", climber_href)
            climber_id: str | None = climber_id_match.group(1) if climber_id_match else None

            # Extract ascent date and ID (column 1)
            date_cell: Tag = cells[1]
            date_link: Tag | None = date_cell.find(
                "a", href=lambda x: x and "ascent.aspx?aid=" in x
            )  # type: ignore[assignment]
            if not date_link:
                continue

            date_text: str = date_link.get_text(strip=True)
            # Skip rows with "Unknown" dates or invalid formats
            if date_text == "Unknown" or not date_text:
                date_text_value: str | None = None
            else:
                # Extract date format (YYYY, YYYY-MM, or YYYY-MM-DD) - ignore trailing characters
                date_pattern = re.compile(r"^\d{4}(-\d{2})?(-\d{2})?")
                match = date_pattern.match(date_text)
                date_text_value = match.group(0) if match else None

            ascent_href: str = date_link["href"]  # type: ignore[assignment]
            ascent_id_match = re.search(r"aid=(\d+)", ascent_href)
            if not ascent_id_match:
                continue
            ascent_id: str = ascent_id_match.group(1)

            # Check for GPX track (column 3)
            gps_cell: Tag = cells[3]
            gps_img: Tag | None = gps_cell.find("img", src=lambda x: x and "GPS.gif" in x)  # type: ignore[assignment]
            has_gpx: bool = gps_img is not None

            # Check for trip report (column 4)
            tr_cell: Tag = cells[4]
            tr_text: str = tr_cell.get_text(strip=True)
            has_trip_report: bool = tr_text.startswith("TR-")
            trip_report_words: int | None = None
            if has_trip_report:
                # Extract word count (format: "TR-123")
                tr_match = re.search(r"TR-(\d+)", tr_text)
                if tr_match:
                    trip_report_words = int(tr_match.group(1))

            # Extract route name (column 5)
            route_cell: Tag = cells[5]
            route: str | None = route_cell.get_text(strip=True) or None

            ascents.append(
                Ascent(
                    ascent_id=ascent_id,
                    climber_name=climber_name,
                    climber_id=climber_id,
                    date=date_text_value,
                    has_gpx=has_gpx,
                    has_trip_report=has_trip_report,
                    trip_report_words=trip_report_words,
                    route=route,
                )
            )

        return ascents
