#!/usr/bin/env python3
"""
Example: Filter peaks by elevation.

This script demonstrates how to:
- Search for peaks
- Fetch details for each result
- Filter by minimum elevation
- Display filtered results
"""

import json
import subprocess
import sys


def search_and_filter(query: str, min_elevation_ft: int):
    """Search for peaks and filter by minimum elevation."""
    # Search for peaks
    print(f"Searching for '{query}'...")
    result = subprocess.run(
        ["peakbagger", "search", query, "--format", "json"],
        capture_output=True,
        text=True,
        check=True,
    )
    search_results = json.loads(result.stdout)
    print(f"Found {len(search_results)} peaks\n")

    # Fetch details and filter
    print(f"Filtering peaks with elevation >= {min_elevation_ft:,} ft...\n")
    filtered_peaks = []

    for peak_result in search_results:
        result = subprocess.run(
            ["peakbagger", "info", peak_result["pid"], "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        peak_data = json.loads(result.stdout)

        elevation = peak_data["elevation"]["feet"]
        if elevation and elevation >= min_elevation_ft:
            filtered_peaks.append(peak_data)

    # Display results
    if filtered_peaks:
        print(f"Found {len(filtered_peaks)} peaks matching criteria:\n")
        for peak in sorted(filtered_peaks, key=lambda p: p["elevation"]["feet"], reverse=True):
            print(
                f"  {peak['name']:40} {peak['elevation']['feet']:>6,} ft  "
                f"({peak['elevation']['meters']:,} m)"
            )
    else:
        print(f"No peaks found with elevation >= {min_elevation_ft:,} ft")


def main():
    """Main entry point."""
    query = sys.argv[1] if len(sys.argv) > 1 else "Colorado"
    min_elevation = int(sys.argv[2]) if len(sys.argv) > 2 else 14000

    search_and_filter(query, min_elevation)


if __name__ == "__main__":
    main()
