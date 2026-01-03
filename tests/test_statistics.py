"""
Comprehensive tests for statistics module.

Tests cover:
- Statistics calculation with various date formats
- Date range filtering
- Period parsing
- Edge cases and error handling
"""

from datetime import datetime, timedelta

import pytest

from peakbagger.models import Ascent
from peakbagger.statistics import AscentAnalyzer


def create_ascent(
    ascent_id: str = "1",
    climber_name: str = "Test Climber",
    peak_name: str = "Test Peak",
    date: str | None = None,
    has_gpx: bool = False,
    has_trip_report: bool = False,
) -> Ascent:
    """Helper function to create an Ascent with required fields."""
    return Ascent(
        ascent_id=ascent_id,
        climber_name=climber_name,
        peak_name=peak_name,
        date=date,
        has_gpx=has_gpx,
        has_trip_report=has_trip_report,
    )


class TestAscentAnalyzerCalculateStatistics:
    """Tests for AscentAnalyzer.calculate_statistics method."""

    @pytest.fixture
    def sample_ascents(self) -> list[Ascent]:
        """Create sample ascents with various dates and attributes."""
        return [
            Ascent(
                ascent_id="1",
                climber_name="John Doe",
                peak_name="Mount Rainier",
                date="2024-06-15",
                has_gpx=True,
                has_trip_report=True,
            ),
            Ascent(
                ascent_id="2",
                climber_name="Jane Smith",
                peak_name="Mount Adams",
                date="2024-06-20",
                has_gpx=False,
                has_trip_report=True,
            ),
            Ascent(
                ascent_id="3",
                climber_name="Bob Johnson",
                peak_name="Mount Hood",
                date="2024-03-10",
                has_gpx=True,
                has_trip_report=False,
            ),
            Ascent(
                ascent_id="4",
                climber_name="Alice Williams",
                peak_name="Denali",
                date="2023-07-05",
                has_gpx=True,
                has_trip_report=True,
            ),
            Ascent(
                ascent_id="5",
                climber_name="Charlie Brown",
                peak_name="Mount Si",
                date="2020-05-15",
                has_gpx=False,
                has_trip_report=False,
            ),
            # Date with month precision only
            Ascent(
                ascent_id="6",
                climber_name="David Clark",
                peak_name="Old Peak",
                date="2024-01",
                has_gpx=False,
                has_trip_report=False,
            ),
            # Date with year precision only
            Ascent(
                ascent_id="7",
                climber_name="Eve Davis",
                peak_name="Ancient Peak",
                date="2019",
                has_gpx=False,
                has_trip_report=False,
            ),
            # Ascent without date
            Ascent(
                ascent_id="8",
                climber_name="Frank Miller",
                peak_name="Unknown Date Peak",
                date=None,
                has_gpx=False,
                has_trip_report=False,
            ),
        ]

    def test_calculate_statistics_with_reference_date(self, sample_ascents):
        """Test statistics calculation with specific reference date."""
        reference_date = datetime(2024, 7, 1)
        stats = AscentAnalyzer.calculate_statistics(sample_ascents, reference_date=reference_date)

        assert stats.total_ascents == 8
        assert stats.ascents_with_gpx == 3
        assert stats.ascents_with_trip_reports == 3

        # Temporal statistics (from July 1, 2024)
        assert stats.last_3_months >= 2  # June 2024 ascents
        assert stats.last_year >= 3  # 2024 ascents
        assert stats.last_5_years >= 4  # Recent ascents

        # Monthly distribution should have all months initialized
        assert len(stats.monthly_distribution) == 12
        assert all(month in stats.monthly_distribution for month in AscentAnalyzer.MONTH_NAMES)

    def test_calculate_statistics_default_reference_date(self, sample_ascents):
        """Test statistics calculation with default reference date (today)."""
        stats = AscentAnalyzer.calculate_statistics(sample_ascents)

        assert stats.total_ascents == 8
        assert stats.ascents_with_gpx == 3
        assert stats.ascents_with_trip_reports == 3
        assert isinstance(stats.monthly_distribution, dict)
        assert isinstance(stats.seasonal_pattern, dict)

    def test_calculate_statistics_empty_list(self):
        """Test statistics calculation with empty ascent list."""
        stats = AscentAnalyzer.calculate_statistics([])

        assert stats.total_ascents == 0
        assert stats.ascents_with_gpx == 0
        assert stats.ascents_with_trip_reports == 0
        assert stats.last_3_months == 0
        assert stats.last_year == 0
        assert stats.last_5_years == 0
        assert all(count == 0 for count in stats.monthly_distribution.values())

    def test_calculate_statistics_seasonal_window(self, sample_ascents):
        """Test seasonal pattern calculation with different window sizes."""
        reference_date = datetime(2024, 6, 15)

        # Narrow window (7 days)
        stats_narrow = AscentAnalyzer.calculate_statistics(
            sample_ascents, reference_date=reference_date, seasonal_window_days=7
        )

        # Wide window (30 days)
        stats_wide = AscentAnalyzer.calculate_statistics(
            sample_ascents, reference_date=reference_date, seasonal_window_days=30
        )

        # Wide window should capture more ascents in seasonal pattern
        assert stats_wide.seasonal_pattern is not None
        assert stats_narrow.seasonal_pattern is not None
        assert sum(stats_wide.seasonal_pattern.values()) >= sum(
            stats_narrow.seasonal_pattern.values()
        )

    def test_calculate_statistics_year_wraparound(self):
        """Test seasonal pattern calculation handles year wraparound correctly."""
        ascents = [
            create_ascent(ascent_id="1", peak_name="Peak A", date="2023-12-25"),
            create_ascent(ascent_id="2", peak_name="Peak B", date="2024-01-05"),
        ]

        reference_date = datetime(2024, 1, 1)
        stats = AscentAnalyzer.calculate_statistics(
            ascents, reference_date=reference_date, seasonal_window_days=14
        )

        # Both ascents should be within seasonal window due to wraparound handling
        assert stats.seasonal_pattern is not None
        assert sum(stats.seasonal_pattern.values()) >= 1

    def test_calculate_statistics_invalid_date_formats(self):
        """Test that invalid date formats are gracefully skipped."""
        ascents = [
            create_ascent(ascent_id="1", peak_name="Valid Date", date="2024-06-15", has_gpx=True),
            create_ascent(ascent_id="2", peak_name="Invalid Date 1", date="not-a-date"),
            create_ascent(
                ascent_id="3", peak_name="Invalid Date 2", date="2024-13-45"
            ),  # Invalid month/day
            create_ascent(
                ascent_id="4", peak_name="Invalid Date 3", date="2024-06-15-extra"
            ),  # Too many parts
        ]

        stats = AscentAnalyzer.calculate_statistics(ascents)

        # Should count all ascents but only process valid dates for temporal analysis
        assert stats.total_ascents == 4
        # Only 1 valid date should be in monthly distribution
        assert sum(stats.monthly_distribution.values()) == 1

    def test_calculate_statistics_monthly_distribution(self):
        """Test monthly distribution calculation."""
        ascents = [
            create_ascent(ascent_id=str(i), peak_name=f"Peak {i}", date=f"2024-{i:02d}-15")
            for i in range(1, 13)  # One ascent per month
        ]

        stats = AscentAnalyzer.calculate_statistics(ascents)

        # Each month should have exactly 1 ascent
        assert all(count == 1 for count in stats.monthly_distribution.values())
        assert sum(stats.monthly_distribution.values()) == 12


class TestAscentAnalyzerFilterByDateRange:
    """Tests for AscentAnalyzer.filter_by_date_range method."""

    @pytest.fixture
    def dated_ascents(self) -> list[Ascent]:
        """Create ascents spanning multiple years."""
        return [
            create_ascent(ascent_id="1", peak_name="Peak 2020", date="2020-05-15"),
            create_ascent(ascent_id="2", peak_name="Peak 2021", date="2021-08-20"),
            create_ascent(ascent_id="3", peak_name="Peak 2022", date="2022-11-10"),
            create_ascent(ascent_id="4", peak_name="Peak 2023", date="2023-03-05"),
            create_ascent(ascent_id="5", peak_name="Peak 2024", date="2024-06-15"),
        ]

    def test_filter_by_date_range_after_only(self, dated_ascents):
        """Test filtering with only 'after' parameter."""
        after_date = datetime(2022, 1, 1)
        filtered = AscentAnalyzer.filter_by_date_range(dated_ascents, after=after_date)

        assert len(filtered) == 3  # 2022, 2023, 2024
        assert all(a.date and a.date >= "2022-01-01" for a in filtered)  # type: ignore[operator]

    def test_filter_by_date_range_before_only(self, dated_ascents):
        """Test filtering with only 'before' parameter."""
        before_date = datetime(2022, 1, 1)
        filtered = AscentAnalyzer.filter_by_date_range(dated_ascents, before=before_date)

        assert len(filtered) == 2  # 2020, 2021
        assert all(a.date and a.date <= "2022-01-01" for a in filtered)  # type: ignore[operator]

    def test_filter_by_date_range_both_bounds(self, dated_ascents):
        """Test filtering with both 'after' and 'before' parameters."""
        after_date = datetime(2021, 1, 1)
        before_date = datetime(2023, 12, 31)
        filtered = AscentAnalyzer.filter_by_date_range(
            dated_ascents, after=after_date, before=before_date
        )

        assert len(filtered) == 3  # 2021, 2022, 2023
        assert all(a.date and a.date.startswith(("2021", "2022", "2023")) for a in filtered)

    def test_filter_by_date_range_no_filters(self, dated_ascents):
        """Test filtering with no date filters returns all dated ascents."""
        filtered = AscentAnalyzer.filter_by_date_range(dated_ascents)

        assert len(filtered) == 5  # All ascents

    def test_filter_by_date_range_excludes_no_date(self):
        """Test that ascents without dates are excluded."""
        ascents = [
            create_ascent(ascent_id="1", peak_name="Dated Peak", date="2024-06-15"),
            create_ascent(ascent_id="2", peak_name="Undated Peak", date=None),
        ]

        filtered = AscentAnalyzer.filter_by_date_range(ascents)

        assert len(filtered) == 1
        assert filtered[0].peak_name == "Dated Peak"

    def test_filter_by_date_range_handles_month_precision(self):
        """Test filtering with month-precision dates."""
        ascents = [
            create_ascent(ascent_id="1", peak_name="Full Date", date="2024-06-15"),
            create_ascent(ascent_id="2", peak_name="Month Only", date="2024-03"),
            create_ascent(ascent_id="3", peak_name="Year Only", date="2023"),
        ]

        after_date = datetime(2024, 1, 1)
        filtered = AscentAnalyzer.filter_by_date_range(ascents, after=after_date)

        assert len(filtered) == 2  # Full date and month-only from 2024

    def test_filter_by_date_range_invalid_dates_skipped(self):
        """Test that ascents with invalid date formats are skipped."""
        ascents = [
            create_ascent(ascent_id="1", peak_name="Valid", date="2024-06-15"),
            create_ascent(ascent_id="2", peak_name="Invalid", date="not-a-date"),
            create_ascent(ascent_id="3", peak_name="Too many parts", date="2024-06-15-16"),
        ]

        filtered = AscentAnalyzer.filter_by_date_range(ascents)

        assert len(filtered) == 1
        assert filtered[0].peak_name == "Valid"

    def test_filter_by_date_range_empty_list(self):
        """Test filtering empty ascent list."""
        filtered = AscentAnalyzer.filter_by_date_range([])

        assert len(filtered) == 0


class TestAscentAnalyzerParseWithinPeriod:
    """Tests for AscentAnalyzer.parse_within_period method."""

    def test_parse_within_period_days(self):
        """Test parsing day-based periods."""
        assert AscentAnalyzer.parse_within_period("10d") == timedelta(days=10)
        assert AscentAnalyzer.parse_within_period("1d") == timedelta(days=1)
        assert AscentAnalyzer.parse_within_period("365d") == timedelta(days=365)

    def test_parse_within_period_months(self):
        """Test parsing month-based periods (approximated as 30 days)."""
        assert AscentAnalyzer.parse_within_period("1m") == timedelta(days=30)
        assert AscentAnalyzer.parse_within_period("3m") == timedelta(days=90)
        assert AscentAnalyzer.parse_within_period("12m") == timedelta(days=360)

    def test_parse_within_period_years(self):
        """Test parsing year-based periods."""
        assert AscentAnalyzer.parse_within_period("1y") == timedelta(days=365)
        assert AscentAnalyzer.parse_within_period("5y") == timedelta(days=1825)
        assert AscentAnalyzer.parse_within_period("10y") == timedelta(days=3650)

    def test_parse_within_period_case_insensitive(self):
        """Test that parsing is case insensitive."""
        assert AscentAnalyzer.parse_within_period("3M") == timedelta(days=90)
        assert AscentAnalyzer.parse_within_period("1Y") == timedelta(days=365)
        assert AscentAnalyzer.parse_within_period("10D") == timedelta(days=10)

    def test_parse_within_period_with_whitespace(self):
        """Test that leading/trailing whitespace is handled."""
        assert AscentAnalyzer.parse_within_period("  3m  ") == timedelta(days=90)
        assert AscentAnalyzer.parse_within_period("\t1y\n") == timedelta(days=365)

    def test_parse_within_period_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Period cannot be empty"):
            AscentAnalyzer.parse_within_period("")

        with pytest.raises(ValueError, match="Period cannot be empty"):
            AscentAnalyzer.parse_within_period("   ")

    def test_parse_within_period_invalid_format_raises_error(self):
        """Test that invalid formats raise ValueError."""
        # No unit
        with pytest.raises(ValueError, match="Invalid period format"):
            AscentAnalyzer.parse_within_period("10")

        # No number
        with pytest.raises(ValueError, match="Invalid period format"):
            AscentAnalyzer.parse_within_period("m")

        # Invalid unit
        with pytest.raises(ValueError, match="Invalid period format"):
            AscentAnalyzer.parse_within_period("10w")  # weeks not supported

        # Text instead of number
        with pytest.raises(ValueError, match="Invalid period format"):
            AscentAnalyzer.parse_within_period("tendays")

        # Mixed format
        with pytest.raises(ValueError, match="Invalid period format"):
            AscentAnalyzer.parse_within_period("10 days")

    def test_parse_within_period_negative_number_fails(self):
        """Test that negative numbers don't match the pattern."""
        with pytest.raises(ValueError, match="Invalid period format"):
            AscentAnalyzer.parse_within_period("-10d")

    def test_parse_within_period_decimal_number_fails(self):
        """Test that decimal numbers don't match the pattern."""
        with pytest.raises(ValueError, match="Invalid period format"):
            AscentAnalyzer.parse_within_period("1.5m")

    def test_parse_within_period_zero_value(self):
        """Test that zero value is accepted."""
        assert AscentAnalyzer.parse_within_period("0d") == timedelta(days=0)
        assert AscentAnalyzer.parse_within_period("0m") == timedelta(days=0)
        assert AscentAnalyzer.parse_within_period("0y") == timedelta(days=0)


class TestAscentAnalyzerEdgeCases:
    """Edge case and integration tests for AscentAnalyzer."""

    def test_all_ascents_without_dates(self):
        """Test statistics calculation when no ascents have dates."""
        ascents = [
            create_ascent(
                ascent_id=str(i),
                peak_name=f"Peak {i}",
                date=None,
                has_gpx=(i % 2 == 0),
                has_trip_report=(i % 3 == 0),
            )
            for i in range(10)
        ]

        stats = AscentAnalyzer.calculate_statistics(ascents)

        assert stats.total_ascents == 10
        assert stats.ascents_with_gpx == 5
        assert stats.ascents_with_trip_reports == 4
        # Temporal stats should all be 0 when no dates
        assert stats.last_3_months == 0
        assert stats.last_year == 0
        assert stats.last_5_years == 0
        assert sum(stats.monthly_distribution.values()) == 0

    def test_single_ascent(self):
        """Test statistics with a single ascent."""
        ascents = [
            create_ascent(
                ascent_id="1",
                climber_name="Solo Climber",
                peak_name="Solo Peak",
                date="2024-06-15",
                has_gpx=True,
                has_trip_report=True,
            )
        ]

        stats = AscentAnalyzer.calculate_statistics(ascents, reference_date=datetime(2024, 7, 1))

        assert stats.total_ascents == 1
        assert stats.ascents_with_gpx == 1
        assert stats.ascents_with_trip_reports == 1
        assert stats.last_3_months == 1
        assert stats.monthly_distribution["June"] == 1

    def test_extreme_date_ranges(self):
        """Test filtering with extreme date ranges."""
        ascents = [
            create_ascent(ascent_id="1", peak_name="Ancient", date="1900-01-01"),
            create_ascent(ascent_id="2", peak_name="Future", date="2099-12-31"),
            create_ascent(ascent_id="3", peak_name="Modern", date="2024-06-15"),
        ]

        # Filter for 21st century
        filtered = AscentAnalyzer.filter_by_date_range(
            ascents, after=datetime(2000, 1, 1), before=datetime(2100, 1, 1)
        )

        assert len(filtered) == 2  # Future and Modern

    def test_large_seasonal_window(self):
        """Test seasonal pattern with very large window (entire year)."""
        ascents = [
            create_ascent(ascent_id=str(i), peak_name=f"Peak {i}", date=f"2024-{i:02d}-15")
            for i in range(1, 13)
        ]

        stats = AscentAnalyzer.calculate_statistics(
            ascents, reference_date=datetime(2024, 6, 15), seasonal_window_days=365
        )

        # With 365-day window, all ascents should be in seasonal pattern
        assert stats.seasonal_pattern is not None
        assert sum(stats.seasonal_pattern.values()) == 12
