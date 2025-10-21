#!/usr/bin/env bash
# Setup git hooks and commit message template for peakbagger-cli

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Setting up git hooks and commit message template..."

# Set commit message template
git config commit.template "${PROJECT_ROOT}/.gitmessage"
echo "✓ Commit message template configured"

# Install pre-commit hooks
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo "✓ Pre-commit hooks installed"
else
    echo "⚠ pre-commit not found. Install with: uv tool install pre-commit"
    echo "  Then run: pre-commit install"
fi

echo ""
echo "Git configuration complete!"
echo ""
echo "Your commits will now use the conventional commit template."
echo "The template will appear when you run: git commit"
