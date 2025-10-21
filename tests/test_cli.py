"""Smoke tests for peakbagger CLI commands."""

import json

import pytest
from click.testing import CliRunner

from peakbagger.cli import main


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.mark.vcr()
def test_search_mount_rainier(cli_runner):
    """Test searching for Mount Rainier returns results."""
    result = cli_runner.invoke(main, ["peak", "search", "Mount Rainier"])

    assert result.exit_code == 0
    assert "Mount Rainier" in result.output
    # Should show the table with results
    assert "Location" in result.output or "Washington" in result.output


@pytest.mark.vcr()
def test_search_mount_rainier_json(cli_runner):
    """Test searching for Mount Rainier with JSON output."""
    result = cli_runner.invoke(main, ["peak", "search", "Mount Rainier", "--format", "json"])

    assert result.exit_code == 0
    # Output may have "Searching..." message before JSON, extract just the JSON part
    output_lines = result.output.strip().split("\n")
    # Find the JSON array (starts with '[')
    json_start = next(i for i, line in enumerate(output_lines) if line.startswith("["))
    json_output = "\n".join(output_lines[json_start:])
    data = json.loads(json_output)
    assert isinstance(data, list)
    assert len(data) > 0
    # Check first result has expected fields
    first = data[0]
    assert "name" in first
    assert "pid" in first
    assert "Mount Rainier" in first["name"]


@pytest.mark.vcr()
def test_show_peak_2296(cli_runner):
    """Test showing details for Mount Rainier (pid=2296)."""
    result = cli_runner.invoke(main, ["peak", "show", "2296"])

    assert result.exit_code == 0
    assert "Mount Rainier" in result.output
    # Should show elevation (14,400+ ft range)
    assert "14," in result.output and "ft" in result.output


@pytest.mark.vcr()
def test_show_peak_2296_json(cli_runner):
    """Test showing Mount Rainier details with JSON output."""
    result = cli_runner.invoke(main, ["peak", "show", "2296", "--format", "json"])

    assert result.exit_code == 0
    # Output may have "Fetching..." message before JSON, extract just the JSON part
    output_lines = result.output.strip().split("\n")
    # Find the JSON object (starts with '{')
    json_start = next(i for i, line in enumerate(output_lines) if line.startswith("{"))
    json_output = "\n".join(output_lines[json_start:])
    data = json.loads(json_output)
    assert isinstance(data, dict)
    assert data["pid"] == "2296"
    assert "Mount Rainier" in data["name"]
    assert data["elevation"]["feet"] > 14000  # Mount Rainier is 14,400+ ft


@pytest.mark.vcr()
def test_ascents_1798(cli_runner):
    """Test listing ascents for Mount Pilchuck (pid=1798)."""
    result = cli_runner.invoke(main, ["peak", "ascents", "1798", "--limit", "10"])

    assert result.exit_code == 0
    # Should show some ascents
    assert "ascents" in result.output.lower()


@pytest.mark.vcr()
def test_ascents_1798_json(cli_runner):
    """Test listing ascents with JSON output."""
    result = cli_runner.invoke(
        main, ["peak", "ascents", "1798", "--limit", "10", "--format", "json"]
    )

    assert result.exit_code == 0
    # Output may have messages before AND after JSON, extract just the JSON part
    output_lines = result.output.strip().split("\n")
    # Find the JSON object (starts with '{')
    json_start = next(i for i, line in enumerate(output_lines) if line.startswith("{"))
    # Find where JSON ends (look for final '}' followed by non-JSON text or end)
    json_end = json_start
    brace_count = 0
    for i in range(json_start, len(output_lines)):
        line = output_lines[i]
        brace_count += line.count("{") - line.count("}")
        json_end = i
        if brace_count == 0:
            break
    json_output = "\n".join(output_lines[json_start : json_end + 1])
    data = json.loads(json_output)
    assert isinstance(data, dict)
    assert "ascents" in data
    assert isinstance(data["ascents"], list)


@pytest.mark.vcr()
def test_stats_1798(cli_runner):
    """Test statistics for Mount Pilchuck (pid=1798)."""
    result = cli_runner.invoke(main, ["peak", "stats", "1798"])

    assert result.exit_code == 0
    # Should show statistics
    assert "statistics" in result.output.lower() or "ascents" in result.output.lower()


@pytest.mark.vcr()
def test_stats_1798_json(cli_runner):
    """Test statistics with JSON output."""
    result = cli_runner.invoke(main, ["peak", "stats", "1798", "--format", "json"])

    assert result.exit_code == 0
    # Output may have messages before JSON, extract just the JSON part
    output_lines = result.output.strip().split("\n")
    # Find the JSON object (starts with '{')
    json_start = next(i for i, line in enumerate(output_lines) if line.startswith("{"))
    json_output = "\n".join(output_lines[json_start:])
    data = json.loads(json_output)
    assert isinstance(data, dict)
    # Should have statistics keys
    assert "total_ascents" in data or "ascent_count" in data
