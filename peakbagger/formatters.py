"""Output formatters for peak data (Rich tables and JSON)."""

import json
from datetime import datetime
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.text import Text

from peakbagger.models import Ascent, AscentStatistics, Peak, SearchResult


def _strip_emojis(text: str) -> str:
    """Remove emoji characters from text for clean table display."""
    import unicodedata

    return "".join(c for c in text if unicodedata.category(c) not in ("So", "Sk")).strip()


class PeakFormatter:
    """Formatter for peak data output."""

    def __init__(self) -> None:
        # Use a very wide console to prevent any text truncation
        # Tables will extend beyond terminal width if needed
        self.console: Console = Console(width=500)

    def _parse_date_for_sort(self, ascent: Ascent) -> datetime:
        """Return date for sorting. None/invalid dates sort to the end.

        Args:
            ascent: Ascent object to extract date from

        Returns:
            datetime object for sorting, or datetime.min for invalid/missing dates
        """

        if not ascent.date:
            return datetime.min
        try:
            date_parts = ascent.date.split("-")
            if len(date_parts) == 3:
                return datetime.strptime(ascent.date, "%Y-%m-%d")
            elif len(date_parts) == 2:
                return datetime.strptime(ascent.date, "%Y-%m")
            elif len(date_parts) == 1:
                return datetime.strptime(ascent.date, "%Y")
            else:
                return datetime.min
        except ValueError:
            return datetime.min

    def format_search_results(
        self, results: list[SearchResult], output_format: str = "text"
    ) -> None:
        """
        Format and print search results.

        Args:
            results: List of SearchResult objects
            output_format: Either 'text' or 'json'
        """
        if output_format == "json":
            self._print_json([r.to_dict() for r in results])
        else:
            self._print_search_table(results)

    def format_peak_detail(self, peak: Peak, output_format: str = "text") -> None:
        """
        Format and print detailed peak information.

        Args:
            peak: Peak object
            output_format: Either 'text' or 'json'
        """
        if output_format == "json":
            self._print_json(peak.to_dict())
        else:
            self._print_peak_detail(peak)

    def format_peaks(self, peaks: list[Peak], output_format: str = "text") -> None:
        """
        Format and print multiple peaks with full details.

        Args:
            peaks: List of Peak objects
            output_format: Either 'text' or 'json'
        """
        if output_format == "json":
            self._print_json([p.to_dict() for p in peaks])
        else:
            for peak in peaks:
                self._print_peak_detail(peak)
                if peak != peaks[-1]:  # Add separator between peaks
                    self.console.print("\n" + "─" * 80 + "\n")

    def _print_json(self, data: dict[str, Any] | list[dict[str, Any]]) -> None:
        """Print data as formatted JSON.

        Uses plain print() instead of console.print() to avoid Rich processing
        escape sequences in the JSON, which would make it invalid.
        """
        # This is intentional CLI output, not logging. The tool only handles public
        # peak data from PeakBagger.com - no credentials or sensitive information.
        print(json.dumps(data, indent=2, ensure_ascii=False))

    def _print_search_table(self, results: list[SearchResult]) -> None:
        """Print search results as a Rich table."""
        if not results:
            self.console.print("[yellow]No results found.[/yellow]")
            return

        table: Table = Table(
            title="Search Results", show_header=True, header_style="bold cyan", box=None
        )
        table.add_column("Peak ID", style="dim", no_wrap=True)
        table.add_column("Name", style="green", no_wrap=True)
        table.add_column("Location", style="cyan", no_wrap=True)
        table.add_column("Range", style="magenta", no_wrap=True)
        table.add_column("Elevation", style="yellow", no_wrap=True)
        table.add_column("URL", style="blue not underline", no_wrap=True)

        for result in results:
            # Format location
            location: str = result.location if result.location else "-"

            # Format range
            range_name: str = result.range if result.range else "-"

            # Format elevation (ft/m)
            elevation: str = "-"
            if result.elevation_ft:
                elevation = f"{result.elevation_ft:,} ft"
                if result.elevation_m:
                    elevation += f" / {result.elevation_m:,} m"

            # Format URL
            url: str = f"https://www.peakbagger.com/{result.url}"

            table.add_row(result.pid, result.name, location, range_name, elevation, url)

        self.console.print(table)

    def _build_peak_details_table(self, peak: Peak) -> Table:
        """Build a Rich table with peak metric rows."""
        table: Table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Field", style="yellow", width=20, no_wrap=True)
        table.add_column("Value", style="white", no_wrap=True)

        if peak.elevation_ft:
            elev_text = f"{peak.elevation_ft:,} ft"
            if peak.elevation_m:
                elev_text += f" ({peak.elevation_m:,} m)"
            table.add_row("Elevation", elev_text)

        if peak.prominence_ft:
            prom_text = f"{peak.prominence_ft:,} ft"
            if peak.prominence_m:
                prom_text += f" ({peak.prominence_m} m)"
            table.add_row("Prominence", prom_text)

        if peak.isolation_mi:
            iso_text = f"{peak.isolation_mi} mi"
            if peak.isolation_km:
                iso_text += f" ({peak.isolation_km} km)"
            table.add_row("Isolation", iso_text)

        if peak.latitude and peak.longitude:
            table.add_row("Coordinates", f"{peak.latitude}, {peak.longitude}")
        if peak.county:
            table.add_row("County", peak.county)
        if peak.country:
            table.add_row("Country", peak.country)

        if peak.ascent_count is not None:
            ascent_text = f"{peak.ascent_count:,}"
            if peak.viewable_ascent_count is not None:
                ascent_text += f" ({peak.viewable_ascent_count:,} viewable)"
            table.add_row("Ascents Logged", ascent_text)

        peak_url: str = f"https://www.peakbagger.com/peak.aspx?pid={peak.pid}"
        table.add_row("URL", f"[blue not underline]{peak_url}[/blue not underline]")

        return table

    def _print_routes_section(self, routes: list[dict[str, Any]]) -> None:
        """Print the routes section for a peak."""
        self.console.print(f"\n[bold yellow]Routes ({len(routes)})[/bold yellow]")
        for i, route in enumerate(routes, 1):
            route_text = f"  {i}. [green]{route['name']}[/green]"
            details = []
            if "trailhead" in route:
                th_text = route["trailhead"]
                if "trailhead_elevation_ft" in route:
                    th_text += f" ({route['trailhead_elevation_ft']:,} ft)"
                details.append(f"Trailhead: {th_text}")
            if "vertical_gain_ft" in route:
                details.append(f"Gain: {route['vertical_gain_ft']:,} ft")
            if "distance_mi" in route:
                details.append(f"Distance: {route['distance_mi']} mi")
            if details:
                route_text += f"\n     {', '.join(details)}"
            self.console.print(route_text)

    def _print_peak_lists_section(self, peak_lists: list[dict[str, Any]]) -> None:
        """Print the peak lists section (show first 10)."""
        self.console.print(f"\n[bold yellow]Peak Lists ({len(peak_lists)} total)[/bold yellow]")
        display_lists = peak_lists[:10]
        for i, peak_list in enumerate(display_lists, 1):
            list_name = peak_list["list_name"]
            rank = peak_list["rank"]
            url = peak_list.get("url", "")
            list_text = f"  {i}. [green]{list_name}[/green] [dim](Rank #{rank})[/dim]"
            if url:
                list_text += f" - [blue not underline]{url}[/blue not underline]"
            self.console.print(list_text)
        if len(peak_lists) > 10:
            remaining = len(peak_lists) - 10
            self.console.print(f"  [dim]... and {remaining} more[/dim]")

    def _print_peak_detail(self, peak: Peak) -> None:
        """Print detailed peak information as formatted text."""
        # Title
        title: str = f"{peak.name}"
        if peak.state:
            title += f", {peak.state}"
        self.console.print(f"\n[bold cyan]{title}[/bold cyan]")
        self.console.print(f"[dim]Peak ID: {peak.pid}[/dim]\n")

        self.console.print(self._build_peak_details_table(peak))

        if peak.routes and len(peak.routes) > 0:
            self._print_routes_section(peak.routes)

        if peak.peak_lists and len(peak.peak_lists) > 0:
            self._print_peak_lists_section(peak.peak_lists)

    def format_ascent_statistics(
        self,
        stats: AscentStatistics,
        ascents: list[Ascent] | None = None,
        output_format: str = "text",
        limit: int | None = None,
    ) -> None:
        """
        Format and print ascent statistics.

        Args:
            stats: AscentStatistics object
            ascents: Optional list of ascents to display (also controls list visibility)
            output_format: Either 'text' or 'json'
            limit: Maximum number of ascents to display (applied after sorting)
        """
        if output_format == "json":
            data = stats.to_dict()
            if ascents is not None:
                # Sort and apply limit to JSON output as well
                sorted_ascents = sorted(ascents, key=self._parse_date_for_sort, reverse=True)
                display_limit = limit if limit is not None else 100
                data["ascents"] = [a.to_dict() for a in sorted_ascents[:display_limit]]
            self._print_json(data)
        else:
            self._print_ascent_statistics(stats, ascents, limit)

    def _print_overall_stats(self, stats: AscentStatistics) -> None:
        """Print the overall statistics section."""
        self.console.print("\n[bold cyan]=== Overall Statistics ===[/bold cyan]\n")
        overall_table: Table = Table(show_header=False, box=None, padding=(0, 2))
        overall_table.add_column("Metric", style="yellow", width=25, no_wrap=True)
        overall_table.add_column("Value", style="white", no_wrap=True)

        overall_table.add_row("Total ascents", str(stats.total_ascents))

        if stats.total_ascents > 0:
            gpx_pct = (stats.ascents_with_gpx / stats.total_ascents) * 100
            tr_pct = (stats.ascents_with_trip_reports / stats.total_ascents) * 100
            overall_table.add_row("With GPX tracks", f"{stats.ascents_with_gpx} ({gpx_pct:.1f}%)")
            overall_table.add_row(
                "With trip reports", f"{stats.ascents_with_trip_reports} ({tr_pct:.1f}%)"
            )

        self.console.print(overall_table)

    def _print_temporal_breakdown(self, stats: AscentStatistics) -> None:
        """Print the temporal breakdown section."""
        self.console.print("\n[bold cyan]=== Temporal Breakdown ===[/bold cyan]\n")
        temporal_table: Table = Table(show_header=False, box=None, padding=(0, 2))
        temporal_table.add_column("Period", style="yellow", width=25, no_wrap=True)
        temporal_table.add_column("Ascents", style="white", no_wrap=True)

        temporal_table.add_row("Last 3 months", str(stats.last_3_months))
        temporal_table.add_row("Last year", str(stats.last_year))
        temporal_table.add_row("Last 5 years", str(stats.last_5_years))

        self.console.print(temporal_table)

    def _print_seasonal_pattern(self, stats: AscentStatistics) -> None:
        """Print the seasonal pattern section."""
        if not stats.seasonal_pattern:
            return
        self.console.print("\n[bold cyan]=== Seasonal Pattern ===[/bold cyan]\n")
        seasonal_months = [
            (month, count) for month, count in stats.seasonal_pattern.items() if count > 0
        ]
        if seasonal_months:
            for month, count in seasonal_months:
                self.console.print(f"  {month:12s}: {count}")
        else:
            self.console.print("  [dim]No ascents in seasonal window[/dim]")

    def _print_monthly_distribution(self, stats: AscentStatistics) -> None:
        """Print the monthly distribution section."""
        self.console.print("\n[bold cyan]=== Monthly Distribution ===[/bold cyan]\n")
        for month, count in stats.monthly_distribution.items():
            self.console.print(f"  {month:12s}: {count}")

    def _print_ascent_list(self, ascents: list[Ascent], limit: int | None) -> None:
        """Print the ascent list table."""
        self.console.print(f"\n[bold cyan]=== Ascent List ({len(ascents)} total) ===[/bold cyan]\n")

        sorted_ascents = sorted(ascents, key=self._parse_date_for_sort, reverse=True)
        display_limit = limit if limit is not None else 100
        displayed_ascents = sorted_ascents[:display_limit]

        ascent_table: Table = Table(show_header=True, header_style="bold cyan", box=None)
        ascent_table.add_column("#", style="dim", no_wrap=True)
        ascent_table.add_column("Date", style="yellow", no_wrap=True)
        ascent_table.add_column("Climber", style="green", no_wrap=True)
        ascent_table.add_column("GPX", style="green", justify="center", no_wrap=True)
        ascent_table.add_column("TR", style="yellow", justify="center", no_wrap=True)
        ascent_table.add_column("Route", style="cyan", no_wrap=True)
        ascent_table.add_column("URL", style="blue not underline", no_wrap=True)

        for i, ascent in enumerate(displayed_ascents, 1):
            date_str = ascent.date if ascent.date else "Unknown"
            gpx_indicator = "✓" if ascent.has_gpx else "-"
            tr_indicator = str(ascent.trip_report_words) if ascent.has_trip_report else "-"
            route_str = ascent.route if ascent.route else "-"
            climber_name = _strip_emojis(ascent.climber_name)
            ascent_url = f"https://www.peakbagger.com/climber/ascent.aspx?aid={ascent.ascent_id}"

            ascent_table.add_row(
                str(i),
                date_str,
                climber_name,
                gpx_indicator,
                tr_indicator,
                route_str,
                ascent_url,
            )

        self.console.print(ascent_table)

    def _print_ascent_statistics(
        self,
        stats: AscentStatistics,
        ascents: list[Ascent] | None = None,
        limit: int | None = None,
    ) -> None:
        """Print ascent statistics as formatted text.

        Args:
            stats: AscentStatistics object
            ascents: Optional list of ascents to display
            limit: Maximum number of ascents to display (applied after sorting)
        """
        self._print_overall_stats(stats)
        self._print_temporal_breakdown(stats)
        self._print_seasonal_pattern(stats)
        self._print_monthly_distribution(stats)

        if ascents:
            self._print_ascent_list(ascents, limit)

    def _add_ascent_identity_rows(self, table: Table, ascent: Ascent) -> None:
        """Add ascent ID, climber, date, type, and peak rows to the table."""
        ascent_url = f"https://www.peakbagger.com/climber/ascent.aspx?aid={ascent.ascent_id}"
        ascent_id_display = (
            f"{ascent.ascent_id} [blue not underline]{ascent_url}[/blue not underline]"
        )
        table.add_row("Ascent ID", ascent_id_display)

        climber_display = ascent.climber_name
        if ascent.climber_id:
            climber_url = f"https://www.peakbagger.com/climber/climber.aspx?cid={ascent.climber_id}"
            climber_display += f" [dim]({ascent.climber_id})[/dim] [blue not underline]{climber_url}[/blue not underline]"
        table.add_row("Climber", climber_display)

        if ascent.date:
            table.add_row("Date", ascent.date)
        if ascent.ascent_type:
            table.add_row("Ascent Type", ascent.ascent_type)

        if ascent.peak_name:
            peak_display = ascent.peak_name
            if ascent.peak_id:
                peak_url = f"https://www.peakbagger.com/peak.aspx?pid={ascent.peak_id}"
                peak_display += f" [dim]({ascent.peak_id})[/dim] [blue not underline]{peak_url}[/blue not underline]"
            table.add_row("Peak", peak_display)

        if ascent.location:
            table.add_row("Location", ascent.location)
        if ascent.elevation_ft and ascent.elevation_m:
            table.add_row("Elevation", f"{ascent.elevation_ft:,} ft ({ascent.elevation_m:,} m)")
        if ascent.route:
            table.add_row("Route", ascent.route)

    def _add_ascent_metrics_rows(self, table: Table, ascent: Ascent) -> None:
        """Add GPX, distance, duration, and trip report rows to the table."""
        table.add_row("Has GPX", "Yes" if ascent.has_gpx else "No")

        if ascent.elevation_gain_ft:
            table.add_row("Elevation Gain", f"{ascent.elevation_gain_ft:,} ft")
        if ascent.distance_mi:
            table.add_row("Distance", f"{ascent.distance_mi} mi")
        if ascent.duration_hours:
            hours = int(ascent.duration_hours)
            minutes = int((ascent.duration_hours - hours) * 60)
            dur_display = f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
            table.add_row("Duration", dur_display)

        has_tr_text = "Yes" if ascent.has_trip_report else "No"
        if ascent.trip_report_words:
            has_tr_text += f" ({ascent.trip_report_words:,} words)"
        table.add_row("Has Trip Report", has_tr_text)

    def _build_ascent_detail_table(self, ascent: Ascent) -> Table:
        """Build a Rich table with ascent detail rows."""
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("Field", style="cyan", width=20, no_wrap=True)
        table.add_column("Value", style="white", no_wrap=True)

        self._add_ascent_identity_rows(table, ascent)
        self._add_ascent_metrics_rows(table, ascent)

        return table

    def _print_trip_report(self, ascent: Ascent) -> None:
        """Print the trip report section for an ascent."""
        if not ascent.trip_report_text:
            return
        self.console.print("\n[bold cyan]Trip Report:[/bold cyan]")
        self.console.print("─" * 60)
        report_text = Text(ascent.trip_report_text)
        self.console.print(report_text)

        if ascent.trip_report_url:
            self.console.print(f"\n[bold]External Link:[/bold] {ascent.trip_report_url}")

    def format_ascent_detail(self, ascent: Ascent, output_format: str) -> None:
        """
        Format and display a single ascent's detailed information.

        Args:
            ascent: Ascent object with detailed data
            output_format: "text" or "json"
        """
        if output_format == "json":
            self._print_json(ascent.to_dict())
        else:
            self.console.print(self._build_ascent_detail_table(ascent))
            self._print_trip_report(ascent)
