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

1. **Update**: find outdated packages, review changelogs, bump.
2. **Review**: packages already bumped in the current diff; check changelogs, flag anything to adopt or address, no further bumps.

Pick the mode without asking. `$ARGUMENTS` naming one settles it; else Review if the branch's diff against the default branch changes a package version in `pyproject.toml` or `uv.lock` (a `requires-python` change belongs to `update-python`, doesn't count), else Update. State the mode in the reply's first line.

Repo needs:

- `just check` recipe running full lint, type-check and tests. Invoking this skill is the request to run it. Missing: say so, stop.
- Optionally `docs/version-pins.md` (Mode 1, step 4).

---

## Changelog review procedure

For each direct dependency, apply this procedure:

- Read the **full changelog** between old and new version, not only breaking changes. Cover:
  - Breaking changes, removed features
  - Deprecations (plan future work)
  - New features worth adopting here
  - New config options or flags worth enabling
- Grep the codebase only when the changelog names a symbol, flag or config key whose adoption needs checking ("ParamType is now generic" -> grep ParamType subclasses). Passive bug fix: no search.
- Report under those four categories, linking the changelog.
- Prefer `gh release view <tag> -R owner/repo` for tagged GitHub releases: works on private repos, skips guessing CHANGELOG.md / CHANGES.rst / HISTORY.rst. WebFetch the project's changelog URL only if `gh` returns nothing useful.

Routine bumps (Mode 1, step 2): cursory scan, is the change safe, not what to adopt.

### Adoption summary

After per-package reviews, before bumping, present one consolidated list:

| Change | Applies? | Recommendation |
| --- | --- | --- |

Every new feature and config option surfaced above gets a verdict: "n/a - we don't use X" or "yes - proposed change is Y". No opportunities: say so.

---

## Mode 1: Update

1. `uv tree --outdated`: what's outdated, why each package is installed. Work deepest (indirect) to shallowest (direct).

2. Sort each bump by the version boundaries in `.fieldkit/conventions/python/setup.md` (for `0.x`, the minor is the breaking one):
   - **Routine**: indirect dependency, or a direct one's patch; lock-only refresh inside constraints already chosen. Cursory scan, bump without waiting, `just check`, commit these first, on their own.
   - **Minor**: a direct dependency's minor, or any date-based version. Full review, then wait for the user.
   - **Major**: a direct dependency's major. Full review, flagged, then wait for the user.

   Indirect dependency held back by its parent's cap: retry once direct bumps land; report any still held back.

3. When bumping:
   - Change versions only through `uv`, never by editing `pyproject.toml` constraints or `uv.lock`.
     - Change a constraint (raise a floor to the new minor): `uv add` for main deps, `uv add --dev` for dev deps.
     - Pick up a version the constraint already allows (lock-only refresh): `uv lock --upgrade-package <name>`, or `uv lock --upgrade` for all.
   - Follow the pinning convention in `.fieldkit/conventions/python/setup.md`.
   - Bump whose `requires-python` excludes the project's Python waits on `update-python`: report, leave out, carry on.
   - Batch minor bumps, one `just check` at the end. Bump majors one at a time, each with its own `just check`, so failures attribute cleanly. User can override.

4. Check pins `uv tree --outdated` can't see ("Moved by a dependency update" in `.fieldkit/conventions/python/setup.md`). Find them two ways:
   - **Sweep the tree:** `[build-system] requires`, `.python-version`, `Dockerfile` `FROM` and `COPY --from=`, `uses:` and `version:` in `.github/`, service `image:` tags, `docker run` images, and `rev:` in `.pre-commit-config.yaml`.
   - **Read `docs/version-pins.md`** if present: which pins must agree, why, how to verify a raise.

   Two disagree: file is stale, propose a fix alongside the bumps. No file: report the sweep's pins.

   Check an image tag naming an OS release (`mongo:7.0-noble`) for a newer one; re-resolve the digest of any image whose tag you raise (`docker buildx imagetools inspect`). Python's own pins belong to `update-python`: report a newer Python, recommend running it after this update lands.

5. New config options or rules worth enabling: propose, wait for approval before editing config. Adoption is part of the update: make the change, and any small cleanup it surfaces (newly flagged lint violations), on the update branch, not a follow-up issue. Benchmark a performance option (parallelism flag) across a range of values; more is not always better.

---

## Mode 2: Review

1. Diff the branch against the default branch for version bumps in `pyproject.toml` and `uv.lock` (lock-only refresh touches only the latter).

2. Apply the changelog review procedure above to each bumped package. No further bumps.

---

## Verifying linter bumps

When bumping a linter (ruff, mypy, djlint, rumdl, etc):

- Clear the linter's cache before re-running checks, or the old version's cache can make `just check` falsely report clean: `ruff clean`, `rm -rf .mypy_cache`.
- Preview rules enabled (ruff `preview = true`): list every new rule from the changelog, run the linter to verify each, on a freshly cleared cache.
- The post-bump run is the source of truth: investigate an "All checks passed" that contradicts new rules in the changelog.

---

## Notes

- Some bumps need a step outside uv and a suite `just check` skips: new `playwright` needs `playwright install`, then the browser suite.
- Library adds inline types ("inline types", "py.typed" or "replaces typeshed" in the changelog): check for a `types-<package>` stub in dev deps, propose removing it; the typeshed stubs PyPI page usually states the action.
- `just check` fails after a bump: check the base branch for the same failure before blaming the bump (`git stash && <linter> && git stash pop`). Pre-existing: say what an issue for it would contain, ask whether to file or fix here, continue.
