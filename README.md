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
- `repo-skills-overlay/` - the kit's own additions to those vendored skills,
  appended by `just openspec-refresh` after it regenerates them; one
  `<skill-name>.md` per skill patched.
- `schemas/` - kit-owned OpenSpec workflow schemas, linked file-by-file into
  an opt-in consumer repo's `openspec/schemas/`.
- `agents/` - shared Claude Code subagents, symlinked into `~/.claude/agents`
  by `just install` (see Setup).
- `statusline/` - the shared Claude Code status line script, symlinked to
  `~/.claude/statusline-command.sh` and wired up via `settings.json`'s
  `statusLine` key by `just install` (see Setup).
- `hooks/` - shared hooks of both kinds, told apart by filename: the git
  `pre-commit` hook, symlinked into an *opt-in* consumer repo's `.git/hooks` by
  `.fieldkit/scripts/enable-hooks.sh` (not by `just install` - `.git/hooks` is
  per-clone; see "Blocking commits to the default branch"), and the Claude Code
  `stop-format-drift.py` session hook, registered machine-wide by `just install`
  (see "Catching formatter drift").
- further areas as needs emerge - e.g. more Claude Code assets, shared scripts,
  editor/CI config.

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
   carry no AI attribution, `statusLine` to run the kit's linked
   `statusline-command.sh`, and a `hooks.Stop` entry for the format-drift hook
   (see "Catching formatter drift") - if the existing file already differs from
   any of those, it shows the diff and asks before changing it. Each of these
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
`config.yaml`), symlinks `.claude/skills/openspec-*` to the kit's vendored
copies in `repo-skills/`, links the `review-gated` schema into
`openspec/schemas/`, and selects it in `config.yaml`. It's idempotent - rerun
it after an `openspec-refresh` (below) that adds a new skill, or after the
kit gains a new schema file. Commit `openspec/` and the `.claude/skills`
symlinks.

The workflow is `review-gated`
([ADR 034](docs/decisions/034-review-gated-openspec-schema.md)), the kit's
replacement for the stock `spec-driven` schema: bite-sized tasks, a human
review gate ending every stage, and a final whole-change review before
archive. `conventions/specs.md` describes what that asks of an author and a
reviewer. The schema itself lives in `schemas/review-gated/`; note that its
files are linked individually rather than the directory being linked,
because OpenSpec's schema discovery doesn't follow a symlinked directory.

One thing the script can't do for you: the linked templates are fragments
with no H1, and while `rumdl check` in the consumer repo resolves the symlink
and honours the kit's own ignore for them, rumdl's language server reads only
the workspace-root config - so an editor will flag `MD041` on them until the
repo ignores it too. Add to the repo's rumdl config (StudyNav's
`pyproject.toml` has the worked example):

```toml
[tool.rumdl.per-file-ignores]
"**/schemas/*/templates/*.md" = ["MD041", "MD032"]
```

The leading `**/` matters - the language server passes an absolute path,
already resolved to the kit.

The kit owns keeping the vendored skills current: `just openspec-refresh`
bumps the pinned `openspec` version, regenerates `repo-skills/` from it, and
re-applies `repo-skills-overlay/*.md` on top - the rsync is `--delete`, so
kit additions to a vendored skill live in the overlay or they don't survive.
Adopting repos pick up the change through their symlinks next session; no
per-repo `openspec update` needed.

## Blocking commits to the default branch

`conventions/git.md` says never to commit directly to the default branch, but
that's instruction-only - it holds only if whatever is committing has read it.
The kit ships a `pre-commit` hook
([ADR 023](docs/decisions/023-block-default-branch-commits-via-hook.md)) that
enforces it structurally, firing on the actual `git commit` regardless of what
triggered it - you, a raw agent `git` call, or a subagent that skipped the
`push` skill.

It's opt-in per repo, and per *clone* - `.git/hooks` isn't version controlled,
so a fresh checkout needs it again. From the repo root:

```bash
.fieldkit/scripts/enable-hooks.sh
```

This symlinks `.git/hooks/pre-commit` to the kit's copy, so kit updates land
without reinstalling. It's idempotent, leaves any other hooks in `.git/hooks`
alone, and refuses rather than clobbers if a real `pre-commit` file is already
there. The kit repo installs the hook on itself the same way, running
`./scripts/enable-hooks.sh` from its own root.

The hook takes the default branch from the `fieldkit.defaultBranch` git config
when set, otherwise `origin/HEAD`, otherwise `main` - so an explicit override
always wins. `git commit --no-verify`
bypasses it - deliberately left as your escape hatch, and deliberately absent
from the hook's own output so an agent that hits the block branches instead of
routing around it.

## Auto-fixing and catching formatter drift

A formatter - your editor on save, or an auto-fixer - can rewrite a file *after*
Claude edited it, sometimes after Claude has already committed and pushed for
the turn, leaving the reformat stranded until someone notices. The kit ships a
Claude Code `Stop` hook
([ADR 024](docs/decisions/024-stop-hook-for-formatter-drift.md)) that fires as a
turn ends and does two things in one process:

1. Runs your repo's fix command, if it has one (see below).
2. Stops Claude from finishing when the working tree holds changes to files its
   own last commit included that it didn't write itself - asking it to check the
   diff, re-run affected tests, and commit and push them.

Both live in one hook on purpose: Claude Code runs all of an event's hooks *in
parallel*, so a separate fixer and detector would race rather than run in order.

`just install` registers it in `~/.claude/settings.json`, so it applies to every
session on the machine - no per-repo step. Unlike the `pre-commit` hook it needs
no per-clone install, since it lives in `~/.claude`, not `.git/`.

To turn on step 1, name the command in the repo's git config - there's no
default, and repos that set nothing skip straight to step 2:

```bash
git config fieldkit.fixCommand "just fix"
```

Its output is discarded rather than fed back to Claude, and a failing or hanging
fixer can never block the turn. This is the per-repo opt-in auto-fixer
[ADR 007](docs/decisions/007-agents-dont-run-linters.md) anticipated: agents
still don't run linters, and the kit still owns no format command of its own -
only the mechanism.

Like `fieldkit.defaultBranch`, it's per *clone*, so a fresh checkout needs it
set again. Git config can't be committed, so put the command in a `setup`-style
recipe rather than leaving it as folklore - that keeps it version-controlled and
reviewable while still needing a deliberate human run, so no command is ever
auto-executed out of repo content. The kit does this to itself with
`just setup`.

The hook stays quiet unless the drift pattern actually holds: it exits silently
outside a git repo, on a clean tree, before the session's first commit, on files
Claude edited itself, and on untracked files. When it does fire, Claude can
judge that the change wasn't formatter output, say so, and finish anyway.

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

The kit uses its own tooling on itself. Two steps are per *clone* rather than
per machine, so run them again after a fresh checkout:

```bash
just setup                 # fix command for the format-drift Stop hook
./scripts/enable-hooks.sh  # pre-commit hook blocking default-branch commits
```
