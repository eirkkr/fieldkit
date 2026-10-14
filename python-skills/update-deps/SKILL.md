---
name: update-deps
description: >-
  Review and/or update Python dependencies in a uv project, checking
  changelogs thoroughly for breaking changes, deprecations, and new features
  worth adopting.
argument-hint: "[update|review]"
---

# Update Dependencies

Two modes:

1. **Update** - find outdated packages, review changelogs, and bump them.
2. **Review** - given already-bumped packages in the current diff, check changelogs and flag anything to adopt or address, without bumping further.

Pick the mode; don't ask. `$ARGUMENTS` naming one settles it. Otherwise run Review if the branch's diff against the default branch changes a package version in `pyproject.toml` or `uv.lock`, else Update. A `requires-python` change belongs to `update-python` and doesn't count. State the mode in the reply's first line so a wrong pick is caught early.

The repo needs:

- a `just check` recipe running the full lint, type-check, and test suite. Invoking this skill is the request to run it. If it's missing, say so and stop.
- optionally, `docs/version-pins.md` (see Mode 1, step 4).

---

## Changelog review procedure

For each direct dependency, apply this procedure:

- Fetch and read the **full changelog** between the old and new version. Be thorough - do not stop at breaking changes. Cover all of:
  - Breaking changes and removed features
  - Deprecations (plan for future work)
  - New features worth adopting in this codebase
  - New config options or flags worth enabling
- Search the codebase ONLY when the changelog names a specific symbol, flag, or config key that may need adoption verification (e.g. "ParamType is now generic" -> grep for ParamType subclasses). Do not run open-ended "is this used" searches - if the changelog item is a passive bug fix, no search is needed.
- Report findings under those four categories, with a direct link to the changelog so the user can verify independently.
- Prefer `gh release view <tag> -R owner/repo` for tagged GitHub releases - it works on private repos and avoids guessing between CHANGELOG.md / CHANGES.rst / HISTORY.rst paths. Fall back to WebFetch on the project's documented changelog URL only if `gh` returns nothing useful.

For routine bumps (Mode 1, step 2): a cursory scan is sufficient - focus on whether the change is safe rather than what to adopt.

### Adoption summary

After the per-package reviews and before bumping, present a separate consolidated list:

| Change | Applies? | Recommendation |
| ------ | -------- | -------------- |

Include every "new feature" or "new config option" surfaced above, with an explicit "n/a - we don't use X" or "yes - proposed change is Y" verdict. Empty rows are not allowed; if there are no adoption opportunities, say so explicitly. This forces the adoption review to be visible rather than buried.

---

## Mode 1: Update

1. Run `uv tree --outdated` to see what's outdated and why each package is installed. Work from deepest (indirect) to shallowest (direct) dependencies.

2. Sort each bump by the version boundaries in `.fieldkit/conventions/python/setup.md` (for `0.x`, the minor is the breaking one):
   - **Routine** - an indirect dependency, or a direct one's patch: a lock-only refresh inside constraints already chosen. Cursory scan, bump without waiting, `just check`, and commit these first, on their own.
   - **Minor** - a direct dependency's minor, or any date-based version. Full review, then wait for the user.
   - **Major** - a direct dependency's major. Full review, flagged, then wait for the user.

   An indirect dependency held back by its parent's cap is retried once the direct bumps land; report any still held back.

3. When bumping:
   - Always use `uv` commands; never hand-edit version constraints in `pyproject.toml` or change `uv.lock` directly.
     - To change a constraint (e.g. raise a floor to the new minor): `uv add` for main deps, `uv add --dev` for dev deps.
     - To pick up a version that already satisfies the existing constraint (a lock-only refresh): `uv lock --upgrade-package <name>`, or `uv lock --upgrade` to refresh every dependency at once.
   - Follow the pinning convention in `.fieldkit/conventions/python/setup.md`.
   - A bump whose `requires-python` excludes the project's Python waits on `update-python`: report it, leave it out, carry on.
   - Batch the minor bumps and run `just check` once at the end. Bump majors one at a time, each with its own `just check`, so failures attribute cleanly. The user can override this default.

4. Check the pins `uv tree --outdated` can't see (see "Moved by a dependency update" in `.fieldkit/conventions/python/setup.md`). Find them two ways:
   - **Sweep the tree:** `[build-system] requires`, `.python-version`, `Dockerfile` `FROM` and `COPY --from=`, `uses:` and `version:` in `.github/`, service `image:` tags, `docker run` images, and `rev:` in `.pre-commit-config.yaml`.
   - **Read `docs/version-pins.md`** if present: which pins must agree, why, and how to verify a raise.

   If the two disagree, the file is stale - propose a fix alongside the bumps. With no file, report the sweep's pins.

   Check an image tag naming an OS release (`mongo:7.0-noble`) for a newer one, and re-resolve the digest of any image whose tag you raise (`docker buildx imagetools inspect`). Leave Python's own pins to `update-python`: report a newer Python, and recommend running it after this update lands.

5. If new config options or rules are worth enabling, propose the change and wait for approval before editing config files. Adopting a newly-available option is part of the dependency update, not separate work: make the change - and any small cleanup it surfaces, such as fixing newly-flagged lint violations - on the dependency-update branch itself rather than deferring it to a follow-up issue. If the option is performance-related (e.g. a parallelism flag), benchmark it empirically across a range of values rather than assuming more is better.

---

## Mode 2: Review

1. Diff the branch against the default branch for version bumps in `pyproject.toml` and `uv.lock` (a lock-only refresh touches only the latter).

2. For each bumped package, apply the changelog review procedure above. Do not bump versions further.

---

## Verifying linter bumps

When bumping a linter (ruff, mypy, djlint, rumdl, etc):

- Clear the linter's cache before re-running checks. Stale caches from the previous version can make `just check` falsely report clean. For ruff: `ruff clean`. For mypy: `rm -rf .mypy_cache`.
- If preview rules are enabled (e.g. ruff `preview = true`), enumerate every new rule from the changelog and run the linter on the codebase to verify each one. Do not assume "didn't fire" without confirming on a freshly invalidated cache.
- Treat the post-bump linter run as the source of truth - any "ruff check / All checks passed" message that contradicts new rules in the changelog should be investigated, not trusted.

---

## Notes

- Some bumps need a step outside uv and a suite `just check` skips: a new `playwright` needs `playwright install`, then the browser suite.
- When a library adds inline types (look for "inline types", "py.typed", or "replaces typeshed" in the changelog), check whether the project has a `types-<package>` stub in dev deps and propose removing it. The typeshed stubs PyPI page usually states the recommended action explicitly.
- If `just check` fails after a bump, verify the failure is not pre-existing on the base branch before assuming the bump caused it (a quick `git stash && <linter> && git stash pop` confirms). If it is, say what an issue for it would contain and ask whether to file it or fix it here, then continue.
