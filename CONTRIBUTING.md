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

# Install pre-commit hooks
uv run pre-commit install

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

# Install pre-commit hooks
pre-commit install
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

### Pre-commit Hooks

Pre-commit hooks automatically check code before commits:

```bash
# Install hooks (one time setup)
uv run pre-commit install

# Run manually on all files
uv run pre-commit run --all-files
```

**Hooks verify:**

- **Ruff**: Formatting and linting (replaces Black, isort, flake8)
- **Bandit**: Security vulnerability checks
- **mypy**: Type checking
- File hygiene (trailing whitespace, end of file newlines, etc.)

### Manual Formatting and Linting

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

## Release Process (Maintainers Only)

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

### Creating a Release

```bash
# Preview what would be released
uv run semantic-release --noop version

# Create the release (updates version, changelog, creates tag)
uv run semantic-release version

# Build the package
uv build

# Publish to PyPI
uv tool run twine upload dist/*

# Create GitHub release
gh release create v0.2.0 --notes-from-tag
```

### Version Bumping Examples

| Commit Type | Example | New Version |
|-------------|---------|-------------|
| `fix:` | `fix: handle missing county data` | `0.1.1` |
| `feat:` | `feat: add JSON export for search results` | `0.2.0` |
| `feat:` with breaking change | `feat: new CLI structure`<br>`BREAKING CHANGE: ...` | `1.0.0` |
| Multiple `fix:` commits | 3x `fix:` commits | `0.1.1` (single bump) |
| `fix:` + `feat:` | Both types present | `0.2.0` (highest bump wins) |

### Manual Version Override

```bash
# Force a specific bump type
uv run semantic-release version --patch
uv run semantic-release version --minor
uv run semantic-release version --major

# Set exact version
uv run semantic-release version --bump-version 0.3.0
```

### Troubleshooting Releases

#### "No release will be made"

- No commits since last release follow conventional format
- Add a conventional commit or use `--patch/--minor/--major` flag

#### "Token value is missing"

- This warning is safe to ignore for manual releases
- Only needed for GitHub Actions automation

#### Wrong version calculated

- Review commits: `git log v0.1.0..HEAD --oneline`
- Check commit types match conventional format
- Use `--noop` flag to preview before committing

## License

Contributing to peakbagger-cli means your contributions receive MIT License terms.
