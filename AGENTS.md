# Repository Guidelines

- Use [Conventional Commits](https://www.conventionalcommits.org/) for all commit messages.
- Whenever changes are made, bump the version in both `pyproject.toml` and `custom_components/assist_traces/manifest.json`.
  - Patch for documentation and backward-compatible bug fixes.
  - Minor for new features.
  - Major for breaking changes.
- Document all classes and methods with docstrings.
- Run `ruff format .` and `ruff check .` before committing.
- Run `pytest --cov` and ensure coverage is at least 85% before committing.
