"""Data models for PeakBagger entities."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Peak:
    """Represents a mountain peak with its metadata."""

    pid: str  # Peak ID
    name: str  # Peak name (e.g., "Mount Rainier")
    state: str | None = None  # State/Province (e.g., "Washington")
    elevation_ft: int | None = None  # Elevation in feet
    elevation_m: int | None = None  # Elevation in meters
    prominence_ft: int | None = None  # Prominence in feet
    prominence_m: int | None = None  # Prominence in meters
    latitude: float | None = None  # Latitude in decimal degrees
    longitude: float | None = None  # Longitude in decimal degrees
    isolation_mi: float | None = None  # True isolation in miles
    isolation_km: float | None = None  # True isolation in kilometers
    county: str | None = None  # County/region
    country: str | None = None  # Country

    def to_dict(self) -> dict[str, Any]:
        """Convert peak to dictionary for JSON serialization."""
        return {
            "pid": self.pid,
            "name": self.name,
            "state": self.state,
            "elevation": {
                "feet": self.elevation_ft,
                "meters": self.elevation_m,
            },
            "prominence": {
                "feet": self.prominence_ft,
                "meters": self.prominence_m,
            },
            "location": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "county": self.county,
                "country": self.country,
            },
            "isolation": {
                "miles": self.isolation_mi,
                "kilometers": self.isolation_km,
            },
            "url": f"https://www.peakbagger.com/peak.aspx?pid={self.pid}",
        }


@dataclass
class SearchResult:
    """Represents a brief search result for a peak."""

    pid: str  # Peak ID
    name: str  # Peak name
    url: str  # Relative URL to peak page

    def to_dict(self) -> dict[str, str]:
        """Convert search result to dictionary."""
        return {
            "pid": self.pid,
            "name": self.name,
            "url": f"https://www.peakbagger.com/{self.url}",
        }
