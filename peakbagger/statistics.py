"""Statistics calculation for peak ascents."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from peakbagger.models import Ascent, AscentStatistics


def _parse_ascent_date(date_str: str) -> datetime | None:
    """Parse an ascent date string in YYYY-MM-DD, YYYY-MM, or YYYY format.

    Args:
        date_str: Date string to parse.

    Returns:
        Parsed datetime, or None if the format is unrecognized or invalid.
    """
    date_parts = date_str.split("-")
    try:
        if len(date_parts) == 3:
            return datetime.strptime(date_str, "%Y-%m-%d")
        if len(date_parts) == 2:
            return datetime.strptime(date_str, "%Y-%m")
        if len(date_parts) == 1:
            return datetime.strptime(date_str, "%Y")
    except ValueError:
        pass
    return None


class AscentAnalyzer:
    """Analyzer for calculating statistics from ascent data."""

    MONTH_NAMES: ClassVar[list[str]] = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    @staticmethod
    def _parse_dated_ascents(ascents: list[Ascent]) -> list[tuple[Ascent, datetime]]:
        """Parse ascent dates, returning only those with valid dates."""
        dated: list[tuple[Ascent, datetime]] = []
        for ascent in ascents:
            if ascent.date:
                parsed = _parse_ascent_date(ascent.date)
                if parsed is not None:
                    dated.append((ascent, parsed))
        return dated

    @staticmethod
    def _count_temporal(
        dated_ascents: list[tuple[Ascent, datetime]],
        reference_date: datetime,
    ) -> tuple[int, int, int]:
        """Count ascents in the last 3 months, 1 year, and 5 years."""
        last_3m = 0
        last_1y = 0
        last_5y = 0
        cutoff_3m = reference_date - timedelta(days=90)
        cutoff_1y = reference_date - timedelta(days=365)
        cutoff_5y = reference_date - timedelta(days=365 * 5)
        for _, date in dated_ascents:
            if cutoff_3m <= date <= reference_date:
                last_3m += 1
            if cutoff_1y <= date <= reference_date:
                last_1y += 1
            if cutoff_5y <= date <= reference_date:
                last_5y += 1
        return last_3m, last_1y, last_5y

    @staticmethod
    def _build_monthly_distribution(
        dated_ascents: list[tuple[Ascent, datetime]],
    ) -> dict[str, int]:
        """Build month-name to count mapping across all years."""
        distribution = dict.fromkeys(AscentAnalyzer.MONTH_NAMES, 0)
        for _, date in dated_ascents:
            distribution[AscentAnalyzer.MONTH_NAMES[date.month - 1]] += 1
        return distribution

    @staticmethod
    def _build_seasonal_pattern(
        dated_ascents: list[tuple[Ascent, datetime]],
        reference_date: datetime,
        window_days: int,
    ) -> dict[str, int]:
        """Build seasonal pattern counting ascents within a day-of-year window."""
        pattern = dict.fromkeys(AscentAnalyzer.MONTH_NAMES, 0)
        ref_doy = reference_date.timetuple().tm_yday
        for _, date in dated_ascents:
            diff = date.timetuple().tm_yday - ref_doy
            if diff > 180:
                diff -= 365
            elif diff < -180:
                diff += 365
            if abs(diff) <= window_days:
                pattern[AscentAnalyzer.MONTH_NAMES[date.month - 1]] += 1
        return pattern

    @staticmethod
    def calculate_statistics(
        ascents: list[Ascent],
        reference_date: datetime | None = None,
        seasonal_window_days: int = 14,
    ) -> AscentStatistics:
        """
        Calculate comprehensive statistics from ascent data.

        Args:
            ascents: List of Ascent objects
            reference_date: Reference date for seasonal analysis (default: today)
            seasonal_window_days: Days before/after reference date for seasonal window

        Returns:
            AscentStatistics object with calculated stats
        """
        from peakbagger.models import AscentStatistics

        if reference_date is None:
            reference_date = datetime.now()

        total_ascents = len(ascents)
        ascents_with_gpx = sum(1 for a in ascents if a.has_gpx)
        ascents_with_trip_reports = sum(1 for a in ascents if a.has_trip_report)

        dated_ascents = AscentAnalyzer._parse_dated_ascents(ascents)
        last_3_months, last_year, last_5_years = AscentAnalyzer._count_temporal(
            dated_ascents, reference_date
        )
        monthly_distribution = AscentAnalyzer._build_monthly_distribution(dated_ascents)
        seasonal_pattern = AscentAnalyzer._build_seasonal_pattern(
            dated_ascents, reference_date, seasonal_window_days
        )

        return AscentStatistics(
            total_ascents=total_ascents,
            ascents_with_gpx=ascents_with_gpx,
            ascents_with_trip_reports=ascents_with_trip_reports,
            last_3_months=last_3_months,
            last_year=last_year,
            last_5_years=last_5_years,
            monthly_distribution=monthly_distribution,
            seasonal_pattern=seasonal_pattern,
        )

    @staticmethod
    def filter_by_date_range(
        ascents: list[Ascent],
        after: datetime | None = None,
        before: datetime | None = None,
    ) -> list[Ascent]:
        """
        Filter ascents by date range.

        Args:
            ascents: List of Ascent objects
            after: Include ascents on or after this date
            before: Include ascents on or before this date

        Returns:
            Filtered list of ascents
        """
        filtered = []
        for ascent in ascents:
            if not ascent.date:
                continue

            date = _parse_ascent_date(ascent.date)
            if date is None:
                continue

            if after and date < after:
                continue
            if before and date > before:
                continue

            filtered.append(ascent)

        return filtered

    @staticmethod
    def parse_within_period(period: str) -> timedelta:
        """
        Parse a human-readable period into timedelta.

        Supported formats:
        - "3m" - 3 months (90 days)
        - "1y" - 1 year (365 days)
        - "10d" - 10 days
        - "5y" - 5 years

        Args:
            period: Period string (e.g., "3m", "1y", "10d")

        Returns:
            timedelta representing the period

        Raises:
            ValueError: If period format is invalid
        """
        period = period.strip().lower()

        if not period:
            raise ValueError("Period cannot be empty")

        # Extract number and unit
        import re

        match = re.match(r"^(\d+)([dmy])$", period)
        if not match:
            raise ValueError(
                f"Invalid period format: '{period}'. Expected format like '3m', '1y', '10d', '5y'"
            )

        value = int(match.group(1))
        unit = match.group(2)

        if unit == "d":
            return timedelta(days=value)
        elif unit == "m":
            return timedelta(days=value * 30)  # Approximate month as 30 days
        elif unit == "y":
            return timedelta(days=value * 365)
        else:
            raise ValueError(f"Unknown unit: {unit}")
