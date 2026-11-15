# 072 - Constant tables are frozendict

## Decision

On Python 3.15+, a constant lookup table is a `frozendict` ([PEP 814](https://peps.python.org/pep-0814/)), annotated `Mapping[K, V]`. The rule is in `conventions/python/code.md`.

## Reason

A `dict` constant is immutable only by agreement: nothing stops a later edit changing it, and a module's tables are shared by every caller. A `frozendict` refuses the change at runtime, where `Mapping` alone refuses it only for the type checker. It is also hashable when its keys and values are, so a table can sit in a frozen dataclass or a set without a rewrite.

`MappingProxyType` is a read-only view of a dict, so whoever holds the dict can still change it, and it cannot be hashed. A `frozendict` copies what it is given, so it has neither problem.

The annotation is `Mapping[K, V]` because a constant is read, and the weakest type covering the reads is the right one. It rejects `TABLE[k] = v` in the type checker exactly as `frozendict[K, V]` does, and it needs no change if a table's concrete type ever does. `Mapping` has no `|`, so a table that is an operand or result of `|` stays unannotated and mypy infers `frozendict[K, V]`. A function's mapping parameter is `Mapping[K, V]` so that it accepts a table.

Rejected:

- **Leave tables as `dict`.** Cheapest, but immutability stays a habit.
- **Annotate `frozendict[K, V]` everywhere.** More exact, but it ties each signature that names a table to the builtin. Right only where a table must be hashed through its type.
- **Keep `MappingProxyType`.** A view, not hashable.

## Consequences

`isinstance(x, dict)` is false for a `frozendict`, so a table passed to code that tests for `dict` is converted first.
