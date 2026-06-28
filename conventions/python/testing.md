# Testing

pytest conventions for Python repos.

## Structure and naming

Write flat test functions - no class grouping. Each function gets a one-line
docstring stating the behaviour under test (not how the test works):

```python
def test_parse_empty_input_returns_none() -> None:
    """An empty string returns None."""
    assert parse("") is None
```

Mirror the source layout under `tests/`, one file per module:
`tests/test_<module>.py` for top-level modules,
`tests/<package>/test_<module>.py` for subpackages. Shared fixtures go in
`conftest.py` at the appropriate directory level.

## CLI testing

Test entry points in-process with `monkeypatch.setattr` rather than subprocess -
faster, and pytest can capture output:

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

If `main()` does not call `sys.exit`, no `SystemExit` is raised - assert the
return value or side effects directly instead.

## Golden / fixture-comparison tests

When asserting against a stored fixture or expected output, strip volatile fields
before comparing - timestamps, generated IDs, anything that changes between runs.
Normalise on a copy so the original is not mutated:

```python
def test_export_matches_fixture(result: dict) -> None:
    """Exported record matches the stored fixture."""
    stable = {k: v for k, v in result.items() if k not in {"created_at", "_id"}}
    assert stable == load_fixture("expected_export.json")
```

Document which fields are volatile near the test or extract them into a shared
helper if the same set recurs across tests.
