# Python code conventions

Conventions for authoring Python source: docstrings, imports, member ordering,
and exception handling. Several rules below have no automated enforcement and
rely on review. See [README.md](README.md) for the index and the always-on
`uv run` rule.

## Docstrings

- Google-style; comply with ruff's `D` rules.
- Modules and classes: single line, sentence case, no trailing period.
- Public functions and methods: summary line, then `Args:` / `Returns:` /
  `Raises:` as needed; descriptions are full sentences ending in a period.
- Private (`_`-prefixed): not required; add one only when the logic isn't
  self-evident.

## Imports

- A package's `__all__` is its public surface. Import public symbols from the
  owning package, not the module that defines them (even a private `_`-module).
- Annotation-only imports under `TYPE_CHECKING` count as public usage (they
  are a real cross-package contract). Test imports do not: a symbol used only
  by tests stays private.
- An annotation-only import can live under `if TYPE_CHECKING:` without
  `from __future__ import annotations` on Python 3.14+, where PEP 649 defers
  annotation evaluation by default. Below 3.14, a runtime-evaluated annotation
  - notably a module- or class-level variable annotation - still needs the
  symbol imported at runtime, so don't move it.
- A symbol used only within its own package isn't re-exported; in-package
  callers import it directly from its defining module.
- Re-export a public symbol from the package that owns it, not from a parent.
- A module that `__init__` imports during initialisation can't import back from
  the package (it's only half-built at that point); import shared symbols
  directly from the source file instead, even when they are public.
- Name a module by what it exposes. A `_`-prefix marks a module as internal to
  its package, not part of its public surface.

## Member ordering

Relies on review (no linter). Order modules: constants, then public functions
and classes, then private helpers (callers above callees). Order class members:

1. Class variables and constants
2. `__init__`, then other dunders
3. Properties
4. Public instance methods
5. Classmethods
6. Private and static methods

Within a group, put callers above callees and more central members higher.

## Exception handling

On Python 3.14+ (PEP 758), an `except` clause catching several types is
written *without* parentheses: `except KeyError, ValueError:`. This is
current syntax, not a Python-2 relic - ruff's formatter rewrites the
parenthesised `except (KeyError, ValueError):` to this form under a `py314`+
target, so the bare form is the house style. Don't "correct" it by adding
parentheses; the formatter only reverts the change, and lint does not flag
it. Parentheses are still required when binding the caught exception with
`as` (`except (KeyError, ValueError) as exc:`).
