"""Output formatters for peak data (Rich tables and JSON)."""

import json
from typing import Any

from rich.console import Console
from rich.table import Table

from peakbagger.models import Peak, SearchResult


class PeakFormatter:
    """Formatter for peak data output."""

    def __init__(self) -> None:
        self.console: Console = Console()

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
        """Print data as formatted JSON."""
        print(json.dumps(data, indent=2))

    def _print_search_table(self, results: list[SearchResult]) -> None:
        """Print search results as a Rich table."""
        if not results:
            self.console.print("[yellow]No results found.[/yellow]")
            return

        table: Table = Table(title="Search Results", show_header=True, header_style="bold cyan", expand=True)
        table.add_column("Peak ID", style="dim")
        table.add_column("Name", style="green")
        table.add_column("URL", style="blue", overflow="fold")

        for result in results:
            url: str = f"https://www.peakbagger.com/{result.url}"
            table.add_row(result.pid, result.name, url)

        self.console.print(table)
        self.console.print(
            f"\n[dim]Found {len(results)} peak(s). Use 'peakbagger info <PID>' for details.[/dim]"
        )

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
        table.add_column("Field", style="yellow", width=20)
        table.add_column("Value", style="white")

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

        # Add PeakBagger URL
        peak_url: str = f"https://www.peakbagger.com/peak.aspx?pid={peak.pid}"
        table.add_row("URL", f"[blue]{peak_url}[/blue]")

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
            self.console.print(f"\n[bold yellow]Peak Lists ({len(peak.peak_lists)} total)[/bold yellow]")
            display_lists = peak.peak_lists[:10]
            for peak_list in display_lists:
                list_name = peak_list["list_name"]
                rank = peak_list["rank"]
                url = peak_list.get("url", "")
                self.console.print(f"  • {list_name} [dim](Rank #{rank})[/dim]")
                if url:
                    self.console.print(f"    [blue]{url}[/blue]")
            if len(peak.peak_lists) > 10:
                remaining = len(peak.peak_lists) - 10
                self.console.print(f"  [dim]... and {remaining} more[/dim]")
