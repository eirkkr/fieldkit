# Field Kit

Shared dev conventions, tooling, and reusable assets, drawn on across my repos.

Like a survival field kit: the **manual** (conventions) and the **instruments**
(reusable tooling) live in one place, and every repo reaches into the same kit.

## Layout

- `CLAUDE.md` - the entry point a consumer repo `@`-imports; holds the
  always-on rules directly and points to the opt-in, load-on-demand ones.
- `conventions/` - the load-on-demand docs: `git`, `github`, `decisions`,
  `specs`, `ai`, and `python/` for Python repos - a slim `README.md` hub
  indexing `code`, `setup`, and `testing`, each read on demand.
- `docs/decisions/` - ADRs recording this repo's own non-obvious design
  choices; the one `docs/` subtree.
- `skills/` - shared Claude Code skills, symlinked into `~/.claude/skills` by
  `just install` (see Setup).
- `repo-skills/` - vendored OpenSpec Claude Code skills, symlinked into an
  *opt-in* consumer repo's `.claude/skills` by
  `.fieldkit/scripts/enable-openspec.sh` (not by `just install` - see
  "Adopting OpenSpec in a consumer repo").
- `agents/` - shared Claude Code subagents, symlinked into `~/.claude/agents`
  by `just install` (see Setup).
- `statusline/` - the shared Claude Code status line script, symlinked to
  `~/.claude/statusline-command.sh` and wired up via `settings.json`'s
  `statusLine` key by `just install` (see Setup).
- further areas as needs emerge - e.g. more Claude Code assets (hooks), shared
  scripts, editor/CI config.

## Setup

Requires [just](https://just.systems), [uv](https://docs.astral.sh/uv/), and
Node >= 20.19.0 (for the pinned `openspec` CLI; `just install` only checks the
version - upgrade yourself first, e.g. `sudo n lts`).

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
   docs or CLAUDE.md rather than machine-local memory files. It also sets
   `attribution: {commit: "", pr: "", sessionUrl: false}` so commits and PRs
   carry no AI attribution, and `statusLine` to run the kit's linked
   `statusline-command.sh` - if the existing file already differs from either
   of those, it shows the diff and asks before changing it. Each of these
   only touches its own key, leaving the rest of the file alone.

4. **Start sessions from the repo root.** The load-on-demand files are
   referenced relative to the consumer repo root, so launch `claude` there, not
   a subdirectory. Worth repeating in each consumer repo's README.

5. **First run.** Accept Claude Code's external-import dialog for `@.fieldkit` -
   declining permanently disables it. Verify with `/memory`: `CLAUDE.md` and the
   convention files should show as loaded.

## Adopting OpenSpec in a consumer repo

OpenSpec ([ADR 021](docs/decisions/021-adopt-openspec-centralised-via-kit.md))
is opt-in per repo. `just install` (Setup step 1) already puts the pinned
`openspec` CLI on `PATH`, but adds no OpenSpec skills anywhere - a repo that
skips the steps below carries no OpenSpec context at all.

To opt in, from the consumer repo root (after Setup steps 1-2):

```bash
.fieldkit/scripts/enable-openspec.sh
```

This creates the repo's `openspec/` content dir (`specs/`, `changes/`,
`config.yaml`) and symlinks `.claude/skills/openspec-*` to the kit's vendored
copies in `repo-skills/`. It's idempotent - rerun it after an
`openspec-refresh` (below) that adds a new skill. Commit both `openspec/` and
the `.claude/skills` symlinks.

The kit owns keeping the vendored skills current: `just openspec-refresh`
bumps the pinned `openspec` version and regenerates `repo-skills/` from it.
Adopting repos pick up the change through their symlinks next session; no
per-repo `openspec update` needed.

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

Requires [just](https://just.systems), [uv](https://docs.astral.sh/uv/), and
Node >= 20.19.0. Run `just` to list available commands.
