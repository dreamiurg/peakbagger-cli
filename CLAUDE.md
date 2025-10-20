# Claude Instructions for peakbagger-cli

This file contains project-specific instructions for Claude Code (or any AI assistant) working on this project.

## Project Overview

A Python CLI tool for scraping mountain peak data from PeakBagger.com. Uses Click for CLI, cloudscraper for Cloudflare bypass, BeautifulSoup for HTML parsing, and Rich for terminal output.

## Technology Stack

- **Python**: 3.12+ (use modern syntax: `X | None` instead of `Optional[X]`)
- **Package Manager**: `uv` (NOT pip) - use `uv run`, `uv sync`, `uv add`
- **CLI Framework**: Click
- **Scraping**: cloudscraper + BeautifulSoup4 + lxml
- **Output**: Rich (tables, colors) + JSON
- **Linting/Formatting**: Ruff (NOT Black, isort, or flake8)
- **Version Management**: python-semantic-release
- **Pre-commit**: Configured with multiple hooks

## Development Commands

```bash
# Run CLI during development
uv run peakbagger search "Mount Rainier"
uv run peakbagger info 2296

# Format and lint
uv run ruff format peakbagger tests
uv run ruff check --fix peakbagger tests

# Run pre-commit hooks
uv run pre-commit run --all-files

# Run tests
uv run pytest --cov=peakbagger

# Build package
uv build

# Preview next release
uv run semantic-release --noop version

# Create release
uv run semantic-release version
```

## Commit Message Format

**CRITICAL**: This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated version management with python-semantic-release.

### Format

```
<type>: <description>

[optional body]

[optional footer]
```

### Commit Types

**Types that trigger releases:**
- `fix:` - Bug fix (PATCH: 0.1.0 → 0.1.1)
- `feat:` - New feature (MINOR: 0.1.0 → 0.2.0)
- `perf:` - Performance improvement (PATCH)
- Footer with `BREAKING CHANGE:` - Breaking change (MAJOR: 0.1.0 → 1.0.0)

**Types that don't trigger releases:**
- `docs:` - Documentation only changes
- `style:` - Code style/formatting (no logic changes)
- `refactor:` - Code refactoring (no feature change)
- `test:` - Adding or updating tests
- `chore:` - Maintenance, dependencies, tooling
- `ci:` - CI/CD configuration
- `build:` - Build system changes

### Examples

```bash
# Patch release
git commit -m "fix: handle missing elevation data in scraper"

# Minor release
git commit -m "feat: add --limit flag to search command"

# Major release
git commit -m "feat: redesign CLI commands

BREAKING CHANGE: renamed --full to --detailed for consistency"

# No release
git commit -m "docs: update README installation instructions"
git commit -m "chore: update dependencies"
git commit -m "refactor: extract parsing logic into helper methods"
```

### Commit Message Guidelines

- **First line**: Imperative mood ("add" not "added" or "adds")
- **First line**: Lowercase after colon
- **First line**: No period at end
- **First line**: Max 50 characters (preferably)
- **Body**: Wrap at 72 characters
- **Body**: Explain *why* not *what* (the diff shows what changed)

### Multi-line Commits

```bash
git commit -m "feat: add support for batch peak lookup

Adds new --batch flag that accepts a file containing peak IDs.
Processes peaks with proper rate limiting and error handling.

Closes #42"
```

## Code Style

- **Type hints**: Always use for function parameters and return values
- **Docstrings**: Required for all public functions and classes
- **Modern Python**: Use `X | None`, not `Optional[X]`
- **Error handling**: Use proper exception chaining (`raise ... from e`)
- **Rich output**: Use Rich for user-facing terminal output, not print()
- **JSON output**: Must be valid, parseable JSON (no Rich formatting in JSON mode)

## Project Structure

```
peakbagger/
├── __init__.py       # Version string (__version__)
├── cli.py            # Click commands (main entry point)
├── client.py         # HTTP client with rate limiting
├── scraper.py        # HTML parsing with BeautifulSoup
├── models.py         # Data models (Peak, SearchResult)
└── formatters.py     # Output formatting (Rich tables, JSON)
```

## Important Project-Specific Rules

### 1. Rate Limiting is Mandatory
- **Always** respect the 2-second default rate limit
- Client has `rate_limit_seconds` parameter (default: 2.0)
- Never bypass or reduce rate limiting in production code

### 2. HTML Parsing Best Practices
- Test parsing against real HTML saved locally
- PeakBagger.com structure may change - make parsing resilient
- Always handle missing data gracefully (return None, not crash)
- Use `get_text(strip=True)` to clean whitespace

### 3. Output Formats
- **Text mode**: Use Rich tables with colors (default)
- **JSON mode**: Pure JSON, no Rich formatting, must be parseable
- Both modes must show the same data (just different format)

### 4. Cloudflare Bypass
- Use cloudscraper, not plain requests
- Set clear User-Agent identifying the tool
- PeakBagger.com blocks curl and simple requests

### 5. Testing Against Real Website
- Use increased rate limits during development (`--rate-limit 5.0`)
- Test with well-known peaks (Mount Rainier: 2296, Denali: 271)
- Don't hammer the server - save sample HTML for testing

## Release Process

This project uses **python-semantic-release** for version management.

### Before Making Changes
- Check current version: `uv run semantic-release version --print`
- Preview what would be released: `uv run semantic-release --noop version`

### Creating a Release
1. Ensure commits follow conventional format
2. Run: `uv run semantic-release version`
3. Build: `uv build`
4. Publish: `uv tool run twine upload dist/*`

### Version Strategy
- Currently in `0.x.x` (pre-1.0 indicates beta/unstable)
- Breaking changes in 0.x still bump MINOR (0.1.0 → 0.2.0)
- After 1.0.0, breaking changes bump MAJOR

## Common Mistakes to Avoid

1. ❌ Using `pip` instead of `uv`
2. ❌ Using `Optional[X]` instead of `X | None`
3. ❌ Using `print()` instead of Rich Console
4. ❌ Committing without conventional commit format
5. ❌ Using Black, isort, or flake8 (we use Ruff for everything)
6. ❌ Reducing rate limits below 2 seconds
7. ❌ Testing extensively against live website (save HTML samples)

## Files to Always Update Together

When changing functionality:
- Update code in `peakbagger/`
- Update relevant examples in `examples/` if applicable
- Update README.md if user-facing behavior changes
- Update CONTRIBUTING.md if development process changes

## Documentation Philosophy

- **Less is more** - only document project-specific information
- No generic Git/GitHub instructions (developers know this)
- Focus on what makes *this* project different
- Link to external docs rather than duplicating them

## Dependencies

### Production
- click >= 8.0.0
- cloudscraper >= 1.2.0
- beautifulsoup4 >= 4.9.0
- lxml >= 4.6.0
- rich >= 10.0.0

### Development
- pytest + pytest-cov
- ruff
- pre-commit
- python-semantic-release

**Always use `uv add` and `uv add --dev`** to manage dependencies.

## Questions or Unclear Instructions?

If instructions conflict or are unclear:
1. Check CONTRIBUTING.md for release process details
2. Check pyproject.toml for configuration
3. Check this file for project-specific rules
4. When in doubt, ask the user before proceeding
