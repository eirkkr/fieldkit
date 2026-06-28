# Running Python commands

Prefix every invocation with `uv run` so the project venv is used rather than
the system Python:

```sh
uv run python script.py
uv run pytest
uv run ruff check .
```

Use `uv run python`, not `python3` or `python` - this applies in the shell and
in subprocess calls within scripts.
