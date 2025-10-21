"""Data models for PeakBagger entities."""

from typing import Any

from pydantic import BaseModel, Field


class Peak(BaseModel):
    """Represents a mountain peak with its metadata."""

    pid: str = Field(description="Peak ID")
    name: str = Field(description="Peak name (e.g., 'Mount Rainier')")
    state: str | None = Field(None, description="State/Province (e.g., 'Washington')")
    elevation_ft: int | None = Field(None, description="Elevation in feet")
    elevation_m: int | None = Field(None, description="Elevation in meters")
    prominence_ft: int | None = Field(None, description="Prominence in feet")
    prominence_m: int | None = Field(None, description="Prominence in meters")
    latitude: float | None = Field(None, description="Latitude in decimal degrees")
    longitude: float | None = Field(None, description="Longitude in decimal degrees")
    isolation_mi: float | None = Field(None, description="True isolation in miles")
    isolation_km: float | None = Field(None, description="True isolation in kilometers")
    county: str | None = Field(None, description="County/region")
    country: str | None = Field(None, description="Country")
    peak_lists: list[dict[str, Any]] = Field(
        default_factory=list, description="Peak lists with ranks"
    )
    routes: list[dict[str, Any]] = Field(default_factory=list, description="Route information")
    ascent_count: int | None = Field(None, description="Total number of ascents logged")
    viewable_ascent_count: int | None = Field(None, description="Number of viewable ascents")

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
            "peak_lists": self.peak_lists,
            "routes": self.routes,
            "ascent_count": self.ascent_count,
            "viewable_ascent_count": self.viewable_ascent_count,
        }


class SearchResult(BaseModel):
    """Represents a brief search result for a peak."""

    pid: str = Field(description="Peak ID")
    name: str = Field(description="Peak name")
    url: str = Field(description="Relative URL to peak page")
    location: str | None = Field(None, description="Location (e.g., 'USA-WA')")
    range: str | None = Field(None, description="Mountain range (e.g., 'Cascade Range')")
    elevation_ft: int | None = Field(None, description="Elevation in feet")
    elevation_m: int | None = Field(None, description="Elevation in meters")

    def to_dict(self) -> dict[str, Any]:
        """Convert search result to dictionary."""
        return {
            "pid": self.pid,
            "name": self.name,
            "url": f"https://www.peakbagger.com/{self.url}",
            "location": self.location,
            "range": self.range,
            "elevation": {
                "feet": self.elevation_ft,
                "meters": self.elevation_m,
            },
        }


class Ascent(BaseModel):
    """Represents a single ascent of a peak."""

    ascent_id: str = Field(description="Ascent ID (from aid parameter)")
    climber_name: str = Field(description="Name of climber")
    climber_id: str | None = Field(None, description="Climber ID (from cid parameter)")
    date: str | None = Field(None, description="Ascent date (YYYY-MM-DD, YYYY-MM, or YYYY format)")
    has_gpx: bool = Field(False, description="Whether ascent has GPS track")
    has_trip_report: bool = Field(False, description="Whether ascent has trip report")
    trip_report_words: int | None = Field(None, description="Number of words in trip report")
    route: str | None = Field(None, description="Route name")

    # New fields for detailed ascent reports
    ascent_type: str | None = Field(None, description="Ascent type (e.g., 'Successful Summit Attained')")
    peak_name: str | None = Field(None, description="Peak name")
    peak_id: str | None = Field(None, description="Peak ID")
    location: str | None = Field(None, description="Location (e.g., 'USA-Washington')")
    elevation_ft: int | None = Field(None, description="Peak elevation in feet")
    elevation_m: int | None = Field(None, description="Peak elevation in meters")

    # GPX-derived metrics (when available)
    elevation_gain_ft: int | None = Field(None, description="Elevation gain from GPX in feet")
    distance_mi: float | None = Field(None, description="Distance from GPX in miles")
    duration_hours: float | None = Field(None, description="Duration from GPX in hours")

    # Trip report content
    trip_report_text: str | None = Field(None, description="Full text of trip report")
    trip_report_url: str | None = Field(None, description="External URL if linked in trip report")

    def to_dict(self) -> dict[str, Any]:
        """Convert ascent to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "ascent_id": self.ascent_id,
            "climber": {
                "name": self.climber_name,
                "id": self.climber_id,
            },
            "date": self.date,
            "has_gpx": self.has_gpx,
            "route": self.route,
            "url": f"https://www.peakbagger.com/climber/ascent.aspx?aid={self.ascent_id}",
        }

        # Add trip report info
        result["trip_report"] = {
            "has_report": self.has_trip_report,
            "word_count": self.trip_report_words,
        }

        # Add detailed fields if present
        if self.ascent_type:
            result["ascent_type"] = self.ascent_type

        if self.peak_name or self.peak_id:
            result["peak"] = {}
            if self.peak_name:
                result["peak"]["name"] = self.peak_name
            if self.peak_id:
                result["peak"]["id"] = self.peak_id
            if self.location:
                result["peak"]["location"] = self.location
            if self.elevation_ft is not None:
                result["peak"]["elevation_ft"] = self.elevation_ft
            if self.elevation_m is not None:
                result["peak"]["elevation_m"] = self.elevation_m

        # Add GPX metrics if any are present
        if self.elevation_gain_ft or self.distance_mi or self.duration_hours:
            result["gpx_metrics"] = {}
            if self.elevation_gain_ft is not None:
                result["gpx_metrics"]["elevation_gain_ft"] = self.elevation_gain_ft
            if self.distance_mi is not None:
                result["gpx_metrics"]["distance_mi"] = self.distance_mi
            if self.duration_hours is not None:
                result["gpx_metrics"]["duration_hours"] = self.duration_hours

        # Add full trip report text if present
        if self.trip_report_text:
            result["trip_report"]["text"] = self.trip_report_text
        if self.trip_report_url:
            result["trip_report"]["external_url"] = self.trip_report_url

        return result


class AscentStatistics(BaseModel):
    """Statistics about ascents of a peak."""

    total_ascents: int = Field(description="Total number of ascents")
    ascents_with_gpx: int = Field(description="Number of ascents with GPX tracks")
    ascents_with_trip_reports: int = Field(description="Number of ascents with trip reports")
    last_3_months: int = Field(description="Ascents in the last 3 months")
    last_year: int = Field(description="Ascents in the last year")
    last_5_years: int = Field(description="Ascents in the last 5 years")
    monthly_distribution: dict[str, int] = Field(description="Month name -> count")
    seasonal_pattern: dict[str, int] | None = Field(
        None, description="Month -> count in seasonal window"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert statistics to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "total_ascents": self.total_ascents,
            "with_gpx_tracks": self.ascents_with_gpx,
            "with_trip_reports": self.ascents_with_trip_reports,
            "temporal_breakdown": {
                "last_3_months": self.last_3_months,
                "last_year": self.last_year,
                "last_5_years": self.last_5_years,
            },
            "monthly_distribution": self.monthly_distribution,
        }
        if self.seasonal_pattern is not None:
            result["seasonal_pattern"] = self.seasonal_pattern
        return result
