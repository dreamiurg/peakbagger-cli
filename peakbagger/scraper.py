"""HTML parsing and data extraction for PeakBagger.com."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from bs4 import BeautifulSoup

from peakbagger.logging_config import get_logger
from peakbagger.models import Ascent, Peak, SearchResult

logger = get_logger()

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
        search_header: Tag | None = None
        for h2 in soup.find_all("h2"):  # type: ignore[assignment]
            if h2.get_text(strip=True) == "Peak Search Results":
                search_header = h2
                break
        if not search_header:
            logger.debug("No search results header found")
            return results

        table: Tag | None = search_header.find_next("table", class_="gray")
        if not table:
            logger.debug("No search results table found")
            return results

        rows: list[Tag] = table.find_all("tr")[1:]
        logger.debug(f"Found {len(rows)} result rows to process")

        for row in rows:
            result = PeakBaggerScraper._parse_search_row(row)
            if result:
                results.append(result)

        logger.debug(f"Successfully parsed {len(results)} search results")
        return results

    @staticmethod
    def _parse_search_row(row: Tag) -> SearchResult | None:
        """Parse a single search result table row into a SearchResult."""
        cells: list[Tag] = row.find_all("td")  # type: ignore[assignment]
        if len(cells) < 5:
            return None

        link: Tag | None = cells[1].find("a", href=lambda x: x and "peak.aspx?pid=" in x)  # type: ignore[assignment]
        if not link:
            return None

        href: str = str(link["href"])
        name: str = link.get_text(strip=True)

        match = re.search(r"pid=(-?\d+)", href)
        if not match:
            return None

        pid: str = match.group(1)
        location: str = cells[2].get_text(strip=True)
        range_name: str = cells[3].get_text(strip=True)

        elevation_ft, elevation_m = PeakBaggerScraper._parse_elevation(
            cells[4].get_text(strip=True)
        )

        return SearchResult(
            pid=pid,
            name=name,
            url=href,
            location=location if location else None,
            range=range_name if range_name else None,
            elevation_ft=elevation_ft,
            elevation_m=elevation_m,
        )

    @staticmethod
    def _parse_elevation(text: str) -> tuple[int | None, int | None]:
        """Parse elevation text like '14411 ft / 4392 m' into (ft, m) tuple."""
        elevation_ft: int | None = None
        ft_match = re.search(r"([\d,]+)\s*ft", text) or re.search(r"^([\d,]+)", text)
        if ft_match:
            elevation_ft = int(ft_match.group(1).replace(",", ""))

        elevation_m: int | None = None
        m_match = re.search(r"/\s*([\d,]+)\s*m", text)
        if m_match:
            elevation_m = int(m_match.group(1).replace(",", ""))
        elif elevation_ft is not None:
            elevation_m = round(elevation_ft * 0.3048)

        return elevation_ft, elevation_m

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
            name, state = PeakBaggerScraper._extract_name_and_state(soup)
            if name is None:
                return None

            peak: Peak = Peak(pid=pid, name=name, state=state)

            PeakBaggerScraper._extract_peak_elevation(soup, peak)

            text: str = soup.get_text()
            PeakBaggerScraper._extract_coordinates_and_location(text, peak)
            PeakBaggerScraper._extract_ascent_counts(html, peak)

            peak.peak_lists = PeakBaggerScraper._extract_peak_lists(html)
            peak.routes = PeakBaggerScraper._extract_routes(html)

            logger.debug(f"Successfully parsed peak detail for {name}")
            return peak

        except (AttributeError, ValueError, TypeError):
            logger.exception("Error parsing peak detail")
            return None
        except Exception:
            logger.exception("Unexpected error parsing peak detail")
            return None

    @staticmethod
    def _extract_name_and_state(soup: BeautifulSoup) -> tuple[str | None, str | None]:
        """Extract peak name and state from H1 tag."""
        h1: Tag | None = soup.find("h1")  # type: ignore[assignment]
        if not h1:
            logger.debug("No H1 tag found in peak detail page")
            return None, None

        title_text: str = h1.get_text(strip=True)
        name_parts: list[str] = title_text.rsplit(", ", 1)
        name: str = name_parts[0]
        state: str | None = name_parts[1] if len(name_parts) > 1 else None
        logger.debug(f"Extracted peak name: {name}, state: {state}")
        return name, state

    @staticmethod
    def _extract_peak_elevation(soup: BeautifulSoup, peak: Peak) -> None:
        """Extract elevation and prominence from page."""
        h2: Tag | None = soup.find("h2")  # type: ignore[assignment]
        if h2:
            elevation_text: str = h2.get_text(strip=True)
            elev_match = re.search(r"([\d,]+)\s*feet,\s*([\d,]+)\s*meters", elevation_text)
            if elev_match:
                peak.elevation_ft = int(elev_match.group(1).replace(",", ""))
                peak.elevation_m = int(elev_match.group(2).replace(",", ""))
                logger.debug(f"Extracted elevation: {peak.elevation_ft} ft / {peak.elevation_m} m")

    @staticmethod
    def _extract_coordinates_and_location(text: str, peak: Peak) -> None:
        """Extract prominence, isolation, coordinates, and country from page text."""
        prom_match = re.search(r"Prominence:\s*([\d,]+)\s*ft,\s*([\d,]+)\s*m", text)
        if prom_match:
            peak.prominence_ft = int(prom_match.group(1).replace(",", ""))
            peak.prominence_m = int(prom_match.group(2).replace(",", ""))

        iso_match = re.search(r"True Isolation:\s*([\d.]+)\s*mi,\s*([\d.]+)\s*km", text)
        if iso_match:
            peak.isolation_mi = float(iso_match.group(1))
            peak.isolation_km = float(iso_match.group(2))

        latlon_match = re.search(r"([-\d.]+),\s*([-\d.]+)\s*\(Dec Deg\)", text)
        if latlon_match:
            peak.latitude = float(latlon_match.group(1))
            peak.longitude = float(latlon_match.group(2))

        for country in ("United States", "Canada", "Mexico"):
            if country in text:
                peak.country = country
                break

        county_match = re.search(
            r"County/Second Level Region([^\n]*?)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text
        )
        if county_match:
            peak.county = county_match.group(2).strip()

    @staticmethod
    def _extract_ascent_counts(html: str, peak: Peak) -> None:
        """Extract total and viewable ascent counts from HTML."""
        ascent_count_match = re.search(
            r"Total ascents/attempts logged.*?<b>(\d+)</b>", html, re.DOTALL
        )
        if ascent_count_match:
            peak.ascent_count = int(ascent_count_match.group(1))
            logger.debug(f"Extracted ascent count: {peak.ascent_count}")

        viewable_count_match = re.search(r"\(Total:\s*(\d+)\)", html)
        if viewable_count_match:
            peak.viewable_ascent_count = int(viewable_count_match.group(1))

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

        result = PeakBaggerScraper._find_ascents_table(soup)
        if not result:
            logger.debug("No valid ascents table found")
            return ascents

        data_table, header_map, num_columns = result

        rows = data_table.find_all("tr")
        for row in rows[2:]:
            ascent = PeakBaggerScraper._parse_ascent_row(row, header_map, num_columns)
            if ascent:
                ascents.append(ascent)

        logger.debug(f"Successfully parsed {len(ascents)} ascents")
        return ascents

    @staticmethod
    def _find_ascents_table(soup: BeautifulSoup) -> tuple[Tag, dict[str, int], int] | None:
        """Find the ascents data table and build a header column map."""
        tables: list[Tag] = soup.find_all("table")  # type: ignore[assignment]
        logger.debug(f"Found {len(tables)} tables in HTML")

        for table in tables:
            rows: list[Tag] = table.find_all("tr")
            if len(rows) < 10:
                continue

            if len(rows) <= 1:
                continue

            header_row: Tag = rows[1]
            headers: list[Tag] = header_row.find_all(["th", "td"], recursive=False)  # type: ignore[assignment]

            if len(headers) < 3 or len(headers) > 20:
                continue

            header_texts: list[str] = [h.get_text(strip=True) for h in headers]

            if "Climber" not in header_texts:
                continue
            if not any("Ascent" in h and "Date" in h for h in header_texts):
                continue

            header_map: dict[str, int] = {text: idx for idx, text in enumerate(header_texts)}
            num_columns = len(headers)
            logger.debug(
                f"Found ascents data table with {num_columns} columns: {list(header_map.keys())}"
            )
            return table, header_map, num_columns

        return None

    @staticmethod
    def _parse_ascent_row(row: Tag, header_map: dict[str, int], num_columns: int) -> Ascent | None:
        """Parse a single ascent row from the ascents table."""
        cells: list[Tag] = row.find_all(["td", "th"], recursive=False)  # type: ignore[assignment]
        if len(cells) != num_columns:
            return None

        climber_idx = header_map.get("Climber", -1)
        date_idx = next((header_map[h] for h in header_map if "Ascent" in h and "Date" in h), -1)
        if climber_idx == -1 or date_idx == -1:
            return None

        climber = PeakBaggerScraper._extract_climber_from_cell(cells[climber_idx])
        if not climber:
            return None
        climber_name, climber_id = climber

        ascent_date = PeakBaggerScraper._extract_date_from_cell(cells[date_idx])
        if not ascent_date:
            return None
        ascent_id, date_text_value = ascent_date

        has_gpx = PeakBaggerScraper._extract_gpx_flag(cells, header_map.get("GPS", -1))
        has_trip_report, trip_report_words = PeakBaggerScraper._parse_tr_words(
            cells, header_map.get("TR-Words", -1)
        )

        route_idx = header_map.get("Route", -1)
        route: str | None = None
        if route_idx != -1:
            route = cells[route_idx].get_text(strip=True) or None

        return Ascent(
            ascent_id=ascent_id,
            climber_name=climber_name,
            climber_id=climber_id,
            date=date_text_value,
            has_gpx=has_gpx,
            has_trip_report=has_trip_report,
            trip_report_words=trip_report_words,
            route=route,
        )

    @staticmethod
    def _extract_climber_from_cell(cell: Tag) -> tuple[str, str | None] | None:
        """Extract climber name and ID from a table cell."""
        climber_link: Tag | None = cell.find("a", href=lambda x: x and "climber.aspx?cid=" in x)  # type: ignore[assignment]
        if not climber_link:
            return None
        name: str = climber_link.get_text(strip=True)
        href: str = str(climber_link["href"])
        cid_match = re.search(r"cid=(\d+)", href)
        cid: str | None = cid_match.group(1) if cid_match else None
        return name, cid

    @staticmethod
    def _extract_date_from_cell(cell: Tag) -> tuple[str, str | None] | None:
        """Extract ascent ID and date from a date table cell."""
        date_link: Tag | None = cell.find("a", href=lambda x: x and "ascent.aspx?aid=" in x)  # type: ignore[assignment]
        if not date_link:
            return None
        date_text_value = PeakBaggerScraper._parse_ascent_list_date(date_link.get_text(strip=True))
        href: str = str(date_link["href"])
        aid_match = re.search(r"aid=(\d+)", href)
        if not aid_match:
            return None
        return aid_match.group(1), date_text_value

    @staticmethod
    def _extract_gpx_flag(cells: list[Tag], gps_idx: int) -> bool:
        """Check if a GPX track indicator exists in the GPS column."""
        if gps_idx == -1:
            return False
        gps_img: Tag | None = cells[gps_idx].find("img", src=lambda x: x and "GPS.gif" in x)  # type: ignore[assignment]
        return gps_img is not None

    @staticmethod
    def _parse_ascent_list_date(date_text: str) -> str | None:
        """Parse date text from ascent list, handling Unknown and partial dates."""
        if date_text == "Unknown" or not date_text:
            return None
        date_pattern = re.compile(r"^\d{4}(-\d{2})?(-\d{2})?")
        match = date_pattern.match(date_text)
        return match.group(0) if match else None

    @staticmethod
    def _parse_tr_words(cells: list[Tag], tr_words_idx: int) -> tuple[bool, int | None]:
        """Parse trip report words column."""
        if tr_words_idx == -1:
            return False, None

        tr_text: str = cells[tr_words_idx].get_text(strip=True)
        has_trip_report = tr_text.startswith("TR-")
        trip_report_words: int | None = None
        if has_trip_report:
            tr_match = re.search(r"TR-(\d+)", tr_text)
            if tr_match:
                trip_report_words = int(tr_match.group(1))
        return has_trip_report, trip_report_words

    @staticmethod
    def parse_ascent_detail(html: str, ascent_id: str) -> Ascent | None:
        """Parse detailed ascent information from ascent.aspx page."""
        logger.debug(f"Parsing ascent detail for ascent ID {ascent_id}")
        soup: BeautifulSoup = BeautifulSoup(html, "lxml")

        try:
            peak_name, climber_name, climber_id = PeakBaggerScraper._parse_ascent_header(soup)
            if not climber_name:
                return None

            table: Tag | None = soup.find(
                "table", class_="gray", attrs={"width": "49%", "align": "left"}
            )
            if not table:
                return None

            ascent: Ascent = Ascent(
                ascent_id=ascent_id,
                climber_name=climber_name,
                climber_id=climber_id,
                peak_name=peak_name,
            )

            rows: list[Tag] = table.find_all("tr")  # type: ignore[assignment]
            for row in rows:
                cells: list[Tag] = row.find_all("td", recursive=False)
                if len(cells) < 1:
                    continue

                if len(cells) == 1 and cells[0].get("colspan") == "2":
                    PeakBaggerScraper._parse_trip_report(cells[0], ascent)
                    continue

                if len(cells) < 2:
                    continue

                label = PeakBaggerScraper._extract_label(cells[0])
                PeakBaggerScraper._parse_ascent_field(ascent, label, cells[1])

            # Infer has_trip_report from extracted text
            if ascent.trip_report_text:
                ascent.has_trip_report = True

            # Check for GPX track in the right-side table
            PeakBaggerScraper._detect_gpx_track(soup, ascent)

            logger.debug(f"Successfully parsed ascent detail for {ascent.climber_name}")
            return ascent

        except (AttributeError, ValueError, TypeError):
            logger.exception("Error parsing ascent detail")
            return None
        except Exception:
            logger.exception("Unexpected error parsing ascent detail")
            return None

    @staticmethod
    def _detect_gpx_track(soup: BeautifulSoup, ascent: Ascent) -> None:
        """Check for GPX track link in the right-side table."""
        right_table: Tag | None = soup.find(
            "table", class_="gray", attrs={"width": "50%", "align": "right"}
        )
        if right_table:
            gpx_link: Tag | None = right_table.find("a", href=lambda x: x and "GPXFile.aspx" in x)
            if gpx_link:
                ascent.has_gpx = True

    @staticmethod
    def _parse_ascent_header(
        soup: BeautifulSoup,
    ) -> tuple[str | None, str | None, str | None]:
        """Extract peak name, climber name, and climber ID from header."""
        h1: Tag | None = soup.find("h1")  # type: ignore[assignment]
        if not h1:
            logger.debug("No H1 tag found in ascent detail page")
            return None, None, None

        title_text: str = h1.get_text(strip=True)
        peak_name: str | None = None
        if " on " in title_text:
            parts = title_text.split(" on ", 1)
            peak_name = parts[0].replace("Ascent of ", "").strip()
        elif " in " in title_text:
            parts = title_text.split(" in ", 1)
            peak_name = parts[0].replace("Ascent of ", "").strip()

        h2: Tag | None = soup.find("h2")  # type: ignore[assignment]
        climber_name: str | None = None
        climber_id: str | None = None
        if h2:
            climber_link: Tag | None = h2.find("a", href=lambda x: x and "climber.aspx?cid=" in x)  # type: ignore[assignment]
            if climber_link:
                climber_name = climber_link.get_text(strip=True)
                climber_href: str = str(climber_link["href"])
                cid_match = re.search(r"cid=(\d+)", climber_href)
                if cid_match:
                    climber_id = cid_match.group(1)

        return peak_name, climber_name, climber_id

    @staticmethod
    def _extract_label(label_cell: Tag) -> str:
        """Extract label text from a table cell, handling <b> tags."""
        label_b: Tag | None = label_cell.find("b")  # type: ignore[assignment]
        if label_b:
            return label_b.get_text(strip=True).rstrip(":")
        return label_cell.get_text(strip=True).rstrip(":")

    @staticmethod
    def _parse_trip_report(cell: Tag, ascent: Ascent) -> None:
        """Parse trip report section from a colspan=2 cell."""
        h2_tr: Tag | None = None
        for h2 in cell.find_all("h2"):  # type: ignore[assignment]
            if re.search("Trip Report", h2.get_text(strip=True)):
                h2_tr = h2
                break
        if not h2_tr:
            return

        report_parts: list[str] = []
        for elem in cell.descendants:
            if isinstance(elem, str):
                text = elem.strip()
                if text and text != "URL Link:":
                    report_parts.append(text)

        report_text = " ".join(report_parts)
        report_text = re.sub(r"^Ascent Trip Report\s*", "", report_text)
        report_text = re.sub(r"URL Link:\s*peakbagger\.com\s*", "", report_text)
        report_text = re.sub(r"^peakbagger\.com\s*", "", report_text)

        if report_text:
            ascent.trip_report_text = report_text.strip()

        url_link: Tag | None = cell.find("a", href=re.compile(r"^https?://"))  # type: ignore[assignment]
        if url_link and url_link.get("href"):
            href = str(url_link["href"])
            if "peakbagger.com" not in href:
                ascent.trip_report_url = href

    @staticmethod
    def _parse_ascent_date(value_cell: Tag) -> str | None:
        """Parse date from ascent detail value cell."""
        date_text = value_cell.get_text(strip=True)
        if not date_text or date_text == "Unknown":
            return None

        month_day_year = re.search(r"([A-Z][a-z]+)\s+(\d{1,2}),\s+(\d{4})", date_text)
        if month_day_year:
            from datetime import datetime

            month_name = month_day_year.group(1)
            day = month_day_year.group(2)
            year = month_day_year.group(3)
            try:
                parsed_date = datetime.strptime(f"{month_name} {day} {year}", "%B %d %Y")
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                pass

        iso_match = re.search(r"(\d{4}(?:-\d{2})?(?:-\d{2})?)", date_text)
        return iso_match.group(1) if iso_match else None

    @staticmethod
    def _parse_ascent_field(ascent: Ascent, label: str, value_cell: Tag) -> None:
        """Dispatch ascent detail field parsing based on label."""
        # Exact-match fields first
        if label == "Date":
            ascent.date = PeakBaggerScraper._parse_ascent_date(value_cell)
        elif label == "Ascent Type":
            ascent.ascent_type = value_cell.get_text(strip=True)
        elif label == "Peak":
            PeakBaggerScraper._parse_ascent_peak_field(ascent, value_cell)
        else:
            # Substring-match fields (order matters: "Gain" before "Elevation")
            PeakBaggerScraper._parse_ascent_field_by_keyword(ascent, label, value_cell)

    @staticmethod
    def _parse_ascent_field_by_keyword(ascent: Ascent, label: str, value_cell: Tag) -> None:
        """Parse ascent fields matched by keyword in the label."""
        if "Location" in label:
            ascent.location = value_cell.get_text(strip=True)
        elif "Gain" in label:
            PeakBaggerScraper._parse_ascent_gain(ascent, value_cell)
        elif "Elevation" in label:
            PeakBaggerScraper._parse_ascent_elevation(ascent, value_cell)
        elif "Route" in label:
            route_text = value_cell.get_text(strip=True)
            if route_text:
                ascent.route = route_text
        elif "Distance" in label:
            PeakBaggerScraper._parse_ascent_distance(ascent, value_cell)
        elif "Duration" in label or "Time" in label:
            PeakBaggerScraper._parse_ascent_duration(ascent, value_cell)

    @staticmethod
    def _parse_ascent_gain(ascent: Ascent, value_cell: Tag) -> None:
        """Parse elevation gain from ascent detail."""
        gain_text = value_cell.get_text(strip=True)
        gain_match = re.search(r"([\d,]+)\s*ft", gain_text)
        if gain_match:
            ascent.elevation_gain_ft = int(gain_match.group(1).replace(",", ""))

    @staticmethod
    def _parse_ascent_distance(ascent: Ascent, value_cell: Tag) -> None:
        """Parse distance from ascent detail."""
        dist_text = value_cell.get_text(strip=True)
        dist_match = re.search(r"([\d.]+)\s*mi", dist_text)
        if dist_match:
            ascent.distance_mi = float(dist_match.group(1))

    @staticmethod
    def _parse_ascent_peak_field(ascent: Ascent, value_cell: Tag) -> None:
        """Parse peak link and ID from ascent detail."""
        peak_link: Tag | None = value_cell.find("a", href=lambda x: x and "peak.aspx?pid=" in x)  # type: ignore[assignment]
        if peak_link:
            ascent.peak_name = peak_link.get_text(strip=True)
            peak_href: str = str(peak_link["href"])
            pid_match = re.search(r"pid=(-?\d+)", peak_href)
            if pid_match:
                ascent.peak_id = pid_match.group(1)

    @staticmethod
    def _parse_ascent_elevation(ascent: Ascent, value_cell: Tag) -> None:
        """Parse elevation ft/m from ascent detail."""
        elev_text = value_cell.get_text(strip=True)
        elev_match = re.search(r"([\d,]+)\s*ft\s*/\s*([\d,]+)\s*m", elev_text)
        if elev_match:
            ascent.elevation_ft = int(elev_match.group(1).replace(",", ""))
            ascent.elevation_m = int(elev_match.group(2).replace(",", ""))

    @staticmethod
    def _parse_ascent_duration(ascent: Ascent, value_cell: Tag) -> None:
        """Parse duration from ascent detail."""
        dur_text = value_cell.get_text(strip=True)
        hour_match = re.search(r"([\d.]+)\s*(?:hours?|hrs?)", dur_text, re.IGNORECASE)
        if hour_match:
            ascent.duration_hours = float(hour_match.group(1))
        else:
            time_match = re.search(r"(\d+):(\d+)", dur_text)
            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                ascent.duration_hours = hours + (minutes / 60.0)
