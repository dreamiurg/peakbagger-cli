"""Tests for dynamic ascents parser that handles varying table structures."""

import json
from typing import Any

import pytest
from click.testing import CliRunner

from peakbagger.cli import main


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner with wide terminal for proper table display."""
    return CliRunner(env={"COLUMNS": "200"})


def extract_json_from_output(output: str) -> dict[str, Any]:
    """Extract and parse JSON from CLI output.

    Args:
        output: CLI command output that may contain JSON

    Returns:
        Parsed JSON data as dictionary
    """
    output_lines = output.strip().split("\n")
    json_start = next(i for i, line in enumerate(output_lines) if line.startswith("{"))
    json_end = json_start
    brace_count = 0
    for i in range(json_start, len(output_lines)):
        line = output_lines[i]
        brace_count += line.count("{") - line.count("}")
        json_end = i
        if brace_count == 0:
            break
    json_output = "\n".join(output_lines[json_start : json_end + 1])
    data: dict[str, Any] = json.loads(json_output)
    return data


# Peak 2117: Pratt Mountain - 10 columns
# Headers: Climber, Ascent Date, Type, GPS, TR-Words, Gain-Ft, Mi, Route Icons, Gear Icons, Link
@pytest.mark.vcr()
def test_ascents_pratt_mountain_2117(cli_runner):
    """Test ascents for Pratt Mountain (10-column table format)."""
    result = cli_runner.invoke(main, ["peak", "ascents", "2117", "--limit", "20"])

    assert result.exit_code == 0
    assert "ascents" in result.output.lower()
    # Should find ascents (peak has 681 logged)
    assert "no ascents found" not in result.output.lower()


@pytest.mark.vcr()
def test_ascents_pratt_mountain_2117_json(cli_runner):
    """Test ascents JSON for Pratt Mountain (10-column table)."""
    result = cli_runner.invoke(
        main, ["peak", "ascents", "2117", "--limit", "20", "--format", "json"]
    )

    assert result.exit_code == 0
    # Extract JSON
    data = extract_json_from_output(result.output)

    assert isinstance(data, dict)
    assert "ascents" in data
    assert len(data["ascents"]) > 0
    # Check structure of first ascent
    first = data["ascents"][0]
    assert "ascent_id" in first
    assert "climber" in first
    assert "name" in first["climber"]


# Peak 2296: Mount Rainier - 14 columns
# Headers: Climber, Ascent Date, Type, GPS, TR-Words, Route, Gain-Ft, Trip-Ft, Mi, Trip-Mi, Route Icons, Gear Icons, Qlty, Link
@pytest.mark.vcr()
def test_ascents_mount_rainier_2296(cli_runner):
    """Test ascents for Mount Rainier (14-column table format)."""
    result = cli_runner.invoke(main, ["peak", "ascents", "2296", "--limit", "20"])

    assert result.exit_code == 0
    assert "ascents" in result.output.lower()
    assert "no ascents found" not in result.output.lower()


@pytest.mark.vcr()
def test_ascents_mount_rainier_2296_json(cli_runner):
    """Test ascents JSON for Mount Rainier (14-column table)."""
    result = cli_runner.invoke(
        main, ["peak", "ascents", "2296", "--limit", "20", "--format", "json"]
    )

    assert result.exit_code == 0
    data = extract_json_from_output(result.output)

    assert isinstance(data, dict)
    assert "ascents" in data
    assert len(data["ascents"]) > 0


# Peak 271: Denali - 8 columns
# Headers: Climber, Ascent Date, Type, TR-Words, Route, Gain-Ft, Route Icons, Gear Icons
@pytest.mark.vcr()
def test_ascents_denali_271(cli_runner):
    """Test ascents for Denali (8-column table format, no GPS or Link columns)."""
    result = cli_runner.invoke(main, ["peak", "ascents", "271", "--limit", "20"])

    assert result.exit_code == 0
    assert "ascents" in result.output.lower()
    assert "no ascents found" not in result.output.lower()


@pytest.mark.vcr()
def test_ascents_denali_271_json(cli_runner):
    """Test ascents JSON for Denali (8-column table)."""
    result = cli_runner.invoke(
        main, ["peak", "ascents", "271", "--limit", "20", "--format", "json"]
    )

    assert result.exit_code == 0
    data = extract_json_from_output(result.output)

    assert isinstance(data, dict)
    assert "ascents" in data
    assert len(data["ascents"]) > 0


# Peak 9779: Mount Si - 13 columns
# Headers: Climber, Ascent Date, Type, GPS, TR-Words, Route, Gain-Ft, Trip-Ft, Mi, Route Icons, Gear Icons, Qlty, Link
@pytest.mark.vcr()
def test_ascents_mount_si_9779(cli_runner):
    """Test ascents for Mount Si (13-column table format)."""
    result = cli_runner.invoke(main, ["peak", "ascents", "9779", "--limit", "20"])

    assert result.exit_code == 0
    assert "ascents" in result.output.lower()
    # Mount Si should have ascents logged
    assert "no ascents found" not in result.output.lower()


@pytest.mark.vcr()
def test_ascents_mount_si_9779_json(cli_runner):
    """Test ascents JSON for Mount Si (13-column table)."""
    result = cli_runner.invoke(
        main, ["peak", "ascents", "9779", "--limit", "20", "--format", "json"]
    )

    assert result.exit_code == 0
    data = extract_json_from_output(result.output)

    assert isinstance(data, dict)
    assert "ascents" in data
    assert len(data["ascents"]) > 0


# Peak 2087: Mount Si - 12 columns with nested tables in route icons
# This peak tests the fix for nested table parsing (recursive=False)
# Headers: Climber, Ascent Date, Type, GPS, TR-Words, Route, Gain-Ft, Mi, Route Icons, Gear Icons, Qlty, Link
@pytest.mark.vcr()
def test_ascents_mount_si_2087_nested_tables(cli_runner):
    """Test ascents for Mount Si (12-column table with nested tables in route icons)."""
    result = cli_runner.invoke(main, ["peak", "ascents", "2087", "--limit", "20"])

    assert result.exit_code == 0
    assert "ascents" in result.output.lower()
    # Mount Si 2087 should have many ascents logged
    assert "no ascents found" not in result.output.lower()


@pytest.mark.vcr()
def test_ascents_mount_si_2087_nested_tables_json(cli_runner):
    """Test ascents JSON for Mount Si with nested tables (validates proper cell counting)."""
    result = cli_runner.invoke(
        main, ["peak", "ascents", "2087", "--limit", "20", "--format", "json"]
    )

    assert result.exit_code == 0
    data = extract_json_from_output(result.output)

    assert isinstance(data, dict)
    assert "ascents" in data
    assert len(data["ascents"]) > 0
    # Verify that ascents with nested tables are properly parsed
    first = data["ascents"][0]
    assert "ascent_id" in first
    assert "climber" in first
    assert "date" in first
