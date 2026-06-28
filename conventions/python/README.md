# Python conventions

Language-specific conventions for Python repos. `@`-import this file in a Python
repo; it carries the one always-on rule and an index to the rest, which you read
on demand for the task at hand. Several of the linked rules have no automated
enforcement and rely on review.

## Always

Prefix every Python tool invocation with `uv run` so the project venv is used
rather than the system Python:

```sh
uv run python script.py   # run a script
uv run pytest             # run tests
uv run ruff check .       # run a linter/formatter
```

This applies to exploratory commands in the shell as well as to subprocess calls
in scripts - use `uv run python` rather than `python3` or `python`.

## Load on Demand

Read the matching file before the action; don't load it otherwise. Paths are
relative to the consumer repo root, via the `.fieldkit` symlink.

| Before...                             | Read                                          |
| ------------------------------------- | --------------------------------------------- |
| Writing or editing Python source      | .fieldkit/conventions/python/code.md          |
| Setting up a project or managing deps | .fieldkit/conventions/python/setup.md         |
| Writing or reviewing tests            | .fieldkit/conventions/python/testing.md       |
