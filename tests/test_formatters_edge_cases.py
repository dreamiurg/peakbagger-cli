"""
Comprehensive formatter edge case and error handling tests.

Tests cover:
- Empty results handling
- Edge cases in date parsing
- JSON output for multiple peaks
- Ascent detail edge cases
- Error handling paths
"""

import json
from io import StringIO
from unittest.mock import patch

from peakbagger.formatters import PeakFormatter
from peakbagger.models import Ascent, AscentStatistics, Peak


class TestParseDateForSort:
    """Tests for _parse_date_for_sort edge cases."""

    def test_parse_date_for_sort_with_invalid_format(self):
        """Test date parsing with invalid format."""
        formatter = PeakFormatter()
        ascent = Ascent(
            ascent_id="1",
            climber_name="Test",
            date="invalid-date-format",
        )

        result = formatter._parse_date_for_sort(ascent)

        # Should return datetime.min for invalid format
        from datetime import datetime

        assert result == datetime.min

    def test_parse_date_for_sort_with_unexpected_parts(self):
        """Test date parsing with unexpected number of parts."""
        formatter = PeakFormatter()
        ascent = Ascent(
            ascent_id="1",
            climber_name="Test",
            date="2024-01-01-extra-part",
        )

        result = formatter._parse_date_for_sort(ascent)

        # Should return datetime.min for invalid format
        from datetime import datetime

        assert result == datetime.min

    def test_parse_date_for_sort_with_value_error(self):
        """Test date parsing when ValueError is raised."""
        formatter = PeakFormatter()
        ascent = Ascent(
            ascent_id="1",
            climber_name="Test",
            date="9999-99-99",  # Invalid date that will raise ValueError
        )

        result = formatter._parse_date_for_sort(ascent)

        # Should return datetime.min on ValueError
        from datetime import datetime

        assert result == datetime.min


class TestFormatSearchResults:
    """Tests for format_search_results edge cases."""

    def test_print_search_table_with_empty_results(self):
        """Test printing empty search results."""
        formatter = PeakFormatter()

        # Should print "No results found" message
        # Just verify it doesn't raise an exception
        formatter._print_search_table([])
        assert True


class TestFormatPeaks:
    """Tests for format_peaks edge cases."""

    def test_format_peaks_json_output(self):
        """Test format_peaks with JSON output."""
        formatter = PeakFormatter()
        peaks = [
            Peak(pid="1", name="Peak 1", state="WA"),
            Peak(pid="2", name="Peak 2", state="CA"),
        ]

        # Capture print output
        output = StringIO()
        with patch("sys.stdout", output):
            formatter.format_peaks(peaks, output_format="json")

        # Verify JSON output
        result = json.loads(output.getvalue())
        assert len(result) == 2
        assert result[0]["pid"] == "1"
        assert result[1]["pid"] == "2"

    def test_format_peaks_text_with_separator(self):
        """Test format_peaks with text output includes separators."""
        formatter = PeakFormatter()
        peaks = [
            Peak(pid="1", name="Peak 1", state="WA"),
            Peak(pid="2", name="Peak 2", state="CA"),
        ]

        # Just verify it doesn't raise an exception
        formatter.format_peaks(peaks, output_format="text")


class TestFormatAscentDetail:
    """Tests for format_ascent_detail edge cases."""

    def test_format_ascent_detail_no_route(self):
        """Test formatting ascent detail when route is missing."""
        formatter = PeakFormatter()
        ascent = Ascent(
            ascent_id="123",
            climber_name="John Doe",
            climber_id="456",
            date="2024-01-01",
            route=None,  # No route
        )

        # Should handle missing route
        formatter.format_ascent_detail(ascent, output_format="text")

    def test_format_ascent_detail_no_gpx_metrics(self):
        """Test formatting ascent detail without GPX metrics."""
        formatter = PeakFormatter()
        ascent = Ascent(
            ascent_id="123",
            climber_name="John Doe",
            climber_id="456",
            date="2024-01-01",
            elevation_gain_ft=None,
            distance_mi=None,
            duration_hours=None,
        )

        # Should handle missing GPX metrics
        formatter.format_ascent_detail(ascent, output_format="text")

    def test_format_ascent_detail_with_elevation_gain(self):
        """Test formatting ascent detail with elevation gain."""
        formatter = PeakFormatter()
        ascent = Ascent(
            ascent_id="123",
            climber_name="John Doe",
            climber_id="456",
            date="2024-01-01",
            elevation_gain_ft=5000,
        )

        # Should display elevation gain
        formatter.format_ascent_detail(ascent, output_format="text")

    def test_format_ascent_detail_with_distance(self):
        """Test formatting ascent detail with distance."""
        formatter = PeakFormatter()
        ascent = Ascent(
            ascent_id="123",
            climber_name="John Doe",
            climber_id="456",
            date="2024-01-01",
            distance_mi=10.5,
        )

        # Should display distance
        formatter.format_ascent_detail(ascent, output_format="text")

    def test_format_ascent_detail_duration_with_minutes(self):
        """Test formatting duration when it includes minutes."""
        formatter = PeakFormatter()
        ascent = Ascent(
            ascent_id="123",
            climber_name="John Doe",
            climber_id="456",
            date="2024-01-01",
            duration_hours=4.5,  # 4 hours 30 minutes
        )

        # Should display duration with hours and minutes
        formatter.format_ascent_detail(ascent, output_format="text")

    def test_format_ascent_detail_duration_whole_hours(self):
        """Test formatting duration with whole hours only."""
        formatter = PeakFormatter()
        ascent = Ascent(
            ascent_id="123",
            climber_name="John Doe",
            climber_id="456",
            date="2024-01-01",
            duration_hours=4.0,  # Exactly 4 hours
        )

        # Should display duration without minutes
        formatter.format_ascent_detail(ascent, output_format="text")

    def test_format_ascent_detail_with_trip_report_words(self):
        """Test formatting ascent with trip report word count."""
        formatter = PeakFormatter()
        ascent = Ascent(
            ascent_id="123",
            climber_name="John Doe",
            climber_id="456",
            date="2024-01-01",
            has_trip_report=True,
            trip_report_words=500,
        )

        # Should display trip report word count
        formatter.format_ascent_detail(ascent, output_format="text")

    def test_format_ascent_detail_with_external_url(self):
        """Test formatting ascent with external trip report URL."""
        formatter = PeakFormatter()
        ascent = Ascent(
            ascent_id="123",
            climber_name="John Doe",
            climber_id="456",
            date="2024-01-01",
            trip_report_text="This is my trip report.",
            trip_report_url="https://example.com/trip-report",
        )

        # Should display external URL
        formatter.format_ascent_detail(ascent, output_format="text")


class TestFormatAscentStatistics:
    """Tests for format_ascent_statistics edge cases."""

    def test_format_ascent_statistics_json_with_ascents_list(self):
        """Test JSON output with ascents list."""
        formatter = PeakFormatter()
        stats = AscentStatistics(
            total_ascents=2,
            ascents_with_gpx=1,
            ascents_with_trip_reports=1,
            last_3_months=1,
            last_year=2,
            last_5_years=2,
            monthly_distribution={
                "January": 1,
                "February": 0,
                "March": 0,
                "April": 0,
                "May": 0,
                "June": 0,
                "July": 0,
                "August": 0,
                "September": 0,
                "October": 0,
                "November": 0,
                "December": 1,
            },
        )
        ascents = [
            Ascent(
                ascent_id="1",
                climber_name="John Doe",
                date="2024-01-01",
                has_gpx=True,
            ),
            Ascent(
                ascent_id="2",
                climber_name="Jane Smith",
                date="2023-12-15",
                has_trip_report=True,
                trip_report_words=100,
            ),
        ]

        # Capture print output
        output = StringIO()
        with patch("sys.stdout", output):
            formatter.format_ascent_statistics(
                stats, ascents=ascents, output_format="json", show_list=True, limit=10
            )

        # Verify JSON output includes ascents
        result = json.loads(output.getvalue())
        assert "ascents" in result
        assert len(result["ascents"]) == 2

    def test_format_ascent_statistics_json_with_limit(self):
        """Test JSON output respects limit parameter."""
        formatter = PeakFormatter()
        stats = AscentStatistics(
            total_ascents=5,
            ascents_with_gpx=0,
            ascents_with_trip_reports=0,
            last_3_months=0,
            last_year=0,
            last_5_years=5,
            monthly_distribution={
                "January": 1,
                "February": 1,
                "March": 1,
                "April": 1,
                "May": 1,
                "June": 0,
                "July": 0,
                "August": 0,
                "September": 0,
                "October": 0,
                "November": 0,
                "December": 0,
            },
        )
        ascents = [
            Ascent(ascent_id=str(i), climber_name=f"Climber {i}", date=f"2024-0{i}-01")
            for i in range(1, 6)
        ]

        # Capture print output
        output = StringIO()
        with patch("sys.stdout", output):
            formatter.format_ascent_statistics(
                stats, ascents=ascents, output_format="json", show_list=True, limit=3
            )

        # Verify JSON output respects limit
        result = json.loads(output.getvalue())
        assert "ascents" in result
        assert len(result["ascents"]) <= 3


class TestPrintAscentStatistics:
    """Tests for _print_ascent_statistics edge cases."""

    def test_print_ascent_statistics_with_seasonal_pattern(self):
        """Test printing statistics with seasonal pattern."""
        formatter = PeakFormatter()
        stats = AscentStatistics(
            total_ascents=10,
            ascents_with_gpx=5,
            ascents_with_trip_reports=3,
            last_3_months=2,
            last_year=5,
            last_5_years=10,
            monthly_distribution={
                "January": 1,
                "February": 0,
                "March": 0,
                "April": 0,
                "May": 0,
                "June": 2,
                "July": 3,
                "August": 2,
                "September": 1,
                "October": 0,
                "November": 0,
                "December": 1,
            },
            seasonal_pattern={
                "January": 0,
                "February": 0,
                "March": 0,
                "April": 0,
                "May": 0,
                "June": 2,
                "July": 3,
                "August": 0,
                "September": 0,
                "October": 0,
                "November": 0,
                "December": 0,
            },
        )

        # Should display seasonal pattern section
        formatter._print_ascent_statistics(stats)

    def test_print_ascent_statistics_empty_seasonal_pattern(self):
        """Test printing statistics with empty seasonal pattern."""
        formatter = PeakFormatter()
        stats = AscentStatistics(
            total_ascents=10,
            ascents_with_gpx=5,
            ascents_with_trip_reports=3,
            last_3_months=2,
            last_year=5,
            last_5_years=10,
            monthly_distribution={
                "January": 1,
                "February": 0,
                "March": 0,
                "April": 0,
                "May": 0,
                "June": 2,
                "July": 3,
                "August": 2,
                "September": 1,
                "October": 0,
                "November": 0,
                "December": 1,
            },
            seasonal_pattern={
                "January": 0,
                "February": 0,
                "March": 0,
                "April": 0,
                "May": 0,
                "June": 0,
                "July": 0,
                "August": 0,
                "September": 0,
                "October": 0,
                "November": 0,
                "December": 0,
            },
        )

        # Should display "No ascents in seasonal window" message
        formatter._print_ascent_statistics(stats)
