# Build plan: OpenSpec centralised via the kit

Implements [ADR 021](docs/decisions/021-adopt-openspec-centralised-via-kit.md).
Self-contained: a fresh session can execute this without re-deriving context.
Tick tasks in the commit that does the work; retire (delete) this file in the
final commit.

## Summary

Wire [OpenSpec](https://github.com/Fission-AI/OpenSpec) into the kit so
consumer repos get the full workflow with no per-repo tooling of their own:
the CLI is pinned here by npm lockfile and symlinked onto PATH, and the
generated Claude skills are vendored under a new `repo-skills/` directory.
Adoption is opt-in per repo: an adopting repo runs
`.fieldkit/scripts/enable-openspec.sh`, which creates its `openspec/` content
dir and commits `.claude/skills/openspec-*` symlinks through `.fieldkit`.
Repos that don't opt in carry zero OpenSpec context, and even adopting repos
pay nothing per session until a skill is invoked (the vendored skills carry
`disable-model-invocation: true`).

## What research found

- Package: `@fission-ai/openspec`, latest **1.6.0**; bin entry `openspec ->
  bin/openspec.js`. Requires **Node >= 20.19.0**; this machine has 20.15.1
  with `n` available for upgrading. openspec is *not* currently installed
  anywhere (not on PATH, not in `npm ls -g`).
- `openspec init` creates `openspec/` (`specs/`, `changes/`, `config.yaml`)
  plus, per selected tool, generated assets: `.claude/skills/openspec-*/
  SKILL.md` and/or `.claude/commands/opsx/<id>.md` depending on delivery
  mode (`skills`/`commands`/`both`; default `both`). `--tools` accepts
  `none`, `all`, or a comma-separated list (e.g. `claude`).
  `openspec update` regenerates tool assets from global config +
  `openspec/config.yaml`.
- Use **skills delivery, not commands**: matches ADR 014, and subdirectory
  commands (`.claude/commands/opsx/*`) have a known visibility issue after
  Claude Code's commands->skills merge (Fission-AI/OpenSpec#1076).
- Generated skills shell out to the `openspec` CLI (resolved against the
  consumer repo's cwd) - no repo-local scripts or templates - which is what
  makes centralisation viable.
- Claude Code skill scoping (per current docs): a skill's description loads
  into the system prompt of every session in scope; a project-level
  `.claude/skills/<name>` entry may be a **symlink to a directory outside
  the repo** (documented, followed normally); a user-level skill *shadows* a
  project-level skill of the same name - so the kit must not link the
  OpenSpec skills user-level. `disable-model-invocation: true` in a skill's
  frontmatter drops its idle context cost to zero while keeping it in the
  `/` menu for manual invocation.
- Kit patterns to copy: `scripts/link-skills.sh` (idempotent symlink loop,
  "Already linked /name, no change" on repeat runs), the `install` recipe in
  `justfile`, ADRs 009/014 for asset placement.
- `~/.local/bin` is on PATH.

## Global definition-of-done

`just install` on a clean machine (with Node >= 20.19.0) yields a working
`openspec` on PATH and does **not** add OpenSpec skills to
`~/.claude/skills/`. An adopting repo needs only one run of
`.fieldkit/scripts/enable-openspec.sh`; a repo that skips it shows no
OpenSpec skills in its sessions. All docs that describe the old manual
build-plan flow are brought into line. No formatter/lint runs (CI enforces
markdown style).

## Tasks

### 0. Node prerequisite (manual, sudo)

Upgrade Node: `sudo n lts` (or any version >= 20.19.0). Not scriptable in
`just install` (sudo); the install script only *checks* the version.

- DoD: `node --version` reports >= 20.19.0.

### 1. Pin the CLI [x]

Add root `package.json`: `"private": true`, single dependency
`"@fission-ai/openspec": "1.6.0"` (exact pin; lockfile pins transitives).
Run `npm install` to produce `package-lock.json`; commit both. Add
`node_modules/` to `.gitignore`.

- DoD: `npm ci` from repo root succeeds; `node_modules/.bin/openspec
  --version` prints 1.6.0; `git status` clean of node_modules.

### 2. Install step (CLI only) [x]

New `scripts/install-openspec.sh`, copying the shape of
`scripts/link-skills.sh` (bash, `set -euo pipefail`, `$1` = kit dir,
idempotent with "no change" messages):

1. Check `node --version` >= 20.19.0; exit non-zero with an upgrade hint
   (`sudo n lts`) otherwise.
2. `npm ci --prefix "$kit"` (skip or no-op message when `node_modules` is
   already current, if cheaply detectable; plain `npm ci` is acceptable).
3. `ln -sfn "$kit/node_modules/.bin/openspec" ~/.local/bin/openspec` with
   the same already-linked guard as `link-skills.sh`.

Append the script to the `install` recipe in `justfile`. This step handles
the CLI only - skills are deliberately not linked user-level (ADR 021).

- DoD: `just install` twice - first run installs and links, second prints
  no-change messages; `openspec --version` works from `$HOME`;
  `~/.claude/skills/` contains no `openspec-*` entries.

### 3. Vendor the generated skills under `repo-skills/` [x]

In a scratch dir (not the kit), run `openspec init --tools claude` with
delivery set to **skills only** - find the exact mechanism first (check
`openspec init --help` and `openspec config profile`; open item below). Copy
the generated `.claude/skills/openspec-*` directories into a new top-level
kit directory `repo-skills/` - *not* `skills/` (which `link-skills.sh`
links user-level) and *not* `.claude/skills/` (ADR 014 keeps shipped source
inert in the kit repo). Audit each SKILL.md for assumptions that break when
symlinked into another repo (paths relative to the generating repo,
references to repo-committed files other than `openspec/`). Patch
`disable-model-invocation: true` into each SKILL.md's frontmatter (ADR 021:
skills are invoked deliberately from the `/` menu and cost no idle context).

- DoD: `repo-skills/openspec-*/SKILL.md` committed, each frontmatter
  carrying `disable-model-invocation: true`; `just install` leaves
  `~/.claude/skills/` free of them; SKILL.md audit notes recorded in the PR
  description (or fixes applied).

Findings, folded into Open Items below and the PR description: delivery mode
is a global config key (`openspec config set delivery skills`), not an
`init` flag; the 6 generated dirs are `openspec-{apply-change,archive-change,
explore,propose,sync-specs,update-change}`; `--tools none` needs no
config.yaml tools entry (verified `new change`/`status`/`validate` all work
against it). Audit: no generating-repo-relative paths or non-`openspec/`
file references found. One non-blocking quirk left as-is (upstream content,
re-vendored verbatim by task 5's refresh): several SKILL.md bodies tell the
user to run `/opsx:apply`, `/opsx:continue`, `/opsx:archive` etc., but those
are `commands`-delivery artifacts that skills-only delivery never
generates - harmless (prose suggestion, not a tool call the skill invokes)
but will never resolve for a user following it literally.

### 4. Per-repo enable script [x]

New `scripts/enable-openspec.sh`, run *from a consumer repo's root* (not
passed the kit dir - it finds the kit via the repo's own `.fieldkit`
symlink). Idempotent, same message style as `link-skills.sh`:

1. Verify `./.fieldkit` resolves and `openspec` is on PATH; exit with a
   pointer to the kit README otherwise.
2. If no `openspec/` dir: run `openspec init --tools none`.
3. `mkdir -p .claude/skills`; for each `.fieldkit/repo-skills/openspec-*/`,
   `ln -sfn` a *relative* symlink
   `.claude/skills/<name> -> ../../.fieldkit/repo-skills/<name>` (relative,
   so the link works for any clone location; it dangles harmlessly on
   machines without the kit, same as the `@`-import).
4. Remind (echo) that `openspec/` and the `.claude/skills` symlinks should
   be committed.

- DoD: running twice in a scratch repo - first run creates `openspec/` and
  the symlinks, second prints no-change messages; the symlinks resolve.

### 5. Refresh recipe

Add `just openspec-refresh`: bump/reinstall the package (`npm install
@fission-ai/openspec@latest` or edited pin + `npm install`), regenerate the
skills in a temp dir as in task 3, re-apply the `disable-model-invocation`
frontmatter patch, and rsync the `openspec-*` dirs back into
`repo-skills/` (delete-and-replace so removed files don't linger). This
replaces per-repo `openspec update` - the kit owns regeneration and
adopting repos pick changes up through their symlinks. Note: if a refresh
adds a *new* skill dir, adopting repos need `enable-openspec.sh` re-run to
gain the new symlink; say so in the recipe's output.

- DoD: running the recipe against the currently pinned version is a no-op
  diff; recipe carries its own `#` description line in `justfile`.

### 6. Rework conventions

- Rewrite `conventions/specs.md` around OpenSpec: open with the workflow
  (skills, `openspec/` layout, changes archived on completion), then map the
  surviving guidance onto artifacts - contracts pinned explicitly
  (proposal/design), walking-skeleton build order and per-task
  definition-of-done (tasks), ADR linkage unchanged. Drop the manual
  track-progress-next-to-the-plan mechanics that OpenSpec now provides.
- Update the load-on-demand row in `CLAUDE.md` ("Writing an implementation
  spec or plan") so its wording points at the OpenSpec workflow for repos
  with an `openspec/` dir, still reading `specs.md` for content guidance.

- DoD: no kit doc still teaches the manual build-plan flow as current; the
  ADR-review rule ("bring docs that teach the old pattern into line",
  CLAUDE.md) is satisfied for this change.

### 7. README

- Prerequisites: Node >= 20.19.0 (alongside existing `just`/`uv` prereqs).
- Consumer-repo checklist: adopting repos run
  `.fieldkit/scripts/enable-openspec.sh` from the repo root, then commit
  `openspec/` and the `.claude/skills` symlinks. Repos that don't want
  OpenSpec do nothing and carry no OpenSpec context.

- DoD: a new consumer repo can be onboarded (with or without OpenSpec) from
  the README alone.

### 8. End-to-end verification

In a scratch consumer repo (throwaway dir, `git init`, `.fieldkit` symlink):

1. `.fieldkit/scripts/enable-openspec.sh` - confirm it creates only
   `openspec/` and the `.claude/skills/openspec-*` symlinks; second run is a
   no-op.
2. `openspec new change test-change`, `openspec status`,
   `openspec validate --all` all succeed.
3. `openspec update` there generates no tool files (config has tools none),
   i.e. it cannot fight the symlinked skills.
4. Start Claude Code in that repo and confirm the OpenSpec skills appear in
   the `/` menu but contribute no descriptions to context
   (`disable-model-invocation`), and that invoking one loads it and drives
   the CLI.
5. In a second scratch repo *without* the enable script, confirm no
   OpenSpec skills appear in the session's skill listing.

- DoD: all five checks pass; then retire this file.

## Open items (resolved during task 3)

- Skills-only delivery: no `init` flag - it's the global config key
  `delivery` (`both` by default). Set once per machine with
  `openspec config set delivery skills`, then `openspec init --tools claude`
  generates only `.claude/skills/openspec-*` (no `.claude/commands/`).
  `just install`/`enable-openspec.sh` don't need to set this themselves:
  it only affects `openspec init`/`update` runs against real tool configs,
  and the kit's own regeneration (task 3, task 5) is the only place that
  runs `init --tools claude`.
- Generated skill dirs are exactly: `openspec-apply-change`,
  `openspec-archive-change`, `openspec-explore`, `openspec-propose`,
  `openspec-sync-specs`, `openspec-update-change` - matches the
  `openspec-*` glob assumed elsewhere in this plan, no adjustment needed.
- `openspec/config.yaml` from `--tools none` carries no `tools` field at all
  and needs none added - verified `new change`, `status --json`, and
  `validate` all work against it standalone. No config tweak needed in
  `enable-openspec.sh`.
