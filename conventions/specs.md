# Writing implementation specs

How to write a specification another contributor - or a fresh agent - can
implement without re-deriving your context.

## What a spec is

- A spec defines **contracts, decisions, and constraints** - not the
  artifacts that satisfy them (that is implementation). When unsure where
  something belongs, ask: is this a contract/decision, or the thing built to
  meet it?
- Record non-obvious or reversed decisions as ADRs (see `decisions.md`): the
  spec states the decision, the ADR holds the why and the rejected
  alternatives.
- Flag provisional or placeholder content loudly, so a reader does not mistake
  a rough draft for a settled rule.

## Contracts

- Pin the interface between modules/stages explicitly (fields, types, enums,
  nullability). Prefer file-in/file-out boundaries so each part runs and is
  tested in isolation.
- An example artifact can be authoritative for *shape*, but its *values* must
  be audited before becoming a golden fixture - a golden test enshrines
  whatever is in it, bugs included.

## Build plan

- Break work into ordered tasks, each with an explicit **definition-of-done**
  and, where one exists, a "copy/adapt this existing file" reference. Size the
  detail for the least-skilled likely implementer.
- **Walking-skeleton first:** get the whole thing running end to end (fixtures
  or stubs for unbuilt parts) before deepening any one part; then change one
  thing at a time on a tested base. Build order is not feature order.
- Track progress in-repo next to the plan (a checklist ticked in the commit
  that does the work), not mirrored into issues that drift from an evolving
  spec.
