# Examples

Practical examples demonstrating how to use peakbagger-cli for various tasks.

## Basic Examples

### 1. Simple Search and Info

```bash
# Search for a peak
peakbagger search "Mount Rainier"

# Get detailed info using the peak ID from search results
peakbagger info 2296
```

### 2. JSON Output for Automation

```bash
# Get JSON output
peakbagger search "Denali" --format json

# Extract specific fields with jq
peakbagger info 2296 --format json | jq '.elevation.feet'
```

### 3. Full Details Search

```bash
# Get complete details for all search results
peakbagger search "Whitney" --full
```

## Scripting Examples

See the Python scripts in this directory:

- **batch_peaks.py**: Fetch details for multiple peaks from a list
- **export_peaks.py**: Export peak data to CSV format
- **filter_peaks.py**: Search and filter peaks by elevation
- **trip_planner.py**: Plan trips by finding peaks in a region

## Running Examples

```bash
# Make sure peakbagger-cli is installed
uv sync

# Run a Python example
uv run python examples/batch_peaks.py

# Or if installed globally
python examples/batch_peaks.py
```
