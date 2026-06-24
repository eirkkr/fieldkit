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

## Rolling out a rule change to consumers

After merging a rule change here, a consumer repo may need matching changes -
docs that now contradict the rules, or a command or recipe the rules imply.
Paste this into a session in the consumer repo:

```text
The shared conventions kit (imported here via @.fieldkit) has changed. See what
changed: review the kit's recent history with `git -C .fieldkit log` and
`git -C .fieldkit show <commit>`. It squash-merges, so the latest commit on main
is the change (use a wider range if catching up several). Then reconcile this
repo to the current kit conventions:

1. Audit agent-facing docs and instructions for anything that now contradicts
   the kit, and bring them into line.
2. Make any repo-side change the new rules imply - commands, recipes, config.
3. Leave human-facing tooling alone: don't touch CI, pre-commit, or the linters
   themselves. This reconciles agent instructions, not the human's tools.

Follow the kit's git conventions: show me the proposed changes for approval
before editing, work on a branch, and open a PR.
```

## Feeding failures back to an agent

Agents don't run linters or formatters
([ADR 007](docs/decisions/007-agents-dont-run-linters.md)) - you run those and
hand back any failures. (Tests are different: the agent runs those itself as
part of its loop.) When you do need to feed command output back, do it cheaply:

- Type `!<command>` in the Claude Code prompt. It runs in the session and the
  output lands in context directly - no copy-paste.
- Filter at the source so only failures land, not noise, using the tool's own
  quiet/errors-only flags (the exact command is per-repo) - e.g.
  `pytest -q --tb=line` or `ruff check --output-format=concise`. Pipe through
  `tail`/`grep` for anything still noisy.
- Reach for a cheaper subagent (e.g. Haiku) only when raw output is genuinely
  huge *and* reducing it needs judgement, not a flag: it reads the flood in its
  own window and hands back a digest. For normal runs, flags are cheaper and
  won't silently drop a real failure.

This is human-facing on purpose - it's how you operate the loop, not a rule for
the agent, so it stays out of every session's context.

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
