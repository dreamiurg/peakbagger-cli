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

## Development Setup

```bash
# First time setup - configure git hooks and commit template
bash scripts/setup-git-hooks.sh

# This will:
# - Install pre-commit hooks (prevents commits to master/main)
# - Configure commit message template with conventional commit format
```

## Development Commands

```bash
# Run CLI during development
uv run peakbagger peak search "Mount Rainier"
uv run peakbagger peak show 2296
uv run peakbagger peak ascents 2296
uv run peakbagger peak stats 2296
uv run peakbagger ascent show 12963

# Run with logging (useful for debugging)
uv run peakbagger --verbose peak search "Mount Rainier"  # Show HTTP requests
uv run peakbagger --debug peak show 2296  # Show detailed operations

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
npx semantic-release --dry-run

# Create release (done automatically via GitHub Actions)
# Just merge PR to main/master with conventional commit title
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
- **Logging**: Use loguru logger for all logging (never use print() for debugging)

## Project Structure

```
peakbagger/
├── __init__.py        # Version string (__version__)
├── cli.py             # Click commands (main entry point)
├── client.py          # HTTP client with rate limiting
├── scraper.py         # HTML parsing with BeautifulSoup
├── models.py          # Data models (Peak, SearchResult)
├── formatters.py      # Output formatting (Rich tables, JSON)
└── logging_config.py  # Logging configuration with loguru
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

### 6. Logging Guidelines
- Use loguru logger, NOT print() for debugging or informational output
- Log levels:
  - **INFO**: HTTP requests (method, URL, status code, response time)
  - **DEBUG**: Parsing details, rate-limiting waits, operational details
  - **ERROR**: Errors and exceptions
- By default, no logs are shown (level set to CRITICAL)
- Users enable logging via `--verbose` (INFO) or `--debug` (DEBUG) flags
- All logs go to stderr (allows easy redirection)
- Format:
  - **Verbose mode**: `HH:MM:SS | LEVEL | message` (clean, no file info)
  - **Debug mode**: `HH:MM:SS | LEVEL | file:line - message` (includes source location)

## Release Process

This project uses **semantic-release** (Node.js version) for automated version management and releases.

### Automated Releases

Releases are **fully automated** via GitHub Actions:
1. Push commits to `main` or `master` branch
2. GitHub Actions runs semantic-release
3. Version is bumped, CHANGELOG.md is updated
4. Git tag and GitHub release are created automatically

### Configuration Files

- `.releaserc.json` - Semantic-release configuration
- `.github/workflows/release.yml` - GitHub Actions workflow
- `scripts/update-version.py` - Updates version in pyproject.toml and __init__.py
- `package.json` - Node.js dependencies for semantic-release

### Manual Release Testing

To test what would be released (requires Node.js and npm):

```bash
# Install dependencies (first time only)
npm install

# Test release in dry-run mode (won't actually release)
npx semantic-release --dry-run
```

### Version Strategy
- Currently in `0.x.x` (pre-1.0 indicates beta/unstable)
- Breaking changes in 0.x still bump MINOR (0.1.0 → 0.2.0)
- After 1.0.0, breaking changes bump MAJOR
- Releases are created automatically on push to main/master

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

### Critical: When Output Formats Change

**ALWAYS check and update documentation** when modifying CLI output:

1. **README.md** - Check all "Sample Output" examples:
   - Search command text output (line ~108)
   - Info command text output (line ~150)
   - Info command JSON output (line ~165)

2. **CONTRIBUTING.md** - Check command examples in:
   - Testing section
   - Development tips
   - Release examples

3. **CLAUDE.md** - Update if new fields/formats are added

Output changes include:
- Adding/removing columns in tables
- Adding/removing fields in JSON
- Changing field names or formats
- Modifying table styles or layouts

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
- loguru >= 0.7.3

### Development (Python)
- pytest + pytest-cov
- ruff
- pre-commit
- mypy

### Development (Node.js - for semantic-release)
- semantic-release
- @semantic-release/changelog
- @semantic-release/git
- @semantic-release/exec
- @semantic-release/github

**Always use `uv add` and `uv add --dev`** to manage Python dependencies.
**Use `npm install`** for Node.js dependencies (semantic-release plugins).

## Questions or Unclear Instructions?

If instructions conflict or are unclear:
1. Check CONTRIBUTING.md for release process details
2. Check pyproject.toml for configuration
3. Check this file for project-specific rules
4. When in doubt, ask the user before proceeding
