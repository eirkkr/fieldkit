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

Pick the mode without asking: `$ARGUMENTS` naming one settles it; otherwise Review if the branch's diff against the default branch changes a package version in `pyproject.toml` or `uv.lock` (a `requires-python` change belongs to `update-python` and doesn't count), else Update. State the mode in the reply's first line.

The repo needs:

- a `just check` recipe running the full lint, type-check and test suite. Invoking this skill is the request to run it. If it's missing, say so and stop.
- optionally, `docs/version-pins.md` (see Mode 1, step 4).

---

## Changelog review procedure

For each direct dependency, apply this procedure:

- Read the **full changelog** between the old and new version, not only breaking changes. Cover:
  - Breaking changes and removed features
  - Deprecations (plan for future work)
  - New features worth adopting in this codebase
  - New config options or flags worth enabling
- Grep the codebase only when the changelog names a symbol, flag or config key whose adoption needs checking ("ParamType is now generic" -> grep for ParamType subclasses). A passive bug fix needs no search.
- Report under those four categories, linking the changelog so the user can verify.
- Prefer `gh release view <tag> -R owner/repo` for tagged GitHub releases: it works on private repos and skips guessing between CHANGELOG.md / CHANGES.rst / HISTORY.rst. Fall back to WebFetch on the project's changelog URL only if `gh` returns nothing useful.

For routine bumps (Mode 1, step 2) a cursory scan is enough: is the change safe, not what to adopt.

### Adoption summary

After the per-package reviews and before bumping, present a separate consolidated list:

| Change | Applies? | Recommendation |
| --- | --- | --- |

List every new feature and config option surfaced above, each with a verdict: "n/a - we don't use X" or "yes - proposed change is Y". With no adoption opportunities, say so. This keeps the adoption review visible.

---

## Mode 1: Update

1. Run `uv tree --outdated` to see what's outdated and why each package is installed. Work from deepest (indirect) to shallowest (direct) dependencies.

2. Sort each bump by the version boundaries in `.fieldkit/conventions/python/setup.md` (for `0.x`, the minor is the breaking one):
   - **Routine** - an indirect dependency, or a direct one's patch: a lock-only refresh inside constraints already chosen. Cursory scan, bump without waiting, `just check`, and commit these first, on their own.
   - **Minor** - a direct dependency's minor, or any date-based version. Full review, then wait for the user.
   - **Major** - a direct dependency's major. Full review, flagged, then wait for the user.

   An indirect dependency held back by its parent's cap is retried once the direct bumps land; report any still held back.

3. When bumping:
   - Change versions only through `uv`, never by editing `pyproject.toml` constraints or `uv.lock`.
     - To change a constraint (raise a floor to the new minor): `uv add` for main deps, `uv add --dev` for dev deps.
     - To pick up a version the existing constraint already allows (a lock-only refresh): `uv lock --upgrade-package <name>`, or `uv lock --upgrade` for every dependency.
   - Follow the pinning convention in `.fieldkit/conventions/python/setup.md`.
   - A bump whose `requires-python` excludes the project's Python waits on `update-python`: report it, leave it out, carry on.
   - Batch the minor bumps and run `just check` once at the end. Bump majors one at a time, each with its own `just check`, so failures attribute cleanly. The user can override this default.

4. Check the pins `uv tree --outdated` can't see (see "Moved by a dependency update" in `.fieldkit/conventions/python/setup.md`). Find them two ways:
   - **Sweep the tree:** `[build-system] requires`, `.python-version`, `Dockerfile` `FROM` and `COPY --from=`, `uses:` and `version:` in `.github/`, service `image:` tags, `docker run` images, and `rev:` in `.pre-commit-config.yaml`.
   - **Read `docs/version-pins.md`** if present: which pins must agree, why, and how to verify a raise.

   If the two disagree, the file is stale - propose a fix alongside the bumps. With no file, report the sweep's pins.

   Check an image tag naming an OS release (`mongo:7.0-noble`) for a newer one, and re-resolve the digest of any image whose tag you raise (`docker buildx imagetools inspect`). Leave Python's own pins to `update-python`: report a newer Python, and recommend running it after this update lands.

5. If new config options or rules are worth enabling, propose the change and wait for approval before editing config. Adopting an option is part of the update: make the change, and any small cleanup it surfaces (newly-flagged lint violations), on the update branch rather than a follow-up issue. Benchmark a performance option (a parallelism flag) across a range of values; more is not always better.

---

## Mode 2: Review

1. Diff the branch against the default branch for version bumps in `pyproject.toml` and `uv.lock` (a lock-only refresh touches only the latter).

2. For each bumped package, apply the changelog review procedure above. Do not bump versions further.

---

## Verifying linter bumps

When bumping a linter (ruff, mypy, djlint, rumdl, etc):

- Clear the linter's cache before re-running checks, or the previous version's cache can make `just check` falsely report clean: `ruff clean`, `rm -rf .mypy_cache`.
- If preview rules are enabled (ruff `preview = true`), list every new rule from the changelog and run the linter to verify each, on a freshly cleared cache.
- The post-bump run is the source of truth: investigate an "All checks passed" that contradicts new rules in the changelog.

---

## Notes

- Some bumps need a step outside uv and a suite `just check` skips: a new `playwright` needs `playwright install`, then the browser suite.
- When a library adds inline types ("inline types", "py.typed" or "replaces typeshed" in the changelog), check for a `types-<package>` stub in dev deps and propose removing it; the typeshed stubs PyPI page usually states the action.
- If `just check` fails after a bump, check the base branch for the same failure before blaming the bump (`git stash && <linter> && git stash pop`). If it is pre-existing, say what an issue for it would contain, ask whether to file it or fix it here, then continue.
