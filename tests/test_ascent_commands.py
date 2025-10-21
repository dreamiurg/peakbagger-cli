"""Tests for ascent commands and parsing."""

import json

import pytest
from click.testing import CliRunner

from peakbagger.cli import main
from peakbagger.scraper import PeakBaggerScraper

# Parser Tests


def test_parse_ascent_detail_with_trip_report() -> None:
    """Test parsing ascent detail page with full trip report."""
    scraper = PeakBaggerScraper()

    # Use the sample HTML we saved earlier
    with open("/tmp/ascent_with_tr_12963.html") as f:
        html = f.read()

    ascent = scraper.parse_ascent_detail(html, "12963")

    assert ascent is not None
    assert ascent.ascent_id == "12963"
    assert ascent.climber_name == "Bob Bolton"
    assert ascent.climber_id == "555"
    assert ascent.peak_name == "Mount Pilchuck"
    assert ascent.peak_id == "1798"
    assert ascent.location == "USA-Washington"
    assert ascent.elevation_ft == 5341
    assert ascent.elevation_m == 1627
    assert ascent.date == "1951"
    assert ascent.ascent_type is not None
    assert "Successful" in ascent.ascent_type

    # Check trip report
    assert ascent.trip_report_text is not None
    assert len(ascent.trip_report_text) > 100
    assert "Pilchuck" in ascent.trip_report_text


def test_parse_ascent_detail_minimal() -> None:
    """Test parsing ascent detail page with minimal data."""
    scraper = PeakBaggerScraper()

    with open("/tmp/ascent_1479339.html") as f:
        html = f.read()

    ascent = scraper.parse_ascent_detail(html, "1479339")

    assert ascent is not None
    assert ascent.ascent_id == "1479339"
    assert ascent.climber_name is not None
    assert ascent.peak_name is not None
    # Trip report may be None for this one


# CLI Integration Tests (VCR-based)


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.mark.vcr()
def test_ascent_show_command_text(cli_runner) -> None:
    """Test ascent show command with text output."""
    result = cli_runner.invoke(main, ["ascent", "show", "12963"])

    assert result.exit_code == 0
    assert "Bob Bolton" in result.output
    assert "Mount Pilchuck" in result.output
    assert "Trip Report" in result.output


@pytest.mark.vcr()
def test_ascent_show_command_json(cli_runner) -> None:
    """Test ascent show command with JSON output."""
    result = cli_runner.invoke(main, ["ascent", "show", "12963", "--format", "json"])

    assert result.exit_code == 0

    # Parse JSON output (may have "Fetching ascent..." message before JSON)
    output_lines = result.output.strip().split("\n")
    # Find the JSON object (starts with '{')
    json_start = next(i for i, line in enumerate(output_lines) if line.startswith("{"))
    json_output = "\n".join(output_lines[json_start:])
    data = json.loads(json_output)

    assert data["ascent_id"] == "12963"
    assert data["climber"]["name"] == "Bob Bolton"
    assert data["peak"]["name"] == "Mount Pilchuck"
    assert "trip_report" in data
    # Check that trip report text was extracted
    assert "text" in data["trip_report"]
    assert len(data["trip_report"]["text"]) > 100
