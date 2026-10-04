# Testing

pytest conventions for Python repos.

## Structure and naming

Write flat test functions - no class grouping. Each function gets a one-line docstring stating the behaviour under test (not how the test works):

```python
def test_parse_empty_input_returns_none() -> None:
    """An empty string returns None."""
    assert parse("") is None
```

Mirror the source layout under `tests/`, one file per module: `tests/test_<module>.py` for top-level modules, `tests/<package>/test_<module>.py` for subpackages. Shared fixtures go in `conftest.py` at the appropriate directory level.

## CLI testing

Test entry points in-process with `monkeypatch.setattr` rather than subprocess - faster, and pytest can capture output:

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

If `main()` does not call `sys.exit`, no `SystemExit` is raised - assert the return value or side effects directly instead.

## Golden / fixture-comparison tests

When asserting against a stored fixture or expected output, strip volatile fields before comparing - timestamps, generated IDs, anything that changes between runs. Normalise on a copy so the original is not mutated:

```python
def test_export_matches_fixture(result: dict) -> None:
    """Exported record matches the stored fixture."""
    stable = {k: v for k, v in result.items() if k not in {"created_at", "_id"}}
    assert stable == load_fixture("expected_export.json")
```

Document which fields are volatile near the test or extract them into a shared helper if the same set recurs across tests.

## Expected multi-line text

Expected text of three or more lines follows [code.md's multi-line text rule](code.md#multi-line-text): one dedented block, so the expectation looks like the output it checks.

```python
def test_summary_lists_requisite_types() -> None:
    """The summary lists each requisite type under its heading."""
    result = summarise(RECORDS)

    expected = textwrap.dedent(
        """
        Records                        3

        Requisite types
          PREREQUISITE                 4
          PRE-REQ                      1

        Maximum component depth        1
        """
    ).strip()

    assert result == expected
```

`expected` is the seven lines between the quotes with the eight-space indent they share removed, so the two rows under `Requisite types` keep their two spaces.

A comparison adds two rules:

- **Assign first.** Give the block a name before the assertion. `ruff format` rewraps an inline `assert result == textwrap.dedent(...).strip()` into a parenthesised comparison, pushing the call and the quotes a level deeper than the text between them. Assigned to a name, the block is left as written.
- **Strip the expected side only, never the result.** A stray leading or trailing newline in `result` then still fails the comparison. Output that ends in a newline is matched by ending the block in `.lstrip()`.

A substring check of fewer than three lines stays one literal: `assert "Heading\n  (none)\n" in result`.

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

This meets [code.md's caching rules](code.md#caching): nothing modifies the records, so they can stay plain dicts rather than immutable values. Pytest hands every test the same parameter objects whether or not the loader is cached, so the cache shares nothing new.

Don't cache data read at run time, in a fixture body or a helper a test calls. Each test should own its copy: a shared record one test changes leaks into later tests, intermittently under parallel or random order. Parsing a test data file takes well under a millisecond.
