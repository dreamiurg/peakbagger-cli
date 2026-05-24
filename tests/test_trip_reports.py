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


class DetailValidationScraper:
    """Fake scraper with early detail failures before a valid report."""

    def parse_peak_ascents(self, html: str) -> list[Ascent]:
        assert html == "summary-html"
        return [
            Ascent(
                ascent_id="201",
                climber_name="Emery",
                date="2025-08-01",
                has_trip_report=True,
                trip_report_words=50,
            ),
            Ascent(
                ascent_id="202",
                climber_name="Finley",
                date="2025-08-02",
                has_trip_report=True,
                trip_report_words=50,
            ),
            Ascent(
                ascent_id="203",
                climber_name="Gray",
                date="2025-08-03",
                has_trip_report=True,
                trip_report_words=50,
            ),
            Ascent(
                ascent_id="204",
                climber_name="Harper",
                date="2025-08-04",
                has_trip_report=True,
                trip_report_words=50,
            ),
        ]

    def parse_ascent_detail(self, html: str, ascent_id: str) -> Ascent | None:
        details = {
            "201": Ascent(
                ascent_id="201",
                climber_name="Emery",
                date="2025-08-01",
                has_trip_report=True,
                trip_report_text="   \n\t   ",
            ),
            "202": Ascent(
                ascent_id="202",
                climber_name="Finley",
                date="2025-08-02",
                has_trip_report=True,
                trip_report_text="too short",
            ),
            "204": Ascent(
                ascent_id="204",
                climber_name="Harper",
                date="2025-08-04",
                has_trip_report=True,
                trip_report_text="  " + " ".join(f"valid{i}" for i in range(12)) + "  ",
            ),
        }
        assert html == f"detail-html-{ascent_id}"
        return details.get(ascent_id)


class StubTripReportCollector:
    """Stub collector for CLI tests."""

    last_instance: "StubTripReportCollector | None" = None

    def __init__(self, client: Any, scraper: Any) -> None:
        self.client = client
        self.scraper = scraper
        self.fetch_calls: list[str] = []
        self.collect_calls: list[dict[str, Any]] = []
        StubTripReportCollector.last_instance = self

    def fetch_summary_html(self, peak_id: str) -> str:
        self.fetch_calls.append(peak_id)
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


class TrackingClient(StubClient):
    """Stub client that keeps the most recent instance for failure-path checks."""

    last_instance: "TrackingClient | None" = None

    def __init__(self, rate_limit_seconds: float) -> None:
        super().__init__(rate_limit_seconds)
        TrackingClient.last_instance = self


class RaisingScraper:
    """Scraper stub that fails during construction."""

    def __init__(self) -> None:
        raise RuntimeError("scraper construction failed")


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Click CLI test runner."""
    StubTripReportCollector.last_instance = None
    TrackingClient.last_instance = None
    return CliRunner(env={"COLUMNS": "200"})


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


def test_collector_limit_counts_returned_reports_after_detail_validation() -> None:
    """Collector keeps fetching candidates until it returns the requested reports."""
    client = FakeClient()
    collector = TripReportCollector(client, DetailValidationScraper())

    reports = collector.collect(
        peak_id="1798",
        limit=1,
        min_words=10,
        after="2025-01-01",
        before=None,
        within=None,
    )

    assert [report.ascent_id for report in reports] == ["204"]
    assert reports[0].text == " ".join(f"valid{i}" for i in range(12))
    assert reports[0].word_count == 12
    assert client.requests == [
        (
            "/climber/PeakAscents.aspx",
            {"pid": "1798", "sort": "ascentdate", "u": "ft", "y": "9999"},
        ),
        ("/climber/ascent.aspx", {"aid": "201"}),
        ("/climber/ascent.aspx", {"aid": "202"}),
        ("/climber/ascent.aspx", {"aid": "203"}),
        ("/climber/ascent.aspx", {"aid": "204"}),
    ]


def test_collector_rejects_conflicting_date_filters() -> None:
    """Relative and absolute date filters are mutually exclusive."""
    client = FakeClient()
    collector = TripReportCollector(client, FakeScraper())

    with pytest.raises(ValueError, match="--within cannot be combined"):
        collector.collect(
            peak_id="1798",
            limit=15,
            min_words=1,
            after="2025-01-01",
            before=None,
            within="1y",
        )
    assert client.requests == []


@pytest.mark.parametrize(
    ("option_name", "filters"),
    [
        ("--after", {"after": "not-a-date", "before": None, "within": None}),
        ("--before", {"after": None, "before": "not-a-date", "within": None}),
    ],
)
def test_collector_rejects_invalid_absolute_date_filters_before_fetch(
    option_name: str,
    filters: dict[str, str | None],
) -> None:
    """Collector validates absolute date filters before network requests."""
    client = FakeClient()
    collector = TripReportCollector(client, FakeScraper())

    with pytest.raises(ValueError, match=f"Invalid {option_name} date format"):
        collector.collect(
            peak_id="1798",
            limit=15,
            min_words=1,
            **filters,
        )
    assert client.requests == []


def test_collector_rejects_invalid_within_filter_before_fetch() -> None:
    """Collector validates relative date filters before network requests."""
    client = FakeClient()
    collector = TripReportCollector(client, FakeScraper())

    with pytest.raises(ValueError, match="Invalid period format"):
        collector.collect(
            peak_id="1798",
            limit=15,
            min_words=1,
            after=None,
            before=None,
            within="later",
        )
    assert client.requests == []


def test_formatter_prints_trip_reports_as_json(
    capsys: pytest.CaptureFixture[str],
) -> None:
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


def test_formatter_prints_trip_reports_as_text(
    capsys: pytest.CaptureFixture[str],
) -> None:
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


def test_formatter_separates_equal_trip_reports(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Formatter prints a separator between equal report objects."""
    formatter = PeakFormatter()
    report = TripReport(
        ascent_id="101",
        climber_name="Avery",
        climber_id="501",
        date="2025-07-10",
        text="firm snow good steps",
        word_count=4,
        has_gpx=True,
        route="South Ridge",
    )

    formatter.format_trip_reports([report, report.model_copy()], "text")

    output = capsys.readouterr().out
    assert output.count("-" * 80) == 1
    assert "Trip Reports (2)" in output


def test_formatter_prints_empty_trip_reports_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Formatter text output clearly reports empty trip report results."""
    formatter = PeakFormatter()
    formatter.format_trip_reports([], "text")

    assert "No trip reports found." in capsys.readouterr().out


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
    assert StubTripReportCollector.last_instance.fetch_calls == ["1798"]
    assert StubTripReportCollector.last_instance.collect_calls == []


def test_trip_reports_command_rejects_zero_limit(cli_runner: CliRunner) -> None:
    """Click rejects zero limits before the collector is called."""
    result = cli_runner.invoke(main, ["trip-reports", "1798", "--limit", "0"])

    assert result.exit_code != 0
    assert "Invalid value for '--limit'" in result.output


def test_trip_reports_command_rejects_conflicting_date_filters_before_collector(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Click rejects conflicting date filters before collector work starts."""
    monkeypatch.setattr("peakbagger.cli.PeakBaggerClient", StubClient)
    monkeypatch.setattr("peakbagger.cli.PeakBaggerScraper", StubScraper)
    monkeypatch.setattr("peakbagger.cli.TripReportCollector", StubTripReportCollector)

    result = cli_runner.invoke(
        main,
        ["trip-reports", "1798", "--within", "1y", "--after", "2025-01-01"],
    )

    assert result.exit_code != 0
    assert "--within cannot be combined with --after/--before" in result.output
    assert StubTripReportCollector.last_instance is None


def test_trip_reports_command_rejects_invalid_within_before_collector(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Click rejects invalid relative periods before collector work starts."""
    monkeypatch.setattr("peakbagger.cli.PeakBaggerClient", StubClient)
    monkeypatch.setattr("peakbagger.cli.PeakBaggerScraper", StubScraper)
    monkeypatch.setattr("peakbagger.cli.TripReportCollector", StubTripReportCollector)

    result = cli_runner.invoke(main, ["trip-reports", "1798", "--within", "nope"])

    assert result.exit_code != 0
    assert "Invalid period format" in result.output
    assert StubTripReportCollector.last_instance is None


@pytest.mark.parametrize("option", ["--after", "--before"])
def test_trip_reports_command_rejects_invalid_date_before_collector(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    option: str,
) -> None:
    """Click rejects invalid absolute dates before collector work starts."""
    monkeypatch.setattr("peakbagger.cli.PeakBaggerClient", StubClient)
    monkeypatch.setattr("peakbagger.cli.PeakBaggerScraper", StubScraper)
    monkeypatch.setattr("peakbagger.cli.TripReportCollector", StubTripReportCollector)

    result = cli_runner.invoke(main, ["trip-reports", "1798", option, "bad"])

    assert result.exit_code != 0
    assert f"{option} must be a date in YYYY-MM-DD format" in result.output
    assert StubTripReportCollector.last_instance is None


def test_trip_reports_command_closes_client_when_scraper_construction_fails(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Client is closed when construction fails after client creation."""
    monkeypatch.setattr("peakbagger.cli.PeakBaggerClient", TrackingClient)
    monkeypatch.setattr("peakbagger.cli.PeakBaggerScraper", RaisingScraper)
    monkeypatch.setattr("peakbagger.cli.TripReportCollector", StubTripReportCollector)

    result = cli_runner.invoke(main, ["trip-reports", "1798"])

    assert result.exit_code != 0
    assert TrackingClient.last_instance is not None
    assert TrackingClient.last_instance.closed is True
    assert StubTripReportCollector.last_instance is None


def test_trip_reports_command_rejects_negative_rate_limit(cli_runner: CliRunner) -> None:
    """Click rejects negative rate limits before the command body runs."""
    result = cli_runner.invoke(main, ["trip-reports", "1798", "--rate-limit", "-0.1"])

    assert result.exit_code != 0
    assert "Invalid value for '--rate-limit'" in result.output
