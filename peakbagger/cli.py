"""CLI interface for peakbagger."""

from typing import TYPE_CHECKING

import click

from peakbagger import __version__
from peakbagger.client import PeakBaggerClient
from peakbagger.formatters import PeakFormatter
from peakbagger.scraper import PeakBaggerScraper

if TYPE_CHECKING:
    from peakbagger.models import Peak


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress informational messages",
)
@click.pass_context
def main(ctx: click.Context, quiet: bool) -> None:
    """PeakBagger CLI - Search and retrieve mountain peak data from PeakBagger.com"""
    ctx.ensure_object(dict)
    ctx.obj["quiet"] = quiet


@main.command()
@click.argument("query")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format (text or json)",
)
@click.option(
    "--full",
    is_flag=True,
    help="Fetch full details for all search results",
)
@click.option(
    "--rate-limit",
    type=float,
    default=2.0,
    help="Seconds between requests (default: 2.0)",
)
def search(query: str, output_format: str, full: bool, rate_limit: float) -> None:
    """
    Search for peaks by name.

    QUERY: Search term (e.g., "Mount Rainier", "Denali")

    Examples:

      peakbagger search "Mount Rainier"

      peakbagger search "Denali" --format json

      peakbagger search "Whitney" --full
    """
    client: PeakBaggerClient = PeakBaggerClient(rate_limit_seconds=rate_limit)
    scraper: PeakBaggerScraper = PeakBaggerScraper()
    formatter: PeakFormatter = PeakFormatter()

    try:
        # Fetch search results
        click.echo(f"Searching for '{query}'...")
        html = client.get("/search.aspx", params={"ss": query, "tid": "M"})

        # Parse results
        results = scraper.parse_search_results(html)

        if not results:
            click.echo(f"No results found for '{query}'")
            return

        # If --full flag, fetch details for each peak
        if full:
            click.echo(f"Fetching details for {len(results)} peak(s)...\n")
            peaks: list[Peak] = []
            for result in results:
                detail_html = client.get(f"/{result.url}")
                peak = scraper.parse_peak_detail(detail_html, result.pid)
                if peak:
                    peaks.append(peak)

            formatter.format_peaks(peaks, output_format)
        else:
            # Just show search results
            formatter.format_search_results(results, output_format)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e
    finally:
        client.close()


@main.command()
@click.argument("peak_id")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format (text or json)",
)
@click.option(
    "--rate-limit",
    type=float,
    default=2.0,
    help="Seconds between requests (default: 2.0)",
)
def info(peak_id: str, output_format: str, rate_limit: float) -> None:
    """
    Get detailed information about a specific peak.

    PEAK_ID: The PeakBagger peak ID (e.g., "2296" for Mount Rainier)

    Examples:

      peakbagger info 2296

      peakbagger info 2296 --format json
    """
    client: PeakBaggerClient = PeakBaggerClient(rate_limit_seconds=rate_limit)
    scraper: PeakBaggerScraper = PeakBaggerScraper()
    formatter: PeakFormatter = PeakFormatter()

    try:
        # Fetch peak detail page
        click.echo(f"Fetching peak {peak_id}...")
        html = client.get("/peak.aspx", params={"pid": peak_id})

        # Parse peak data
        peak = scraper.parse_peak_detail(html, peak_id)

        if not peak:
            click.echo(f"Failed to parse peak data for ID {peak_id}", err=True)
            raise click.Abort()

        # Display results
        formatter.format_peak_detail(peak, output_format)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e
    finally:
        client.close()


@main.command(name="peak-ascents")
@click.argument("peak_id")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format (text or json)",
)
@click.option(
    "--stats",
    is_flag=True,
    help="Show temporal and seasonal statistics",
)
@click.option(
    "--list-ascents",
    is_flag=True,
    help="Include list of all ascents",
)
@click.option(
    "--after",
    type=str,
    help="Filter ascents on or after this date (YYYY-MM-DD)",
)
@click.option(
    "--before",
    type=str,
    help="Filter ascents on or before this date (YYYY-MM-DD)",
)
@click.option(
    "--within",
    type=str,
    help="Filter ascents within period from today (e.g., '3m', '1y', '10d')",
)
@click.option(
    "--reference-date",
    type=str,
    help="Reference date for seasonal analysis (YYYY-MM-DD, default: today)",
)
@click.option(
    "--seasonal-window",
    type=int,
    default=14,
    help="Days before/after reference date for seasonal window (default: 14)",
)
@click.option(
    "--with-gpx",
    is_flag=True,
    help="Only show ascents with GPX tracks",
)
@click.option(
    "--with-tr",
    is_flag=True,
    help="Only show ascents with trip reports",
)
@click.option(
    "--rate-limit",
    type=float,
    default=2.0,
    help="Seconds between requests (default: 2.0)",
)
def peak_ascents(
    peak_id: str,
    output_format: str,
    stats: bool,
    list_ascents: bool,
    after: str | None,
    before: str | None,
    within: str | None,
    reference_date: str | None,
    seasonal_window: int,
    with_gpx: bool,
    with_tr: bool,
    rate_limit: float,
) -> None:
    """
    Analyze ascent statistics for a specific peak.

    PEAK_ID: The PeakBagger peak ID (e.g., "1798" for Mount Pilchuck)

    Examples:

      peakbagger peak-ascents 1798

      peakbagger peak-ascents 1798 --stats

      peakbagger peak-ascents 1798 --stats --list-ascents

      peakbagger peak-ascents 1798 --after 2020-01-01

      peakbagger peak-ascents 1798 --within 1y --stats

      peakbagger peak-ascents 1798 --with-gpx

      peakbagger peak-ascents 1798 --with-tr --list-ascents

      peakbagger peak-ascents 1798 --format json
    """
    from datetime import datetime

    from peakbagger.statistics import AscentAnalyzer

    # Validate mutually exclusive date filters
    if within and (after or before):
        click.echo("Error: --within cannot be combined with --after/--before", err=True)
        raise click.Abort()

    client: PeakBaggerClient = PeakBaggerClient(rate_limit_seconds=rate_limit)
    scraper: PeakBaggerScraper = PeakBaggerScraper()
    formatter: PeakFormatter = PeakFormatter()
    analyzer: AscentAnalyzer = AscentAnalyzer()

    try:
        # Fetch ascent list page
        click.echo(f"Fetching ascents for peak {peak_id}...")
        url = "/climber/PeakAscents.aspx"
        params = {"pid": peak_id, "sort": "ascentdate", "u": "ft", "y": "9999"}
        html = client.get(url, params=params)

        # Parse ascents
        ascents = scraper.parse_peak_ascents(html)

        if not ascents:
            click.echo(f"No ascents found for peak ID {peak_id}", err=True)
            return

        click.echo(f"Found {len(ascents)} ascents\n")

        # Apply date filters
        filtered_ascents = ascents
        if within:
            try:
                period = analyzer.parse_within_period(within)
                after_date = datetime.now() - period
                filtered_ascents = analyzer.filter_by_date_range(filtered_ascents, after=after_date)
                click.echo(f"Filtered to {len(filtered_ascents)} ascents within {within}\n")
            except ValueError as e:
                click.echo(f"Error: {e}", err=True)
                raise click.Abort() from e
        elif after or before:
            after_date = datetime.strptime(after, "%Y-%m-%d") if after else None
            before_date = datetime.strptime(before, "%Y-%m-%d") if before else None
            filtered_ascents = analyzer.filter_by_date_range(
                filtered_ascents, after=after_date, before=before_date
            )
            click.echo(f"Filtered to {len(filtered_ascents)} ascents\n")

        # Apply metadata filters
        if with_gpx:
            filtered_ascents = [a for a in filtered_ascents if a.has_gpx]
            click.echo(f"Filtered to {len(filtered_ascents)} ascents with GPX tracks\n")

        if with_tr:
            filtered_ascents = [a for a in filtered_ascents if a.has_trip_report]
            click.echo(f"Filtered to {len(filtered_ascents)} ascents with trip reports\n")

        # Parse reference date for seasonal analysis
        ref_date = None
        if reference_date:
            try:
                ref_date = datetime.strptime(reference_date, "%Y-%m-%d")
            except ValueError as e:
                click.echo(f"Error: Invalid reference date format: {reference_date}", err=True)
                raise click.Abort() from e

        # Calculate statistics
        statistics = analyzer.calculate_statistics(
            filtered_ascents,
            reference_date=ref_date,
            seasonal_window_days=seasonal_window,
        )

        # Display results
        formatter.format_ascent_statistics(
            statistics,
            ascents=filtered_ascents if list_ascents else None,
            output_format=output_format,
            show_list=list_ascents,
        )

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e
    finally:
        client.close()


if __name__ == "__main__":
    main()
