# Contributing to peakbagger-cli

## Quick Setup

```bash
# Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/dreamiurg/peakbagger-cli.git
cd peakbagger-cli
uv sync

# Run the CLI
uv run peakbagger --help
```

## Development Workflow

```bash
# Format and lint
uv run ruff format peakbagger tests
uv run ruff check --fix peakbagger tests

# Run tests
uv run pytest --cov=peakbagger

# Run pre-commit hooks
uv run pre-commit run --all-files
```

## Project Structure

```text
peakbagger/
├── cli.py            # Click commands
├── client.py         # HTTP client with rate limiting
├── scraper.py        # HTML parsing
├── models.py         # Data models
├── formatters.py     # Output formatting (Rich/JSON)
├── statistics.py     # Ascent statistics
└── logging_config.py # Logging setup
```

## Code Guidelines

- Use type hints for all function parameters and return values
- Write docstrings for public functions and classes
- Use modern Python syntax: `X | None` instead of `Optional[X]`
- Handle missing data gracefully (PeakBagger data is inconsistent)
- Use loguru logger for debugging, never `print()`
- Follow existing patterns in similar commands

## Testing

```bash
# Run all tests
uv run pytest

# With coverage report
uv run pytest --cov=peakbagger

# Test against live site (be respectful!)
uv run peakbagger search "Mount Rainier" --rate-limit 5.0
```

## Commit Message Format

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated releases.

**Format:**

```text
<type>: <description>

[optional body]
[optional footer]
```

**Types that trigger releases:**

- `feat:` - New feature (bumps MINOR: 0.1.0 → 0.2.0)
- `fix:` - Bug fix (bumps PATCH: 0.1.0 → 0.1.1)
- `perf:` - Performance improvement (bumps PATCH)
- `BREAKING CHANGE:` in footer - Breaking change (bumps MAJOR: 0.1.0 → 1.0.0)

**Types that don't trigger releases:**

- `docs:`, `style:`, `refactor:`, `test:`, `chore:`, `ci:`, `build:`

**Examples:**

```bash
# Patch release
git commit -m "fix: handle missing elevation data"

# Minor release
git commit -m "feat: add CSV export for search results"

# Major release
git commit -m "feat: redesign CLI

BREAKING CHANGE: removed --full flag in favor of --detailed"
```

## Release Process

Releases are **fully automated** via GitHub Actions when you merge to `main`:

1. GitHub Actions analyzes commits and bumps version
2. CHANGELOG.md is updated
3. Git tag and GitHub release are created
4. Package is built and published to PyPI

**No manual steps needed** - just use conventional commit messages.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
