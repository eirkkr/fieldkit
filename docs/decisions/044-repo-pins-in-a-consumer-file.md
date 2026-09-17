# 044 - A shared skill finds repo-specific pins by sweep and by file

## Decision

`update-deps` ([ADR 043](043-python-skills-opt-in-per-repo.md)) finds the
pins outside `uv tree --outdated` two ways and reconciles them:

- **A sweep** of generic pin sites: `[build-system] requires`,
  `.python-version`, `Dockerfile` `FROM` and `COPY --from=`, `uses:` and
  `version:` under `.github/`, service `image:` tags, `docker run` images,
  and `.pre-commit-config.yaml` revs.
- **An optional `docs/version-pins.md`** in the consumer, recording what a
  sweep can't infer: which pins must agree, why, and how to verify a raise.

A mismatch between the two is reported as the file going stale.

The skill also requires a `just check` recipe by name; `enable-python.sh`
warns when it is missing.

## Reason

In its consumer, the skill hard-coded that repo's pins: its `Dockerfile`, two
CI files, a MongoDB container, and why its three uv pins must agree (an older
uv silently fetches `uv-build` from PyPI, outside `uv.lock`). That doesn't
belong in a shared skill, but it was hard-won, and `conventions/python/setup.md`
states it too generically to act on.

Each source alone fails. A sweep finds sites but not their coupling. A file
goes stale, as the pins themselves do. Together, each checks the other.

A dedicated file rather than a section of a development guide, so the skill
has a fixed path that a renamed heading can't break.

`just check` by name because every Python consumer has one; "the repo's check
command" would mean rediscovering or guessing it each run.

Alternatives rejected:

- **Sweep only.** Loses the coupling.
- **File only.** Stale by construction.
- **A section in `CLAUDE.md`.** Loads every session to serve one skill.
- **Kit-side overlays, as for OpenSpec.** The pins are the consumer's to
  maintain.

## Consequences

- The source consumer moves its pin table and uv note into
  `docs/version-pins.md`, and `DEVELOPMENT.md` links there.
- A consumer without the file still gets the sweep.
- A new kind of pin site goes into the skill's sweep and
  `conventions/python/setup.md`'s list together.
- A consumer without `check` gets a stop, not a substitute.
