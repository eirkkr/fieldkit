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
- Annotation-only imports under `TYPE_CHECKING` count as public usage (they
  are a real cross-package contract). Test imports do not: a symbol used only
  by tests stays private.
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

## Blank-line spacing

Relies on review (no linter). Any statement spanning more than one line is
surrounded by a blank line on each side, unless it's the first or last statement
in its block. Applies to simple statements (assignments, calls, returns,
raises), not to compound headers (`if`, `for`, `with`, `def`, `class`, `try`,
`except`).

## Project setup

Initialise new projects with uv commands rather than hand-authoring
`pyproject.toml`:

```sh
uv init <name>          # scaffold pyproject.toml, .python-version, README
uv add <pkg>            # add a runtime dependency (resolves latest)
uv add --dev <pkg>      # add a dev dependency (resolves latest)
uv sync                 # create/update the lockfile and venv
```

Commit both `pyproject.toml` and `uv.lock`. Do not edit either by hand after
initial setup - use `uv add` / `uv remove` so the lockfile stays consistent.

**Always use the latest available versions** when setting up a project - the
latest stable Python minor and the latest release of each dependency. `uv add`
resolves the latest by default; after it runs, tighten the version range in
`pyproject.toml` to follow the pinning convention below. Check the installed
Python version with `uv run python --version` and use that patch in
`requires-python`.

## Dependencies

After `uv add` installs a package, set its version range in `pyproject.toml`
based on the installed version. Do not hand-edit `pyproject.toml` directly;
use `uv add "pkg>=X.Y,<Z"` to update a constraint.

The minimum is the minor of the installed release (drop the patch); the
maximum depends on the package:

- **Dependencies (major >= 1):** cap at the next major.
  `>=X.Y,<X+1` - e.g. installed `pytest 9.1.1` → `>=9.1,<10`
- **Dependencies (major == 0):** cap at the next minor - 0.x semver treats
  the minor as the breaking-change boundary.
  `>=0.Y,<0.Y+1` - e.g. installed `pymarkdownlnt 0.9.38` → `>=0.9,<0.10`
- **`requires-python`:** pin to the exact installed patch and cap at the next
  minor. Python patch releases can introduce new language features, so the
  minimum must be exact.
  `>=X.Y.Z,<X.Y+1` - e.g. installed Python `3.14.4` → `>=3.14.4,<3.15`

Common mistakes to avoid:

- `>=9.1.1,<10` - patch in the floor; use `>=9.1,<10`
- `>=9,<10` - major in the floor; use `>=9.1,<10`
- `>=0.9.38,<0.10` - patch in the floor for a 0.x package; use `>=0.9,<0.10`
- `>=0.9,<1` - capping a 0.x package at major; use `>=0.9,<0.10`
- `>=3.11` - an old Python version with no upper bound; use `>=3.14.4,<3.15`
