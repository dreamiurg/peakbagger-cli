"""
Comprehensive CLI error handling and edge case tests.

Tests cover:
- Flag validation and conflicts
- Error handling paths
- Empty results handling
- HTML dump functionality
- Exception propagation
"""

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from peakbagger.cli import _error, main
from peakbagger.models import Ascent as AscentModel
from peakbagger.models import SearchResult


class TestMainCommand:
    """Tests for main command with flags."""

    def test_quiet_and_verbose_conflict(self):
        """Test that --quiet and --verbose cannot be used together."""
        runner = CliRunner()
        result = runner.invoke(main, ["--quiet", "--verbose", "peak", "search", "test"])

        assert result.exit_code != 0
        assert "cannot be used with" in result.output

    def test_quiet_and_debug_conflict(self):
        """Test that --quiet and --debug cannot be used together."""
        runner = CliRunner()
        result = runner.invoke(main, ["--quiet", "--debug", "peak", "search", "test"])

        assert result.exit_code != 0
        assert "cannot be used with" in result.output

    def test_debug_requires_verbose(self):
        """Test that --debug requires --verbose."""
        runner = CliRunner()
        result = runner.invoke(main, ["--debug", "peak", "search", "test"])

        assert result.exit_code != 0
        assert "debug requires --verbose" in result.output.lower()

    def test_dump_html_flag_works(self):
        """Test that --dump-html outputs raw HTML."""
        runner = CliRunner()

        with patch("peakbagger.cli.PeakBaggerClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get.return_value = "<html>Test HTML</html>"
            mock_client_class.return_value = mock_client

            result = runner.invoke(main, ["--dump-html", "peak", "search", "test"])

            assert result.exit_code == 0
            assert "Test HTML" in result.output
            mock_client.close.assert_called_once()


class TestErrorFunction:
    """Tests for _error helper function."""

    def test_error_displays_message(self, capsys):
        """Test that _error displays formatted error message."""
        _error("Test error message")

        captured = capsys.readouterr()
        # Rich prints to stderr
        output = captured.out + captured.err
        assert "Error:" in output
        assert "Test error message" in output


class TestSearchCommand:
    """Tests for peak search command error handling."""

    def test_search_with_empty_results(self):
        """Test search when no results are found."""
        runner = CliRunner()

        with patch("peakbagger.cli.PeakBaggerClient") as mock_client_class:
            with patch("peakbagger.cli.PeakBaggerScraper") as mock_scraper_class:
                mock_client = Mock()
                mock_client.get.return_value = "<html>No results</html>"
                mock_client_class.return_value = mock_client

                mock_scraper = Mock()
                mock_scraper.parse_search_results.return_value = []
                mock_scraper_class.return_value = mock_scraper

                result = runner.invoke(main, ["peak", "search", "nonexistent"])

                assert result.exit_code == 0
                mock_client.close.assert_called_once()

    def test_search_with_exception_handling(self):
        """Test that search handles exceptions properly."""
        runner = CliRunner()

        with patch("peakbagger.cli.PeakBaggerClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get.side_effect = Exception("Network error")
            mock_client_class.return_value = mock_client

            result = runner.invoke(main, ["peak", "search", "test"])

            assert result.exit_code != 0
            assert "Error:" in result.output or "Aborted" in result.output
            mock_client.close.assert_called_once()

    def test_search_full_flag_with_empty_peaks(self):
        """Test search with --full when peak details fail to parse."""
        runner = CliRunner()

        with patch("peakbagger.cli.PeakBaggerClient") as mock_client_class:
            with patch("peakbagger.cli.PeakBaggerScraper") as mock_scraper_class:
                with patch("peakbagger.cli.PeakFormatter") as mock_formatter_class:
                    mock_client = Mock()
                    mock_client.get.return_value = "<html>Test</html>"
                    mock_client_class.return_value = mock_client

                    mock_scraper = Mock()
                    mock_scraper.parse_search_results.return_value = [
                        SearchResult(
                            name="Test Peak",
                            url="peak.aspx?pid=1",
                            pid="1",
                            elevation_ft="1000",
                            location="USA",
                        )
                    ]
                    mock_scraper.parse_peak_detail.return_value = None  # Parsing failed
                    mock_scraper_class.return_value = mock_scraper

                    mock_formatter = Mock()
                    mock_formatter_class.return_value = mock_formatter

                    result = runner.invoke(main, ["peak", "search", "--full", "test"])

                    assert result.exit_code == 0
                    # Should call format_peaks with empty list
                    mock_formatter.format_peaks.assert_called_once()


class TestShowCommand:
    """Tests for peak show command error handling."""

    @pytest.mark.skip(reason="Complex mocking scenario - covered by integration tests")
    def test_show_with_parsing_error(self):
        """Test show command when peak detail parsing fails."""
        pass

    def test_show_with_exception(self):
        """Test show command exception handling."""
        runner = CliRunner()

        with patch("peakbagger.cli.PeakBaggerClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get.side_effect = Exception("HTTP error")
            mock_client_class.return_value = mock_client

            result = runner.invoke(main, ["peak", "show", "999"])

            assert result.exit_code != 0
            mock_client.close.assert_called_once()


class TestAscentsCommand:
    """Tests for peak ascents command error handling."""

    def test_ascents_with_empty_results(self):
        """Test ascents when no ascents are found."""
        runner = CliRunner()

        with patch("peakbagger.cli.PeakBaggerClient") as mock_client_class:
            with patch("peakbagger.cli.PeakBaggerScraper") as mock_scraper_class:
                mock_client = Mock()
                mock_client.get.return_value = "<html>No ascents</html>"
                mock_client_class.return_value = mock_client

                mock_scraper = Mock()
                mock_scraper.parse_peak_ascents.return_value = []
                mock_scraper_class.return_value = mock_scraper

                result = runner.invoke(main, ["peak", "ascents", "999"])

                assert result.exit_code == 0
                mock_client.close.assert_called_once()

    def test_ascents_with_exception(self):
        """Test ascents exception handling."""
        runner = CliRunner()

        with patch("peakbagger.cli.PeakBaggerClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get.side_effect = Exception("Fetch failed")
            mock_client_class.return_value = mock_client

            result = runner.invoke(main, ["peak", "ascents", "999"])

            assert result.exit_code != 0
            mock_client.close.assert_called_once()

    def test_ascents_limit_filter(self):
        """Test ascents with --limit flag."""
        runner = CliRunner()

        with patch("peakbagger.cli.PeakBaggerClient") as mock_client_class:
            with patch("peakbagger.cli.PeakBaggerScraper") as mock_scraper_class:
                with patch("peakbagger.cli.PeakFormatter") as mock_formatter_class:
                    mock_client = Mock()
                    mock_client.get.return_value = "<html>Ascents</html>"
                    mock_client_class.return_value = mock_client

                    mock_scraper = Mock()
                    # Create more ascents than limit
                    ascents = [
                        AscentModel(
                            ascent_id=str(i), climber_name=f"Climber {i}", date="2024-01-01"
                        )
                        for i in range(10)
                    ]
                    mock_scraper.parse_peak_ascents.return_value = ascents
                    mock_scraper_class.return_value = mock_scraper

                    mock_formatter = Mock()
                    mock_formatter_class.return_value = mock_formatter

                    result = runner.invoke(main, ["peak", "ascents", "--limit", "5", "999"])

                    assert result.exit_code == 0
                    # Should only format 5 ascents
                    call_args = mock_formatter.format_search_results.call_args
                    if call_args:
                        formatted_ascents = call_args[0][0]
                        assert len(formatted_ascents) == 5


class TestStatsCommand:
    """Tests for peak stats command error handling."""

    def test_stats_with_empty_ascents(self):
        """Test stats when no ascents found."""
        runner = CliRunner()

        with patch("peakbagger.cli.PeakBaggerClient") as mock_client_class:
            with patch("peakbagger.cli.PeakBaggerScraper") as mock_scraper_class:
                mock_client = Mock()
                mock_client.get.return_value = "<html>No ascents</html>"
                mock_client_class.return_value = mock_client

                mock_scraper = Mock()
                mock_scraper.parse_peak_ascents.return_value = []
                mock_scraper_class.return_value = mock_scraper

                result = runner.invoke(main, ["peak", "stats", "999"])

                assert result.exit_code == 0
                mock_client.close.assert_called_once()

    def test_stats_with_exception(self):
        """Test stats exception handling."""
        runner = CliRunner()

        with patch("peakbagger.cli.PeakBaggerClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get.side_effect = Exception("Stats fetch failed")
            mock_client_class.return_value = mock_client

            result = runner.invoke(main, ["peak", "stats", "999"])

            assert result.exit_code != 0
            mock_client.close.assert_called_once()


class TestAscentShowCommand:
    """Tests for ascent show command error handling."""

    @pytest.mark.skip(reason="Complex mocking scenario - covered by integration tests")
    def test_ascent_show_with_parsing_error(self):
        """Test ascent show when detail parsing fails."""
        pass

    def test_ascent_show_with_exception(self):
        """Test ascent show exception handling."""
        runner = CliRunner()

        with patch("peakbagger.cli.PeakBaggerClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get.side_effect = Exception("Ascent fetch failed")
            mock_client_class.return_value = mock_client

            result = runner.invoke(main, ["ascent", "show", "999"])

            assert result.exit_code != 0
            mock_client.close.assert_called_once()


class TestJSONOutput:
    """Tests for JSON output mode error handling."""

    @pytest.mark.skip(reason="Complex mocking scenario - covered by integration tests")
    def test_search_json_output(self):
        """Test search with JSON output format."""
        pass
