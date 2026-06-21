# Field Kit

Shared dev conventions, tooling, and reusable assets, drawn on across my repos.

Like a survival field kit: the **manual** (conventions) and the **instruments**
(reusable tooling) live in one place, and every repo reaches into the same kit.

## Layout

- `CLAUDE.md` - the entry point a consumer repo `@`-imports; pulls in the
  language-agnostic conventions and points to the opt-in language-specific ones.
- `conventions/` - the convention docs themselves: `workflow`, `git`, `github`,
  `style` (language-agnostic), and `python` (opt-in, for Python repos).
- further areas as needs emerge - e.g. Claude Code assets (skills, commands,
  agents, hooks), shared scripts, editor/CI config.

## How it's consumed

Cloned once to a stable path (`~/src/fieldkit`); consumer repos reference what
they need and are granted write/push so a shared rule can be updated from
anywhere. Editing a file here can affect **every** consumer.

## Status

`conventions/` and the `CLAUDE.md` entry point are in place. Still to do: clone
to the stable path and wire the consumer repos. See the open setup issue for the
full build plan.
