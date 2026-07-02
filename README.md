# Field Kit

Shared dev conventions, tooling, and reusable assets, drawn on across my repos.

Like a survival field kit: the **manual** (conventions) and the **instruments**
(reusable tooling) live in one place, and every repo reaches into the same kit.

## Layout

- `CLAUDE.md` - the entry point a consumer repo `@`-imports; pulls in the
  language-agnostic conventions and points to the opt-in language-specific ones.
- `conventions/` - the convention docs themselves: `workflow`, `git`, `github`,
  `decisions`, `specs`, `ai`, and `python/` for Python repos - a slim
  `README.md` hub indexing `code`, `setup`, and `testing`, each read on demand.
- `docs/decisions/` - ADRs recording this repo's own non-obvious design
  choices; the one `docs/` subtree.
- `skills/` - shared Claude Code skills, symlinked into `~/.claude/skills` by
  `just install` (see Setup).
- further areas as needs emerge - e.g. more Claude Code assets (agents, hooks),
  shared scripts, editor/CI config.

## Setup

1. **Clone the kit.** Anywhere - it no longer hardcodes its location:

   ```bash
   git clone https://github.com/eirkkr/fieldkit.git ~/src/fieldkit
   ```

   Then wire the kit's skills into your user-level Claude config (once per
   machine - the skill sources are version-controlled here, but the symlink
   into `~/.claude` is not):

   ```bash
   cd ~/src/fieldkit && just install
   ```

   This makes `/kit-reconcile` available in every repo. See "Rolling out a rule
   change to consumers".

2. **Wire a consumer repo.** From the consumer repo root, link the kit and
   `@`-import through the symlink:

   ```bash
   ln -s ~/src/fieldkit .fieldkit
   echo '.fieldkit' >> .gitignore
   ```

   ```markdown
   @.fieldkit/CLAUDE.md
   ```

   For a Python repo, also add `@.fieldkit/conventions/python/README.md`; it
   stays slim and indexes `code`, `setup`, and `testing`, which Claude reads on
   demand. `.fieldkit` is gitignored - every collaborator or CI checkout runs
   this step once to recreate the symlink.

3. **Grant Claude access to the kit.** `just install` patches
   `~/.claude/settings.json`: adds the kit path to
   `permissions.additionalDirectories` so all consumer sessions can read it
   without a prompt, and sets `autoMemoryEnabled: false` so learnings go into
   docs or CLAUDE.md rather than machine-local memory files.

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
docs that now contradict the rules, or a command or recipe the rules imply. In a
session in the consumer repo, run:

```text
/kit-reconcile
```

It reviews the kit's recent history, then reconciles this repo's agent-facing
docs and tooling to the current conventions, working on a branch and showing the
changes for approval before editing.

Each consumer tracks how far it has caught up in a committed `.fieldkit-rev`
file - the kit commit it was last reconciled to. With no argument the command
reconciles every kit commit since that marker, then advances it; a no-op
reconcile still opens a marker-only PR, recording the repo was checked. On a repo
with no marker yet it reviews just the latest commit, warns, and creates the
file. Override the range with `/kit-reconcile N` (the last N commits) or
`/kit-reconcile latest` (the latest only). See
[ADR 012](docs/decisions/012-reconcile-marker.md).

`/kit-reconcile` reconciles *instructions*, not the codebase. When a convention
change also implies source edits, it surfaces the affected conventions and offers
to file issues; the actual code sweep is a separate, still-to-be-built
`/kit-audit` command.

The skill is defined in `skills/kit-reconcile/SKILL.md` and wired up by
`just install` (see Setup); editing that file updates it everywhere.

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

Requires [just](https://just.systems) and [uv](https://docs.astral.sh/uv/). Run
`just` to list available commands.
