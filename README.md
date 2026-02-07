# peakbagger-cli

[![CI](https://github.com/dreamiurg/peakbagger-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/dreamiurg/peakbagger-cli/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/peakbagger.svg)](https://pypi.org/project/peakbagger/)
[![Python Version](https://img.shields.io/pypi/pyversions/peakbagger.svg)](https://pypi.org/project/peakbagger/)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/dreamiurg/peakbagger-cli/badge)](https://securityscorecards.dev/viewer/?uri=github.com/dreamiurg/peakbagger-cli)
[![codecov](https://codecov.io/gh/dreamiurg/peakbagger-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/dreamiurg/peakbagger-cli)

A command-line interface for searching and retrieving mountain peak data from [PeakBagger.com](https://www.peakbagger.com).

## Features

- 🔍 **Search peaks** by name with instant results
- 📊 **Detailed peak info** including elevation, prominence, isolation, and location
- 📈 **Ascent statistics** - analyze climbing activity, seasonal patterns, and trip reports
- 🎨 **Beautiful output** with formatted tables and colors
- 🤖 **JSON output** for automation and scripting
- 🛡️ **Respectful scraping** with configurable rate limiting

> **For contributors**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## Installation

### Using uvx (Recommended)

Run directly without installation:

```bash
uvx peakbagger peak search "Mount Rainier"
uvx peakbagger peak show 2296
```

### From PyPI

```bash
pip install peakbagger
```

## Usage

### Search for peaks

```bash
peakbagger peak search "Mount Rainier"
peakbagger peak search "Denali" --format json
peakbagger peak search "Whitney" --full  # Fetch full details for all results
```

### Get peak details

```bash
peakbagger peak show 2296  # Mount Rainier
peakbagger peak show 2296 --format json
```

Output includes elevation, prominence, coordinates, routes, and peak lists.

### List peak ascents

```bash
peakbagger peak ascents 1798  # Mount Pilchuck
peakbagger peak ascents 1798 --within 1y  # Last year only
peakbagger peak ascents 1798 --with-gpx  # Only ascents with GPS tracks
peakbagger peak ascents 1798 --with-tr   # Only with trip reports
peakbagger peak ascents 1798 --limit 50  # First 50 ascents
```

Filters: `--after DATE`, `--before DATE`, `--within PERIOD` (e.g., `3m`, `1y`, `10d`)

### Analyze ascent statistics

```bash
peakbagger peak stats 1798
peakbagger peak stats 1798 --within 5y
peakbagger peak stats 1798 --reference-date 2024-07-15 --seasonal-window 30
```

Shows temporal breakdown, seasonal patterns, and monthly distribution.

### Get ascent details

```bash
peakbagger ascent show 12963
peakbagger ascent show 12963 --format json
```

Includes trip reports and route information.

## Examples

### Automation with jq

```bash
# Extract specific fields
peakbagger peak show 2296 --format json | jq '.elevation.feet'
peakbagger peak search "Rainier" --format json | jq '.[].pid'

# Find peaks on a specific list
peakbagger peak show 2296 --format json | jq '.peak_lists[] | select(.list_name | contains("Bulger"))'
```

### Batch processing

```bash
for pid in 2296 271 163756; do
  peakbagger peak show $pid --format json >> peaks.json
done
```

**More examples**: See [`examples/`](examples/) for complete scripts including CSV export and filtering.

## Configuration

### Logging

```bash
# Show HTTP requests
peakbagger --verbose peak search "Mount Rainier"
peakbagger -v peak show 2296

# Show detailed debug info
peakbagger --debug peak search "Mount Rainier"

# Suppress all output except data
peakbagger --quiet peak search "Mount Rainier"
peakbagger -q peak show 2296
```

Logs go to stderr, so you can redirect separately:

```bash
# Save JSON output, show logs on screen
peakbagger -v peak show 2296 --format json > peak.json

# Save output and logs separately
peakbagger -v peak show 2296 --format json > peak.json 2> logs.txt
```

### Rate Limiting

Default: 2 seconds between requests. Adjust as needed:

```bash
peakbagger peak search "Rainier" --rate-limit 3.0  # 3 seconds
```

## Ethical Use

Use this tool for **personal and educational purposes** only. Please:

- ✅ Respect the default rate limits (or increase them)
- ✅ Use for personal research and trip planning
- ✅ Attribute data to PeakBagger.com
- ❌ Don't mass-scrape or create bulk datasets
- ❌ Don't use for commercial purposes without permission
- ❌ Don't bypass rate limits to hammer the server

PeakBagger.com provides this data as a free service to the climbing community. Use this tool responsibly.

## Troubleshooting

**Cloudflare blocks**: Increase rate limit (`--rate-limit 3.0`) and wait before retrying.

**No results**: Try different search terms or verify the peak ID is correct.

**Installation issues**: Requires Python 3.12+ (`python3 --version`).

## Data Source

All data is scraped from [PeakBagger.com](https://www.peakbagger.com). The site aggregates peak information from USGS,
LIDAR data, and user contributions.

**Limitations**: No official API (scrapes HTML), rate-limited for respectful use, data accuracy depends on
PeakBagger.com.

## Support

- **Bug Reports & Features**: [GitHub Issues](https://github.com/dreamiurg/peakbagger-cli/issues)
- **Questions**: [GitHub Discussions](https://github.com/dreamiurg/peakbagger-cli/discussions)

## Other Mountaineering & Outdoors Tools

I climb, scramble, and hike a lot, and I keep building tools around it.
If this one's useful to you, the others might be too:

- **[mountaineers-mcp](https://github.com/dreamiurg/mountaineers-mcp)** --
  MCP server that lets AI assistants search and browse mountaineers.org.
  Activities, courses, trip reports, your account data.
- **[mountaineers-assistant](https://github.com/dreamiurg/mountaineers-assistant)** --
  Chrome extension that syncs your mountaineers.org activity history and
  shows you stats, trends, and climbing partners you can't see on the site.
- **[claude-mountaineering-skills](https://github.com/dreamiurg/claude-mountaineering-skills)** --
  Claude Code plugin that generates route beta reports by pulling conditions,
  forecasts, and trip reports from multiple mountaineering sites.

## License

MIT License - see [LICENSE](LICENSE) file for details.
