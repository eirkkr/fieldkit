# 055 - A Python minor move is its own skill

## Decision

Moving a project to a new Python minor (3.14 to 3.15) goes through `update-python`, a second skill in `python-skills/` ([ADR 043](043-python-skills-opt-in-per-repo.md)). A patch bump inside the minor stays with `update-deps`, whose pin sweep ([ADR 044](044-repo-pins-in-a-consumer-file.md)) already covers `.python-version` and base image tags.

The skill gates on readiness before it changes anything else. It runs `uv lock` and `uv sync --no-build` against the target, so a dependency with a capped `requires-python` or no wheel for the target stops the move before any pin is raised. Then it reads the target's What's New, raises every pin, and checks with a `git grep` for the old minor in all its spellings.

## Reason

`update-deps` was the only route, and a minor move came out of it half done. Its sweep finds the pins that hold a full version, but not the ones that name only the minor: `requires-python`, classifiers, ruff `target-version`, mypy `python_version`. In one Python consumer, three of those sat outside both the sweep and the consumer's own `docs/version-pins.md`.

The work is also shaped differently. `update-deps` goes through changelogs package by package and comes up every few weeks. A minor move comes up once a year, has one source to read (What's New), and in its first weeks is often blocked by a compiled dependency with no wheel yet. That blocker has to stop the run before anything changes, where `update-deps` bumps what it can.

Alternatives rejected:

- **A third mode of `update-deps`.** Every dependency run would carry the readiness gate and the minor-only pin list, and the mode choice, which today reads the diff, would need a new rule. The two share only the adoption summary, which `update-python` points to instead of copying.
- **Prose in `conventions/python/setup.md`.** It already states the `requires-python` form, but a list of pins has no gate and no completion check, and the move it describes is rare enough that nobody remembers the steps.
- **User-invoked.** "Move to 3.15" should reach the skill without the user knowing it exists, and per-repo opt-in already limits its description's context cost to Python repos.

## Consequences

- `enable-python.sh` links the new skill with no change. A consumer that has already opted in reruns it.
- `conventions/python/setup.md` lists the minor-only pins next to the ones `update-deps` sweeps, so the lists change together, as ADR 044 requires for a new kind of pin site.
- `update-deps` hands a minor move to `update-python` when its sweep finds a newer Python minor.
- `update-python` uses `uv sync --no-build` as its wheel probe. If uv drops or renames that flag, the gate stops working silently, so a uv bump that touches it needs the skill checked too.
