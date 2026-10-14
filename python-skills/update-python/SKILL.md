---
name: update-python
description: >-
  Move a uv project to a new Python version, patch (3.14.7 to 3.14.8) or minor
  (3.14 to 3.15): check every dependency is ready, review the release notes,
  and raise every version pin together.
argument-hint: "[X.Y or X.Y.Z]"
---

# Update Python

Moves the project's Python interpreter to a newer release. Package and tool versions are `update-deps` territory, not this skill's.

The move is a **patch** move when the target shares the current minor, and a **minor** move otherwise. A step marked *minor only* is skipped on a patch move.

The repo needs a `just check` recipe running the full lint, type-check, and test suite. Invoking this skill is the request to run it. If it's missing, say so and stop.

## 1. Pick the target

`$ARGUMENTS` names the target minor or exact patch. A minor alone means its newest patch. With no argument, the target is the newest stable release.

- Find releases with `uv python list --all-versions`. uv only knows the releases that existed when its own version shipped, so a release newer than uv returns nothing, or only release candidates. Before you conclude a release is missing, check python.org.
- The target is a final release. Ask before you target a pre-release.
- A base image whose tag names the Python version must exist at the target patch, e.g. `docker manifest inspect python:3.15.0-slim-trixie`. A missing image is a blocker (step 3). An image that gets Python from `uv python install` follows `.python-version` and needs no check.
- A base image tag also names an OS release (`slim-trixie`, `debian:trixie-slim`: Debian 13). Check the registry for a newer release of the same OS (`forky` beside `trixie`), and when one is out, recommend moving to it as part of this move. Ask before you do: a new OS release can drop or rename system packages the image relies on.

Done when the reply's first line states the move and its kind, e.g. "3.14.7 → 3.15.0 (minor)".

## 2. Dependencies first

Packages and tools move before the interpreter ("Moved by an interpreter update" in `.fieldkit/conventions/python/setup.md` says why).

- Run `uv tree --outdated --depth 1` for the direct dependencies, every group included.
- Compare `uv --version` with the newest uv release (`gh release view -R astral-sh/uv --json tagName`).

On a minor move with anything outdated, recommend running `update-deps` first and wait for the user's answer. Going ahead is their call. On a patch move, mention what is outdated and carry on.

Done when the outdated list has been reported, and on a minor move the user has chosen.

## 3. Readiness gate

Prove the dependencies work on the target before you change anything else. On the working tree:

1. On a minor move, set `requires-python` to the form in `.fieldkit/conventions/python/setup.md` first, since `uv python pin` refuses a version outside it. uv has no command for `requires-python`, so it is the one hand edit to `pyproject.toml` this skill makes. Then run `uv python pin <target patch>`.
2. Run `uv lock`. A dependency that caps `requires-python` below the target fails resolution here.
3. Run `uv sync --all-groups --no-build`. A dependency with no wheel for the target fails here, even one that would build from source. For each failure, check whether the sdist is pure Python, which is safe to build. Compiled code with no wheel is a blocker, even with a pure-Python fallback: an image with no compiler installs the fallback without a word, and the package runs without its extension.
4. *Minor only.* Every tool `just check` runs must support the target. That includes the version name in the tool's own config, e.g. ruff `target-version = "py315"` and mypy `python_version`. A tool that rejects the target's version name, or whose newest release predates the target, is a blocker. `update-deps` may have a newer release that clears it.

Done when `uv lock` and the `--no-build` sync both succeed and, on a minor move, every tool is confirmed ready. Otherwise, a blocker list names each package, tool or image, what is missing, and the upstream issue tracking it.

When there are blockers, restore the working tree to how you found it and run `uv sync --all-groups` to put the environment back on the current Python. Then report the list and stop. Say what an issue to retry would contain (the blockers and how to recheck them), and ask whether to file it. When a minor move is blocked and the current minor has a newer patch, offer that patch move instead.

## 4. Review the release notes

On a minor move, read the target's full What's New, `https://docs.python.org/X.Y/whatsnew/X.Y.html`. Read all of it, not just the removals. On both kinds of move, read the changelog for every patch between the current version and the target (`https://docs.python.org/X.Y/whatsnew/changelog.html`). Report under four categories, linking each item:

- Removed features and changed behaviour
- Deprecations (plan for future work)
- New language and standard library features worth adopting in this codebase
- New interpreter options, defaults, or warnings worth enabling

A patch changelog is mostly bug and security fixes. Report the ones that touch modules the codebase uses, and any security fix, and leave out the rest.

Search the codebase only when an item names a specific module, function, or flag. A removed `asyncio` function gets a grep. A passive improvement gets none.

Present the adoption summary exactly as `update-deps` does (`../update-deps/SKILL.md`, "Adoption summary"). Every adoption item gets a verdict, and you wait for approval before making any of them.

Done when every category has been reported, with any empty category stated as empty, and the summary has a verdict on every row.

## 5. Raise every pin

These are the groups in "Moved by an interpreter update" (`.fieldkit/conventions/python/setup.md`), listed site by site.

**Full version**, raised on both kinds of move:

- `.python-version` (already raised in step 3)
- base images whose tag names the Python version: `FROM` in every Dockerfile, service `image:` tags. Where a `FROM` is pinned by digest, re-resolve it for the new tag (`docker buildx imagetools inspect python:<tag>`).
- CI: `python-version:` inputs, matrix entries, cache keys that embed the version

**Minor only**, raised on a minor move:

- `requires-python` (already raised in step 3)
- `Programming Language :: Python :: X.Y` classifiers
- tool targets: ruff `target-version`, mypy `python_version`, pyright `pythonVersion`, and the like
- `.pre-commit-config.yaml` `default_language_version`, tox or nox environment lists
- prose that states the version: README setup steps, contributor docs

Then sweep for anything left. `git grep` the old version in every spelling it takes: the old patch (`3.14.7`) on both kinds of move, and on a minor move also the old minor (`3.14`, `py314`, `cp314`, `python3.14`). Every remaining hit is either raised or justified as history, such as a changelog, an archived design, or a measurement that names the version it ran on.

If `docs/version-pins.md` exists, add any pin site it is missing, and record which pins must agree.

Done when the grep's leftover hits are all justified.

## 6. Verify

1. `uv lock` and `uv sync --all-groups`, so the lock and environment match the final pins.
2. Clear tool caches built under the old interpreter: `ruff clean`, `rm -rf .mypy_cache`, and the like.
3. *Minor only.* With ruff's `UP` rules enabled, run `uv run ruff check --select UP --fix` so the new target's syntax upgrades land in this change. Report what it rewrote.
4. Run `just check`. Read the test output for new `DeprecationWarning`s and add them to step 4's deprecations.
5. Rebuild every Dockerfile stage, and confirm the built image's `python --version` prints the target patch.

If `just check` fails, check whether the failure already exists on the default branch before you blame the move. If it does, say what an issue for it would contain and ask whether to file it or fix it here.

Done when `just check` is green and every image is built on the target.

## 7. Report

- the move, as in step 1
- whether dependencies were brought up to date first, or why not
- every pin changed, by file
- the release-note findings and the adoption summary, with what was adopted
- deprecations to plan for, and the warnings the test run surfaced
- any `docs/version-pins.md` changes
