#!/usr/bin/env python3
"""
Example: Export peak data to CSV format.

This script demonstrates how to:
- Search for peaks
- Fetch details for search results
- Export to CSV file
"""

import csv
import json
import subprocess
import sys
from pathlib import Path


def search_peaks(query: str) -> list[dict]:
    """Search for peaks and return results."""
    try:
        result = subprocess.run(
            ["peakbagger", "search", query, "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error searching for '{query}': {e}", file=sys.stderr)
        return []


def fetch_peak_details(peak_id: str) -> dict | None:
    """Fetch detailed peak information."""
    try:
        result = subprocess.run(
            ["peakbagger", "info", peak_id, "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error fetching peak {peak_id}: {e}", file=sys.stderr)
        return None


def export_to_csv(peaks: list[dict], filename: str):
    """Export peak data to CSV file."""
    if not peaks:
        print("No peaks to export", file=sys.stderr)
        return

    fieldnames = [
        "pid",
        "name",
        "state",
        "elevation_ft",
        "elevation_m",
        "prominence_ft",
        "prominence_m",
        "latitude",
        "longitude",
        "county",
        "country",
    ]

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for peak in peaks:
            row = {
                "pid": peak["pid"],
                "name": peak["name"],
                "state": peak.get("state", ""),
                "elevation_ft": peak["elevation"]["feet"],
                "elevation_m": peak["elevation"]["meters"],
                "prominence_ft": peak["prominence"]["feet"],
                "prominence_m": peak["prominence"]["meters"],
                "latitude": peak["location"]["latitude"],
                "longitude": peak["location"]["longitude"],
                "county": peak["location"].get("county", ""),
                "country": peak["location"].get("country", ""),
            }
            writer.writerow(row)


def main():
    """Search for peaks and export to CSV."""
    query = sys.argv[1] if len(sys.argv) > 1 else "Rainier"

    print(f"Searching for '{query}'...\n")
    search_results = search_peaks(query)

    if not search_results:
        print("No results found")
        return

    print(f"Found {len(search_results)} peaks. Fetching details...\n")

    peaks = []
    for result in search_results:
        print(f"  Fetching {result['name']}...")
        peak_data = fetch_peak_details(result["pid"])
        if peak_data:
            peaks.append(peak_data)

    # Export to CSV
    output_file = "peaks_export.csv"
    export_to_csv(peaks, output_file)
    print(f"\n✓ Exported {len(peaks)} peaks to {output_file}")


if __name__ == "__main__":
    main()
