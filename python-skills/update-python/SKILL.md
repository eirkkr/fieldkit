---
name: update-python
description: >-
  Move a uv project to a new Python minor version (3.14 to 3.15): check every
  dependency is ready, review What's New, and raise every version pin together.
argument-hint: "[X.Y or X.Y.Z]"
---

# Update Python

Moves a project from one Python minor to the next. A patch bump within the same minor (3.14.7 to 3.14.8) is `update-deps` territory, not this skill's.

The repo needs a `just check` recipe running the full lint, type-check, and test suite. Invoking this skill is the request to run it. If it's missing, say so and stop.

## 1. Pick the target

`$ARGUMENTS` names the target minor or exact patch. Otherwise the target is the newest stable minor above the current one. The target patch is the newest stable release of that minor.

- Find releases with `uv python list --all-versions`. uv only knows the releases that existed when its own version shipped, so a release newer than uv returns nothing, or only release candidates. Before you conclude a release is missing, check python.org.
- The target is a final release. Ask before you target a pre-release.
- Every base image the repo builds from must exist at the target patch, e.g. `docker manifest inspect python:3.15.0-slim-trixie` for each `FROM`. A missing image is a blocker (step 2).

Done when the reply's first line states the current version and the target patch, e.g. "3.14.7 → 3.15.0".

## 2. Readiness gate

Prove the dependencies work on the target before you change anything else. On the working tree:

1. `uv python pin <target patch>`, then set `requires-python` to the form in `.fieldkit/conventions/python/setup.md`. uv has no command for `requires-python`, so it is the one hand edit to `pyproject.toml` this skill makes.
2. Run `uv lock`. A dependency that caps `requires-python` below the target fails resolution here.
3. Run `uv sync --all-groups --no-build`. A dependency with no wheel for the target fails here, even one that would build from source. For each failure, check whether the sdist is pure Python, which is safe to build. Compiled code with no wheel is a blocker.
4. Every tool `just check` runs must support the target. That includes the version name in the tool's own config, e.g. ruff `target-version = "py315"` and mypy `python_version`. A tool that rejects the target's version name, or whose newest release predates the target, is a blocker. `update-deps` may have a newer release that clears it.

Done when steps 2 and 3 succeed and every tool is confirmed ready. Otherwise, a blocker list names each package or image, what is missing, and the upstream issue tracking it.

When there are blockers, restore the working tree to how you found it, report the list, and stop. Say what an issue to retry would contain (the blockers and how to recheck them), and ask whether to file it.

## 3. Review What's New

Read the target's full What's New, `https://docs.python.org/X.Y/whatsnew/X.Y.html`. Read all of it, not just the removals, and also read the changelog for the target patch. Report under four categories, linking each item:

- Removed features and changed behaviour
- Deprecations (plan for future work)
- New language and standard library features worth adopting in this codebase
- New interpreter options, defaults, or warnings worth enabling

Search the codebase only when an item names a specific module, function, or flag. A removed `asyncio` function gets a grep. A passive improvement gets none.

Present the adoption summary exactly as `update-deps` does (`../update-deps/SKILL.md`, "Adoption summary"). Every adoption item gets a verdict, and you wait for approval before making any of them.

Done when every category has been reported, with any empty category stated as empty, and the summary has a verdict on every row.

## 4. Raise every pin

The old minor appears in more places than `update-deps` sweeps, because some pins name only the minor. Raise them all in one change:

- `.python-version` and `requires-python` (already raised in step 2)
- `Programming Language :: Python :: X.Y` classifiers
- tool targets: ruff `target-version`, mypy `python_version`, pyright `pythonVersion`, and the like
- base images: `FROM` in every Dockerfile, service `image:` tags
- CI: `python-version:` inputs, matrix entries, cache keys that embed the version
- `.pre-commit-config.yaml` `default_language_version`, tox or nox environment lists
- prose that states the version: README setup steps, contributor docs

Then sweep for anything left. `git grep` the old minor in every spelling it takes (`3.14`, `py314`, `cp314`, `python3.14`). Every remaining hit is either raised or justified as history, such as a changelog, an archived design, or a measurement that names the version it ran on.

If `docs/version-pins.md` exists, add any pin site it is missing, and record which pins must agree.

Done when the grep's leftover hits are all justified.

## 5. Verify

1. `uv lock` and `uv sync --all-groups`, so the lock records the new `requires-python`.
2. Clear tool caches built under the old interpreter: `ruff clean`, `rm -rf .mypy_cache`, and the like.
3. With ruff's `UP` rules enabled, run `uv run ruff check --select UP --fix` so the new target's syntax upgrades land in this change. Report what it rewrote.
4. Run `just check`. Read the test output for new `DeprecationWarning`s and add them to step 3's deprecations.
5. Rebuild every Dockerfile stage, and confirm the built image's `python --version` prints the target patch.

If `just check` fails, check whether the failure already exists on the default branch before you blame the move. If it does, say what an issue for it would contain and ask whether to file it or fix it here.

Done when `just check` is green and every image is built on the target.

## 6. Report

- the version move, as in step 1
- every pin changed, by file
- the What's New findings and the adoption summary, with what was adopted
- deprecations to plan for, and the warnings the test run surfaced
- any `docs/version-pins.md` changes
