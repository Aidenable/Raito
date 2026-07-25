# Contributing to Raito

Thanks for taking the time to contribute! This guide covers the local setup and
the checks your change needs to pass.

By participating you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Development setup

Raito uses [uv](https://docs.astral.sh/uv/) and targets **Python 3.10+**.

```bash
git clone https://github.com/Aidenable/raito
cd raito
uv sync --all-extras
uv run pre-commit install
```

`--all-extras` installs the dev tools plus the optional backends (Redis, SQLite,
PostgreSQL), so the whole test and type-check surface is available.

## Checks

The CI runs the following on Python 3.10, 3.11 and 3.12. Run them locally before
opening a pull request:

```bash
uv run ruff check .          # lint
uv run ruff format --check . # formatting
uv run mypy raito            # type check
uv run pytest                # tests
```

`pre-commit` runs the lint/format/type hooks automatically on commit.

## Building the docs

```bash
uv run sphinx-build -b html docs/source docs/_build/html
```

Open `docs/_build/html/index.html`. The API reference is generated from
docstrings, so keep them accurate.

## Making a change

- Keep pull requests focused on a single concern.
- Match the surrounding code style; add or update tests where it makes sense.
- Update the docs (`docs/source/`) and docstrings when behaviour changes.
- Write commit messages in the [Conventional Commits](https://www.conventionalcommits.org)
  style used across the history: `feat:`, `fix:`, `docs:`, `chore:`, …
- Make sure all checks above pass.

## Reporting issues

- **Bugs and features** — open a GitHub issue with a minimal reproduction.
- **Security vulnerabilities** — do not open a public issue; follow the
  [Security Policy](SECURITY.md).
