# Contributing to peakbagger-cli

Thank you for your interest in contributing to peakbagger-cli! This document provides guidelines and instructions for contributing to the project.

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

`uv` is a fast Python package manager that makes development easier:

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

Tests should be placed in the `tests/` directory:

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

    assert peak is not None
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

We use pre-commit hooks to automatically check code before commits:

```bash
# Install hooks (one time setup)
uv run pre-commit install

# Hooks run automatically on git commit
# Or run manually on all files:
uv run pre-commit run --all-files

# Run specific hook:
uv run pre-commit run ruff --all-files
```

**What the hooks check:**
- **Ruff**: Formatting and linting (replaces Black, isort, flake8)
- **Trailing whitespace**: Removes trailing spaces
- **End of file**: Ensures files end with newline
- **YAML/TOML/JSON**: Validates syntax
- **Bandit**: Security vulnerability checks
- **mypy**: Type checking
- **markdownlint**: Markdown formatting
- **yamllint**: YAML linting

### Manual Formatting and Linting

You can also run Ruff manually:

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
        Elevation in feet, or None if not found
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
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill out the PR template

4. **PR Requirements**:
   - Clear description of changes
   - All tests pass
   - Code is formatted and linted with Ruff
   - Pre-commit hooks pass
   - Documentation is updated
   - Follows project code style

5. **Review Process**:
   - Maintainers will review your PR
   - Address any feedback or requested changes
   - Once approved, your PR will be merged!

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

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Exact steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
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

When requesting features, please include:

1. **Use Case**: Why is this feature needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other solutions you've considered
4. **Additional Context**: Any other relevant information

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

When updating scraper logic:

1. Save sample HTML for testing:
```python
response = client.get('/peak.aspx?pid=2296')
with open('test_peak.html', 'w') as f:
    f.write(response)
```

2. Test parsing locally without network requests
3. Update tests with new HTML structure

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Chat**: Join our Discord (link in README)
- **Email**: maintainer@example.com

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for significant contributions
- GitHub contributors page
- Special thanks in release notes

## License

By contributing to peakbagger-cli, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to peakbagger-cli! 🏔️
