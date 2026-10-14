---
name: update-python
description: >-
  Move a uv project to a new Python version, patch (3.14.7 to 3.14.8) or minor
  (3.14 to 3.15): check dependencies are ready, review the release notes, and
  raise every version pin together.
argument-hint: "[X.Y or X.Y.Z]"
---

# Update Python

Moves the project's Python interpreter; packages and tools belong to `update-deps`. A **patch** move stays in the current minor, a **minor** move leaves it, and steps marked *minor only* are skipped on a patch move.

Invoking this skill is the request to run `just check`. If the repo has no such recipe, say so and stop.

## 1. Pick the target

`$ARGUMENTS` names a minor (its newest patch) or an exact patch; with none, the newest stable release. Ask before targeting a pre-release.

- `uv python list --all-versions` lists only releases older than the installed uv. Check python.org before concluding one is missing.
- A base image whose tag names the Python version (`python:3.15.0-slim-trixie`) must exist at the target (`docker manifest inspect`), or it is a blocker (step 3). An image using `uv python install` needs no check.
- Check every base image's OS release (`trixie` is Debian 13) for a newer one. If one is out, recommend moving to it with this move, and ask first: a new OS release can drop packages the image relies on.

Done when the reply's first line states the move, e.g. "3.14.7 → 3.15.0 (minor)".

## 2. Dependencies first

Run `uv tree --outdated --depth 1 --all-groups`, and compare `uv --version` with `gh release view -R astral-sh/uv --json tagName`. On a minor move with anything outdated, recommend `update-deps` first and wait for the user's answer. On a patch move, report it and carry on. `.fieldkit/conventions/python/setup.md`, "Moved by an interpreter update", says why.

## 3. Readiness gate

Prove the dependencies work on the target before changing anything else:

1. *Minor only:* set `requires-python` to the form in `setup.md` - by hand, since uv has no command for it, and first, since `uv python pin` refuses a version outside it.
2. `uv python pin <target patch>`, then `uv lock`. A dependency capping `requires-python` below the target fails here.
3. `uv sync --all-groups --no-build`. A dependency with no wheel for the target fails here. A pure-Python sdist is safe to build. Compiled code is a blocker, even with a pure-Python fallback, which an image without a compiler installs silently.
4. *Minor only:* every tool `just check` runs must accept the target's version name in its config (ruff `py315`, mypy `python_version`). One that doesn't is a blocker, unless `update-deps` has a release that does.

Done when the lock and sync succeed and the tools are ready. Otherwise, restore the working tree, `uv sync --all-groups` back onto the current Python, and stop with a blocker list: each package, tool or image, what it lacks, and its upstream tracking issue. Say what a retry issue would contain and ask whether to file it. If the current minor has a newer patch, offer that move instead.

## 4. Review the release notes

Read in full the target's What's New on a minor move (`https://docs.python.org/X.Y/whatsnew/X.Y.html`), and on either move the changelog for every patch since the current one (`https://docs.python.org/X.Y/whatsnew/changelog.html`). From a patch changelog, keep security fixes and fixes to modules the codebase uses. Report, with links, under:

- removed features and changed behaviour
- deprecations
- features worth adopting
- options, defaults or warnings worth enabling

Grep the codebase only for a named module, function or flag. Present the adoption summary as `update-deps` does (`../update-deps/SKILL.md`), with a verdict on every row, and wait for approval before adopting anything.

Done when every category is reported, empty ones stated as empty.

## 5. Raise every pin

The two groups in `setup.md`'s "Moved by an interpreter update":

- **Full version**, every move: `.python-version`; `FROM` and service `image:` tags naming Python, with any digest re-resolved (`docker buildx imagetools inspect`); CI `python-version:` inputs, matrices and cache keys.
- **Minor only**: `requires-python`, the `Programming Language :: Python :: X.Y` classifier, tool targets (ruff, mypy, pyright), `.pre-commit-config.yaml` `default_language_version`, tox or nox lists, and prose stating the version.

Then `git grep` every spelling of the old version: the patch (`3.14.7`), and on a minor move the minor (`3.14`, `py314`, `cp314`, `python3.14`). Add any site `docs/version-pins.md` is missing, if the repo has one.

Done when every leftover hit is history: a changelog, an archived design, a measurement naming its version.

## 6. Verify

1. `uv lock` and `uv sync --all-groups`.
2. Clear caches built under the old interpreter (`ruff clean`, `rm -rf .mypy_cache`).
3. *Minor only:* if the project enables ruff's `UP` rules, `uv run ruff check --select UP --fix`, and report what it rewrote.
4. `just check`, adding any new `DeprecationWarning` to step 4's deprecations. A failure the default branch also has isn't the move's: say what an issue for it would contain, and ask whether to file it or fix it here.
5. Rebuild every Dockerfile stage and check `python --version` in the image.

Done when `just check` is green and every image runs the target.

## 7. Report

The move; whether dependencies went first; every pin changed, by file; the release-note findings and what was adopted; deprecations and new warnings; `docs/version-pins.md` changes.
