"""Statistics calculation for peak ascents."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from peakbagger.models import Ascent, AscentStatistics


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
    def calculate_statistics(
        ascents: list["Ascent"],
        reference_date: datetime | None = None,
        seasonal_window_days: int = 14,
    ) -> "AscentStatistics":
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

        # Overall statistics
        total_ascents = len(ascents)
        ascents_with_gpx = sum(1 for a in ascents if a.has_gpx)
        ascents_with_trip_reports = sum(1 for a in ascents if a.has_trip_report)

        # Parse dates for temporal analysis
        dated_ascents = []
        for ascent in ascents:
            if ascent.date:
                try:
                    # Handle different date formats: YYYY-MM-DD, YYYY-MM, YYYY
                    date_parts = ascent.date.split("-")
                    if len(date_parts) == 3:
                        date = datetime.strptime(ascent.date, "%Y-%m-%d")
                    elif len(date_parts) == 2:
                        date = datetime.strptime(ascent.date, "%Y-%m")
                    elif len(date_parts) == 1:
                        date = datetime.strptime(ascent.date, "%Y")
                    else:
                        continue
                    dated_ascents.append((ascent, date))
                except ValueError:
                    continue

        # Temporal breakdown (from reference date)
        last_3_months = sum(
            1
            for _, date in dated_ascents
            if reference_date - timedelta(days=90) <= date <= reference_date
        )
        last_year = sum(
            1
            for _, date in dated_ascents
            if reference_date - timedelta(days=365) <= date <= reference_date
        )
        last_5_years = sum(
            1
            for _, date in dated_ascents
            if reference_date - timedelta(days=365 * 5) <= date <= reference_date
        )

        # Monthly distribution (all time)
        monthly_distribution = dict.fromkeys(AscentAnalyzer.MONTH_NAMES, 0)
        for _, date in dated_ascents:
            month_name = AscentAnalyzer.MONTH_NAMES[date.month - 1]
            monthly_distribution[month_name] += 1

        # Seasonal pattern (ascents within window of reference date across all years)
        seasonal_pattern = dict.fromkeys(AscentAnalyzer.MONTH_NAMES, 0)

        # Calculate seasonal window based on day of year
        for _, date in dated_ascents:
            # Calculate days difference ignoring year
            ref_day_of_year = reference_date.timetuple().tm_yday
            ascent_day_of_year = date.timetuple().tm_yday

            # Handle year wrap-around
            diff = ascent_day_of_year - ref_day_of_year
            if diff > 180:
                diff -= 365
            elif diff < -180:
                diff += 365

            # Check if within seasonal window
            if abs(diff) <= seasonal_window_days:
                month_name = AscentAnalyzer.MONTH_NAMES[date.month - 1]
                seasonal_pattern[month_name] += 1

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
        ascents: list["Ascent"],
        after: datetime | None = None,
        before: datetime | None = None,
    ) -> list["Ascent"]:
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

            try:
                # Parse date
                date_parts = ascent.date.split("-")
                if len(date_parts) == 3:
                    date = datetime.strptime(ascent.date, "%Y-%m-%d")
                elif len(date_parts) == 2:
                    date = datetime.strptime(ascent.date, "%Y-%m")
                elif len(date_parts) == 1:
                    date = datetime.strptime(ascent.date, "%Y")
                else:
                    continue

                # Apply filters
                if after and date < after:
                    continue
                if before and date > before:
                    continue

                filtered.append(ascent)
            except ValueError:
                continue

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
