"""HTML parsing and data extraction for PeakBagger.com."""

import re

from bs4 import BeautifulSoup

from peakbagger.models import Peak, SearchResult


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
        soup = BeautifulSoup(html, "lxml")
        results = []

        # Find all links to peak pages
        peak_links = soup.find_all("a", href=lambda x: x and "peak.aspx?pid=" in x)

        for link in peak_links:
            href = link["href"]
            name = link.get_text(strip=True)

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
        soup = BeautifulSoup(html, "lxml")

        try:
            # Extract peak name and state from H1
            h1 = soup.find("h1")
            if not h1:
                return None

            title_text = h1.get_text(strip=True)
            # Format is usually "Peak Name, State/Province"
            name_parts = title_text.rsplit(", ", 1)
            name = name_parts[0]
            state = name_parts[1] if len(name_parts) > 1 else None

            # Initialize peak object
            peak = Peak(pid=pid, name=name, state=state)

            # Extract elevation from H2
            h2 = soup.find("h2")
            if h2:
                elevation_text = h2.get_text(strip=True)
                # Format: "Elevation: 10,984 feet, 3348 meters"
                elev_match = re.search(r"([\d,]+)\s*feet,\s*([\d,]+)\s*meters", elevation_text)
                if elev_match:
                    peak.elevation_ft = int(elev_match.group(1).replace(",", ""))
                    peak.elevation_m = int(elev_match.group(2).replace(",", ""))

            # Extract prominence (appears in table near H2)
            text = soup.get_text()
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

            return peak

        except Exception as e:
            # Log error but don't crash
            print(f"Error parsing peak detail: {e}")
            return None
