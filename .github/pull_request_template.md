<!--
⚠️ IMPORTANT: PR TITLE MUST FOLLOW CONVENTIONAL COMMIT FORMAT ⚠️

Your PR title determines the version bump when merged:
  - feat: <description>       → MINOR version bump (1.0.0 → 1.1.0)
  - fix: <description>        → PATCH version bump (1.0.0 → 1.0.1)
  - feat!: <description>      → MAJOR version bump (1.0.0 → 2.0.0)
  - chore/docs/refactor/etc:  → NO release

Example PR titles:
  ✅ feat: add batch peak lookup support
  ✅ fix: handle missing elevation data in scraper
  ✅ feat!: restructure CLI to resource-action pattern
  ✅ chore: update pre-commit hooks
  ❌ Add batch peak lookup (missing type prefix)
  ❌ Feature: add batch lookup (wrong format)

A GitHub Action will validate your PR title format.
-->

## Summary

<!-- Brief description of what this PR does -->

## Type of Change

<!-- Mark the relevant option with an [x] - this should match your PR title prefix -->

- [ ] `feat:` New feature (MINOR version bump)
- [ ] `fix:` Bug fix (PATCH version bump)
- [ ] `feat!:` or `fix!:` Breaking change (MAJOR version bump)
- [ ] `docs:` Documentation only (no release)
- [ ] `style:` Code style/formatting (no release)
- [ ] `refactor:` Code refactoring (no release)
- [ ] `perf:` Performance improvement (PATCH version bump)
- [ ] `test:` Adding or updating tests (no release)
- [ ] `chore:` Maintenance, dependencies, tooling (no release)
- [ ] `ci:` CI/CD configuration (no release)

## Changes

<!-- List of specific changes made -->

-
-
-

## Breaking Changes

<!-- If this is a breaking change, describe what breaks and migration path -->

**BREAKING CHANGE:**

## Testing

<!-- How was this tested? -->

## Checklist

- [ ] Code follows project style guidelines (Ruff passing)
- [ ] Self-review of code completed
- [ ] Comments added for hard-to-understand areas
- [ ] Documentation updated (README.md, CLAUDE.md, etc.)
- [ ] No new warnings generated
- [ ] Tests added/updated for changes
- [ ] All tests passing
- [ ] PR title follows conventional commit format

## Related Issues

<!-- Link any related issues -->

Closes #
