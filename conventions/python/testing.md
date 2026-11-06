# Testing

## Structure and naming

Write flat test functions, not classes. Each gets a one-line docstring stating the behaviour under test, not how the test works:

```python
def test_parse_empty_input_returns_none() -> None:
    """An empty string returns None."""
    assert parse("") is None
```

Mirror the source layout under `tests/`, one file per module: `tests/test_<module>.py`, or `tests/<package>/test_<module>.py` for a subpackage. Shared fixtures go in `conftest.py` at the right directory level.

## CLI testing

Test entry points in-process with `monkeypatch.setattr`, not a subprocess: faster, and pytest captures output:

```python
import sys
import pytest

def test_run_exits_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    """A valid invocation exits with code 0."""
    monkeypatch.setattr(sys, "argv", ["prog", "--input", "file.txt"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
```

If `main()` doesn't call `sys.exit`, assert its return value or side effects instead.

## Golden / fixture-comparison tests

Strip volatile fields (timestamps, generated IDs, anything that changes between runs) before comparing against a stored fixture. Normalise a copy, not the original:

```python
def test_export_matches_fixture(result: dict) -> None:
    """Exported record matches the stored fixture."""
    stable = {k: v for k, v in result.items() if k not in {"created_at", "_id"}}
    assert stable == load_fixture("expected_export.json")
```

Name the volatile fields near the test, or in a shared helper if the same set recurs.

## Expected multi-line text

Expected text of three or more lines follows [code.md's multi-line text rule](code.md#multi-line-text). A comparison adds two rules:

- **Assign the block to `expected` before the assertion.** `ruff format` rewraps an inline `assert result == textwrap.dedent(...).strip()` into a parenthesised comparison that puts the opening quotes a level deeper than the text and closing quotes.
- **Strip the expected side only, never the result**, so a stray leading or trailing newline in `result` still fails.

A substring check of fewer than three lines stays one literal.

## Loading test data

Cache a module-level loader whose data feeds collection - fixture `params` or `ids`, or a `parametrize` list. Collection calls it, and the fixture or test usually calls it again:

```python
@cache
def _records() -> list[dict]:
    return json.loads(Path("tests/data/records.json").read_text("utf-8"))


@pytest.fixture(params=_records(), ids=operator.itemgetter("code"))
def record(request: pytest.FixtureRequest) -> dict:
    """One record from the data file."""
    return request.param
```

This meets [code.md's caching rules](code.md#caching): nothing modifies the records, so plain dicts will do. Pytest gives every test the same parameter objects whether or not the loader is cached, so the cache shares nothing new.

Leave data read at run time (in a fixture body or a helper a test calls) uncached, so each test owns its copy: a shared record one test changes leaks into later tests, intermittently under parallel or random order. Parsing a test data file takes well under a millisecond.
