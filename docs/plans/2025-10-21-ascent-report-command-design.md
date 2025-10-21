# Design: Ascent Report Command

**Date:** 2025-10-21
**Feature:** Add CLI command to retrieve individual ascent reports by ID

## Overview

Add a new `ascent show` command to retrieve detailed information about a specific ascent from PeakBagger.com. The command fetches ascent metadata, trip report text, and GPX-derived metrics when available.

## Command Structure

```bash
peakbagger ascent show <ascent_id> [--format text|json] [--rate-limit 2.0]
```

### Arguments
- `ascent_id` (required): PeakBagger ascent ID (e.g., "12963")

### Options
- `--format`: Output format (text or json, default: text)
- `--rate-limit`: Seconds between requests (default: 2.0)

### Examples
```bash
# Text output (default)
peakbagger ascent show 12963

# JSON output
peakbagger ascent show 12963 --format json

# Custom rate limiting
peakbagger ascent show 12963 --rate-limit 5.0
```

## Data Model

Extend the existing `Ascent` model in `models.py` with optional fields for detailed ascent reports:

### New Fields
```python
# Ascent metadata
ascent_type: str | None = None       # "Successful Summit Attained", "Attempt", etc.
peak_name: str | None = None
peak_id: str | None = None
location: str | None = None          # e.g., "USA-Washington"
elevation_ft: int | None = None
elevation_m: int | None = None

# GPX-derived metrics (when available)
elevation_gain_ft: int | None = None
distance_mi: float | None = None
duration_hours: float | None = None

# Trip report content
trip_report_text: str | None = None
trip_report_url: str | None = None   # External URL if linked
```

### Design Rationale
- **Single model**: Reuses existing `Ascent` for both list and detail views
- **Optional fields**: Fields remain None when parsing ascent lists, populated for detail pages
- **Backward compatible**: Existing code continues to work unchanged
- **Consistent serialization**: Extend `to_dict()` method to include new fields

## HTML Parsing

Add `parse_ascent_detail(html: str, ascent_id: str) -> Ascent | None` to `PeakBaggerScraper` class.

### Page Structure
Based on analysis of real PeakBagger ascent pages:

1. **H1 title**: "Ascent of [Peak Name] on [Date]"
2. **H2 subtitle**: "Climber: [Name]"
3. **Left table** (class="gray", width="49%", align="left"):
   - Key-value pairs: `<tr><td><b>Label:</b></td><td>Value</td></tr>`
   - Fields: Date, Ascent Type, Peak, Location, Elevation, Route
   - GPX metrics (if available): Elevation Gain, Distance, Duration
4. **Trip Report section**: `<h2>Ascent Trip Report</h2>` followed by text
   - May include "URL Link:" with external reference

### Parsing Strategy
1. Find gray table (class="gray", width="49%", align="left")
2. Iterate through table rows, extract label/value pairs
3. Use regex for structured data (elevations: "5341 ft / 1627 m")
4. Extract trip report by finding H2 header, get subsequent text
5. Handle missing fields gracefully (return None)
6. Return None if critical fields missing (ascent_id, climber, peak)

### Error Handling
- Follow existing pattern from `parse_peak_detail()`
- Catch exceptions, log without crashing
- Return None for unparseable pages

## Output Formatting

Add `format_ascent_detail(ascent: Ascent, output_format: str)` to `PeakFormatter` class.

### Text Output
Rich table with two columns (Field | Value):

```
┌─────────────────┬────────────────────────────────────┐
│ Field           │ Value                              │
├─────────────────┼────────────────────────────────────┤
│ Ascent ID       │ 12963                              │
│ Climber         │ Bob Bolton                         │
│ Date            │ 1951                               │
│ Ascent Type     │ Successful Summit Attained         │
│ Peak            │ Mount Pilchuck (1798)              │
│ Location        │ USA-Washington                     │
│ Elevation       │ 5,341 ft (1,627 m)                 │
│ Route           │ Standard Route                     │
│ Elevation Gain  │ 2,300 ft (if available)            │
│ Distance        │ 5.4 mi (if available)              │
└─────────────────┴────────────────────────────────────┘

Trip Report:
─────────────────────────────────────────────────────────
[Full trip report text with proper line wrapping]
[Preserving paragraph breaks]

External Link: https://... (if present)
```

### JSON Output
Extend `Ascent.to_dict()`:

```json
{
  "ascent_id": "12963",
  "climber": {
    "name": "Bob Bolton",
    "id": "555"
  },
  "date": "1951",
  "ascent_type": "Successful Summit Attained",
  "peak": {
    "name": "Mount Pilchuck",
    "id": "1798",
    "location": "USA-Washington",
    "elevation_ft": 5341,
    "elevation_m": 1627
  },
  "route": "Standard Route",
  "gpx_metrics": {
    "elevation_gain_ft": 2300,
    "distance_mi": 5.4,
    "duration_hours": 4.5
  },
  "trip_report": {
    "has_report": true,
    "word_count": 169,
    "text": "Full trip report text...",
    "external_url": "https://..."
  },
  "url": "https://www.peakbagger.com/climber/ascent.aspx?aid=12963"
}
```

### Formatting Details
- **Numbers**: Comma-separated thousands (e.g., "5,341 ft")
- **Missing fields**: Skip rows/fields that are None
- **Trip report**: Word wrap at terminal width, preserve paragraphs
- **Colors**: Use Rich styling consistent with existing formatters

## CLI Implementation

### New Command Group
Create `ascent` command group in `cli.py`:

```python
@main.group()
def ascent() -> None:
    """Commands for working with ascents."""
    pass

@ascent.command()
@click.argument("ascent_id")
@click.option("--format", "output_format", ...)
@click.option("--rate-limit", type=float, default=2.0, ...)
def show(ascent_id: str, output_format: str, rate_limit: float) -> None:
    """Get detailed information about a specific ascent."""
    # Implementation
```

### Command Flow
1. Create `PeakBaggerClient` with rate limiting
2. Fetch ascent page: `client.get("/climber/ascent.aspx", params={"aid": ascent_id})`
3. Parse with `scraper.parse_ascent_detail(html, ascent_id)`
4. Format with `formatter.format_ascent_detail(ascent, output_format)`
5. Handle errors, close client

### Error Handling
- Invalid ascent ID (404 or parsing fails)
- Network errors (connection issues)
- Parsing failures (malformed HTML)
- Follow existing pattern from `peak show` command

## Testing

Use VCR-based tests with real PeakBagger data.

### Test Cases
1. **Full ascent with trip report** (aid=12963)
   - Has trip report (169 words)
   - Year-only date format ("1951")
   - Tests text extraction

2. **Minimal ascent** (aid=1479339)
   - No trip report
   - Basic metadata only
   - Tests graceful handling of missing fields

3. **Ascent with GPX metrics** (TBD during implementation)
   - Find real example with elevation gain/distance
   - Tests GPX metric extraction

### Test Coverage
- Parser extracts all available fields correctly
- Formatter produces valid text and JSON output
- CLI command works end-to-end with VCR cassettes
- Graceful handling of missing/malformed data

### Approach
- Record real API responses with VCR during development
- Use cassettes for repeatable tests
- No mocked data - all from actual PeakBagger pages

## Implementation Notes

### Rate Limiting
- Respect 2-second default rate limit
- Allow override with `--rate-limit` option
- Use existing `PeakBaggerClient` rate limiting

### Cloudflare
- Use existing `cloudscraper` client
- Clear User-Agent identifying the tool
- Follow existing patterns from peak commands

### Documentation Updates
After implementation:
- Update README.md with command examples
- Update CLAUDE.md with new command in development section
- Add sample output to documentation

## Dependencies

No new dependencies required. Uses existing:
- click (CLI framework)
- cloudscraper (HTTP client)
- beautifulsoup4 + lxml (HTML parsing)
- rich (terminal output)
- pydantic (data models)

## Success Criteria

1. Command successfully retrieves and displays ascent reports
2. Both text and JSON output formats work correctly
3. Parser handles various ascent page structures
4. Graceful degradation when fields are missing
5. Tests pass with real PeakBagger data
6. Rate limiting respected
7. Error handling matches existing commands
