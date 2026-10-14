# 055 - The Python interpreter has its own skill

## Decision

Every move of a project's Python interpreter, patch or minor, goes through `update-python`, a second skill in `python-skills/` ([ADR 043](043-python-skills-opt-in-per-repo.md)). `update-deps` keeps packages and tools; its pin sweep ([ADR 044](044-repo-pins-in-a-consumer-file.md)) still reads the Python pins, but only reports a newer Python.

The skill moves dependencies first, then gates on readiness - `uv lock` and `uv sync --no-build` against the target - before raising any pin.

## Reason

A minor move through `update-deps` came out half done: its sweep missed the pins that name only the minor (`requires-python`, classifiers, ruff `target-version`, mypy `python_version`). In one Python consumer, three of them were in neither the sweep nor `docs/version-pins.md`.

The split is by what moves, not how far. A first draft left patches with `update-deps`, which meant picking a skill by the size of a bump nobody had looked at yet.

An interpreter move is also shaped differently: one set of release notes, pins across the repo, and in a new minor's first weeks, often a compiled dependency with no wheel. That blocker must stop the run before anything changes, where `update-deps` bumps what it can.

Dependencies go first because a new Python's support arrives in packages' newer releases - including ruff's, mypy's and uv's, which only know a version name released before them. Against a stale lock, the gate reports blockers an update would clear.

Alternatives rejected:

- **A mode of `update-deps`.** Every dependency run would carry the gate and the minor-only pins, for an occasional move.
- **Prose in `conventions/python/setup.md`.** A list of pins has no gate and no completion check, and a minor move is too rare to remember the steps.
- **User-invoked.** "Move to 3.15" should reach the skill unprompted; per-repo opt-in already bounds its context cost.

## Consequences

- `conventions/python/setup.md` lists the minor-only pins beside the others, so the lists change together (ADR 044).
- Where a repo pins a Python base image by digest, Dependabot refreshes the digest and ignores the image's version updates. Neither proposes a new OS release in a tag, so `update-python` checks for one on each move.
- The gate relies on `uv sync --no-build` as its wheel probe; a uv release that changes the flag needs the skill checked.
