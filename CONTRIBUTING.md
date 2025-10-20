# Contributing to peakbagger-cli

Thank you for your interest in contributing to peakbagger-cli! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.12 or higher
- `uv` (recommended) or `pip`
- Git
- Basic knowledge of Python, Click, and web scraping

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR-USERNAME/peakbagger-cli.git
cd peakbagger-cli
```

3. Add the upstream repository:

```bash
git remote add upstream https://github.com/ORIGINAL-OWNER/peakbagger-cli.git
```

## Development Setup

### Using uv (Recommended)

`uv` is a fast Python package manager that simplifies development:

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

# Run the CLI
peakbagger --help
```

## Project Structure

```
peakbagger-cli/
├── peakbagger/           # Main package
│   ├── __init__.py       # Package version and metadata
│   ├── cli.py            # Click CLI commands and main entry point
│   ├── client.py         # HTTP client with rate limiting
│   ├── scraper.py        # HTML parsing and data extraction
│   ├── models.py         # Data models (Peak, SearchResult)
│   └── formatters.py     # Output formatting (Rich tables, JSON)
├── tests/                # Test suite
│   ├── test_client.py
│   ├── test_scraper.py
│   └── test_formatters.py
├── pyproject.toml        # Project configuration and dependencies
├── README.md             # User documentation
├── CONTRIBUTING.md       # This file
├── LICENSE               # MIT License
└── .gitignore            # Git ignore rules
```

### Module Responsibilities

- **cli.py**: Defines Click commands (`search`, `info`), handles CLI arguments and options
- **client.py**: Manages HTTP requests with cloudscraper, implements rate limiting
- **scraper.py**: Parses HTML using BeautifulSoup, extracts peak data
- **models.py**: Defines data structures (Peak, SearchResult) and serialization
- **formatters.py**: Formats output (Rich tables for humans, JSON for machines)

## Development Workflow

### Creating a Feature Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
```

### Making Changes

1. Make your changes in your feature branch
2. Test your changes thoroughly
3. Add/update tests if needed
4. Update documentation if needed

### Running the CLI During Development

```bash
# With uv
uv run peakbagger search "Mount Rainier"
uv run peakbagger info 2296

# With pip (after activating venv)
peakbagger search "Mount Rainier"
peakbagger info 2296
```

### Testing Your Changes

```bash
# Run tests (once test suite is implemented)
uv run pytest

# Run tests with coverage
uv run pytest --cov=peakbagger

# Test manually with real queries
uv run peakbagger search "Denali"
uv run peakbagger info 2296 --format json
```

## Testing

### Writing Tests

Place tests in the `tests/` directory:

```python
# tests/test_scraper.py
import pytest
from peakbagger.scraper import PeakBaggerScraper
from peakbagger.models import Peak

def test_parse_peak_detail():
    """Test parsing peak detail page."""
    html = """<html>...</html>"""  # Sample HTML
    scraper = PeakBaggerScraper()
    peak = scraper.parse_peak_detail(html, "2296")

    assert peak
    assert peak.name == "Mount Rainier"
    assert peak.elevation_ft == 14406
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_scraper.py

# Run with verbose output
uv run pytest -v

# Run with coverage report
uv run pytest --cov=peakbagger --cov-report=html
```

## Code Quality

This project uses automated tools to maintain code quality and consistency.

### Pre-commit Hooks

Pre-commit hooks automatically check code before commits:

```bash
# Install hooks (one time setup)
uv run pre-commit install

# Hooks run automatically on git commit
# Or run manually on all files:
uv run pre-commit run --all-files

# Run specific hook:
uv run pre-commit run ruff --all-files
```

**Hooks verify:**
- **Ruff**: Formatting and linting (replaces Black, isort, flake8)
- **Trailing whitespace**: Removes trailing spaces
- **End of file**: Ensures files end with newline
- **YAML/TOML/JSON**: Validates syntax
- **Bandit**: Security vulnerability checks
- **mypy**: Type checking
- **markdownlint**: Markdown formatting
- **yamllint**: YAML linting

### Manual Formatting and Linting

Run Ruff manually when needed:

```bash
# Format code
uv run ruff format peakbagger tests

# Check formatting without modifying
uv run ruff format --check peakbagger tests

# Lint and auto-fix issues
uv run ruff check --fix peakbagger tests

# Lint without fixing
uv run ruff check peakbagger tests
```

### Style Guidelines

- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and small (prefer composition over complexity)
- Use descriptive variable names
- Add comments for complex logic

### Example

```python
def parse_elevation(html: str) -> Optional[int]:
    """
    Extract elevation in feet from peak detail HTML.

    Args:
        html: HTML content from peak detail page

    Returns:
        Elevation in feet, or None if parsing fails
    """
    soup = BeautifulSoup(html, 'lxml')
    h2 = soup.find('h2')

    if not h2:
        return None

    # Format: "Elevation: 14,406 feet, 4391 meters"
    match = re.search(r'([\d,]+)\s*feet', h2.text)
    return int(match.group(1).replace(',', '')) if match else None
```

## Submitting Changes

### Commit Messages

Write clear, descriptive commit messages:

```
Add support for searching by peak ID range

- Implement --min-id and --max-id flags
- Add validation for ID ranges
- Update documentation with examples
```

Format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description with bullet points if needed

### Pull Request Process

1. **Update your branch** with the latest upstream changes:

```bash
git fetch upstream
git rebase upstream/main
```

2. **Push your changes** to your fork:

```bash
git push origin feature/your-feature-name
```

3. **Create a Pull Request** on GitHub:
   - Open your fork on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Complete the PR template

4. **PR Requirements**:
   - Clear description of changes
   - All tests pass
   - Ruff formats and lints code
   - Pre-commit hooks pass
   - Documentation updates included
   - Code follows project style

5. **Review Process**:
   - Maintainers review your PR
   - Address feedback or requested changes
   - Your PR merges once approved

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of what this PR does

## Changes
- List of changes made
- Use bullet points

## Testing
How did you test these changes?

## Screenshots (if applicable)
For CLI output changes, include before/after screenshots

## Checklist
- [ ] Tests pass
- [ ] Code formatted and linted with Ruff
- [ ] Pre-commit hooks pass
- [ ] Documentation updated
- [ ] CHANGELOG updated (for significant changes)
```

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Description**: Clear bug description
2. **Steps to Reproduce**: Exact reproduction steps
3. **Expected Behavior**: Expected outcome
4. **Actual Behavior**: Actual outcome
5. **Environment**:
   - OS (macOS, Linux, Windows)
   - Python version
   - peakbagger-cli version
6. **Logs/Output**: Relevant error messages or output

Example:

```markdown
**Bug**: Search command fails with Cloudflare error

**Steps to Reproduce**:
1. Run `peakbagger search "Mount Rainier"`
2. Observe error

**Expected**: Search results displayed

**Actual**: Cloudflare 403 error

**Environment**:
- macOS 14.0
- Python 3.12.1
- peakbagger-cli 0.1.0

**Error Output**:
```
Error: Failed to fetch https://www.peakbagger.com/search.aspx: 403 Forbidden
```
```

### Feature Requests

Feature requests require:

1. **Use Case**: Describe the need for this feature
2. **Proposed Solution**: Explain how it should work
3. **Alternatives**: Describe other solutions considered
4. **Additional Context**: Provide relevant information

## Development Tips

### Debugging

```python
# Add print statements (or use Rich console)
from rich.console import Console
console = Console()
console.print(f"[yellow]Debug: {variable}[/yellow]")

# Use pdb for interactive debugging
import pdb; pdb.set_trace()
```

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

When updating scraper logic, follow these steps:

1. Save sample HTML for testing:
```python
response = client.get('/peak.aspx?pid=2296')
with open('test_peak.html', 'w') as f:
    f.write(response)
```

2. Test parsing locally without network requests
3. Update tests with new HTML structure

## Release Process

### Overview

This project uses [python-semantic-release](https://python-semantic-release.readthedocs.io/) to automate version management and releases. The tool analyzes commit messages to determine version bumps and generates changelogs automatically.

### Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
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
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, missing semicolons, etc.)
- `refactor:` - Code refactoring without feature changes
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks, dependency updates
- `ci:` - CI/CD configuration changes
- `build:` - Build system changes

**Examples:**

```bash
# Patch release (0.1.0 → 0.1.1)
git commit -m "fix: correct elevation parsing for peaks without prominence data"

# Minor release (0.1.0 → 0.2.0)
git commit -m "feat: add support for searching peaks by elevation range"

# Major release (0.1.0 → 1.0.0)
git commit -m "feat: redesign CLI interface

BREAKING CHANGE: The --full flag has been replaced with --detailed"

# No release
git commit -m "docs: update installation instructions"
git commit -m "chore: update dependencies"
```

### Creating a Release (Maintainers Only)

#### Step 1: Ensure Commits Follow Convention

Review recent commits to ensure they follow the conventional commit format:

```bash
git log --oneline
```

If needed, amend or reword recent commits before releasing.

#### Step 2: Run Semantic Release

```bash
# Dry run to preview changes (recommended)
uv run semantic-release --noop version

# Actually create the release
uv run semantic-release version
```

This command will:
1. Analyze commit messages since the last release
2. Determine the next version number
3. Update `pyproject.toml` and `peakbagger/__init__.py`
4. Generate/update `CHANGELOG.md`
5. Create a git commit with these changes
6. Create a git tag (e.g., `v0.2.0`)
7. Push the commit and tag to GitHub

#### Step 3: Build and Publish to PyPI

```bash
# Build the package
uv build

# Publish to TestPyPI (optional - for testing)
uv tool run twine upload --repository testpypi dist/*

# Publish to PyPI
uv tool run twine upload dist/*
```

**Note:** You need PyPI credentials configured (see main README for setup).

#### Step 4: Create GitHub Release

After publishing to PyPI, create a GitHub release:

```bash
gh release create v0.2.0 --notes-from-tag
```

Or manually create the release on GitHub using the changelog content.

### Version Bumping Examples

Given the current version is `0.1.0`:

| Commit Type | Example | New Version |
|-------------|---------|-------------|
| `fix:` | `fix: handle missing county data` | `0.1.1` |
| `feat:` | `feat: add JSON export for search results` | `0.2.0` |
| `feat:` with breaking change | `feat: new CLI structure`<br>`BREAKING CHANGE: ...` | `1.0.0` |
| Multiple `fix:` commits | 3x `fix:` commits | `0.1.1` (single bump) |
| `fix:` + `feat:` | Both types present | `0.2.0` (highest bump wins) |

### Checking What Would Be Released

Before creating a release, preview what would happen:

```bash
# Show what version would be created
uv run semantic-release version --print

# Show full details without making changes
uv run semantic-release --noop version
```

### Manual Version Override

If you need to manually set a specific version:

```bash
# Bump to a specific version
uv run semantic-release version --patch  # Force patch bump
uv run semantic-release version --minor  # Force minor bump
uv run semantic-release version --major  # Force major bump

# Or set an exact version
uv run semantic-release version --bump-version 0.3.0
```

### Troubleshooting

**"No release will be made"**
- No commits since last release follow conventional format
- Add a conventional commit or use `--patch/--minor/--major` flag

**"Token value is missing"**
- This warning is safe to ignore for manual releases
- Only needed for GitHub Actions automation

**Wrong version calculated**
- Review commits: `git log v0.1.0..HEAD --oneline`
- Check commit types match conventional format
- Use `--noop` flag to preview before committing

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Chat**: Join our Discord (link in README)
- **Email**: maintainer@example.com

## Recognition

Contributors receive recognition in:
- CHANGELOG.md for significant contributions
- GitHub contributors page
- Release notes with special thanks

## License

Contributing to peakbagger-cli means your contributions receive MIT License terms.

---

Thank you for contributing to peakbagger-cli! 🏔️
