# Tests

This directory contains smoke tests for the peakbagger CLI using VCR.py for HTTP recording.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests without coverage report
uv run pytest --no-cov

# Run specific test file
uv run pytest tests/test_cli.py
```

## Test Strategy

**Philosophy**: Lightweight smoke tests with real HTTP cassettes.

These tests verify that:
1. CLI commands execute successfully
2. HTML parsing works against real PeakBagger.com structure
3. Both text and JSON output formats work

We use [VCR.py](https://vcrpy.readthedocs.io/) to record HTTP interactions once, then replay them for fast, repeatable tests.

## Test Coverage

- `test_search_mount_rainier` - Search command with text output
- `test_search_mount_rainier_json` - Search command with JSON output
- `test_show_peak_2296` - Peak detail command (Mount Rainier)
- `test_show_peak_2296_json` - Peak detail with JSON output
- `test_ascents_1798` - Ascents list command (Mount Pilchuck)
- `test_ascents_1798_json` - Ascents list with JSON output
- `test_stats_1798` - Statistics command (Mount Pilchuck)
- `test_stats_1798_json` - Statistics with JSON output

## VCR Cassettes

HTTP interactions are recorded in `tests/cassettes/` as YAML files. Each test has its own cassette.

### Re-recording Cassettes

If PeakBagger.com's HTML structure changes, you'll need to re-record cassettes:

```bash
# Delete all cassettes
rm -rf tests/cassettes/*.yaml

# Run tests to record fresh cassettes (requires network access)
uv run pytest tests/test_cli.py -v
```

**Note**: Re-recording requires network access and respects the rate limiting (2 seconds between requests), so it will take ~20-30 seconds.

### When to Re-record

- Tests fail with parsing errors
- You suspect PeakBagger.com changed their HTML structure
- You want to update test data (e.g., new ascent counts)

## Writing New Tests

To add a new smoke test:

1. Write test function with `@pytest.mark.vcr()` decorator
2. Use `CliRunner` to invoke CLI commands
3. Assert on output content
4. Run test once to record cassette
5. Commit both test code and cassette

Example:

```python
@pytest.mark.vcr()
def test_my_new_command(cli_runner):
    """Test description."""
    result = cli_runner.invoke(main, ["peak", "search", "Denali"])
    assert result.exit_code == 0
    assert "Denali" in result.output
```

## Troubleshooting

**Tests fail with "No cassette found"**
- Delete cassettes and re-run tests to record fresh ones

**Tests fail with JSONDecodeError**
- CLI may be outputting informational messages before JSON
- Check if output has text before/after JSON and extract accordingly

**Tests fail with parsing errors**
- PeakBagger.com likely changed their HTML
- Re-record cassettes
- If still failing, update the scraper parsing logic
