# 021 - Adopt OpenSpec for specs, centralized via the kit

## Decision

Adopt [OpenSpec](https://github.com/Fission-AI/OpenSpec) as the spec-driven
development workflow across consumer repos, with the kit - not each repo -
carrying the machinery:

- The CLI (`@fission-ai/openspec`, npm) is pinned by a `package.json` +
  `package-lock.json` in this repo; `just install` runs `npm ci` here and
  symlinks the binary into `~/.local/bin/openspec`.
- OpenSpec's generated Claude Code skills are vendored under the kit's
  `skills/` (skills delivery, not slash commands - ADR 014, and upstream
  subdirectory-command visibility issue Fission-AI/OpenSpec#1076) and
  symlinked user-level by the existing `link-skills.sh`.
- A consumer repo's entire footprint is one `openspec init --tools none`,
  which creates only the committed `openspec/` content directory (specs,
  changes, config) - no per-repo tool files or npm install.
- `conventions/specs.md` is reworked from a manual build-plan flow into
  guidance for OpenSpec artifacts (proposal/design/tasks).

Implementation is tracked in `build-plan-openspec.md`, retired when done.

## Reason

The workflow mapping is nearly 1:1. OpenSpec's two layers - living specs in
`openspec/specs/`, disposable change folders in `openspec/changes/` that are
archived on completion - are the pattern `specs.md` already teaches and
RunDrafter already practices by hand (a living `docs/spec/`, ADRs recorded as
decisions settle, `build-plan-*.md` files with per-task definitions-of-done
ticked in the implementing commit and retired when done). The tool codifies
the existing convention instead of imposing a new one, and its `init` is
light enough for gradual adoption in mature, issue-driven repos.

Centralization works because the generated skills contain no repo-local
machinery: they shell out to the `openspec` CLI, which the kit pins and puts
on PATH. That makes them ordinary pull-style assets under ADR 009/014 -
version-controlled here, symlinked user-level, inert in repos that never
invoke them.

Alternatives rejected:

- **GitHub Spec Kit** (`specify-cli`). Its uv-based install suits the
  toolchain, but `specify init` copies load-bearing scaffold into every repo
  (`.specify/` templates and shell scripts, `.claude/commands/speckit.*`),
  and the slash commands invoke those repo-local scripts - so they cannot be
  lifted to user level, every repo drifts to the version that initialized
  it, and upgrades are per-repo chores. Its `constitution.md` duplicates the
  always-on conventions layer this kit already provides, and its per-feature
  spec bundles have no living-spec layer for changes to merge into.
- **Staying manual.** The hand-rolled flow works (RunDrafter proves it) but
  is exactly the per-repo ceremony the kit exists to remove: every plan
  re-creates structure, and nothing enforces the spec/change lifecycle.

## Consequences

- The kit gains its first npm footprint (`package.json`, lockfile, gitignored
  `node_modules/`). Accepted as contained: consumers never touch npm, and the
  lockfile pins the tool centrally.
- Node >= 20.19.0 becomes a machine prerequisite for `just install`.
- The kit owns skill regeneration: version bumps re-run generation here (a
  `just openspec-refresh` recipe) instead of `openspec update` per repo;
  consumers pick changes up through the user-level symlinks.
- The OpenSpec skills are visible in every repo, including ones that never
  adopted it - pull-style and inert until invoked, the same trade ADR 009
  accepted.
- `specs.md`'s manual build-plan mechanics are superseded by the OpenSpec
  workflow; its durable content guidance (explicit contracts, walking
  skeleton, definitions-of-done) survives, reframed around OpenSpec's
  artifacts.
