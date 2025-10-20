"""CLI interface for peakbagger."""

import click

from peakbagger import __version__
from peakbagger.client import PeakBaggerClient
from peakbagger.formatters import PeakFormatter
from peakbagger.scraper import PeakBaggerScraper


@click.group()
@click.version_option(version=__version__)
def main():
    """PeakBagger CLI - Search and retrieve mountain peak data from PeakBagger.com"""
    pass


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
def search(query: str, output_format: str, full: bool, rate_limit: float):
    """
    Search for peaks by name.

    QUERY: Search term (e.g., "Mount Rainier", "Denali")

    Examples:

      peakbagger search "Mount Rainier"

      peakbagger search "Denali" --format json

      peakbagger search "Whitney" --full
    """
    client = PeakBaggerClient(rate_limit_seconds=rate_limit)
    scraper = PeakBaggerScraper()
    formatter = PeakFormatter()

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
            peaks = []
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
def info(peak_id: str, output_format: str, rate_limit: float):
    """
    Get detailed information about a specific peak.

    PEAK_ID: The PeakBagger peak ID (e.g., "2296" for Mount Rainier)

    Examples:

      peakbagger info 2296

      peakbagger info 2296 --format json
    """
    client = PeakBaggerClient(rate_limit_seconds=rate_limit)
    scraper = PeakBaggerScraper()
    formatter = PeakFormatter()

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


if __name__ == "__main__":
    main()
