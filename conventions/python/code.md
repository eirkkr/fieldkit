# Python code conventions

Conventions for authoring Python source: docstrings, imports, member ordering, constants, multi-line text, enum values, record types, caching, and exception handling. Several rules below have no automated enforcement and rely on review.

## Docstrings

- Google-style; comply with ruff's `D` rules.
- Modules and classes: single line, sentence case, no trailing period.
- Public functions and methods: summary line, then `Args:` / `Returns:` / `Raises:` as needed; descriptions are full sentences ending in a period.
- Private (`_`-prefixed): not required; add one only when the logic isn't self-evident.

## Imports

- A package's `__all__` is its public surface. Import a public symbol from the package that owns it - not from the module that defines it (even a private `_`-module), and not from a parent package.
- Re-export what something imports through the package, and every type named in the signature of something re-exported - its parameter and return types. A caller receives those values whether or not it names them, so they are part of the surface. Leaving one out means the first caller that needs its name has to edit `__all__` or reach into the defining module, and the second is easier and silently breaks the rule above. A type's visibility should not depend on which half of a union a caller happened to test with `isinstance`.
- That still rules out a symbol used only inside its own package (in-package callers import it from its defining module), and one whose outside callers reach its defining module directly.
- An annotation-only import under `TYPE_CHECKING` counts as public usage - it is a real cross-package contract. A test import doesn't: a symbol used only by tests stays private, unless a public signature names it.
- On Python 3.14+ an annotation-only import can sit under `if TYPE_CHECKING:` without `from __future__ import annotations`, since PEP 649 defers annotation evaluation. Below 3.14 a runtime-evaluated annotation - notably a module- or class-level variable annotation - still needs the symbol imported at runtime, so don't move it.
- A module that `__init__` imports during initialisation can't import back from the package (it's only half-built at that point); it imports shared symbols directly from the source file, even public ones.
- Import a helper module as a namespace when its bare symbols would be ambiguous: `from pkg import _flasher as flasher`, called as `flasher.success(...)` - aliasing drops the `_`, the path keeps it. `current_actor()` could come from anywhere; `auth.current_actor()` says which subsystem answers. Import a named type directly - the name already says what it is.
- Import a module the same way throughout a file; two forms read as two dependencies.
- Name a module by what it exposes. A `_`-prefix marks a module as internal to its package, not part of its public surface.

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

Put a constant at the top of the module that uses it. Wrapping a group of them in a class or a frozen dataclass buys nothing - a module is already a namespace, so `limiter.API_READ` reads just as well as `Limits.API_READ` would, with no class to write and no instance to make. The standard library works this way too: `errno.ENOENT`, `stat.S_IRUSR`, `string.punctuation`.

Two cases:

- **One module uses it** - give it a leading underscore. Do this even if only one function reads it, so a reader can see every fixed value the module sets in one place, without opening the functions.
- **Several modules use it** - give the whole group a module of its own, and import that module by name so callers read `coll_names.HTTP_LOG`.

Use an `Enum` instead when one of these is true:

- Something has to handle every value, and should fail to type-check when a new one is added (`match` ending in `assert_never`).
- Something loops over the values, or asks whether a value is one of them.
- An argument should be typed as one of them, so any other string is an error.

If none of them is true, an `Enum` is work for nothing. A name that is written once and handed to a library or a template is just a string, and a `frozenset` is enough on its own to ask whether a value is in the set.

None of this helps when the same value is also written outside Python. Take a submit button: Python defines `SAVE = "save"` and checks `if SAVE in request.form`, while the template hand-writes `name="save"`. Nothing connects the two, so renaming the constant just means Python stops finding the button - no error, no failing import, the button silently does nothing.

Pick the side that owns the value and pass it to the other, so it is written once. For a template, that means handing the constants to the template engine and rendering `name="{{ SAVE }}"` instead of typing the string again.

## Multi-line text

Relies on review (no linter). Write text of three or more lines as it will appear, in one triple-quoted string passed through `textwrap.dedent`, with the opening and closing quotes on lines of their own. A line here is a line of the text produced, blank ones included.

```python
_BODY = textwrap.dedent(
    """
    Hello,

    Your report is ready.
    """
).strip()
```

`_BODY` is `"Hello,\n\nYour report is ready."`. `dedent` removes only the indent every line shares, so a line indented further than the others keeps the difference. `inspect.cleandoc` would do the work of both calls in one, but `textwrap` is where a reader looks for text handling, and `cleandoc` also expands tabs.

Don't write the text as adjacent string literals each ending in `\n`, or as a list of literals passed to `"\n".join`. Both put quotes and an escape on every line, and the reader has to look past them to see the text:

```python
_SUMMARY = (
    "Records                        3\n"
    "\n"
    "Requisite types\n"
    "  PREREQUISITE                 4\n"
    "  PRE-REQ                      1\n"
    "\n"
    "Maximum component depth        1"
)
```

`.strip()` drops the newline after the opening quotes and the one before the closing quotes. Where the text must end in a newline - a file's contents, a usage message written to a terminal - end the block in `.lstrip()`, which drops only the first:

```python
_USAGE = textwrap.dedent(
    """
    usage: prog [-h] FILE
      -h  show this help
    """
).lstrip()
```

`_USAGE` is `"usage: prog [-h] FILE\n  -h  show this help\n"`.

Four cases stay as one literal per line:

- **A line that ends in spaces.** Editors and hooks strip trailing whitespace from source, which would change the text without anyone seeing it.
- **A first line that is indented or blank.** `.strip()` and `.lstrip()` both remove that indent or blank line.
- **One long line wrapped across adjacent literals.** With no `\n` between them the literals make a single line of output, which is not multi-line text.
- **An f-string that inserts a value which can itself hold a newline.** The value goes in before `dedent` runs and its second line has no indent, so the lines no longer share one and nothing is removed.

[testing.md](testing.md#expected-multi-line-text) applies this to the text a test expects.

## Enum values

- `enum.auto()` when nothing outside the enum reads the value - the members are only ever compared to each other. A hand-written number there is bookkeeping: it has to track whatever ordering the enum declares, and inserting a member renumbers the rest.
- Explicit values when something outside does read them - a value persisted or serialised, one a library matches on, or one that *is* the payload (an enum whose values are the classes it dispatches to). That value is part of a contract, not an implementation detail.

## Record types

Choose by what the object is for:

- **A value**, never changed once built: `NamedTuple`. The default, as a house choice - Python's own docs do not name one.
- **A record changed after it is made** - a collector, a builder: `@dataclass`. A `NamedTuple` holding lists reads as a value and isn't one.
- **A value a tuple cannot express** - it needs `__post_init__`, or must not unpack or equal a bare tuple: `@dataclass(frozen=True)`.
- **The shape of a dict something else owns** - a JSON payload, a stored document: `TypedDict`, at that boundary only.

## Caching

`functools.cache` fits a function only when all three hold:

1. **The result depends only on the arguments**, and nothing it reads changes while the process runs - a class's schema, a checked-in file. Config, the environment and the database fail this; read them per call.
2. **No caller modifies the result.** Every caller gets the same object, so a cached list or dict is a shared global. Return an immutable value (`NamedTuple`, `tuple`, `frozenset`) to enforce it.
3. **It is called repeatedly with the same arguments**, and recomputing costs something or sharing one object is the point.

Never cache an instance method: the cache keeps every instance alive (ruff's `B019`). `@classmethod` over `@cache` is fine. Arguments must be hashable, since they are the key.

[testing.md](testing.md#loading-test-data) applies this to test data loaders.

## Exception handling

On Python 3.14+ (PEP 758), an `except` clause catching several types is written *without* parentheses: `except KeyError, ValueError:`. This is current syntax, not a Python-2 relic - ruff's formatter rewrites the parenthesised `except (KeyError, ValueError):` to this form under a `py314`+ target, so the bare form is the house style. Don't "correct" it by adding parentheses; the formatter only reverts the change, and lint does not flag it. Parentheses are still required when binding the caught exception with `as` (`except (KeyError, ValueError) as exc:`).
