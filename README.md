# fieldkit

Shared dev conventions, tooling, and reusable assets, drawn on across my repos.

Like a survival field kit: the **manual** (conventions) and the **instruments**
(reusable tooling) live in one place, and every repo reaches into the same kit.

## Planned layout

- `conventions/` — convention docs, referenced from each repo (e.g. `@`-imported
  into a `CLAUDE.md`): `git`, `github`, `workflow`, `style`.
- further areas as needs emerge — e.g. Claude Code assets (skills, commands,
  agents, hooks), shared scripts, editor/CI config.

## How it's consumed

Cloned once to a stable path (`~/src/fieldkit`); consumer repos reference what
they need and are granted write/push so a shared rule can be updated from
anywhere. Editing a file here can affect **every** consumer.

## Status

Stub. See the open setup issue for the full build plan.
