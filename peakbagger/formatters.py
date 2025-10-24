"""Output formatters for peak data (Rich tables and JSON)."""

import json
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.text import Text

from peakbagger.models import Ascent, AscentStatistics, Peak, SearchResult


class PeakFormatter:
    """Formatter for peak data output."""

    def __init__(self) -> None:
        # Use a very wide console to prevent any text truncation
        # Tables will extend beyond terminal width if needed
        self.console: Console = Console(width=500)

    def _parse_date_for_sort(self, ascent: Ascent) -> Any:
        """Return date for sorting. None/invalid dates sort to the end.

        Args:
            ascent: Ascent object to extract date from

        Returns:
            datetime object for sorting, or datetime.min for invalid/missing dates
        """
        from datetime import datetime

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

    def _print_peak_detail(self, peak: Peak) -> None:
        """Print detailed peak information as formatted text."""
        # Title
        title: str = f"{peak.name}"
        if peak.state:
            title += f", {peak.state}"
        self.console.print(f"\n[bold cyan]{title}[/bold cyan]")
        self.console.print(f"[dim]Peak ID: {peak.pid}[/dim]\n")

        # Create details table
        table: Table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Field", style="yellow", width=20, no_wrap=True)
        table.add_column("Value", style="white", no_wrap=True)

        # Add elevation
        if peak.elevation_ft:
            elev_text = f"{peak.elevation_ft:,} ft"
            if peak.elevation_m:
                elev_text += f" ({peak.elevation_m:,} m)"
            table.add_row("Elevation", elev_text)

        # Add prominence
        if peak.prominence_ft:
            prom_text = f"{peak.prominence_ft:,} ft"
            if peak.prominence_m:
                prom_text += f" ({peak.prominence_m} m)"
            table.add_row("Prominence", prom_text)

        # Add isolation
        if peak.isolation_mi:
            iso_text = f"{peak.isolation_mi} mi"
            if peak.isolation_km:
                iso_text += f" ({peak.isolation_km} km)"
            table.add_row("Isolation", iso_text)

        # Add location
        if peak.latitude and peak.longitude:
            table.add_row("Coordinates", f"{peak.latitude}, {peak.longitude}")

        if peak.county:
            table.add_row("County", peak.county)

        if peak.country:
            table.add_row("Country", peak.country)

        # Add ascent counts
        if peak.ascent_count is not None:
            ascent_text = f"{peak.ascent_count:,}"
            if peak.viewable_ascent_count is not None:
                ascent_text += f" ({peak.viewable_ascent_count:,} viewable)"
            table.add_row("Ascents Logged", ascent_text)

        # Add PeakBagger URL
        peak_url: str = f"https://www.peakbagger.com/peak.aspx?pid={peak.pid}"
        table.add_row("URL", f"[blue not underline]{peak_url}[/blue not underline]")

        self.console.print(table)

        # Add routes section
        if peak.routes and len(peak.routes) > 0:
            self.console.print(f"\n[bold yellow]Routes ({len(peak.routes)})[/bold yellow]")
            for i, route in enumerate(peak.routes, 1):
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

        # Add peak lists section (show first 10)
        if peak.peak_lists and len(peak.peak_lists) > 0:
            self.console.print(
                f"\n[bold yellow]Peak Lists ({len(peak.peak_lists)} total)[/bold yellow]"
            )
            display_lists = peak.peak_lists[:10]
            for i, peak_list in enumerate(display_lists, 1):
                list_name = peak_list["list_name"]
                rank = peak_list["rank"]
                url = peak_list.get("url", "")
                list_text = f"  {i}. [green]{list_name}[/green] [dim](Rank #{rank})[/dim]"
                if url:
                    list_text += f" - [blue not underline]{url}[/blue not underline]"
                self.console.print(list_text)
            if len(peak.peak_lists) > 10:
                remaining = len(peak.peak_lists) - 10
                self.console.print(f"  [dim]... and {remaining} more[/dim]")

    def format_ascent_statistics(
        self,
        stats: AscentStatistics,
        ascents: list[Ascent] | None = None,
        output_format: str = "text",
        show_list: bool = False,
        limit: int | None = None,
    ) -> None:
        """
        Format and print ascent statistics.

        Args:
            stats: AscentStatistics object
            ascents: Optional list of ascents to display
            output_format: Either 'text' or 'json'
            show_list: Whether to include list of ascents
            limit: Maximum number of ascents to display (applied after sorting)
        """
        if output_format == "json":
            data = stats.to_dict()
            if show_list and ascents:
                # Sort and apply limit to JSON output as well
                sorted_ascents = sorted(ascents, key=self._parse_date_for_sort, reverse=True)
                display_limit = limit if limit is not None else 100
                data["ascents"] = [a.to_dict() for a in sorted_ascents[:display_limit]]
            self._print_json(data)
        else:
            self._print_ascent_statistics(stats, ascents if show_list else None, limit)

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
        # Overall Statistics
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

        # Temporal Breakdown
        self.console.print("\n[bold cyan]=== Temporal Breakdown ===[/bold cyan]\n")
        temporal_table: Table = Table(show_header=False, box=None, padding=(0, 2))
        temporal_table.add_column("Period", style="yellow", width=25, no_wrap=True)
        temporal_table.add_column("Ascents", style="white", no_wrap=True)

        temporal_table.add_row("Last 3 months", str(stats.last_3_months))
        temporal_table.add_row("Last year", str(stats.last_year))
        temporal_table.add_row("Last 5 years", str(stats.last_5_years))

        self.console.print(temporal_table)

        # Seasonal Pattern
        if stats.seasonal_pattern:
            self.console.print("\n[bold cyan]=== Seasonal Pattern ===[/bold cyan]\n")
            seasonal_months = [
                (month, count) for month, count in stats.seasonal_pattern.items() if count > 0
            ]
            if seasonal_months:
                for month, count in seasonal_months:
                    self.console.print(f"  {month:12s}: {count}")
            else:
                self.console.print("  [dim]No ascents in seasonal window[/dim]")

        # Monthly Distribution
        self.console.print("\n[bold cyan]=== Monthly Distribution ===[/bold cyan]\n")
        for month, count in stats.monthly_distribution.items():
            self.console.print(f"  {month:12s}: {count}")

        # List of ascents (if requested)
        if ascents:
            self.console.print(
                f"\n[bold cyan]=== Ascent List ({len(ascents)} total) ===[/bold cyan]\n"
            )

            # Sort ascents by date (newest first), with None dates at the end
            sorted_ascents = sorted(ascents, key=self._parse_date_for_sort, reverse=True)

            # Apply limit after sorting (default to 100 if not specified)
            display_limit = limit if limit is not None else 100
            displayed_ascents = sorted_ascents[:display_limit]

            # Create table for ascents
            ascent_table: Table = Table(show_header=True, header_style="bold cyan", box=None)
            ascent_table.add_column("#", style="dim", no_wrap=True)
            ascent_table.add_column("Date", style="yellow", no_wrap=True)
            ascent_table.add_column("Climber", style="green", no_wrap=True)
            ascent_table.add_column("GPX", style="green", justify="center", no_wrap=True)
            ascent_table.add_column("TR", style="yellow", justify="center", no_wrap=True)
            ascent_table.add_column("Route", style="cyan", no_wrap=True)
            ascent_table.add_column("URL", style="blue not underline", no_wrap=True)

            # Helper to strip emojis from text
            def strip_emojis(text: str) -> str:
                """Remove emoji characters from text."""
                import re

                # Pattern matches emoji ranges
                emoji_pattern = re.compile(
                    "["
                    "\U0001f600-\U0001f64f"  # emoticons
                    "\U0001f300-\U0001f5ff"  # symbols & pictographs
                    "\U0001f680-\U0001f6ff"  # transport & map symbols
                    "\U0001f1e0-\U0001f1ff"  # flags (iOS)
                    "\U00002702-\U000027b0"
                    "\U000024c2-\U0001f251"
                    "]+",
                    flags=re.UNICODE,
                )
                return emoji_pattern.sub("", text).strip()

            for i, ascent in enumerate(displayed_ascents, 1):
                date_str = ascent.date if ascent.date else "Unknown"
                gpx_indicator = "✓" if ascent.has_gpx else "-"
                tr_indicator = str(ascent.trip_report_words) if ascent.has_trip_report else "-"
                route_str = ascent.route if ascent.route else "-"
                climber_name = strip_emojis(ascent.climber_name)
                ascent_url = (
                    f"https://www.peakbagger.com/climber/ascent.aspx?aid={ascent.ascent_id}"
                )

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

    def format_ascent_detail(self, ascent: Ascent, output_format: str) -> None:
        """
        Format and display a single ascent's detailed information.

        Args:
            ascent: Ascent object with detailed data
            output_format: "text" or "json"
        """
        if output_format == "json":
            # JSON output
            self._print_json(ascent.to_dict())
        else:
            # Text output with Rich table
            table = Table(show_header=True, header_style="bold magenta", box=None)
            table.add_column("Field", style="cyan", width=20, no_wrap=True)
            table.add_column("Value", style="white", no_wrap=True)

            # Basic info
            table.add_row("Ascent ID", ascent.ascent_id)
            table.add_row("Climber", ascent.climber_name)

            if ascent.date:
                table.add_row("Date", ascent.date)

            if ascent.ascent_type:
                table.add_row("Ascent Type", ascent.ascent_type)

            # Peak info
            if ascent.peak_name:
                peak_display = ascent.peak_name
                if ascent.peak_id:
                    peak_display += f" ({ascent.peak_id})"
                table.add_row("Peak", peak_display)

            if ascent.location:
                table.add_row("Location", ascent.location)

            if ascent.elevation_ft and ascent.elevation_m:
                elev_display = f"{ascent.elevation_ft:,} ft ({ascent.elevation_m:,} m)"
                table.add_row("Elevation", elev_display)

            if ascent.route:
                table.add_row("Route", ascent.route)

            # GPX metrics
            if ascent.elevation_gain_ft:
                table.add_row("Elevation Gain", f"{ascent.elevation_gain_ft:,} ft")

            if ascent.distance_mi:
                table.add_row("Distance", f"{ascent.distance_mi} mi")

            if ascent.duration_hours:
                hours = int(ascent.duration_hours)
                minutes = int((ascent.duration_hours - hours) * 60)
                dur_display = f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
                table.add_row("Duration", dur_display)

            self.console.print(table)

            # Trip report section
            if ascent.trip_report_text:
                self.console.print("\n[bold cyan]Trip Report:[/bold cyan]")
                self.console.print("─" * 60)
                # Word wrap the trip report
                report_text = Text(ascent.trip_report_text)
                self.console.print(report_text)

                if ascent.trip_report_url:
                    self.console.print(f"\n[bold]External Link:[/bold] {ascent.trip_report_url}")
