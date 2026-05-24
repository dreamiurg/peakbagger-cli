"""Tests for trip report collection and output."""

import pytest

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
