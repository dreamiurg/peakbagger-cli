#!/usr/bin/env python3
"""Update version in pyproject.toml and __init__.py for semantic-release.

This script is called by semantic-release during the prepare phase.
"""

import re
import sys
from pathlib import Path


def update_version(new_version: str) -> None:
    """Update version in pyproject.toml and peakbagger/__init__.py.

    Args:
        new_version: The new version string (e.g., "0.3.1")
    """
    project_root = Path(__file__).parent.parent

    # Update pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    content = pyproject_path.read_text()
    updated_content = re.sub(
        r'^version = ".*"$',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE,
    )
    pyproject_path.write_text(updated_content)
    print(f"Updated {pyproject_path}")

    # Update peakbagger/__init__.py
    init_path = project_root / "peakbagger" / "__init__.py"
    content = init_path.read_text()
    updated_content = re.sub(
        r'^__version__ = ".*"$',
        f'__version__ = "{new_version}"',
        content,
        flags=re.MULTILINE,
    )
    init_path.write_text(updated_content)
    print(f"Updated {init_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: update-version.py <version>", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]
    update_version(version)
    print(f"Successfully updated version to {version}")
