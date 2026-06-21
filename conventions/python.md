# Python conventions

Language-specific conventions for Python repos. Import this only where it
applies. Several rules below have no automated enforcement and rely on review.

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
- A symbol used only within its own package isn't re-exported; in-package
  callers import it directly from its defining module.
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

## Blank-line spacing

Relies on review (no linter). Any statement spanning more than one line is
surrounded by a blank line on each side, unless it's the first or last statement
in its block. Applies to simple statements (assignments, calls, returns,
raises), not to compound headers (`if`, `for`, `with`, `def`, `class`, `try`,
`except`).

## Dependencies

When adding entries to `pyproject.toml`, pin to the minor version, not the
patch (e.g. `>=5.6.0,<6` not `>=5.6.3,<6`).
