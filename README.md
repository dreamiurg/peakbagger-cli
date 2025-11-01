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
- 🌐 **Cloudflare bypass** for reliable access

> **For contributors**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code guidelines, and release process.

## Installation

### Using uvx (Recommended - No Installation Required)

Run directly without installation using `uvx`:

```bash
# Run commands directly
uvx peakbagger peak search "Mount Rainier"
uvx peakbagger peak show 2296

# With options
uvx peakbagger peak search "Denali" --format json
```

This fetches and runs the latest version automatically. No installation or virtual environment needed.

### From PyPI

```bash
pip install peakbagger
```

### From Source

Using `uv`:

```bash
git clone https://github.com/dreamiurg/peakbagger-cli.git
cd peakbagger-cli
uv sync
```

Using `pip`:

```bash
git clone https://github.com/dreamiurg/peakbagger-cli.git
cd peakbagger-cli
pip install -e .
```

## Quick Start

```bash
# Search for a peak
peakbagger peak search "Mount Rainier"

# Get detailed information
peakbagger peak show 2296

# List recent ascents
peakbagger peak ascents 1798

# Analyze ascent statistics
peakbagger peak stats 1798

# Get JSON output for scripting
peakbagger peak search "Denali" --format json
```

## Usage

### Peak Search Command

Search for peaks by name:

```bash
peakbagger peak search QUERY [OPTIONS]
```

**Arguments:**

- `QUERY`: Search term (e.g., "Mount Rainier", "Denali", "Whitney")

**Options:**

- `--format [text|json]`: Output format (default: text)
- `--full`: Fetch full details for all search results
- `--rate-limit FLOAT`: Seconds between requests (default: 2.0)

**Examples:**

```bash
# Basic search - shows table with Peak ID and Name
peakbagger peak search "Mount Rainier"

# Get full details for all results
peakbagger peak search "Denali" --full

# JSON output for automation
peakbagger peak search "Whitney" --format json

# Custom rate limiting (3 seconds between requests)
peakbagger peak search "Rainier" --rate-limit 3.0
```

**Sample Output (text):**

```text
Search Results
 Peak ID  Name                                  Location  Range          Elevation            URL
 2296     Mount Rainier                         USA-WA    Cascade Range  14,406 ft / 4,391 m  https://www.peakbagger.com/peak.aspx?pid=2296
 24166    Mount Rainier - Southeast Crater Rim  USA-WA    Cascade Range  14,200 ft / 4,328 m  https://www.peakbagger.com/peak.aspx?pid=24166
 163756   Mount Rainier - Columbia Crest        USA-WA    Cascade Range  14,396 ft / 4,388 m  https://www.peakbagger.com/peak.aspx?pid=163756
 93794    Rainier Lookout Site                  USA-WA    Cascade Range  500 ft / 152 m       https://www.peakbagger.com/peak.aspx?pid=93794
 -88211   Rainier View                          USA-WA    -              400 ft / 122 m       https://www.peakbagger.com/peak.aspx?pid=-88211
```

### Peak Show Command

Get detailed information about a specific peak:

```bash
peakbagger peak show PEAK_ID [OPTIONS]
```

**Arguments:**

- `PEAK_ID`: The PeakBagger peak ID (e.g., "2296" for Mount Rainier)

**Options:**

- `--format [text|json]`: Output format (default: text)
- `--rate-limit FLOAT`: Seconds between requests (default: 2.0)

**Examples:**

```bash
# Get peak details (Mount Rainier)
peakbagger peak show 2296

# JSON output
peakbagger peak show 2296 --format json
```

**Sample Output (text):**

```text
Mount Rainier, Washington
Peak ID: 2296

  Elevation               14,406 ft (4,391 m)
  Prominence              13,241 ft (4036 m)
  Isolation               731.13 mi (1176.64 km)
  Coordinates             46.851731, -121.760395
  County                  Pierce
  Country                 United States
  Ascents Logged          4,388 (3,960 viewable)
  URL                     https://www.peakbagger.com/peak.aspx?pid=2296

Routes (3)
  1. Glacier Climb: Disappointment Cleaver
     Trailhead: Paradise (5,420 ft), Gain: 8,986 ft, Distance: 8.0 mi
  2. Glacier Climb: Emmons Glacier
     Trailhead: White River Campground (4,260 ft), Gain: 10,346 ft, Distance: 7.45 mi
  3. Glacier Climb: Kautz Glacier
     Trailhead: Paradise (5,420 ft), Gain: 9,286 ft, Distance: 5.65 mi

Peak Lists (39 total)
  1. Mountaineers 6-Peak Pin - New Version (Rank #1) - https://www.peakbagger.com/list.aspx?lid=5030
  2. Mountaineers 5-Peak Pin (Rank #1) - https://www.peakbagger.com/list.aspx?lid=5031
  3. Mountaineers 6-Peak Pin [Historic] (Rank #1) - https://www.peakbagger.com/list.aspx?lid=50301
  4. Contiguous 48 U.S. State High Points (Rank #3) - https://www.peakbagger.com/list.aspx?lid=12005
  5. U.S. State High Points (Rank #4) - https://www.peakbagger.com/list.aspx?lid=12003
  6. Mazamas Sixteen Northwest Peaks Award (Rank #1) - https://www.peakbagger.com/list.aspx?lid=5063
  7. United States State/Territory High Points (Rank #4) - https://www.peakbagger.com/list.aspx?lid=120031
  8. Triple Crown CoHPs (Rank #1) - https://www.peakbagger.com/list.aspx?lid=823
  9. USA Lower 48 Range3 High Points (Rank #3) - https://www.peakbagger.com/list.aspx?lid=16110
  10. Chemeketan Eighteen Northwest Peaks Award (Rank #1) - https://www.peakbagger.com/list.aspx?lid=5012
  ... and 29 more
```

**Sample Output (JSON):**

```json
{
  "pid": "2296",
  "name": "Mount Rainier",
  "state": "Washington",
  "elevation": {
    "feet": 14406,
    "meters": 4391
  },
  "prominence": {
    "feet": 13241,
    "meters": 4036
  },
  "location": {
    "latitude": 46.851731,
    "longitude": -121.760395,
    "county": "Pierce",
    "country": "United States"
  },
  "isolation": {
    "miles": 731.13,
    "kilometers": 1176.64
  },
  "url": "https://www.peakbagger.com/peak.aspx?pid=2296",
  "peak_lists": [
    {
      "list_name": "Mountaineers 6-Peak Pin - New Version",
      "rank": 1,
      "url": "https://www.peakbagger.com/list.aspx?lid=5030"
    },
    {
      "list_name": "U.S. State High Points",
      "rank": 4,
      "url": "https://www.peakbagger.com/list.aspx?lid=12003"
    }
  ],
  "routes": [
    {
      "name": "Glacier Climb: Disappointment Cleaver",
      "trailhead": "Paradise",
      "trailhead_elevation_ft": 5420,
      "vertical_gain_ft": 8986,
      "distance_mi": 8.0
    }
  ]
}
```

### Peak Ascents Command

List ascents for a specific peak with optional filtering:

```bash
peakbagger peak ascents PEAK_ID [OPTIONS]
```

**Arguments:**

- `PEAK_ID`: The PeakBagger peak ID (e.g., "1798" for Mount Pilchuck)

**Options:**

- `--format [text|json]`: Output format (default: text)
- `--after DATE`: Filter ascents on or after date (YYYY-MM-DD)
- `--before DATE`: Filter ascents on or before date (YYYY-MM-DD)
- `--within PERIOD`: Filter ascents within period from today (e.g., '3m', '1y', '10d')
- `--with-gpx`: Only show ascents with GPX tracks
- `--with-tr`: Only show ascents with trip reports
- `--limit N`: Maximum number of ascents to display (default: 100)
- `--rate-limit FLOAT`: Seconds between requests (default: 2.0)

**Examples:**

```bash
# List recent ascents (Mount Pilchuck)
peakbagger peak ascents 1798

# Show ascents from the last year
peakbagger peak ascents 1798 --within 1y

# Filter by date range
peakbagger peak ascents 1798 --after 2020-01-01 --before 2023-12-31

# Show only ascents with GPX tracks
peakbagger peak ascents 1798 --with-gpx

# Show only ascents with trip reports
peakbagger peak ascents 1798 --with-tr

# Combine filters (ascents from last year with trip reports)
peakbagger peak ascents 1798 --within 1y --with-tr

# Show first 50 ascents only
peakbagger peak ascents 1798 --limit 50

# JSON output
peakbagger peak ascents 1798 --format json
```

**Use Cases:**

- **Trip Planning**: Check recent climbs to gauge popularity and current conditions
- **Route Research**: See which routes are most popular
- **GPX Track Finding**: Filter to ascents with GPS tracks for route planning
- **Trip Report Research**: Find detailed trip reports for beta

### Peak Stats Command

Show statistical analysis of ascents for a specific peak:

```bash
peakbagger peak stats PEAK_ID [OPTIONS]
```

**Arguments:**

- `PEAK_ID`: The PeakBagger peak ID (e.g., "1798" for Mount Pilchuck)

**Options:**

- `--format [text|json]`: Output format (default: text)
- `--after DATE`: Include only ascents on or after date (YYYY-MM-DD)
- `--before DATE`: Include only ascents on or before date (YYYY-MM-DD)
- `--within PERIOD`: Analyze ascents within period from today (e.g., '3m', '1y', '10d')
- `--reference-date DATE`: Reference date for seasonal analysis (YYYY-MM-DD, default: today)
- `--seasonal-window N`: Days before/after reference date for seasonal window (default: 14)
- `--rate-limit FLOAT`: Seconds between requests (default: 2.0)

**Examples:**

```bash
# Basic ascent statistics (Mount Pilchuck)
peakbagger peak stats 1798

# Analyze ascents from the last 5 years
peakbagger peak stats 1798 --within 5y

# Filter by date range
peakbagger peak stats 1798 --after 2020-01-01 --before 2023-12-31

# Custom seasonal analysis (check July climbing conditions)
peakbagger peak stats 1798 --reference-date 2024-07-15 --seasonal-window 30

# JSON output
peakbagger peak stats 1798 --format json
```

**Sample Output (text):**

```text
=== Overall Statistics ===

  Total ascents                1687
  With GPX tracks              64 (3.8%)
  With trip reports            222 (13.2%)

=== Temporal Breakdown ===

  Last 3 months                48
  Last year                    106
  Last 5 years                 397

=== Seasonal Pattern ===

  October     : 110
  November    : 19

=== Monthly Distribution ===

  January     : 110
  February    : 23
  March       : 27
  April       : 48
  May         : 136
  June        : 204
  July        : 320
  August      : 248
  September   : 205
  October     : 155
  November    : 87
  December    : 31
```

**Use Cases:**

- **Seasonal Analysis**: Find the best time of year to climb based on historical patterns
- **Popularity Trends**: Understand climbing activity over different time periods
- **Data Analysis**: Export to JSON for custom analysis and visualization

### Get Ascent Details

Get detailed information about a specific ascent, including trip reports:

```bash
peakbagger ascent show ASCENT_ID [OPTIONS]
```

**Arguments:**

- `ASCENT_ID`: The PeakBagger ascent ID (e.g., "12963")

**Options:**

- `--format [text|json]`: Output format (default: text)
- `--rate-limit FLOAT`: Seconds between requests (default: 2.0)

**Examples:**

```bash
# Get detailed ascent information
peakbagger ascent show 12963

# JSON output
peakbagger ascent show 12963 --format json
```

**Sample Output (text):**

```text
Field                 Value
 Ascent ID             12963 https://www.peakbagger.com/climber/ascent.aspx?aid=12963
 Climber               Bob Bolton (555) https://www.peakbagger.com/climber/climber.aspx?cid=555
 Date                  1951
 Ascent Type           Successful Summit Attained
 Peak                  Mount Pilchuck (1798) https://www.peakbagger.com/peak.aspx?pid=1798
 Location              USA-Washington
 Elevation             5,341 ft (1,627 m)
 Has GPX               No
 Has Trip Report       No

Trip Report:
────────────────────────────────────────────────────────
My dad took a group of kids to hike Pilchuck including my oldest sister Elsie. Not sure about my next older sister Erlene. I must have begged to go along because I can't believe they would have taken me if I hadn't begged. But I did well for a 4-year-old on the ascent, and always remembered that of the 12 hikers I was 4 years old and 4th to the summit. The descent, on the other hand, was somewhat of a disaster as my quads gave out pretty quickly and I had to ride my dad's shoulders much of the way. This was when I learned I had a problem with my quads that I've struggled with all my life. It affected my running days during the 1990s and 2000s, and every year conditioning my quads has been an important part of "spring training", if you will. Note that my dad and I returned to Pilchuck 50 years later when he was 86, see that TR here .
```

**Sample Output (JSON):**

```json
{
  "ascent_id": "12963",
  "climber": {
    "name": "Bob Bolton",
    "id": "555"
  },
  "date": "1951",
  "has_gpx": false,
  "route": null,
  "url": "https://www.peakbagger.com/climber/ascent.aspx?aid=12963",
  "trip_report": {
    "has_report": true,
    "word_count": null,
    "text": "My dad took a group of kids to hike Pilchuck..."
  },
  "ascent_type": "Successful Summit Attained",
  "peak": {
    "name": "Mount Pilchuck",
    "id": "1798",
    "location": "USA-Washington",
    "elevation_ft": 5341,
    "elevation_m": 1627
  }
}
```

**Use Cases:**

- **Trip Report Research**: Read detailed trip reports for route beta and conditions
- **Historical Ascents**: Learn about classic climbs and early ascents
- **Route Information**: Get details about specific routes and approaches

## Automation Examples

### Pipe to jq for filtering

```bash
# Get just the elevation in feet
peakbagger peak show 2296 --format json | jq '.elevation.feet'

# Search and extract peak IDs
peakbagger peak search "Rainier" --format json | jq '.[].pid'

# Get all route names for a peak
peakbagger peak show 2296 --format json | jq '.routes[].name'

# Find peaks on a specific list (search multiple peaks, filter by list)
peakbagger peak show 2296 --format json | jq '.peak_lists[] | select(.list_name | contains("Bulger"))'

# Get the easiest route (shortest distance)
peakbagger peak show 2296 --format json | jq '.routes | sort_by(.distance_mi) | .[0]'
```

### Batch processing

```bash
# Get details for multiple peaks
for pid in 2296 271 163756; do
  peakbagger peak show $pid --format json >> peaks.json
done
```

### Integration with scripts

```python
import subprocess
import json

# Search for peaks
result = subprocess.run(
    ["peakbagger", "peak", "search", "Denali", "--format", "json"],
    capture_output=True,
    text=True
)
peaks = json.loads(result.stdout)

for peak in peaks:
    print(f"{peak['name']}: {peak['pid']}")
```

**More examples:** See the [`examples/`](examples/) directory for complete scripts including
batch processing, CSV export, and filtering by elevation.

## Configuration

### Global Options

The CLI supports global flags that apply to all commands:

```bash
# Show verbose logging (HTTP requests)
peakbagger --verbose peak search "Mount Rainier"
peakbagger -v peak show 2296

# Show debug logging (detailed operations)
peakbagger --debug peak search "Mount Rainier"

# Suppress informational messages
peakbagger --quiet peak search "Mount Rainier"
peakbagger -q peak show 2296
```

### Logging

By default, the CLI shows minimal output. Use logging flags to see what's happening under the hood:

**Verbose Mode (`--verbose` / `-v`)**: Shows HTTP requests with timing

```bash
peakbagger --verbose peak show 2296
# Output:
# 18:55:25 | INFO     | GET https://www.peakbagger.com/peak.aspx?pid=2296 - 200 - 847ms
```

**Debug Mode (`--debug`)**: Shows detailed parsing and rate limiting with file locations

```bash
peakbagger --debug peak show 2296
# Output:
# 18:55:25 | INFO     | client.py:77 - GET https://www.peakbagger.com/peak.aspx?pid=2296 - 200 - 847ms
# 18:55:25 | DEBUG    | scraper.py:114 - Parsing peak detail for peak ID 2296
# 18:55:25 | DEBUG    | scraper.py:130 - Extracted peak name: Mount Rainier, state: Washington
# 18:55:25 | DEBUG    | scraper.py:144 - Extracted elevation: 14406 ft / 4391 m
# 18:55:25 | DEBUG    | client.py:45 - Rate limiting: waiting 2.00s before next request
```

**Redirecting Logs**: Logs go to stderr, so you can redirect them separately:

```bash
# Save output to file, show logs on screen
peakbagger -v peak show 2296 --format json > peak.json

# Save output to file, discard logs
peakbagger -v peak show 2296 --format json > peak.json 2>/dev/null

# Save both output and logs separately
peakbagger -v peak show 2296 --format json > peak.json 2> logs.txt
```

### Rate Limiting

The CLI waits 2 seconds between requests by default to respect PeakBagger.com's servers. Adjust this as needed:

```bash
# Wait 3 seconds between requests
peakbagger peak search "Rainier" --rate-limit 3.0

# Minimum recommended: 1 second
peakbagger peak show 2296 --rate-limit 1.0
```

## Data Source

All data is scraped from [PeakBagger.com](https://www.peakbagger.com).
The site aggregates peak information from USGS, LIDAR data, and user contributions.

## Limitations

- **No official API**: This tool scrapes HTML; website changes may break functionality
- **Rate limiting**: Runs slowly to respect the website (2s default between requests)
- **Data accuracy**: Depends on PeakBagger.com's data quality
- **No authentication**: Accesses public peak data only

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

### Cloudflare blocks

Cloudflare errors require these actions:

- Increase the rate limit: `--rate-limit 3.0`
- Wait a few minutes before retrying
- Check PeakBagger.com access in your browser

### No results found

- Try different search terms (e.g., "Rainier" instead of "Mount Rainier")
- Check the peak ID is correct for `info` command
- Verify PeakBagger.com is online

### Installation issues

Verify Python 3.12+ installation:

```bash
python3 --version  # Should be 3.12 or higher
```

## Support

- **Bug Reports & Feature Requests**: [GitHub Issues](https://github.com/dreamiurg/peakbagger-cli/issues)
- **Questions & Discussions**: [GitHub Discussions](https://github.com/dreamiurg/peakbagger-cli/discussions)

## License

MIT License - see [LICENSE](LICENSE) file for details.
