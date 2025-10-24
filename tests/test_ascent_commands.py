"""Tests for ascent commands and parsing."""

import json

import pytest
from click.testing import CliRunner

from peakbagger.cli import main

# CLI Integration Tests (VCR-based)


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner with wide terminal for proper table display."""
    return CliRunner(env={"COLUMNS": "200"})


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
