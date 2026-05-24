# Trip Reports Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `peakbagger trip-reports <peak_id>` so callers can retrieve full
PeakBagger trip report text for a peak in one CLI invocation.

**Architecture:** Add a small trip report domain model and a focused collector
module that owns summary filtering and detail-page retrieval. Keep Click command
code thin: parse options, handle `--dump-html`, call the collector, and pass
report models to the formatter.

**Tech Stack:** Python 3.12, Click, Pydantic v2, Rich, pytest, existing PeakBagger client/scraper/statistics helpers.

---

## File Structure

- Modify `peakbagger/models.py`: add `TripReport`, a stable JSON-facing output model.
- Create `peakbagger/trip_reports.py`: add `TripReportCollector`,
  `count_report_words`, and lightweight protocols for fakeable client/scraper
  dependencies.
- Modify `peakbagger/formatters.py`: add `format_trip_reports()` and text rendering for report lists.
- Modify `peakbagger/cli.py`: add top-level `trip-reports` command.
- Create `tests/test_trip_reports.py`: unit tests for the collector, model contract, formatter, and CLI command.
- Modify `README.md`: document the new command near existing ascent commands and add a `jq` example.

## Behavioral Contract

- Command shape: `peakbagger trip-reports PEAK_ID`.
- Options:
  - `--format text|json`, default `text`.
  - `--limit INTEGER`, default `15`, minimum `1`.
  - `--min-words INTEGER`, default `1`, minimum `0`.
  - `--within PERIOD`, same semantics as existing ascent commands.
  - `--after YYYY-MM-DD`.
  - `--before YYYY-MM-DD`.
  - `--rate-limit FLOAT`, default `2.0`.
- `--within` must not be combined with `--after` or `--before`.
- `--dump-html` should print the initial `PeakAscents.aspx` HTML and exit before detail-page fetches.
- JSON output is a list of objects. Each object contains `ascent_id`, `url`,
  `climber`, `date`, `text`, `word_count`, `has_gpx`, `route`, and optional
  `external_url`.
- Filtering order: fetch ascent summaries, apply date filters, require trip
  reports, apply summary word-count filter when available, apply limit, fetch
  selected details, then verify detail text and actual word count.

### Task 1: Trip Report Model And Collector

**Files:**

- Modify: `peakbagger/models.py`
- Create: `peakbagger/trip_reports.py`
- Create: `tests/test_trip_reports.py`

- [ ] **Step 1: Write failing collector/model tests**

Create `tests/test_trip_reports.py` with this initial content:

```python
"""Tests for trip report collection and output."""

import json
from typing import Any

import pytest
from click.testing import CliRunner

from peakbagger.cli import main
from peakbagger.formatters import PeakFormatter
from peakbagger.models import Ascent, TripReport
from peakbagger.trip_reports import TripReportCollector, count_report_words


class FakeClient:
    """Fake PeakBagger client that records requested URLs."""

    def __init__(self) -> None:
        self.requests: list[tuple[str, dict[str, str] | None]] = []
        self.closed = False

    def get(self, url: str, params: dict[str, str] | None = None) -> str:
        self.requests.append((url, params))
        if "PeakAscents.aspx" in url:
            return "summary-html"
        aid = (params or {}).get("aid")
        return f"detail-html-{aid}"

    def close(self) -> None:
        self.closed = True


class FakeScraper:
    """Fake scraper with deterministic summary and detail ascents."""

    def parse_peak_ascents(self, html: str) -> list[Ascent]:
        assert html == "summary-html"
        return [
            Ascent(
                ascent_id="101",
                climber_name="Avery",
                climber_id="501",
                date="2025-07-10",
                has_gpx=True,
                has_trip_report=True,
                trip_report_words=140,
                route="South Ridge",
            ),
            Ascent(
                ascent_id="102",
                climber_name="Blair",
                climber_id="502",
                date="2024-08-01",
                has_gpx=False,
                has_trip_report=True,
                trip_report_words=25,
                route="West Ridge",
            ),
            Ascent(
                ascent_id="103",
                climber_name="Casey",
                climber_id="503",
                date="2025-06-01",
                has_gpx=False,
                has_trip_report=False,
                trip_report_words=None,
            ),
            Ascent(
                ascent_id="104",
                climber_name="Devon",
                climber_id="504",
                date="2023-01-01",
                has_gpx=False,
                has_trip_report=True,
                trip_report_words=220,
                route="Old Trail",
            ),
        ]

    def parse_ascent_detail(self, html: str, ascent_id: str) -> Ascent | None:
        details = {
            "101": Ascent(
                ascent_id="101",
                climber_name="Avery",
                climber_id="501",
                date="2025-07-10",
                has_gpx=True,
                has_trip_report=True,
                trip_report_text=" ".join(f"condition{i}" for i in range(120)),
                trip_report_url="https://example.com/avery-report",
                route="South Ridge",
            ),
            "104": Ascent(
                ascent_id="104",
                climber_name="Devon",
                climber_id="504",
                date="2023-01-01",
                has_gpx=False,
                has_trip_report=True,
                trip_report_text=" ".join(f"old{i}" for i in range(210)),
                route="Old Trail",
            ),
        }
        assert html == f"detail-html-{ascent_id}"
        return details.get(ascent_id)


def test_count_report_words_counts_peakbagger_text() -> None:
    """Word count treats normal words and contractions as words."""
    assert count_report_words("Snow was firm. Didn't use crampons.") == 6


def test_trip_report_json_contract() -> None:
    """TripReport exposes the flat automation-friendly JSON contract."""
    report = TripReport(
        ascent_id="101",
        climber_name="Avery",
        climber_id="501",
        date="2025-07-10",
        text="firm snow good steps",
        word_count=4,
        has_gpx=True,
        route="South Ridge",
        external_url="https://example.com/avery-report",
    )

    assert report.to_dict() == {
        "ascent_id": "101",
        "url": "https://www.peakbagger.com/climber/ascent.aspx?aid=101",
        "climber": {"name": "Avery", "id": "501"},
        "date": "2025-07-10",
        "text": "firm snow good steps",
        "word_count": 4,
        "has_gpx": True,
        "route": "South Ridge",
        "external_url": "https://example.com/avery-report",
    }


def test_collector_filters_before_detail_fetches() -> None:
    """Collector applies summary filters before fetching detail pages."""
    client = FakeClient()
    scraper = FakeScraper()
    collector = TripReportCollector(client, scraper)

    reports = collector.collect(
        peak_id="1798",
        limit=2,
        min_words=100,
        after="2025-01-01",
        before=None,
        within=None,
    )

    assert [report.ascent_id for report in reports] == ["101"]
    assert reports[0].word_count == 120
    assert reports[0].has_gpx is True
    assert reports[0].external_url == "https://example.com/avery-report"
    assert client.requests == [
        (
            "/climber/PeakAscents.aspx",
            {"pid": "1798", "sort": "ascentdate", "u": "ft", "y": "9999"},
        ),
        ("/climber/ascent.aspx", {"aid": "101"}),
    ]


def test_collector_rejects_conflicting_date_filters() -> None:
    """Relative and absolute date filters are mutually exclusive."""
    collector = TripReportCollector(FakeClient(), FakeScraper())

    with pytest.raises(ValueError, match="--within cannot be combined"):
        collector.collect(
            peak_id="1798",
            limit=15,
            min_words=1,
            after="2025-01-01",
            before=None,
            within="1y",
        )
```

- [ ] **Step 2: Run the new tests and verify they fail**

Run:

```bash
uv run pytest tests/test_trip_reports.py -v
```

Expected: FAIL during import because `TripReport` and `peakbagger.trip_reports` do not exist yet.

- [ ] **Step 3: Add the `TripReport` model**

In `peakbagger/models.py`, add this class after `Ascent` and before `AscentStatistics`:

```python
class TripReport(BaseModel):
    """Detailed trip report output for one ascent."""

    ascent_id: str = Field(description="Ascent ID")
    climber_name: str = Field(description="Name of climber")
    climber_id: str | None = Field(None, description="Climber ID")
    date: str | None = Field(None, description="Ascent date")
    text: str = Field(description="Full trip report text")
    word_count: int = Field(description="Number of words in trip report text")
    has_gpx: bool = Field(False, description="Whether ascent has a GPX track")
    route: str | None = Field(None, description="Route name")
    external_url: str | None = Field(None, description="External trip report URL")

    @property
    def url(self) -> str:
        """Return the PeakBagger ascent URL."""
        return f"https://www.peakbagger.com/climber/ascent.aspx?aid={self.ascent_id}"

    def to_dict(self) -> dict[str, Any]:
        """Convert trip report to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "ascent_id": self.ascent_id,
            "url": self.url,
            "climber": {
                "name": self.climber_name,
                "id": self.climber_id,
            },
            "date": self.date,
            "text": self.text,
            "word_count": self.word_count,
            "has_gpx": self.has_gpx,
            "route": self.route,
        }
        if self.external_url:
            result["external_url"] = self.external_url
        return result
```

- [ ] **Step 4: Add the collector module**

Create `peakbagger/trip_reports.py` with:

```python
"""Trip report collection for peak ascents."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Protocol

from peakbagger.models import Ascent, TripReport
from peakbagger.statistics import AscentAnalyzer


class TripReportClient(Protocol):
    """Client interface needed by TripReportCollector."""

    def get(self, url: str, params: dict[str, str] | None = None) -> str:
        """Fetch a URL and return HTML."""
        ...


class TripReportScraper(Protocol):
    """Scraper interface needed by TripReportCollector."""

    def parse_peak_ascents(self, html: str) -> list[Ascent]:
        """Parse ascent summaries from a peak ascent list page."""
        ...

    def parse_ascent_detail(self, html: str, ascent_id: str) -> Ascent | None:
        """Parse a detailed ascent page."""
        ...


def count_report_words(text: str) -> int:
    """Count words in PeakBagger trip report text."""
    return len(re.findall(r"\\b[\\w'-]+\\b", text))


class TripReportCollector:
    """Collect detailed trip reports for a peak."""

    def __init__(self, client: TripReportClient, scraper: TripReportScraper) -> None:
        """Initialize the collector with HTTP and parsing dependencies."""
        self.client = client
        self.scraper = scraper
        self.analyzer = AscentAnalyzer()

    def fetch_summary_html(self, peak_id: str) -> str:
        """Fetch the peak ascent summary page for a peak."""
        return self.client.get(
            "/climber/PeakAscents.aspx",
            params={"pid": peak_id, "sort": "ascentdate", "u": "ft", "y": "9999"},
        )

    def collect(
        self,
        *,
        peak_id: str,
        limit: int,
        min_words: int,
        within: str | None,
        after: str | None,
        before: str | None,
    ) -> list[TripReport]:
        """Collect filtered trip reports for a peak."""
        summary_html = self.fetch_summary_html(peak_id)
        summaries = self.scraper.parse_peak_ascents(summary_html)
        candidates = self._filter_summaries(
            summaries=summaries,
            min_words=min_words,
            within=within,
            after=after,
            before=before,
        )[:limit]

        reports: list[TripReport] = []
        for summary in candidates:
            detail_html = self.client.get("/climber/ascent.aspx", params={"aid": summary.ascent_id})
            detail = self.scraper.parse_ascent_detail(detail_html, summary.ascent_id)
            if detail is None or not detail.trip_report_text:
                continue
            report = self._build_report(detail=detail, summary=summary)
            if report.word_count >= min_words:
                reports.append(report)
        return reports

    def _filter_summaries(
        self,
        *,
        summaries: list[Ascent],
        min_words: int,
        within: str | None,
        after: str | None,
        before: str | None,
    ) -> list[Ascent]:
        """Filter summaries before detail-page fetches."""
        filtered = self._apply_date_filters(summaries, within=within, after=after, before=before)
        reports = [ascent for ascent in filtered if ascent.has_trip_report]
        return [
            ascent
            for ascent in reports
            if ascent.trip_report_words is None or ascent.trip_report_words >= min_words
        ]

    def _apply_date_filters(
        self,
        summaries: list[Ascent],
        *,
        within: str | None,
        after: str | None,
        before: str | None,
    ) -> list[Ascent]:
        """Apply relative or absolute date filters to ascent summaries."""
        if within and (after or before):
            raise ValueError("--within cannot be combined with --after/--before")

        if within:
            period = self.analyzer.parse_within_period(within)
            return self.analyzer.filter_by_date_range(
                summaries,
                after=datetime.now() - period,
            )

        after_date = self._parse_filter_date(after, "--after") if after else None
        before_date = self._parse_filter_date(before, "--before") if before else None
        if after_date or before_date:
            return self.analyzer.filter_by_date_range(
                summaries,
                after=after_date,
                before=before_date,
            )
        return summaries

    @staticmethod
    def _parse_filter_date(value: str | None, option_name: str) -> datetime | None:
        """Parse a YYYY-MM-DD filter date."""
        if value is None:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid {option_name} date format: {value}. Expected YYYY-MM-DD") from e

    @staticmethod
    def _build_report(*, detail: Ascent, summary: Ascent) -> TripReport:
        """Build a TripReport from detail data with summary fallbacks."""
        text = detail.trip_report_text or ""
        return TripReport(
            ascent_id=detail.ascent_id,
            climber_name=detail.climber_name,
            climber_id=detail.climber_id,
            date=detail.date or summary.date,
            text=text,
            word_count=count_report_words(text),
            has_gpx=detail.has_gpx or summary.has_gpx,
            route=detail.route or summary.route,
            external_url=detail.trip_report_url,
        )
```

- [ ] **Step 5: Run the task tests and verify they pass**

Run:

```bash
uv run pytest tests/test_trip_reports.py -v
```

Expected: PASS for the four tests added in Step 1.

- [ ] **Step 6: Run focused style checks**

Run:

```bash
uv run ruff check peakbagger/models.py peakbagger/trip_reports.py tests/test_trip_reports.py
uv run ruff format --check peakbagger/models.py peakbagger/trip_reports.py tests/test_trip_reports.py
```

Expected: PASS. If format fails, run:

```bash
uv run ruff format peakbagger/models.py peakbagger/trip_reports.py tests/test_trip_reports.py
```

Then rerun the two checks.

### Task 2: CLI, Formatter, Documentation, And Integration Tests

**Files:**

- Modify: `peakbagger/cli.py`
- Modify: `peakbagger/formatters.py`
- Modify: `README.md`
- Modify: `tests/test_trip_reports.py`

- [ ] **Step 1: Add failing CLI and formatter tests**

Append this content to `tests/test_trip_reports.py`:

```python
class StubTripReportCollector:
    """Stub collector for CLI tests."""

    last_instance: "StubTripReportCollector | None" = None

    def __init__(self, client: Any, scraper: Any) -> None:
        self.client = client
        self.scraper = scraper
        self.collect_calls: list[dict[str, Any]] = []
        StubTripReportCollector.last_instance = self

    def fetch_summary_html(self, peak_id: str) -> str:
        return f"<html>summary for {peak_id}</html>"

    def collect(
        self,
        *,
        peak_id: str,
        limit: int,
        min_words: int,
        within: str | None,
        after: str | None,
        before: str | None,
    ) -> list[TripReport]:
        self.collect_calls.append(
            {
                "peak_id": peak_id,
                "limit": limit,
                "min_words": min_words,
                "within": within,
                "after": after,
                "before": before,
            }
        )
        return [
            TripReport(
                ascent_id="101",
                climber_name="Avery",
                climber_id="501",
                date="2025-07-10",
                text="firm snow good steps",
                word_count=4,
                has_gpx=True,
                route="South Ridge",
            )
        ]


class StubClient:
    """Stub client for CLI tests."""

    def __init__(self, rate_limit_seconds: float) -> None:
        self.rate_limit_seconds = rate_limit_seconds
        self.closed = False

    def close(self) -> None:
        self.closed = True


class StubScraper:
    """Stub scraper for CLI tests."""


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Click CLI test runner."""
    return CliRunner(env={"COLUMNS": "200"})


def test_formatter_prints_trip_reports_as_json(capsys: pytest.CaptureFixture[str]) -> None:
    """Formatter emits valid JSON for trip report lists."""
    formatter = PeakFormatter()
    formatter.format_trip_reports(
        [
            TripReport(
                ascent_id="101",
                climber_name="Avery",
                climber_id="501",
                date="2025-07-10",
                text="firm snow good steps",
                word_count=4,
                has_gpx=True,
                route="South Ridge",
            )
        ],
        "json",
    )

    data = json.loads(capsys.readouterr().out)
    assert data == [
        {
            "ascent_id": "101",
            "url": "https://www.peakbagger.com/climber/ascent.aspx?aid=101",
            "climber": {"name": "Avery", "id": "501"},
            "date": "2025-07-10",
            "text": "firm snow good steps",
            "word_count": 4,
            "has_gpx": True,
            "route": "South Ridge",
        }
    ]


def test_formatter_prints_trip_reports_as_text(capsys: pytest.CaptureFixture[str]) -> None:
    """Formatter text output includes metadata and full report text."""
    formatter = PeakFormatter()
    formatter.format_trip_reports(
        [
            TripReport(
                ascent_id="101",
                climber_name="Avery",
                climber_id="501",
                date="2025-07-10",
                text="firm snow good steps",
                word_count=4,
                has_gpx=True,
                route="South Ridge",
            )
        ],
        "text",
    )

    output = capsys.readouterr().out
    assert "Trip Reports (1)" in output
    assert "Avery" in output
    assert "firm snow good steps" in output
    assert "https://www.peakbagger.com/climber/ascent.aspx?aid=101" in output


def test_trip_reports_command_outputs_json(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CLI wires options into the collector and emits JSON."""
    monkeypatch.setattr("peakbagger.cli.PeakBaggerClient", StubClient)
    monkeypatch.setattr("peakbagger.cli.PeakBaggerScraper", StubScraper)
    monkeypatch.setattr("peakbagger.cli.TripReportCollector", StubTripReportCollector)

    result = cli_runner.invoke(
        main,
        [
            "trip-reports",
            "1798",
            "--limit",
            "5",
            "--min-words",
            "3",
            "--after",
            "2025-01-01",
            "--format",
            "json",
            "--rate-limit",
            "0",
        ],
    )

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["ascent_id"] == "101"
    assert StubTripReportCollector.last_instance is not None
    assert StubTripReportCollector.last_instance.collect_calls == [
        {
            "peak_id": "1798",
            "limit": 5,
            "min_words": 3,
            "within": None,
            "after": "2025-01-01",
            "before": None,
        }
    ]
    assert StubTripReportCollector.last_instance.client.closed is True


def test_trip_reports_command_dump_html(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Global --dump-html prints the summary page and skips collection."""
    monkeypatch.setattr("peakbagger.cli.PeakBaggerClient", StubClient)
    monkeypatch.setattr("peakbagger.cli.PeakBaggerScraper", StubScraper)
    monkeypatch.setattr("peakbagger.cli.TripReportCollector", StubTripReportCollector)

    result = cli_runner.invoke(main, ["--dump-html", "trip-reports", "1798"])

    assert result.exit_code == 0
    assert result.output == "<html>summary for 1798</html>\n"
    assert StubTripReportCollector.last_instance is not None
    assert StubTripReportCollector.last_instance.collect_calls == []
```

- [ ] **Step 2: Run the expanded tests and verify they fail**

Run:

```bash
uv run pytest tests/test_trip_reports.py -v
```

Expected: FAIL because `PeakFormatter.format_trip_reports` and
`peakbagger.cli.TripReportCollector` are not implemented yet.

- [ ] **Step 3: Add formatter support**

In `peakbagger/formatters.py`:

1. Change the import to include `TripReport`:

```python
from peakbagger.models import Ascent, AscentStatistics, Peak, SearchResult, TripReport
```

1. Add this public method near the other `format_*` methods:

```python
    def format_trip_reports(
        self,
        reports: list[TripReport],
        output_format: str = "text",
    ) -> None:
        """
        Format and print detailed trip reports.

        Args:
            reports: List of trip reports.
            output_format: Either 'text' or 'json'.
        """
        if output_format == "json":
            self._print_json([report.to_dict() for report in reports])
        else:
            self._print_trip_reports(reports)
```

1. Add this private text renderer before `format_ascent_detail()`:

```python
    def _print_trip_reports(self, reports: list[TripReport]) -> None:
        """Print detailed trip reports as readable text."""
        if not reports:
            self.console.print("[yellow]No trip reports found.[/yellow]")
            return

        self.console.print(f"\\n[bold cyan]Trip Reports ({len(reports)})[/bold cyan]\\n")
        for index, report in enumerate(reports, 1):
            metadata = Table(show_header=False, box=None, padding=(0, 2))
            metadata.add_column("Field", style="cyan", width=14, no_wrap=True)
            metadata.add_column("Value", style="white", no_wrap=True)
            metadata.add_row("Ascent ID", f"{report.ascent_id} [blue not underline]{report.url}[/blue not underline]")
            metadata.add_row("Climber", report.climber_name)
            if report.date:
                metadata.add_row("Date", report.date)
            metadata.add_row("Words", f"{report.word_count:,}")
            metadata.add_row("Has GPX", "Yes" if report.has_gpx else "No")
            if report.route:
                metadata.add_row("Route", report.route)
            if report.external_url:
                metadata.add_row("External URL", report.external_url)

            self.console.print(f"[bold yellow]Report {index}[/bold yellow]")
            self.console.print(metadata)
            self.console.print(Text(report.text))
            if index != len(reports):
                self.console.print("\\n" + "-" * 80 + "\\n")
```

- [ ] **Step 4: Add CLI command**

In `peakbagger/cli.py`:

1. Add this import near the other project imports:

```python
from peakbagger.trip_reports import TripReportCollector
```

1. Add this command after the `ascent()` group definition and before
   `@peak.command()`:

```python
@main.command("trip-reports")
@click.argument("peak_id")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format (text or json)",
)
@click.option(
    "--limit",
    type=click.IntRange(min=1),
    default=15,
    help="Maximum number of trip reports to fetch (default: 15)",
)
@click.option(
    "--min-words",
    type=click.IntRange(min=0),
    default=1,
    help="Minimum trip report word count (default: 1)",
)
@click.option(
    "--after",
    type=str,
    help="Include only ascents on or after this date (YYYY-MM-DD)",
)
@click.option(
    "--before",
    type=str,
    help="Include only ascents on or before this date (YYYY-MM-DD)",
)
@click.option(
    "--within",
    type=str,
    help="Include only ascents within period from today (e.g., '3m', '1y', '10d')",
)
@click.option(
    "--rate-limit",
    type=float,
    default=2.0,
    help="Seconds between requests (default: 2.0)",
)
@click.pass_context
def trip_reports(
    ctx: click.Context,
    peak_id: str,
    output_format: str,
    limit: int,
    min_words: int,
    after: str | None,
    before: str | None,
    within: str | None,
    rate_limit: float,
) -> None:
    """
    Get detailed trip reports for a specific peak.

    PEAK_ID: The PeakBagger peak ID (e.g., "1798" for Mount Pilchuck)

    Examples:

      peakbagger trip-reports 1798

      peakbagger trip-reports 1798 --limit 15 --min-words 100 --within 2y

      peakbagger trip-reports 1798 --format json
    """
    client: PeakBaggerClient = PeakBaggerClient(rate_limit_seconds=rate_limit)
    scraper: PeakBaggerScraper = PeakBaggerScraper()
    formatter: PeakFormatter = PeakFormatter()
    collector = TripReportCollector(client, scraper)

    try:
        if ctx.obj.get("dump_html"):
            click.echo(collector.fetch_summary_html(peak_id))
            return

        reports = collector.collect(
            peak_id=peak_id,
            limit=limit,
            min_words=min_words,
            within=within,
            after=after,
            before=before,
        )
        formatter.format_trip_reports(reports, output_format)
    except Exception as e:
        _error(str(e))
        raise click.Abort() from e
    finally:
        client.close()
```

- [ ] **Step 5: Update README usage docs**

In `README.md`, after the "Get ascent details" section, add:

````markdown
### Get trip reports for a peak

```bash
peakbagger trip-reports 1798
peakbagger trip-reports 1798 --limit 15 --min-words 100 --within 2y
peakbagger trip-reports 1798 --format json
```

Returns full trip report text for matching ascents, including ascent ID, URL,
climber, date, word count, GPX availability, route, and external trip report
links when available. Filters are applied before fetching detail pages where the
ascent summary includes enough information.

````

In the "Automation with jq" section, add:

```markdown
peakbagger trip-reports 1798 --format json | jq '.[].text'
```

- [ ] **Step 6: Run the expanded trip report tests**

Run:

```bash
uv run pytest tests/test_trip_reports.py -v
```

Expected: PASS.

- [ ] **Step 7: Run CLI help smoke checks**

Run:

```bash
uv run peakbagger trip-reports --help
uv run peakbagger --dump-html trip-reports 1798 --rate-limit 0
```

Expected:

- Help output includes `--min-words`, `--within`, and `--format`.
- Dump HTML command exits 0 and prints HTML from the ascent summary page. If the
  live site blocks or network is unavailable, record the failure and rely on the
  unit test for this behavior.

- [ ] **Step 8: Run focused and full validation**

Run:

```bash
uv run ruff format peakbagger tests
uv run ruff check peakbagger tests
uv run ty check
uv run pytest
```

Expected: PASS.

## Self-Review

- Spec coverage: The plan covers top-level command shape, JSON and text output,
  summary filtering, date filters, word-count filters, rate limiting reuse, dump
  HTML behavior, README docs, and preservation of existing commands.
- Placeholder scan: No unresolved placeholder markers or unspecified test-writing steps remain.
- Type consistency: `TripReport`, `TripReportCollector`, `count_report_words`,
  `format_trip_reports`, and `trip_reports` names are used consistently across
  model, service, formatter, CLI, and tests.
