# Python code conventions

Conventions for authoring Python source. Several rules below have no linter and rely on review.

## Docstrings

- Google-style; comply with ruff's `D` rules.
- Modules and classes: single line, sentence case.
- Public functions and methods: summary line, then `Args:` / `Returns:` / `Raises:` as needed; descriptions are full sentences ending in a period.
- Private (`_`-prefixed): not required; add one only when the logic isn't self-evident.

## Imports

- A package's `__all__` is its public surface. Import a public symbol from the package that owns it - not from the module that defines it (even a private `_`-module), and not from a parent package.
- Re-export what something imports through the package, plus every type in the signature of something re-exported (parameters and returns). A caller receives those values whether or not it names them, so they are part of the surface. Leave one out and the first caller needing its name either edits `__all__` or reaches into the defining module, the easier of which silently breaks the rule above. A type's visibility must not depend on which half of a union a caller tested with `isinstance`.
- A symbol used only inside its own package stays out (in-package callers import it from its defining module), as does one whose outside callers reach its defining module directly.
- An annotation-only import under `TYPE_CHECKING` counts as public usage, a real cross-package contract. A test import doesn't: a symbol used only by tests stays private unless a public signature names it.
- On Python 3.14+ an annotation-only import can sit under `if TYPE_CHECKING:` without `from __future__ import annotations` (PEP 649 defers annotation evaluation). Below 3.14 a runtime-evaluated annotation, notably a module- or class-level variable annotation, still needs the runtime import: leave it.
- A module that `__init__` imports during initialisation can't import back from the half-built package; it imports shared symbols directly from the source file, even public ones.
- Import a helper module as a namespace when its bare symbols would be ambiguous: `from pkg import _flasher as flasher`, called as `flasher.success(...)` (the alias drops the `_`, the path keeps it). `auth.current_actor()` says which subsystem answers; bare `current_actor()` doesn't. Import a named type directly: its name says what it is.
- Import a module the same way throughout a file; two forms read as two dependencies.
- Name a module by what it exposes. A `_`-prefix marks it internal to its package.

## Member ordering

Relies on review (no linter). Order modules: constants, then public functions and classes, then private helpers (callers above callees). Order class members:

1. Class variables and constants
2. `__init__`, then other dunders
3. Properties
4. Public instance methods
5. Classmethods
6. Private and static methods

Within a group, put callers above callees and more central members higher.

## Constants

Put a constant at the top of the module that uses it. A class or frozen dataclass around a group adds nothing: a module is already a namespace, so `limiter.API_READ` reads as well as `Limits.API_READ`, as in the standard library (`errno.ENOENT`, `stat.S_IRUSR`).

Two cases:

- **One module uses it** - give it a leading underscore, even if one function reads it, so every fixed value the module sets is visible in one place.
- **Several modules use it** - give the whole group a module of its own, and import that module by name so callers read `coll_names.HTTP_LOG`.

Use an `Enum` instead when one of these is true:

- Something has to handle every value, and should fail to type-check when a new one is added (`match` ending in `assert_never`).
- Something loops over the values, or asks whether a value is one of them.
- An argument should be typed as one of them, so any other string is an error.

Otherwise an `Enum` is wasted work: a name written once and handed to a library or template is just a string, and a `frozenset` answers membership.

A constant doesn't help when the same value is also written outside Python. Python defines `SAVE = "save"` and checks `if SAVE in request.form`, while the template hand-writes `name="save"`. Nothing connects them: rename the constant and the button silently does nothing, with no error or failing import.

Let the side that owns the value pass it to the other, so it is written once: hand the constants to the template engine and render `name="{{ SAVE }}"`.

## Constant tables

On Python 3.15+ ([PEP 814](https://peps.python.org/pep-0814/)), write a lookup table the code never changes, at module or class level, as `frozendict({...})`. Never use `MappingProxyType`. Annotate it `Mapping[K, V]` when it is annotated at all, and leave it unannotated when it is an operand or result of `|`, since `Mapping` has no `|` and mypy infers `frozendict`. Type a function's mapping parameter `Mapping[K, V]`, not `dict`. Before passing a table to code that tests `isinstance(x, dict)`, convert it with `dict(table)`. Why: [ADR 072](../../docs/decisions/072-constant-tables-are-frozendict.md).

## Multi-line text

Relies on review (no linter). Write text of three or more lines as it will appear: one triple-quoted block passed through `textwrap.dedent`, the call ending in `.strip()`, with the opening and closing quotes on lines of their own. Blank lines count as lines; shorter text stays one literal.

```python
_BODY = textwrap.dedent(
    """
    Hello,

    Your report is ready.
    """
).strip()
```

`_BODY` is `"Hello,\n\nYour report is ready."`: `dedent` removes the shared indent (a line indented further keeps the difference) and `.strip()` removes whitespace at both ends.

End in `.lstrip()` instead where the text must end in a newline:

```python
_USAGE = textwrap.dedent(
    """
    usage: prog [-h] FILE
      FILE  the file to read
      -h    show this help
    """
).lstrip()
```

`_USAGE` is `"usage: prog [-h] FILE\n  FILE  the file to read\n  -h    show this help\n"`.

Avoid adjacent literals each ending in `\n` and lists passed to `"\n".join`: the reader has to look past quotes to see the text. Prefer `textwrap` to `inspect.cleandoc`, which also expands tabs and is not where a reader looks for text handling.

Four cases stay as adjacent literals:

- **A line that ends in spaces** - inside the block, editors and pre-commit hooks strip them.
- **A first line that is indented or blank** - `.strip()` and `.lstrip()` both remove that indent or blank line.
- **One long line wrapped across literals** - with no `\n` between them it is one line of output, not multi-line text.
- **An f-string that inserts a value which can span lines** - the value goes in before `dedent` runs, and the value's second line starts at column 0, so the string's lines share no indent to remove.

[testing.md](testing.md#expected-multi-line-text) applies this to the text a test expects.

## Enum values

- `enum.auto()` when nothing outside the enum reads the value and members are only compared to each other; a hand-written number is bookkeeping that inserting a member renumbers.
- Explicit values when something outside reads them: a value persisted or serialised, one a library matches on, or one that *is* the payload (an enum whose values are the classes it dispatches to). That value is part of a contract.

## Record types

Choose by what the object is for:

- **A value**, never changed once built: `NamedTuple`, the house default.
- **A record changed after it is made** (a collector, a builder): `@dataclass`. A `NamedTuple` holding lists reads as a value and isn't one.
- **A value a tuple cannot express** - it needs `__post_init__`, or must not unpack or equal a bare tuple: `@dataclass(frozen=True)`.
- **The shape of a dict something else owns** - a JSON payload, a stored document: `TypedDict`, at that boundary only.

## Caching

`functools.cache` fits a function only when all three hold:

1. **The result depends only on the arguments**, and nothing it reads changes while the process runs (a class's schema, a checked-in file). Config, the environment and the database fail this; read them per call.
2. **No caller modifies the result.** Every caller gets the same object, so a cached list or dict is a shared global. Return an immutable value (`NamedTuple`, `tuple`, `frozenset`).
3. **It is called repeatedly with the same arguments**, and recomputing costs something or sharing one object is the point.

Never cache an instance method: the cache keeps every instance alive (ruff `B019`). `@classmethod` over `@cache` is fine. Arguments must be hashable.

[testing.md](testing.md#loading-test-data) applies this to test data loaders.

## Narrowing a type

Narrow a value the type allows but an earlier step has ruled out (an optional field already filtered on) with `typing.cast`, or change the type so the case cannot arise. A guard for it is never reached, so no test covers it and a coverage-gated repo cannot keep it. The cast is only as true as that step: name the step in a comment.

## Exception handling

On Python 3.14+ (PEP 758), an `except` catching several types takes *no* parentheses: `except KeyError, ValueError:`. This is current syntax, not a Python 2 relic: ruff's formatter rewrites the parenthesised form to it under a `py314`+ target, and reverts any parentheses added back. Parentheses stay required when binding with `as` (`except (KeyError, ValueError) as exc:`).
