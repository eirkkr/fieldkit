# Writing implementation specs

How to write a specification another contributor - or a fresh agent - can
implement without re-deriving your context. In a repo with an `openspec/`
directory (see ADR 021), OpenSpec carries the artifacts and lifecycle
described here; this file is the content guidance for what goes in them.

## Workflow

- OpenSpec has two layers: living specs in `openspec/specs/` (the current,
  agreed behaviour of each capability) and disposable change folders in
  `openspec/changes/<name>/` (a proposal in flight). A change is archived to
  `openspec/changes/archive/` on completion, syncing its delta into the
  living specs.
- The `openspec-*` skills are model-discoverable: Claude can invoke them on
  its own when a repo has `openspec/` activated, or you can invoke one
  directly from the `/` menu.
- A change's artifacts are `proposal.md` (what & why), `design.md` (how),
  and `tasks.md` (implementation steps) - the sections below map the
  durable guidance from the old manual flow onto these three.

## What a spec is

- A spec defines **contracts, decisions, and constraints** - not the
  artifacts that satisfy them (that is implementation). When unsure where
  something belongs, ask: is this a contract/decision, or the thing built to
  meet it?
- Record non-obvious or reversed decisions as ADRs (see `decisions.md`): the
  spec states the decision, the ADR holds the why and the rejected
  alternatives. Write the ADR when the decision settles - while drafting the
  change's artifacts, not as a deferred doc task - so the rationale does not
  accumulate in `proposal.md`/`design.md` and drift from the record.
- Flag provisional or placeholder content loudly, so a reader does not mistake
  a rough draft for a settled rule.

## Contracts (proposal.md, design.md)

- Pin the interface between modules/stages explicitly (fields, types, enums,
  nullability) in `design.md`. Prefer file-in/file-out boundaries so each
  part runs and is tested in isolation.
- An example artifact can be authoritative for *shape*, but its *values* must
  be audited before becoming a golden fixture - a golden test enshrines
  whatever is in it, bugs included.

## Build plan (tasks.md)

- Break work into ordered tasks, each with an explicit **definition-of-done**
  and, where one exists, a "copy/adapt this existing file" reference. Size the
  detail for the least-skilled likely implementer.
- **Walking-skeleton first:** get the whole thing running end to end (fixtures
  or stubs for unbuilt parts) before deepening any one part; then change one
  thing at a time on a tested base. Build order is not feature order.
- Progress lives in `tasks.md`'s own checkboxes, ticked as
  `openspec-apply-change` (or you, by hand) completes each task; `openspec
  status` reads them back. No separate progress doc to keep in sync.
