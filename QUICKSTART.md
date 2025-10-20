# Quick Start Guide

Get started with peakbagger-cli in 5 minutes.

## Installation

```bash
# With uv (recommended)
git clone <repo-url>
cd peakbagger-cli
uv sync

# With pip
pip install peakbagger-cli
```

## Basic Commands

```bash
# Search for peaks
peakbagger search "Mount Rainier"

# Get peak details
peakbagger info 2296

# JSON output
peakbagger search "Denali" --format json
peakbagger info 2296 --format json

# Full details from search
peakbagger search "Whitney" --full
```

## Common Use Cases

### Finding a peak ID

```bash
# Search returns peak IDs
peakbagger search "Rainier"
# Output includes Peak ID column - use that ID with 'info' command
```

### Automation & Scripting

```bash
# Extract elevation with jq
peakbagger info 2296 --format json | jq '.elevation.feet'

# Search and get all peak IDs
peakbagger search "Colorado" --format json | jq '.[].pid'

# Batch processing
for pid in 2296 271 163756; do
  peakbagger info $pid --format json >> peaks.json
done
```

### Python Integration

```python
import subprocess
import json

result = subprocess.run(
    ["peakbagger", "search", "Rainier", "--format", "json"],
    capture_output=True, text=True
)
peaks = json.loads(result.stdout)
print(peaks[0]["name"])
```

## Options

- `--format [text|json]`: Output format
- `--full`: Get complete details (search only)
- `--rate-limit FLOAT`: Seconds between requests (default: 2.0)

## Examples

See `examples/` directory for:
- Batch processing multiple peaks
- Exporting to CSV
- Filtering by elevation
- More advanced usage

## Next Steps

- Read [README.md](README.md) for full documentation
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Check [examples/](examples/) for code samples
