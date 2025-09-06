# Repository Guidelines

- Use [Conventional Commits](https://www.conventionalcommits.org/) for all commit messages.
- Whenever changes are made, bump the version in both `pyproject.toml` and `custom_components/assist_traces/manifest.json`.
  - Patch for documentation and backward-compatible bug fixes.
  - Minor for new features.
  - Major for breaking changes.
- Run `ruff check .` and `pytest` before committing.
