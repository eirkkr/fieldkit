# 072 - Constant tables are frozendict

## Decision

On Python 3.15+, a lookup table that the code never changes, at module or class level, is a `frozendict` ([PEP 814](https://peps.python.org/pep-0814/)), written `NAME = frozendict({...})`. Where a table carries an annotation it is `Mapping[K, V]`; a table that is an operand or result of `|` carries none, and mypy infers `frozendict[K, V]`. `MappingProxyType` is not used for a table. A mapping a function receives is typed `Mapping[K, V]`, not `dict`, so it accepts a table.

## Reason

A `dict` constant is immutable only by agreement: nothing stops a later edit changing it, and a module's tables are shared by every caller. A `frozendict` refuses the change at runtime, where `Mapping` alone refuses it only for the type checker. It is also hashable when its keys and values are, so a table can sit in a frozen dataclass or a set without a rewrite.

`MappingProxyType` is a read-only view of a dict, so whoever holds the dict can still change it, and it cannot be hashed. A `frozendict` copies what it is given, so it has neither problem.

The annotation is `Mapping[K, V]` because a constant is read, and the weakest type covering the reads is the right one. It rejects `TABLE[k] = v` in the type checker exactly as `frozendict[K, V]` does, and it needs no change if a table's concrete type ever does. Nothing needs the hashability in the type today.

Rejected:

- **Leave tables as `dict`.** Cheapest, but immutability stays a property of the annotation and the habit.
- **Annotate `frozendict[K, V]` everywhere.** More exact, and the right choice where a table must be hashed through its type; none is. It would also tie each signature that names a table to the builtin.
- **Keep `MappingProxyType`.** See above: a view, not hashable.

## Consequences

- `Mapping` has no `|`, so a table that is an operand or result of `|` stays unannotated, and the type checker infers the joined table.
- `isinstance(x, dict)` is false for a `frozendict`: convert a table with `dict(table)` before passing it to code that tests for `dict`.
- A table that must be hashable through its type is annotated `frozendict[K, V]` for that case.
