# Build plan: OpenSpec centralised via the kit

Implements [ADR 021](docs/decisions/021-adopt-openspec-centralised-via-kit.md).
Self-contained: a fresh session can execute this without re-deriving context.
Tick tasks in the commit that does the work; retire (delete) this file in the
final commit.

## Summary

Wire [OpenSpec](https://github.com/Fission-AI/OpenSpec) into the kit so
consumer repos get the full workflow with zero per-repo tooling: the CLI is
pinned here by npm lockfile and symlinked onto PATH, the generated Claude
skills are vendored under `skills/` and reach `~/.claude/skills/` through the
existing `link-skills.sh`, and a consumer repo's only step is
`openspec init --tools none`.

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
  makes user-level centralisation viable.
- Kit patterns to copy: `scripts/link-skills.sh` (idempotent symlink loop,
  "Already linked /name, no change" on repeat runs), the `install` recipe in
  `justfile`, ADRs 009/014 for the pull-style user-level asset model.
- `~/.local/bin` is on PATH.

## Global definition-of-done

`just install` on a clean machine (with Node >= 20.19.0) yields a working
`openspec` on PATH and the OpenSpec skills in `~/.claude/skills/`; a second
run is a no-op. A consumer repo needs only `openspec init --tools none`. All
docs that describe the old manual build-plan flow are brought into line. No
formatter/lint runs (CI enforces markdown style).

## Tasks

### 0. Node prerequisite (manual, sudo)

Upgrade Node: `sudo n lts` (or any version >= 20.19.0). Not scriptable in
`just install` (sudo); the install script only *checks* the version.

- DoD: `node --version` reports >= 20.19.0.

### 1. Pin the CLI

Add root `package.json`: `"private": true`, single dependency
`"@fission-ai/openspec": "1.6.0"` (exact pin; lockfile pins transitives).
Run `npm install` to produce `package-lock.json`; commit both. Add
`node_modules/` to `.gitignore`.

- DoD: `npm ci` from repo root succeeds; `node_modules/.bin/openspec
  --version` prints 1.6.0; `git status` clean of node_modules.

### 2. Install step

New `scripts/install-openspec.sh`, copying the shape of
`scripts/link-skills.sh` (bash, `set -euo pipefail`, `$1` = kit dir,
idempotent with "no change" messages):

1. Check `node --version` >= 20.19.0; exit non-zero with an upgrade hint
   (`sudo n lts`) otherwise.
2. `npm ci --prefix "$kit"` (skip or no-op message when `node_modules` is
   already current, if cheaply detectable; plain `npm ci` is acceptable).
3. `ln -sfn "$kit/node_modules/.bin/openspec" ~/.local/bin/openspec` with
   the same already-linked guard as `link-skills.sh`.

Append the script to the `install` recipe in `justfile`.

- DoD: `just install` twice - first run installs and links, second prints
  no-change messages; `openspec --version` works from `$HOME`.

### 3. Vendor the generated skills

In a scratch dir (not the kit), run `openspec init --tools claude` with
delivery set to **skills only** - find the exact mechanism first (check
`openspec init --help` and `openspec config profile`; open item below). Copy
the generated `.claude/skills/openspec-*` directories into the kit's
`skills/` (top level, *not* `.claude/skills/` - ADR 014 keeps shipped source
inert in the kit repo). Audit each SKILL.md for assumptions that break at
user level (paths relative to the generating repo, references to
repo-committed files other than `openspec/`). `link-skills.sh` needs no
changes.

- DoD: `just install` links the new skills; `ls -l ~/.claude/skills/` shows
  `openspec-*` symlinks into the kit; SKILL.md audit notes recorded in the
  PR description (or fixes applied).

### 4. Refresh recipe

Add `just openspec-refresh`: bump/reinstall the package (`npm install
@fission-ai/openspec@latest` or edited pin + `npm install`), regenerate the
skills in a temp dir as in task 3, and rsync the `openspec-*` dirs back into
`skills/` (delete-and-replace so removed files don't linger). This replaces
per-repo `openspec update` - the kit owns regeneration.

- DoD: running the recipe against the currently pinned version is a no-op
  diff; recipe documented by a comment line in `justfile` (recipes carry
  their own `#` description).

### 5. Rework conventions

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

### 6. README

- Prerequisites: Node >= 20.19.0 (alongside existing `just`/`uv` prereqs).
- Consumer-repo checklist: add `openspec init --tools none` (creates the
  committed `openspec/` dir; skills and CLI come from the kit - no per-repo
  tool files or npm).

- DoD: a new consumer repo can be onboarded from the README alone.

### 7. End-to-end verification

In a scratch consumer repo (throwaway dir, `git init`):

1. `openspec init --tools none` - confirm only `openspec/` is created (no
   `.claude/` writes).
2. `openspec new change test-change`, `openspec status`,
   `openspec validate --all` all succeed.
3. `openspec update` there generates no tool files (config has tools none),
   i.e. it cannot fight the user-level skills.
4. Start Claude Code in that repo and confirm the OpenSpec skills resolve
   and drive the CLI.

- DoD: all four checks pass; then retire this file.

## Open items (resolve during task 3)

- Exact flag/config for skills-only delivery at init time (`--profile`?
  `openspec config profile` global default? per-run flag).
- Exact names of the generated skill dirs (docs say `openspec-*`); adjust
  `skills/` contents, ADR 021 wording, and this plan's DoDs to reality.
- Whether any generated asset expects `openspec/config.yaml` to list
  `claude` as a tool in consumer repos; if so, document the minimal
  config.yaml tweak in the README step instead of `--tools none`.
