# 055 - The Python interpreter has its own skill

## Decision

Every move of a project's Python interpreter, patch (3.14.7 to 3.14.8) or minor (3.14 to 3.15), goes through `update-python`, a second skill in `python-skills/` ([ADR 043](043-python-skills-opt-in-per-repo.md)). `update-deps` keeps packages and tools. Its pin sweep ([ADR 044](044-repo-pins-in-a-consumer-file.md)) still reads `.python-version` and Python base images, but it reports a newer Python and leaves the move to `update-python`.

The skill gates on readiness before it changes anything else. It runs `uv lock` and `uv sync --no-build` against the target, so a dependency with a capped `requires-python` or no wheel for the target stops the move before any other pin is raised. Then it reads the release notes, raises every pin, and checks with a `git grep` for the old version in all its spellings. Dependencies go first: the skill checks for outdated packages and an outdated uv, and on a minor move recommends `update-deps` before it goes on. `update-deps`, in turn, recommends `update-python` after it, and reports a bump that needs a newer Python as waiting on it.

A minor move adds the steps a patch move has no use for: What's New, tool readiness, the pins that name only the minor, and ruff's `UP` fixes.

## Reason

`update-deps` was the only route, and a minor move came out of it half done. Its sweep finds the pins that hold a full version, but not the ones that name only the minor: `requires-python`, classifiers, ruff `target-version`, mypy `python_version`. In one Python consumer, three of those sat outside both the sweep and the consumer's own `docs/version-pins.md`.

The split is by what moves, not by how far. A first draft gave `update-python` minor moves only and left patches with `update-deps`, which meant choosing a skill by the size of a bump the user had not looked at yet. With the interpreter in one place, packages go to one skill and the interpreter to the other, and a patch move just skips the minor-only steps.

The interpreter is also shaped differently from a package. `update-deps` goes through changelogs package by package, bumping what it can. An interpreter move has one set of release notes, touches pins across the repo, and in a new minor's first weeks is often blocked by a compiled dependency with no wheel yet. That blocker has to stop the run before anything changes.

Dependencies go first because a new Python's support arrives in packages' newer releases. Run against a stale lock, the readiness gate reports blockers that a dependency update would clear, and ruff, mypy and uv only know a new version name from a release that postdates it. Once dependencies are green, a failure after the move belongs to Python. The exception is a package release that drops the current Python, which uv refuses to resolve, so `update-deps` holds that one bump back for after the move. On a patch move the order barely matters, so the skill notes what is outdated and carries on.

Alternatives rejected:

- **A mode of `update-deps`.** Every dependency run would carry the readiness gate and the minor-only pin list, and the mode choice, which today reads the diff, would need a new rule. The two share only the adoption summary, which `update-python` points to instead of copying.
- **Minor moves only, patches in `update-deps`.** The first draft, rejected above: one interpreter split across two skills by bump size.
- **Prose in `conventions/python/setup.md`.** It already states the `requires-python` form, but a list of pins has no gate and no completion check, and a minor move is rare enough that nobody remembers the steps.
- **User-invoked.** "Move to 3.15" should reach the skill without the user knowing it exists, and per-repo opt-in already limits its description's context cost to Python repos.

## Consequences

- `enable-python.sh` links the new skill with no change. A consumer that has already opted in reruns it.
- `conventions/python/setup.md` lists the minor-only pins next to the ones `update-deps` sweeps, so the lists change together, as ADR 044 requires for a new kind of pin site.
- A patch move pays for a readiness gate that rarely finds anything. It takes seconds, and catches a base image not yet published at the new patch.
- `update-python` uses `uv sync --no-build` as its wheel probe. If uv drops or renames that flag, the gate stops working silently, so a uv bump that touches it needs the skill checked too.
