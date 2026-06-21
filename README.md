# Field Kit

Shared dev conventions, tooling, and reusable assets, drawn on across my repos.

Like a survival field kit: the **manual** (conventions) and the **instruments**
(reusable tooling) live in one place, and every repo reaches into the same kit.

## Layout

- `CLAUDE.md` - the entry point a consumer repo `@`-imports; pulls in the
  language-agnostic conventions and points to the opt-in language-specific ones.
- `conventions/` - the convention docs themselves: `workflow`, `git`, `github`,
  `style`, `decisions` (language-agnostic), and `python` (opt-in, for Python
  repos).
- further areas as needs emerge - e.g. Claude Code assets (skills, commands,
  agents, hooks), shared scripts, editor/CI config.

## Setup

1. **Clone to the fixed path.** The imports in `CLAUDE.md` are absolute
   (`@~/src/fieldkit/...`), so the clone must live at `~/src/fieldkit`:

   ```bash
   git clone https://github.com/eirkkr/fieldkit.git ~/src/fieldkit
   ```

2. **Wire a consumer repo.** Add to that repo's own `CLAUDE.md`:

   ```markdown
   @~/src/fieldkit/CLAUDE.md
   ```

   For a Python repo, also add `@~/src/fieldkit/conventions/python.md`. Or
   import individual `conventions/*` files if you want only some.

3. **Grant Claude access to the path.** A consumer session runs in the consumer
   repo, so to let Claude read and edit the kit from there, add the path to that
   repo's `.claude/settings.json`:

   ```json
   { "permissions": { "additionalDirectories": ["~/src/fieldkit"] } }
   ```

   or run `/add-dir ~/src/fieldkit` in-session. (If `~` isn't expanded, use the
   full absolute path.)

## Updating a shared rule

Every consumer reads the same files, so editing one here affects **all** of
them. Make changes in `~/src/fieldkit`, commit on a branch, and push - it's a
normal git repo. You have push access as the owner; add collaborators with write
access on GitHub if others consume it. Consumers pick up the change next
session.

## Status

`conventions/` and the `CLAUDE.md` entry point are in place. Still to do: clone
to the stable path and wire the consumer repos. See the open setup issue for the
full build plan.
