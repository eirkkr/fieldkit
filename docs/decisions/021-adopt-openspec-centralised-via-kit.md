# 021 - Adopt OpenSpec for specs, centralised via the kit

## Decision

Adopt [OpenSpec](https://github.com/Fission-AI/OpenSpec) as the spec-driven
development workflow, with the kit - not each repo - carrying the machinery,
and with adoption opt-in per repo:

- The CLI (`@fission-ai/openspec`, npm) is pinned by a `package.json` +
  `package-lock.json` in this repo; `just install` runs `npm ci` here and
  symlinks the binary into `~/.local/bin/openspec`.
- OpenSpec's generated Claude Code skills are vendored under a new kit
  directory `repo-skills/` (skills delivery, not slash commands - ADR 014,
  and upstream subdirectory-command visibility issue
  Fission-AI/OpenSpec#1076). Unlike `skills/`, this directory is *not*
  linked user-level by `just install`. Each vendored SKILL.md is patched
  with `disable-model-invocation: true`, so even in adopting repos the
  skills cost no context until a session invokes one (`/openspec-...`).
- A repo opts in by running `.fieldkit/scripts/enable-openspec.sh` from its
  root, which runs `openspec init --tools none` (creating the committed
  `openspec/` content directory) and commits symlinks
  `.claude/skills/openspec-* -> ../../.fieldkit/repo-skills/openspec-*`.
  Repos that don't opt in carry nothing.
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

Centralisation works because the generated skills contain no repo-local
machinery: they shell out to the `openspec` CLI, which the kit pins and puts
on PATH, so a single kit copy can serve every repo through symlinks (a
project-level `.claude/skills/<name>` entry may be a symlink to a directory
outside the repo - documented Claude Code behaviour).

Per-repo opt-in, rather than the user-level linking the kit uses for its own
skills, follows ADR 009's placement logic. A skill's description loads into
the system prompt of every session in scope, so a user-level OpenSpec set
would tax every repo - including small ones that will never adopt it - for
nothing. That context cost makes these skills behave more like the
conventions (push, per-repo opt-in via the `.fieldkit` symlink) than like
the kit's own always-wanted skills (pull, user-level). Opting in through
committed symlinks also means the skills appear exactly where an `openspec/`
directory exists, and kit-side refreshes still propagate through the links.

The same logic recurses inside an adopting repo: most sessions (lint fixes,
pushing a branch) don't touch specs, so the skills are also hidden
per-session via `disable-model-invocation: true` - zero idle context, with
invocation from the `/` menu as the per-session opt-in. The cost is that
Claude won't proactively suggest the workflow; acceptable because OpenSpec's
commands are deliberate, user-initiated actions, driven the same way as
`/push` and `/pr`.

Alternatives rejected:

- **GitHub Spec Kit** (`specify-cli`). Its uv-based install suits the
  toolchain, but `specify init` copies load-bearing scaffold into every repo
  (`.specify/` templates and shell scripts, `.claude/commands/speckit.*`),
  and the slash commands invoke those repo-local scripts - so they cannot be
  lifted out of the repo, every repo drifts to the version that initialised
  it, and upgrades are per-repo chores. Its `constitution.md` duplicates the
  always-on conventions layer this kit already provides, and its per-feature
  spec bundles have no living-spec layer for changes to merge into.
- **User-level linking with per-repo opt-out.** Claude Code supports
  silencing a user-level skill per project (`skillOverrides: "off"` in
  `.claude/settings.json`), but that inverts the burden: every repo that
  *doesn't* use OpenSpec must enumerate and silence the skill names, and
  must revisit the list whenever a refresh adds a skill.
- **Staying manual.** The hand-rolled flow works (RunDrafter proves it) but
  is exactly the per-repo ceremony the kit exists to remove: every plan
  re-creates structure, and nothing enforces the spec/change lifecycle.

## Consequences

- The kit gains its first npm footprint (`package.json`, lockfile, gitignored
  `node_modules/`). Accepted as contained: consumers never touch npm, and the
  lockfile pins the tool centrally.
- Node >= 20.19.0 becomes a machine prerequisite for `just install`.
- The kit now has two skill tiers: `skills/` (user-level, linked everywhere
  by `just install`) and `repo-skills/` (per-repo opt-in, linked by the
  enable script). `link-skills.sh` must not touch `repo-skills/`.
- The kit must never also link the OpenSpec skills user-level: a user-level
  skill shadows a project-level one of the same name, which would defeat the
  per-repo links.
- Adopting repos commit `.claude/skills` symlinks that resolve through
  `.fieldkit` and dangle on machines without the kit clone - the same trade
  the `@`-import already makes (ADR 006).
- The kit owns skill regeneration: version bumps re-run generation here (a
  `just openspec-refresh` recipe) instead of `openspec update` per repo;
  adopting repos pick changes up through their symlinks. Regeneration must
  re-apply the `disable-model-invocation` patch.
- `specs.md`'s manual build-plan mechanics are superseded by the OpenSpec
  workflow; its durable content guidance (explicit contracts, walking
  skeleton, definitions-of-done) survives, reframed around OpenSpec's
  artifacts.
