# Contributing to peakbagger-cli

## Development Setup

### Prerequisites

- Python 3.12 or higher
- `uv` (recommended) or `pip`

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up the development environment
uv sync

# Run the CLI
uv run peakbagger --help
```

### Using pip

```bash
# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Project Structure

```text
peakbagger-cli/
├── peakbagger/           # Main package
│   ├── __init__.py       # Package version and metadata
│   ├── cli.py            # Click CLI commands and main entry point
│   ├── client.py         # HTTP client with rate limiting
│   ├── scraper.py        # HTML parsing and data extraction
│   ├── models.py         # Data models (Peak, SearchResult)
│   └── formatters.py     # Output formatting (Rich tables, JSON)
├── tests/                # Test suite
├── pyproject.toml        # Project configuration and dependencies
└── .pre-commit-config.yaml  # Code quality hooks
```

### Module Responsibilities

- **cli.py**: Defines Click commands (`search`, `info`), handles CLI arguments and options
- **client.py**: Manages HTTP requests with cloudscraper, implements rate limiting
- **scraper.py**: Parses HTML using BeautifulSoup, extracts peak data
- **models.py**: Defines data structures (Peak, SearchResult) and serialization
- **formatters.py**: Formats output (Rich tables for humans, JSON for machines)

## Code Quality

### Formatting and Linting

```bash
# Format code
uv run ruff format peakbagger tests

# Lint and auto-fix issues
uv run ruff check --fix peakbagger tests

# Lint without fixing
uv run ruff check peakbagger tests
```

### Style Guidelines

- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use descriptive variable names

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=peakbagger

# Test manually with real queries
uv run peakbagger search "Mount Rainier"
uv run peakbagger info 2296 --format json
```

## Development Tips

### Testing Against Real Website

Be respectful when testing against PeakBagger.com:

```bash
# Use increased rate limits during development
uv run peakbagger search "test" --rate-limit 5.0

# Test with well-known peaks that are unlikely to change
# Good: Mount Rainier (2296), Denali (271)
# Avoid: Obscure peaks that might not exist
```

### Working with HTML Parsing

When updating scraper logic:

1. Save sample HTML for testing:

   ```python
   response = client.get('/peak.aspx?pid=2296')
   with open('test_peak.html', 'w') as f:
       f.write(response)
   ```

1. Test parsing locally without network requests
1. Update tests with new HTML structure

## Release Process

### Automated Releases (Default)

**Releases are fully automated via GitHub Actions.** When commits are merged to the `main` branch:

1. GitHub Actions analyzes commit messages
2. If a release-triggering commit is found, the version is bumped automatically
3. CHANGELOG.md is updated
4. A Git tag and GitHub release are created

**No manual intervention needed** - just merge your PR with a conventional commit message.

### Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>: <description>

[optional body]

[optional footer(s)]
```

**Types that trigger releases:**

- `fix:` - Patches a bug (PATCH version bump: 0.1.0 → 0.1.1)
- `feat:` - Adds a new feature (MINOR version bump: 0.1.0 → 0.2.0)
- `perf:` - Performance improvement (PATCH version bump)
- `BREAKING CHANGE:` in footer - Breaking change (MAJOR version bump: 0.1.0 → 1.0.0)

**Types that don't trigger releases:**

- `docs:`, `style:`, `refactor:`, `test:`, `chore:`, `ci:`, `build:`

**Examples:**

```bash
# Patch release (0.1.0 → 0.1.1)
git commit -m "fix: correct elevation parsing for peaks without prominence data"

# Minor release (0.1.0 → 0.2.0)
git commit -m "feat: add support for searching peaks by elevation range"

# Major release (0.1.0 → 1.0.0)
git commit -m "feat: redesign CLI interface

BREAKING CHANGE: The --full flag has been replaced with --detailed"
```

### Manual Release (Fallback Only)

Manual releases are rarely needed but available for testing or troubleshooting:

```bash
# Preview what would be released
uv run semantic-release version --print

# Create release locally (testing/development only)
uv run semantic-release version --no-push --no-vcs-release
```

### Version Bumping Examples

| Commit Type | Example | New Version |
|-------------|---------|-------------|
| `fix:` | `fix: handle missing county data` | `0.1.1` |
| `feat:` | `feat: add JSON export for search results` | `0.2.0` |
| `feat:` with breaking change | `feat: new CLI structure`<br>`BREAKING CHANGE: ...` | `1.0.0` |
| Multiple `fix:` commits | 3x `fix:` commits | `0.1.1` (single bump) |
| `fix:` + `feat:` | Both types present | `0.2.0` (highest bump wins) |

## License

Contributing to peakbagger-cli means your contributions receive MIT License terms.
