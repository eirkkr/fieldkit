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
- `docs/decisions/` - ADRs recording this repo's own non-obvious design
  choices; the one `docs/` subtree.
- further areas as needs emerge - e.g. Claude Code assets (skills, commands,
  agents, hooks), shared scripts, editor/CI config.

## Setup

1. **Clone the kit.** Anywhere - it no longer hardcodes its location:

   ```bash
   git clone https://github.com/eirkkr/fieldkit.git ~/src/fieldkit
   ```

2. **Wire a consumer repo.** From the consumer repo root, link the kit and
   `@`-import through the symlink:

   ```bash
   ln -s ~/src/fieldkit .fieldkit
   echo '.fieldkit' >> .gitignore
   ```

   ```markdown
   @.fieldkit/CLAUDE.md
   ```

   For a Python repo, also add `@.fieldkit/conventions/python.md`, or import
   individual `conventions/*` files for only some. `.fieldkit` is gitignored, so
   every clone, collaborator, and CI checkout recreates it.

3. **Grant Claude access to the kit.** A consumer session runs in the consumer
   repo, so add your clone path to that repo's `.claude/settings.json`:

   ```json
   { "permissions": { "additionalDirectories": ["~/src/fieldkit"] } }
   ```

   or run `/add-dir ~/src/fieldkit` in-session. Point it at the real clone path,
   not the symlink.

4. **Start sessions from the repo root.** The load-on-demand files are
   referenced relative to the consumer repo root, so launch `claude` there, not
   a subdirectory. Worth repeating in each consumer repo's README.

5. **First run.** Accept Claude Code's external-import dialog for `@.fieldkit` -
   declining permanently disables it. Verify with `/memory`: `CLAUDE.md` and the
   convention files should show as loaded.

## Updating a shared rule

Every consumer reads the same files, so editing one here affects **all** of
them. Make changes in your kit clone, commit on a branch, and push - it's a
normal git repo. You have push access as the owner; add collaborators with write
access on GitHub if others consume it. Consumers pick up the change next
session.

## Development

Markdown is linted with [pymarkdown](https://github.com/jackdewinter/pymarkdown)
(line length 80, table rows exempt; config in `.pymarkdown`). Needs
[just](https://just.systems) and [uv](https://docs.astral.sh/uv/) - the recipes
run the linter via `uvx`, so no install step is required.

| Task             | Command      |
| ---------------- | ------------ |
| Lint all docs    | `just check` |
| Auto-fix issues  | `just fix`   |

## Status

`conventions/` and the `CLAUDE.md` entry point are in place. Still to do: wire
the consumer repos. See the open setup issue for the full build plan.
