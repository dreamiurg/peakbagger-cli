"""CLI interface for peakbagger."""

from typing import TYPE_CHECKING

import click
from rich.console import Console

from peakbagger import __version__
from peakbagger.client import PeakBaggerClient
from peakbagger.formatters import PeakFormatter
from peakbagger.logging_config import configure_logging
from peakbagger.scraper import PeakBaggerScraper

if TYPE_CHECKING:
    from peakbagger.models import Peak

# Module-level console for status messages (stderr to keep stdout clean for data)
_console = Console(stderr=True)


def _status(ctx: click.Context, message: str, style: str | None = None) -> None:
    """
    Print a status message to stderr using Rich.

    Respects --quiet and --dump-html flags to keep output clean.

    Args:
        ctx: Click context containing options
        message: Status message to display
        style: Optional Rich style (e.g., "bold yellow", "red")
    """
    # Suppress status messages if --quiet or --dump-html is set
    if ctx.obj.get("quiet") or ctx.obj.get("dump_html"):
        return

    if style:
        _console.print(message, style=style)
    else:
        _console.print(message)


def _error(message: str) -> None:
    """
    Print an error message to stderr using Rich.

    Always shown regardless of --quiet or --dump-html flags.

    Args:
        message: Error message to display
    """
    _console.print(f"[bold red]Error:[/bold red] {message}")


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress informational messages",
)
@click.option(
    "--dump-html",
    is_flag=True,
    help="Dump raw HTML to stdout instead of parsing",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging (INFO level - shows HTTP requests)",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging (DEBUG level - shows detailed operations)",
)
@click.pass_context
def main(ctx: click.Context, quiet: bool, dump_html: bool, verbose: bool, debug: bool) -> None:
    """PeakBagger CLI - Search and retrieve mountain peak data from PeakBagger.com"""
    # Validate mutually exclusive flags
    if quiet and (verbose or debug):
        raise click.UsageError("--quiet cannot be used with --verbose or --debug")

    ctx.ensure_object(dict)
    ctx.obj["quiet"] = quiet
    ctx.obj["dump_html"] = dump_html
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug

    # Configure logging based on flags
    configure_logging(verbose=verbose, debug=debug)


@main.group()
def peak() -> None:
    """Commands for working with peaks."""
    pass


@main.group()
def ascent() -> None:
    """Commands for working with ascents."""
    pass


@peak.command()
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
@click.pass_context
def search(
    ctx: click.Context, query: str, output_format: str, full: bool, rate_limit: float
) -> None:
    """
    Search for peaks by name.

    QUERY: Search term (e.g., "Mount Rainier", "Denali")

    Examples:

      peakbagger peak search "Mount Rainier"

      peakbagger peak search "Denali" --format json

      peakbagger peak search "Whitney" --full
    """
    client: PeakBaggerClient = PeakBaggerClient(rate_limit_seconds=rate_limit)
    scraper: PeakBaggerScraper = PeakBaggerScraper()
    formatter: PeakFormatter = PeakFormatter()

    try:
        # Fetch search results
        _status(ctx, f"Searching for '{query}'...")
        html = client.get("/search.aspx", params={"ss": query, "tid": "M"})

        # If dump-html flag is set, print HTML and exit
        if ctx.obj.get("dump_html"):
            click.echo(html)
            return

        # Parse results
        results = scraper.parse_search_results(html)

        if not results:
            _status(ctx, f"No results found for '{query}'")
            return

        # If --full flag, fetch details for each peak
        if full:
            _status(ctx, f"Fetching details for {len(results)} peak(s)...\n")
            peaks: list[Peak] = []
            for result in results:
                detail_html = client.get(f"/{result.url}")
                peak_obj = scraper.parse_peak_detail(detail_html, result.pid)
                if peak_obj:
                    peaks.append(peak_obj)

            formatter.format_peaks(peaks, output_format)
        else:
            # Just show search results
            formatter.format_search_results(results, output_format)
            if output_format == "text":
                _status(
                    ctx,
                    f"Found {len(results)} peak(s). Use 'peakbagger peak show <PID>' for details.",
                )

    except Exception as e:
        _error(str(e))
        raise click.Abort() from e
    finally:
        client.close()


@peak.command()
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
@click.pass_context
def show(ctx: click.Context, peak_id: str, output_format: str, rate_limit: float) -> None:
    """
    Get detailed information about a specific peak.

    PEAK_ID: The PeakBagger peak ID (e.g., "2296" for Mount Rainier)

    Examples:

      peakbagger peak show 2296

      peakbagger peak show 2296 --format json
    """
    client: PeakBaggerClient = PeakBaggerClient(rate_limit_seconds=rate_limit)
    scraper: PeakBaggerScraper = PeakBaggerScraper()
    formatter: PeakFormatter = PeakFormatter()

    try:
        # Fetch peak detail page
        _status(ctx, f"Fetching peak {peak_id}...")
        html = client.get("/peak.aspx", params={"pid": peak_id})

        # If dump-html flag is set, print HTML and exit
        if ctx.obj.get("dump_html"):
            click.echo(html)
            return

        # Parse peak data
        peak_obj = scraper.parse_peak_detail(html, peak_id)

        if not peak_obj:
            _error(f"Failed to parse peak data for ID {peak_id}")
            raise click.Abort()

        # Display results
        formatter.format_peak_detail(peak_obj, output_format)

    except Exception as e:
        _error(str(e))
        raise click.Abort() from e
    finally:
        client.close()


@peak.command()
@click.argument("peak_id")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format (text or json)",
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
    "--limit",
    type=int,
    default=100,
    help="Maximum number of ascents to display (default: 100)",
)
@click.option(
    "--rate-limit",
    type=float,
    default=2.0,
    help="Seconds between requests (default: 2.0)",
)
@click.pass_context
def ascents(
    ctx: click.Context,
    peak_id: str,
    output_format: str,
    after: str | None,
    before: str | None,
    within: str | None,
    with_gpx: bool,
    with_tr: bool,
    limit: int,
    rate_limit: float,
) -> None:
    """
    List ascents for a specific peak with optional filtering.

    PEAK_ID: The PeakBagger peak ID (e.g., "1798" for Mount Pilchuck)

    Examples:

      peakbagger peak ascents 1798

      peakbagger peak ascents 1798 --within 1y

      peakbagger peak ascents 1798 --with-gpx

      peakbagger peak ascents 1798 --after 2020-01-01 --limit 50

      peakbagger peak ascents 1798 --format json
    """
    from datetime import datetime

    from peakbagger.statistics import AscentAnalyzer

    # Validate mutually exclusive date filters
    if within and (after or before):
        _error("--within cannot be combined with --after/--before")
        raise click.Abort()

    client: PeakBaggerClient = PeakBaggerClient(rate_limit_seconds=rate_limit)
    scraper: PeakBaggerScraper = PeakBaggerScraper()
    formatter: PeakFormatter = PeakFormatter()
    analyzer: AscentAnalyzer = AscentAnalyzer()

    try:
        # Fetch ascent list page
        _status(ctx, f"Fetching ascents for peak {peak_id}...")
        url = "/climber/PeakAscents.aspx"
        params = {"pid": peak_id, "sort": "ascentdate", "u": "ft", "y": "9999"}
        html = client.get(url, params=params)

        # If dump-html flag is set, print HTML and exit
        if ctx.obj.get("dump_html"):
            click.echo(html)
            return

        # Parse ascents
        ascent_list = scraper.parse_peak_ascents(html)

        if not ascent_list:
            _error(f"No ascents found for peak ID {peak_id}")
            return

        _status(ctx, f"Found {len(ascent_list)} ascents\n")

        # Apply date filters
        filtered_ascents = ascent_list
        if within:
            try:
                period = analyzer.parse_within_period(within)
                after_date: datetime | None = datetime.now() - period
                filtered_ascents = analyzer.filter_by_date_range(filtered_ascents, after=after_date)
                _status(ctx, f"Filtered to {len(filtered_ascents)} ascents within {within}\n")
            except ValueError as e:
                _error(str(e))
                raise click.Abort() from e
        elif after or before:
            after_date = datetime.strptime(after, "%Y-%m-%d") if after else None
            before_date = datetime.strptime(before, "%Y-%m-%d") if before else None
            filtered_ascents = analyzer.filter_by_date_range(
                filtered_ascents, after=after_date, before=before_date
            )
            _status(ctx, f"Filtered to {len(filtered_ascents)} ascents\n")

        # Apply metadata filters
        if with_gpx:
            filtered_ascents = [a for a in filtered_ascents if a.has_gpx]
            _status(ctx, f"Filtered to {len(filtered_ascents)} ascents with GPX tracks\n")

        if with_tr:
            filtered_ascents = [a for a in filtered_ascents if a.has_trip_report]
            _status(ctx, f"Filtered to {len(filtered_ascents)} ascents with trip reports\n")

        # Display ascent list (not statistics)
        # Create a simple statistics object just for formatting the list
        statistics = analyzer.calculate_statistics(filtered_ascents)

        # Display only the list, not stats
        formatter.format_ascent_statistics(
            statistics,
            ascents=filtered_ascents[:limit],  # Apply limit
            output_format=output_format,
            show_list=True,  # Always show list for ascents command
        )

        if len(filtered_ascents) > limit:
            _status(ctx, f"\nShowing first {limit} of {len(filtered_ascents)} ascents")

    except Exception as e:
        _error(str(e))
        raise click.Abort() from e
    finally:
        client.close()


@peak.command()
@click.argument("peak_id")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format (text or json)",
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
    help="Analyze ascents within period from today (e.g., '3m', '1y', '10d')",
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
    "--rate-limit",
    type=float,
    default=2.0,
    help="Seconds between requests (default: 2.0)",
)
@click.pass_context
def stats(
    ctx: click.Context,
    peak_id: str,
    output_format: str,
    after: str | None,
    before: str | None,
    within: str | None,
    reference_date: str | None,
    seasonal_window: int,
    rate_limit: float,
) -> None:
    """
    Show statistical analysis of ascents for a specific peak.

    PEAK_ID: The PeakBagger peak ID (e.g., "1798" for Mount Pilchuck)

    Examples:

      peakbagger peak stats 1798

      peakbagger peak stats 1798 --within 5y

      peakbagger peak stats 1798 --reference-date 2024-07-15

      peakbagger peak stats 1798 --after 2020-01-01

      peakbagger peak stats 1798 --format json
    """
    from datetime import datetime

    from peakbagger.statistics import AscentAnalyzer

    # Validate mutually exclusive date filters
    if within and (after or before):
        _error("--within cannot be combined with --after/--before")
        raise click.Abort()

    client: PeakBaggerClient = PeakBaggerClient(rate_limit_seconds=rate_limit)
    scraper: PeakBaggerScraper = PeakBaggerScraper()
    formatter: PeakFormatter = PeakFormatter()
    analyzer: AscentAnalyzer = AscentAnalyzer()

    try:
        # Fetch ascent list page
        _status(ctx, f"Fetching ascents for peak {peak_id}...")
        url = "/climber/PeakAscents.aspx"
        params = {"pid": peak_id, "sort": "ascentdate", "u": "ft", "y": "9999"}
        html = client.get(url, params=params)

        # If dump-html flag is set, print HTML and exit
        if ctx.obj.get("dump_html"):
            click.echo(html)
            return

        # Parse ascents
        ascent_list = scraper.parse_peak_ascents(html)

        if not ascent_list:
            _error(f"No ascents found for peak ID {peak_id}")
            return

        _status(ctx, f"Found {len(ascent_list)} ascents\n")

        # Apply date filters
        filtered_ascents = ascent_list
        if within:
            try:
                period = analyzer.parse_within_period(within)
                after_date: datetime | None = datetime.now() - period
                filtered_ascents = analyzer.filter_by_date_range(filtered_ascents, after=after_date)
                _status(ctx, f"Analyzing {len(filtered_ascents)} ascents within {within}\n")
            except ValueError as e:
                _error(str(e))
                raise click.Abort() from e
        elif after or before:
            after_date = datetime.strptime(after, "%Y-%m-%d") if after else None
            before_date = datetime.strptime(before, "%Y-%m-%d") if before else None
            filtered_ascents = analyzer.filter_by_date_range(
                filtered_ascents, after=after_date, before=before_date
            )
            _status(ctx, f"Analyzing {len(filtered_ascents)} ascents\n")

        # Parse reference date for seasonal analysis
        ref_date = None
        if reference_date:
            try:
                ref_date = datetime.strptime(reference_date, "%Y-%m-%d")
            except ValueError as e:
                _error(f"Invalid reference date format: {reference_date}")
                raise click.Abort() from e

        # Calculate statistics
        statistics = analyzer.calculate_statistics(
            filtered_ascents,
            reference_date=ref_date,
            seasonal_window_days=seasonal_window,
        )

        # Display only statistics, not the list
        formatter.format_ascent_statistics(
            statistics,
            ascents=None,  # Don't show list for stats command
            output_format=output_format,
            show_list=False,
        )

    except Exception as e:
        _error(str(e))
        raise click.Abort() from e
    finally:
        client.close()


@ascent.command("show")
@click.argument("ascent_id")
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
@click.pass_context
def show_ascent(ctx: click.Context, ascent_id: str, output_format: str, rate_limit: float) -> None:
    """
    Get detailed information about a specific ascent.

    ASCENT_ID: The PeakBagger ascent ID (e.g., "12963" for a Mount Pilchuck ascent)

    Examples:

      peakbagger ascent show 12963

      peakbagger ascent show 12963 --format json
    """
    client: PeakBaggerClient = PeakBaggerClient(rate_limit_seconds=rate_limit)
    scraper: PeakBaggerScraper = PeakBaggerScraper()
    formatter: PeakFormatter = PeakFormatter()

    try:
        # Fetch ascent detail page
        _status(ctx, f"Fetching ascent {ascent_id}...")
        html = client.get("/climber/ascent.aspx", params={"aid": ascent_id})

        # If dump-html flag is set, print HTML and exit
        if ctx.obj.get("dump_html"):
            click.echo(html)
            return

        # Parse ascent data
        ascent_obj = scraper.parse_ascent_detail(html, ascent_id)

        if not ascent_obj:
            _error(f"Failed to parse ascent data for ID {ascent_id}")
            raise click.Abort()

        # Display results
        formatter.format_ascent_detail(ascent_obj, output_format)

    except Exception as e:
        _error(str(e))
        raise click.Abort() from e
    finally:
        client.close()


if __name__ == "__main__":
    main()
