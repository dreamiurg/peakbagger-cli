#!/usr/bin/env python3
"""
Example: Fetch details for multiple peaks from a list.

This script demonstrates how to:
- Read a list of peak IDs
- Fetch details for each peak
- Export to JSON file
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def fetch_peak_details(peak_id: str) -> dict[str, Any] | None:
    """Fetch peak details using peakbagger CLI."""
    try:
        result = subprocess.run(
            ["peakbagger", "info", peak_id, "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)  # type: ignore[no-any-return]
    except subprocess.CalledProcessError as e:
        print(f"Error fetching peak {peak_id}: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for peak {peak_id}: {e}", file=sys.stderr)
        return None


def main():
    """Fetch details for a list of peaks."""
    # List of peak IDs to fetch
    # Examples: Mount Rainier, Denali, Mount Whitney
    peak_ids = ["2296", "271", "163756"]

    print(f"Fetching details for {len(peak_ids)} peaks...\n")

    peaks = []
    for peak_id in peak_ids:
        print(f"Fetching peak {peak_id}...")
        peak_data = fetch_peak_details(peak_id)
        if peak_data:
            peaks.append(peak_data)
            print(f"  ✓ {peak_data['name']}")
        else:
            print(f"  ✗ Failed to fetch peak {peak_id}")

    # Save to JSON file
    output_file = Path("peaks_batch.json")
    with open(output_file, "w") as f:
        json.dump(peaks, f, indent=2)

    print(f"\n✓ Saved {len(peaks)} peaks to {output_file}")


if __name__ == "__main__":
    main()
