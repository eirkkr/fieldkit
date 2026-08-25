# Python code conventions

Conventions for authoring Python source: docstrings, imports, member
ordering, constants, enum values, and exception handling. Several rules
below have no automated enforcement and rely on review.

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
- Import a helper module as a namespace when its bare symbols would be
  ambiguous: `from pkg import _flasher as flasher`, called as
  `flasher.success(...)` - aliasing drops the `_`, the path keeps it.
  `current_actor()` could come from anywhere; `auth.current_actor()` says which
  subsystem answers. Import a named type directly - the name already says what
  it is.
- Import a module the same way throughout a file; two forms read as two
  dependencies.
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

## Constants

A module-level name in `UPPER_SNAKE` is the default home for a fixed value.
Python modules are already namespace objects, so a class or frozen dataclass
wrapped around a group of them adds an indentation level and an instance
nobody needs, without adding a guarantee. Two shapes cover nearly everything:

- **Private to one module** - `_`-prefixed, declared at the top, used by that
  module's functions. Correct even when only one function reads it: a local
  in `UPPER_SNAKE` is a local wearing constant clothing, and renaming it to
  lowercase loses the signal that the value is fixed. Keeping it at the top
  also lets a reader see the module's whole authored-value surface without
  opening the functions.
- **A shared vocabulary** - a module whose job is holding a related set of
  public names, imported as a namespace and read dotted (`colls.HTTP_LOG`,
  `limits.API_READ`). This is what `errno`, `signal`, and `stat` are.

Reach for an `Enum` instead when the set has one of three properties, none of
which is tidiness:

1. Something branches on it and should be exhaustive (`match` +
   `assert_never`).
2. Something iterates the set, or tests membership against it.
3. A parameter should be typed "one of these", so a stray string is a type
   error.

Absent all three, an enum is churn: names that are only ever spelled once and
handed to a library or a template are strings, and a `frozenset` is the right
container for a pure membership test.

Constants shared across languages - a form field name Python matches and a
template renders, a key both a client and a server spell - are the case the
container choice doesn't fix. Neither a module nor an enum stops the literal
being written twice, and the duplicate fails silently: the comparison simply
stops matching. Inject the value into the other language from the one that
owns it rather than spelling it in both.

## Enum values

- `enum.auto()` when nothing outside the enum reads the value - the members
  are only ever compared to each other. A hand-written number there is
  bookkeeping: it has to track whatever ordering the enum declares, and
  inserting a member renumbers the rest.
- Explicit values when something outside does read them - a value persisted or
  serialised, one a library matches on, or one that *is* the payload (an enum
  whose values are the classes it dispatches to). That value is part of a
  contract, not an implementation detail.

## Exception handling

On Python 3.14+ (PEP 758), an `except` clause catching several types is
written *without* parentheses: `except KeyError, ValueError:`. This is
current syntax, not a Python-2 relic - ruff's formatter rewrites the
parenthesised `except (KeyError, ValueError):` to this form under a `py314`+
target, so the bare form is the house style. Don't "correct" it by adding
parentheses; the formatter only reverts the change, and lint does not flag
it. Parentheses are still required when binding the caught exception with
`as` (`except (KeyError, ValueError) as exc:`).
