"""HTML parsing and data extraction for PeakBagger.com."""

import re
from typing import TYPE_CHECKING, Any

from bs4 import BeautifulSoup
from loguru import logger

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
        logger.debug("Parsing search results from HTML")
        soup: BeautifulSoup = BeautifulSoup(html, "lxml")
        results: list[SearchResult] = []

        # Find the search results table (has "Peak Search Results" header before it)
        # Format: <h2>Peak Search Results</h2><table class="gray">...
        search_header: Tag | None = soup.find("h2", string="Peak Search Results")  # type: ignore[assignment]
        if not search_header:
            logger.debug("No search results header found")
            return results

        # Find the next table after the header
        table: Tag | None = search_header.find_next("table", class_="gray")  # type: ignore[assignment]
        if not table:
            logger.debug("No search results table found")
            return results

        # Skip header row, process data rows
        rows: list[Tag] = table.find_all("tr")[1:]  # type: ignore[assignment]
        logger.debug(f"Found {len(rows)} result rows to process")

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

        logger.debug(f"Successfully parsed {len(results)} search results")
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
        logger.debug(f"Parsing peak detail for peak ID {pid}")
        soup: BeautifulSoup = BeautifulSoup(html, "lxml")

        try:
            # Extract peak name and state from H1
            h1: Tag | None = soup.find("h1")  # type: ignore[assignment]
            if not h1:
                logger.debug("No H1 tag found in peak detail page")
                return None

            title_text: str = h1.get_text(strip=True)
            # Format is usually "Peak Name, State/Province"
            name_parts: list[str] = title_text.rsplit(", ", 1)
            name: str = name_parts[0]
            state: str | None = name_parts[1] if len(name_parts) > 1 else None

            logger.debug(f"Extracted peak name: {name}, state: {state}")

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
                    logger.debug(
                        f"Extracted elevation: {peak.elevation_ft} ft / {peak.elevation_m} m"
                    )

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

            # Extract ascent counts
            # Format: "Total ascents/attempts logged by registered Peakbagger.com users: <b>4388</b>"
            ascent_count_match = re.search(
                r"Total ascents/attempts logged.*?<b>(\d+)</b>", html, re.DOTALL
            )
            if ascent_count_match:
                peak.ascent_count = int(ascent_count_match.group(1))
                logger.debug(f"Extracted ascent count: {peak.ascent_count}")

            # Format: "(Total: 3960)"
            viewable_count_match = re.search(r"\(Total:\s*(\d+)\)", html)
            if viewable_count_match:
                peak.viewable_ascent_count = int(viewable_count_match.group(1))

            logger.debug(f"Successfully parsed peak detail for {name}")
            return peak

        except Exception as e:
            logger.error(f"Error parsing peak detail: {e}")
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

        Dynamically handles varying table structures across different peaks.
        Different peaks have different column counts (8-14 columns observed).

        Args:
            html: HTML content from peak ascents page

        Returns:
            List of Ascent objects
        """
        logger.debug("Parsing peak ascents from HTML")
        soup: BeautifulSoup = BeautifulSoup(html, "lxml")
        ascents: list[Ascent] = []

        # Find all tables
        tables: list[Tag] = soup.find_all("table")  # type: ignore[assignment]
        logger.debug(f"Found {len(tables)} tables in HTML")

        # Look for the data table with dynamic header detection
        data_table: Tag | None = None
        header_map: dict[str, int] = {}
        num_columns: int = 0

        for table in tables:
            rows: list[Tag] = table.find_all("tr")  # type: ignore[assignment]
            if len(rows) < 10:
                continue

            # Check if second row has expected headers
            if len(rows) > 1:
                header_row: Tag = rows[1]
                headers: list[Tag] = header_row.find_all(["th", "td"])  # type: ignore[assignment]

                # Table must have reasonable number of columns (not the merged giant table)
                if len(headers) < 3 or len(headers) > 20:
                    continue

                header_texts: list[str] = [h.get_text(strip=True) for h in headers]

                # Check for required columns: "Climber" and "Ascent Date"
                if "Climber" in header_texts and any(
                    "Ascent" in h and "Date" in h for h in header_texts
                ):
                    # Build header map for dynamic column access
                    for idx, header_text in enumerate(header_texts):
                        header_map[header_text] = idx

                    data_table = table
                    num_columns = len(headers)
                    logger.debug(
                        f"Found ascents data table with {num_columns} columns: {list(header_map.keys())}"
                    )
                    break

        if not data_table or not header_map:
            logger.debug("No valid ascents table found")
            return ascents

        # Get column indices (fallback to -1 if column doesn't exist)
        climber_idx = header_map.get("Climber", -1)
        date_idx = next((header_map[h] for h in header_map if "Ascent" in h and "Date" in h), -1)
        gps_idx = header_map.get("GPS", -1)
        tr_words_idx = header_map.get("TR-Words", -1)
        route_idx = header_map.get("Route", -1)

        if climber_idx == -1 or date_idx == -1:
            return ascents

        rows = data_table.find_all("tr")

        # Process data rows (skip first 2 rows: separator and header)
        for row in rows[2:]:
            cells: list[Tag] = row.find_all(["td", "th"])  # type: ignore[assignment]

            # Skip rows that don't match the expected column count
            if len(cells) != num_columns:
                continue

            # Extract climber name and ID (required column)
            climber_cell: Tag = cells[climber_idx]
            climber_link: Tag | None = climber_cell.find(
                "a", href=lambda x: x and "climber.aspx?cid=" in x
            )  # type: ignore[assignment]
            if not climber_link:
                continue

            climber_name: str = climber_link.get_text(strip=True)
            climber_href: str = climber_link["href"]  # type: ignore[assignment]
            climber_id_match = re.search(r"cid=(\d+)", climber_href)
            climber_id: str | None = climber_id_match.group(1) if climber_id_match else None

            # Extract ascent date and ID (required column)
            date_cell: Tag = cells[date_idx]
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

            # Check for GPX track (optional column)
            has_gpx: bool = False
            if gps_idx != -1:
                gps_cell: Tag = cells[gps_idx]
                gps_img: Tag | None = gps_cell.find("img", src=lambda x: x and "GPS.gif" in x)  # type: ignore[assignment]
                has_gpx = gps_img is not None

            # Check for trip report (optional column)
            has_trip_report: bool = False
            trip_report_words: int | None = None
            if tr_words_idx != -1:
                tr_cell: Tag = cells[tr_words_idx]
                tr_text: str = tr_cell.get_text(strip=True)
                has_trip_report = tr_text.startswith("TR-")
                if has_trip_report:
                    # Extract word count (format: "TR-123")
                    tr_match = re.search(r"TR-(\d+)", tr_text)
                    if tr_match:
                        trip_report_words = int(tr_match.group(1))

            # Extract route name (optional column)
            route: str | None = None
            if route_idx != -1:
                route_cell: Tag = cells[route_idx]
                route = route_cell.get_text(strip=True) or None

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

        logger.debug(f"Successfully parsed {len(ascents)} ascents")
        return ascents

    @staticmethod
    def parse_ascent_detail(html: str, ascent_id: str) -> Ascent | None:
        """
        Parse detailed ascent information from ascent.aspx page.

        Args:
            html: HTML content from ascent detail page
            ascent_id: Ascent ID

        Returns:
            Ascent object with extracted data, or None if parsing fails
        """
        logger.debug(f"Parsing ascent detail for ascent ID {ascent_id}")
        soup: BeautifulSoup = BeautifulSoup(html, "lxml")

        try:
            # Extract title: "Ascent of [Peak Name] on [Date]" or "Ascent of [Peak Name] in [Year]"
            h1: Tag | None = soup.find("h1")  # type: ignore[assignment]
            if not h1:
                logger.debug("No H1 tag found in ascent detail page")
                return None

            title_text: str = h1.get_text(strip=True)
            # Parse "Ascent of Peak Name on/in Date"
            peak_name: str | None = None
            if " on " in title_text:
                parts = title_text.split(" on ", 1)
                peak_name = parts[0].replace("Ascent of ", "").strip()
            elif " in " in title_text:
                parts = title_text.split(" in ", 1)
                peak_name = parts[0].replace("Ascent of ", "").strip()

            # Extract climber from H2: "Climber: [Name]"
            h2: Tag | None = soup.find("h2")  # type: ignore[assignment]
            climber_name: str | None = None
            climber_id: str | None = None
            if h2:
                climber_link: Tag | None = h2.find(
                    "a", href=lambda x: x and "climber.aspx?cid=" in x
                )  # type: ignore[assignment]
                if climber_link:
                    climber_name = climber_link.get_text(strip=True)
                    climber_href: str = climber_link["href"]  # type: ignore[assignment]
                    cid_match = re.search(r"cid=(\d+)", climber_href)
                    if cid_match:
                        climber_id = cid_match.group(1)

            if not climber_name:
                return None

            # Find the left gray table (width="49%", align="left")
            table: Tag | None = soup.find(
                "table", class_="gray", attrs={"width": "49%", "align": "left"}
            )  # type: ignore[assignment]
            if not table:
                return None

            # Initialize Ascent object with basic info
            ascent: Ascent = Ascent(
                ascent_id=ascent_id,
                climber_name=climber_name,
                climber_id=climber_id,
                peak_name=peak_name,
            )

            # Extract data from table rows
            rows: list[Tag] = table.find_all("tr")  # type: ignore[assignment]
            for row in rows:
                cells: list[Tag] = row.find_all("td")  # type: ignore[assignment]
                if len(cells) < 1:
                    continue

                # Check for colspan=2 (trip report section)
                if len(cells) == 1 and cells[0].get("colspan") == "2":
                    # Trip report section
                    h2_tr: Tag | None = cells[0].find("h2", string=re.compile("Trip Report"))  # type: ignore[assignment]
                    if h2_tr:
                        # Extract trip report text
                        # Get all text after the h2
                        report_parts: list[str] = []
                        for elem in cells[0].descendants:
                            if isinstance(elem, str):
                                text = elem.strip()
                                if text and text != "URL Link:":
                                    report_parts.append(text)

                        # Join and clean up
                        report_text = " ".join(report_parts)
                        # Remove "Ascent Trip Report" header
                        report_text = re.sub(r"^Ascent Trip Report\s*", "", report_text)
                        # Remove URL Link label and peakbagger.com text
                        report_text = re.sub(r"URL Link:\s*peakbagger\.com\s*", "", report_text)
                        report_text = re.sub(r"^peakbagger\.com\s*", "", report_text)

                        if report_text:
                            ascent.trip_report_text = report_text.strip()

                        # Extract external URL if present
                        url_link: Tag | None = cells[0].find("a", href=re.compile(r"^https?://"))  # type: ignore[assignment]
                        if url_link and url_link.get("href"):
                            href = url_link["href"]  # type: ignore[assignment]
                            # Only store if not peakbagger.com
                            if "peakbagger.com" not in href:
                                ascent.trip_report_url = href
                    continue

                if len(cells) < 2:
                    continue

                # Get label from first cell
                # Some labels have <b> tags, others are just text
                label_cell = cells[0]
                label_b: Tag | None = label_cell.find("b")  # type: ignore[assignment]
                if label_b:
                    label: str = label_b.get_text(strip=True).rstrip(":")
                else:
                    label = label_cell.get_text(strip=True).rstrip(":")

                value_cell = cells[1]

                # Parse based on label
                if label == "Date":
                    date_text = value_cell.get_text(strip=True)
                    # Try to parse different date formats
                    # Format: "Sunday, January 23, 1966" -> extract date
                    # Format: "1951" -> just year
                    # Format: "2024-10-21" -> ISO format
                    if date_text and date_text != "Unknown":
                        # Try to parse full date from "Month Day, Year" format
                        month_day_year = re.search(
                            r"([A-Z][a-z]+)\s+(\d{1,2}),\s+(\d{4})", date_text
                        )
                        if month_day_year:
                            from datetime import datetime

                            month_name = month_day_year.group(1)
                            day = month_day_year.group(2)
                            year = month_day_year.group(3)
                            try:
                                parsed_date = datetime.strptime(
                                    f"{month_name} {day} {year}", "%B %d %Y"
                                )
                                ascent.date = parsed_date.strftime("%Y-%m-%d")
                            except ValueError:
                                # Fall back to ISO format if already in that format
                                iso_match = re.search(r"(\d{4}(?:-\d{2})?(?:-\d{2})?)", date_text)
                                if iso_match:
                                    ascent.date = iso_match.group(1)
                        else:
                            # Try ISO format or just year
                            iso_match = re.search(r"(\d{4}(?:-\d{2})?(?:-\d{2})?)", date_text)
                            if iso_match:
                                ascent.date = iso_match.group(1)

                elif label == "Ascent Type":
                    # Extract text after the image
                    type_text = value_cell.get_text(strip=True)
                    ascent.ascent_type = type_text

                elif label == "Peak":
                    # Extract peak link and ID
                    peak_link: Tag | None = value_cell.find(
                        "a", href=lambda x: x and "peak.aspx?pid=" in x
                    )  # type: ignore[assignment]
                    if peak_link:
                        ascent.peak_name = peak_link.get_text(strip=True)
                        peak_href: str = peak_link["href"]  # type: ignore[assignment]
                        pid_match = re.search(r"pid=(-?\d+)", peak_href)
                        if pid_match:
                            ascent.peak_id = pid_match.group(1)

                elif "Location" in label:
                    ascent.location = value_cell.get_text(strip=True)

                elif "Elevation" in label:
                    # Parse "5341 ft / 1627 m"
                    elev_text = value_cell.get_text(strip=True)
                    elev_match = re.search(r"([\d,]+)\s*ft\s*/\s*([\d,]+)\s*m", elev_text)
                    if elev_match:
                        ascent.elevation_ft = int(elev_match.group(1).replace(",", ""))
                        ascent.elevation_m = int(elev_match.group(2).replace(",", ""))

                elif label == "Route" or "Route" in label:
                    route_text = value_cell.get_text(strip=True)
                    if route_text:
                        ascent.route = route_text

                elif "Elevation Gain" in label or "Gain" in label:
                    # Parse GPX-derived elevation gain
                    gain_text = value_cell.get_text(strip=True)
                    gain_match = re.search(r"([\d,]+)\s*ft", gain_text)
                    if gain_match:
                        ascent.elevation_gain_ft = int(gain_match.group(1).replace(",", ""))

                elif "Distance" in label:
                    # Parse GPX-derived distance
                    dist_text = value_cell.get_text(strip=True)
                    dist_match = re.search(r"([\d.]+)\s*mi", dist_text)
                    if dist_match:
                        ascent.distance_mi = float(dist_match.group(1))

                elif "Duration" in label or "Time" in label:
                    # Parse GPX-derived duration
                    dur_text = value_cell.get_text(strip=True)
                    # Try to parse hours (could be "4.5 hours" or "4:30")
                    hour_match = re.search(r"([\d.]+)\s*(?:hours?|hrs?)", dur_text, re.IGNORECASE)
                    if hour_match:
                        ascent.duration_hours = float(hour_match.group(1))
                    else:
                        # Try H:MM format
                        time_match = re.search(r"(\d+):(\d+)", dur_text)
                        if time_match:
                            hours = int(time_match.group(1))
                            minutes = int(time_match.group(2))
                            ascent.duration_hours = hours + (minutes / 60.0)

            logger.debug(f"Successfully parsed ascent detail for {ascent.climber_name}")
            return ascent

        except Exception as e:
            logger.error(f"Error parsing ascent detail: {e}")
            return None
