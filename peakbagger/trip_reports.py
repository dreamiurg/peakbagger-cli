"""Trip report collection for peak ascents."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, TypedDict, Unpack

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


class _CollectOptions(TypedDict):
    limit: int
    min_words: int
    within: str | None
    after: str | None
    before: str | None


@dataclass(frozen=True)
class _TripReportFilters:
    limit: int
    min_words: int
    within: str | None
    after: str | None
    before: str | None


def count_report_words(text: str) -> int:
    """Count words in PeakBagger trip report text."""
    return len(re.findall(r"\b[\w'-]+\b", text))


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
        **options: Unpack[_CollectOptions],
    ) -> list[TripReport]:
        """Collect filtered trip reports for a peak."""
        filters = _TripReportFilters(**options)
        self._validate_filters(filters)
        summary_html = self.fetch_summary_html(peak_id)
        summaries = self.scraper.parse_peak_ascents(summary_html)
        candidates = self._filter_summaries(
            summaries=summaries,
            filters=filters,
        )

        reports: list[TripReport] = []
        for summary in candidates:
            if len(reports) == filters.limit:
                break
            detail_html = self.client.get("/climber/ascent.aspx", params={"aid": summary.ascent_id})
            detail = self.scraper.parse_ascent_detail(detail_html, summary.ascent_id)
            if detail is None or not detail.trip_report_text:
                continue
            text = detail.trip_report_text.strip()
            if not text:
                continue
            report = self._build_report(detail=detail, summary=summary, text=text)
            if report.word_count >= filters.min_words:
                reports.append(report)
        return reports

    def _filter_summaries(
        self,
        *,
        summaries: list[Ascent],
        filters: _TripReportFilters,
    ) -> list[Ascent]:
        """Filter summaries before detail-page fetches."""
        filtered = self._apply_date_filters(summaries, filters=filters)
        reports = [ascent for ascent in filtered if ascent.has_trip_report]
        return [
            ascent
            for ascent in reports
            if ascent.trip_report_words is None or ascent.trip_report_words >= filters.min_words
        ]

    def _validate_filters(self, filters: _TripReportFilters) -> None:
        """Validate filter options before any network work."""
        if filters.limit < 1:
            raise ValueError("limit must be at least 1")
        if filters.min_words < 0:
            raise ValueError("min_words must be non-negative")
        if filters.within and (filters.after or filters.before):
            raise ValueError("--within cannot be combined with --after/--before")
        if filters.within:
            self.analyzer.parse_within_period(filters.within)
        if filters.after:
            self._parse_filter_date(filters.after, "--after")
        if filters.before:
            self._parse_filter_date(filters.before, "--before")

    def _apply_date_filters(
        self,
        summaries: list[Ascent],
        *,
        filters: _TripReportFilters,
    ) -> list[Ascent]:
        """Apply relative or absolute date filters to ascent summaries."""
        if filters.within:
            period = self.analyzer.parse_within_period(filters.within)
            return self.analyzer.filter_by_date_range(
                summaries,
                after=datetime.now() - period,
            )

        after_date = self._parse_filter_date(filters.after, "--after") if filters.after else None
        before_date = (
            self._parse_filter_date(filters.before, "--before") if filters.before else None
        )
        if after_date or before_date:
            return self.analyzer.filter_by_date_range(
                summaries,
                after=after_date,
                before=before_date,
            )
        return summaries

    @staticmethod
    def _parse_filter_date(value: str, option_name: str) -> datetime:
        """Parse a YYYY-MM-DD filter date."""
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(
                f"Invalid {option_name} date format: {value}. Expected YYYY-MM-DD"
            ) from e

    @staticmethod
    def _build_report(*, detail: Ascent, summary: Ascent, text: str) -> TripReport:
        """Build a TripReport from detail data with summary fallbacks."""
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
