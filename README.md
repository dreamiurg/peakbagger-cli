# peakbagger-cli

A modern command-line interface for searching and retrieving mountain peak data from [PeakBagger.com](https://www.peakbagger.com).

Python 3.12+, Click, and Rich deliver a beautiful terminal experience.

## Features

- 🔍 **Search peaks** by name with instant results
- 📊 **Detailed peak info** including elevation, prominence, isolation, and location
- 🎨 **Beautiful output** with Rich-formatted tables and colors
- 🤖 **JSON output** for automation and scripting
- ⚡ **Fast and modern** using `uv` for dependency management
- 🛡️ **Respectful scraping** with configurable rate limiting
- 🌐 **Cloudflare bypass** for reliable access

## Installation

### Using uvx (Recommended - No Installation Required)

Run directly without installation using `uvx`:

```bash
# Run commands directly
uvx --from peakbagger-cli peakbagger search "Mount Rainier"
uvx --from peakbagger-cli peakbagger info 2296

# With options
uvx --from peakbagger-cli peakbagger search "Denali" --format json
```

This fetches and runs the latest version automatically. No installation or virtual environment needed.

### From PyPI

```bash
pip install peakbagger-cli
```

### From Source

Using `uv`:

```bash
git clone https://github.com/yourusername/peakbagger-cli.git
cd peakbagger-cli
uv sync
```

Using `pip`:

```bash
git clone https://github.com/yourusername/peakbagger-cli.git
cd peakbagger-cli
pip install -e .
```

## Quick Start

```bash
# Search for a peak
peakbagger search "Mount Rainier"

# Get detailed information
peakbagger info 2296

# Get JSON output for scripting
peakbagger search "Denali" --format json
```

## Usage

### Search Command

Search for peaks by name:

```bash
peakbagger search QUERY [OPTIONS]
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
peakbagger search "Mount Rainier"

# Get full details for all results
peakbagger search "Denali" --full

# JSON output for automation
peakbagger search "Whitney" --format json

# Custom rate limiting (3 seconds between requests)
peakbagger search "Rainier" --rate-limit 3.0
```

**Sample Output (text):**

```
                  Search Results
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Peak ID ┃ Name                             ┃ URL                             ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2296    │ Mount Rainier                    │ https://www.peakbagger.com/peak │
│         │                                  │ .aspx?pid=2296                  │
│ 24166   │ Mount Rainier - Southeast Crater │ https://www.peakbagger.com/peak │
│         │ Rim                              │ .aspx?pid=24166                 │
│ 163756  │ Mount Rainier - Columbia Crest   │ https://www.peakbagger.com/peak │
│         │                                  │ .aspx?pid=163756                │
└─────────┴──────────────────────────────────┴─────────────────────────────────┘

Found 3 peaks. Use 'peakbagger info <PID>' for details.
```

### Info Command

Get detailed information about a specific peak:

```bash
peakbagger info PEAK_ID [OPTIONS]
```

**Arguments:**
- `PEAK_ID`: The PeakBagger peak ID (e.g., "2296" for Mount Rainier)

**Options:**
- `--format [text|json]`: Output format (default: text)
- `--rate-limit FLOAT`: Seconds between requests (default: 2.0)

**Examples:**

```bash
# Get peak details (Mount Rainier)
peakbagger info 2296

# JSON output
peakbagger info 2296 --format json
```

**Sample Output (text):**

```
Mount Rainier, Washington
Peak ID: 2296

  Elevation               14,406 ft (4,391 m)
  Prominence              13,241 ft (4036 m)
  Isolation               731.13 mi (1176.64 km)
  Coordinates             46.851731, -121.760395
  County                  Pierce
  Country                 United States
  URL                     https://www.peakbagger.com/peak.aspx?pid=2296

Routes (3)
  1. Glacier Climb: Disappointment Cleaver
     Trailhead: Paradise (5,420 ft), Gain: 8,986 ft, Distance: 8.0 mi
  2. Glacier Climb: Emmons Glacier
     Trailhead: White River Campground (4,260 ft), Gain: 10,346 ft, Distance: 7.45 mi
  3. Glacier Climb: Kautz Glacier
     Trailhead: Paradise (5,420 ft), Gain: 9,286 ft, Distance: 5.65 mi

Peak Lists (39 total)
  • Mountaineers 6-Peak Pin - New Version (Rank #1)
  • Mountaineers 5-Peak Pin (Rank #1)
  • Contiguous 48 U.S. State High Points (Rank #3)
  • U.S. State High Points (Rank #4)
  • Washington Bulger List (Rank #1)
  ... and 34 more
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
      "rank": 1
    },
    {
      "list_name": "U.S. State High Points",
      "rank": 4
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

## Automation Examples

### Pipe to jq for filtering

```bash
# Get just the elevation in feet
peakbagger info 2296 --format json | jq '.elevation.feet'

# Search and extract peak IDs
peakbagger search "Rainier" --format json | jq '.[].pid'

# Get all route names for a peak
peakbagger info 2296 --format json | jq '.routes[].name'

# Find peaks on a specific list (search multiple peaks, filter by list)
peakbagger info 2296 --format json | jq '.peak_lists[] | select(.list_name | contains("Bulger"))'

# Get the easiest route (shortest distance)
peakbagger info 2296 --format json | jq '.routes | sort_by(.distance_mi) | .[0]'
```

### Batch processing

```bash
# Get details for multiple peaks
for pid in 2296 271 163756; do
  peakbagger info $pid --format json >> peaks.json
done
```

### Integration with scripts

```python
import subprocess
import json

# Search for peaks
result = subprocess.run(
    ["peakbagger", "search", "Denali", "--format", "json"],
    capture_output=True,
    text=True
)
peaks = json.loads(result.stdout)

for peak in peaks:
    print(f"{peak['name']}: {peak['pid']}")
```

**More examples:** See the [`examples/`](examples/) directory for complete scripts including batch processing, CSV export, and filtering by elevation.

## Configuration

### Rate Limiting

The CLI waits 2 seconds between requests by default to respect PeakBagger.com's servers. Adjust this as needed:

```bash
# Wait 3 seconds between requests
peakbagger search "Rainier" --rate-limit 3.0

# Minimum recommended: 1 second
peakbagger info 2296 --rate-limit 1.0
```

## Project Structure

```
peakbagger-cli/
├── peakbagger/
│   ├── __init__.py       # Package metadata
│   ├── cli.py            # Click CLI commands
│   ├── client.py         # HTTP client with rate limiting
│   ├── scraper.py        # HTML parsing logic
│   ├── models.py         # Data models
│   └── formatters.py     # Output formatting (Rich/JSON)
├── tests/                # Test suite (coming soon)
├── pyproject.toml        # Project configuration
├── README.md             # This file
├── CONTRIBUTING.md       # Contribution guide
└── LICENSE               # MIT License
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/peakbagger-cli.git
cd peakbagger-cli

# Set up development environment with uv
uv sync

# Run the CLI
uv run peakbagger --help
```

### Running Commands

```bash
# Run CLI commands during development
uv run peakbagger search "Rainier"
uv run peakbagger info 2296

# Check version
uv run peakbagger --version
```

## Technical Details

### Dependencies

- **Click**: CLI framework
- **cloudscraper**: Cloudflare bypass for HTTP requests
- **BeautifulSoup4**: HTML parsing
- **lxml**: Fast XML/HTML parser
- **Rich**: Beautiful terminal output

### How It Works

1. **Search**: Queries PeakBagger.com's search endpoint with your query
2. **Parse**: Extracts peak information from HTML using BeautifulSoup
3. **Format**: Displays results as Rich tables (text) or JSON
4. **Rate Limit**: Waits between requests to respect the server

### Data Sources

This tool scrapes all data from [PeakBagger.com](https://www.peakbagger.com), which aggregates peak information from USGS, LIDAR data, and user contributions.

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

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style guidelines, and submission instructions.

## Support

- **Bug Reports & Feature Requests**: [GitHub Issues](https://github.com/yourusername/peakbagger-cli/issues)
- **Questions & Discussions**: [GitHub Discussions](https://github.com/yourusername/peakbagger-cli/discussions)

## License

MIT License - see [LICENSE](LICENSE) file for details.
