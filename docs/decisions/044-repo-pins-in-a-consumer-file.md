# 044 - A shared skill finds repo-specific pins by sweep and by file

## Decision

The kit's `update-deps` skill (see [ADR 043](043-python-skills-opt-in-per-repo.md))
finds the version pins outside `uv tree --outdated` in two ways and
reconciles them:

- **A sweep** of the tree for the pin sites the kit can name generically -
  `[build-system] requires`, `.python-version`, `FROM` and `COPY --from=` in
  a `Dockerfile`, `uses:`/`version:` under `.github/`, service `image:` tags
  and `docker run` images, `.pre-commit-config.yaml` revs.
- **An optional consumer file, `docs/version-pins.md`**, recording what a
  sweep cannot infer: which sites must name the same version, why, and how to
  confirm a raise worked.

A sweep hit the file omits, or a file entry the sweep no longer finds, is
reported as the file going stale, with a correction proposed alongside the
bumps.

The skill also requires a `just check` recipe by name rather than leaving the
check command to the consumer, and `enable-python.sh` warns when one is
missing.

## Reason

The skill as it existed in its consumer hard-coded that repo's pins: a table
naming its `Dockerfile`, two CI files, and a MongoDB service container, plus a
paragraph on why its three uv pins had to agree - an older uv silently
resolves `uv-build` from PyPI, a floating fetch `uv.lock` and `--frozen` don't
cover. None of that belongs in a shared skill, but all of it was earned, and
the generic statement of it in `conventions/python/setup.md` is not enough to
act on in a specific repo.

Either source alone fails in a known way. A sweep alone finds sites but not
their coupling - it sees three uv versions without knowing they must match or
what breaks if they don't. A file alone goes stale silently, the exact
failure mode the pins have, one level up: a pin added in a new workflow is
invisible until someone thinks to record it. Using both lets each check the
other.

A separate file rather than a section of a consumer's development guide,
because the skill needs one path it can find without parsing prose headings,
and a heading renamed for a human reader would silently disconnect it.
`docs/` because that is where consumers keep human-readable reference; the
file is written for people as well as the skill.

`just check` by name because every Python consumer already has one, and a
skill told to run "the repo's check command" has to discover it each time -
or guess, which is worse than stopping.

Alternatives rejected:

- **Sweep only.** Loses the coupling rules above.
- **File only.** Stale by construction.
- **A section in the consumer's `CLAUDE.md`.** Loads every session to serve
  one skill.
- **Per-consumer overlays on the skill**, as `repo-skills-overlay/` does for
  OpenSpec. Overlays are kit-side; the pins are the consumer's to maintain.

## Consequences

- The consumer the skill came from moves its pin table and uv-coupling
  paragraph into `docs/version-pins.md`, and its `DEVELOPMENT.md` points
  there instead of repeating the list.
- A consumer with no pins file still gets the sweep; the file is additive.
- The sweep's site list lives in the skill; when a new kind of pin site turns
  up in any consumer, it is added there, and `conventions/python/setup.md`'s
  list is kept in step.
- A consumer without a `check` recipe gets a stop from the skill rather than
  a substitute - adding the recipe is the fix.
