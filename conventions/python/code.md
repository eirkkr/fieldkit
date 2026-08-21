# Python code conventions

Conventions for authoring Python source: docstrings, imports, member
ordering, enum values, and exception handling. Several rules below have no
automated enforcement and rely on review.

## Docstrings

- Google-style; comply with ruff's `D` rules.
- Modules and classes: single line, sentence case, no trailing period.
- Public functions and methods: summary line, then `Args:` / `Returns:` /
  `Raises:` as needed; descriptions are full sentences ending in a period.
- Private (`_`-prefixed): not required; add one only when the logic isn't
  self-evident.

## Imports

- A package's `__all__` is its public surface. Import a public symbol from the
  package that owns it - not from the module that defines it (even a private
  `_`-module), and not from a parent package.
- Re-export only what something imports through the package. That rules out a
  symbol used only inside its own package (in-package callers import it from
  its defining module), and one whose outside callers reach its defining
  module directly.
- An annotation-only import under `TYPE_CHECKING` counts as public usage - it
  is a real cross-package contract. A test import doesn't: a symbol used only
  by tests stays private.
- On Python 3.14+ an annotation-only import can sit under `if TYPE_CHECKING:`
  without `from __future__ import annotations`, since PEP 649 defers annotation
  evaluation. Below 3.14 a runtime-evaluated annotation - notably a module- or
  class-level variable annotation - still needs the symbol imported at runtime,
  so don't move it.
- A module that `__init__` imports during initialisation can't import back from
  the package (it's only half-built at that point); it imports shared symbols
  directly from the source file, even public ones.
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

## Enum values

A member's value is declared with `enum.auto()` when nothing outside the enum
reads it - that is, the members are only ever compared to each other. A
hand-written number there is bookkeeping to maintain for no gain: it has to be
kept consistent with whatever ordering the enum declares, and inserting a
member renumbers the rest.

Values are written out when something outside the enum reads them: a value
persisted to a database or serialised onto the wire, one handed to a library
that matches on it, or one that *is* the payload (an enum whose values are the
classes it dispatches to). Such a value is part of a contract, and `auto()`
would leave it to declaration order.

## Exception handling

On Python 3.14+ (PEP 758), an `except` clause catching several types is
written *without* parentheses: `except KeyError, ValueError:`. This is
current syntax, not a Python-2 relic - ruff's formatter rewrites the
parenthesised `except (KeyError, ValueError):` to this form under a `py314`+
target, so the bare form is the house style. Don't "correct" it by adding
parentheses; the formatter only reverts the change, and lint does not flag
it. Parentheses are still required when binding the caught exception with
`as` (`except (KeyError, ValueError) as exc:`).
