---
name: update-deps
description: >-
  Review and/or update Python dependencies in a uv project, checking
  changelogs thoroughly for breaking changes, deprecations, and new features
  worth adopting.
argument-hint: "[update|review]"
---

# Update Dependencies

Dependency management for a uv project. The skill runs in one of two modes:

1. **Update** - find outdated packages, review changelogs, and bump them.
2. **Review** - given already-bumped packages in the current diff, check
   changelogs and flag anything to adopt or address, without bumping further.

Pick the mode rather than asking for it. `$ARGUMENTS` naming a mode settles
it. Otherwise, if the branch's diff against the default branch changes a
version in `pyproject.toml` or `uv.lock`, run Review; if not, run Update.
State the mode chosen as the first line of the reply, so a wrong pick is
corrected before any work rests on it.

This skill assumes two things of the repo:

- a `just check` recipe that runs its full lint, type-check, and test suite.
  Running it after a bump is part of invoking this skill - that invocation is
  the request to run the linters. If the recipe is missing, say so and stop
  rather than guessing at a substitute.
- optionally, a `docs/version-pins.md` listing the pins outside
  `uv tree --outdated` (see Mode 1, step 4).

---

## Changelog review procedure

For each direct dependency, apply this procedure:

- Fetch and read the **full changelog** between the old and new version. Be
  thorough - do not stop at breaking changes. Cover all of:
  - Breaking changes and removed features
  - Deprecations (plan for future work)
  - New features worth adopting in this codebase
  - New config options or flags worth enabling
- Search the codebase ONLY when the changelog names a specific symbol,
  flag, or config key that may need adoption verification (e.g. "ParamType
  is now generic" -> grep for ParamType subclasses). Do not run open-ended
  "is this used" searches - if the changelog item is a passive bug fix,
  no search is needed.
- Report findings clearly, organised by the four categories above.
- Include a direct link to the changelog so the user can verify independently.
- Prefer `gh release view <tag> -R owner/repo` for tagged GitHub releases -
  it works on private repos and avoids guessing between CHANGELOG.md /
  CHANGES.rst / HISTORY.rst paths. Fall back to WebFetch on the project's
  documented changelog URL only if `gh` returns nothing useful.

For indirect dependencies: a cursory scan is sufficient - focus on whether the
change is safe rather than what to adopt.

### Adoption summary

After the per-package reviews and before bumping, present a separate
consolidated list:

| Change | Applies? | Recommendation |
| ------ | -------- | -------------- |

Include every "new feature" or "new config option" surfaced above, with an
explicit "n/a - we don't use X" or "yes - proposed change is Y" verdict.
Empty rows are not allowed; if there are no adoption opportunities, say so
explicitly. This forces the adoption review to be visible rather than buried.

---

## Mode 1: Update

1. Run `uv tree --outdated` to see what's outdated and why each package is
   installed. Work from deepest (indirect) to shallowest (direct) dependencies.

2. For each package, apply the changelog review procedure above, then wait for
   the user to confirm before bumping.

3. When bumping:
   - Always use `uv` commands; never hand-edit version constraints in
     `pyproject.toml` or change `uv.lock` directly.
     - To change a constraint (e.g. raise a floor to the new minor):
       `uv add` for main deps, `uv add --dev` for dev deps.
     - To pick up a version that already satisfies the existing constraint
       (a lock-only refresh): `uv lock --upgrade-package <name>`, or
       `uv lock --upgrade` to refresh every dependency at once.
   - Follow the pinning convention in `.fieldkit/conventions/python/setup.md`.
   - For patch and minor bumps, batch them and run `just check` once at
     the end. For major version bumps, do one at a time so failures
     attribute cleanly. The user can override this default.

4. Check the version pins `uv tree --outdated` cannot see - the list in
   `.fieldkit/conventions/python/setup.md` under "Version pins the dependency
   tooling does not manage". None is a project dependency, so each goes stale
   silently. Find them two ways, and reconcile the results:
   - **Sweep the tree** for pin sites: `[build-system] requires` in
     `pyproject.toml`, `.python-version`, `FROM` and `COPY --from=` lines in
     any `Dockerfile`, `uses:` and `version:` in `.github/`, `image:` on
     service containers, and `rev:` in `.pre-commit-config.yaml`.
   - **Read `docs/version-pins.md`** if the repo has one. It records what a
     sweep cannot infer: which sites must name the same version, why, and how
     to confirm a raise worked.

   A sweep hit the file doesn't list, or a file entry the sweep no longer
   finds, means the file is stale - propose the correction alongside the
   bumps. With no file, report the sweep's pins and say none are recorded.

5. If new config options or rules are worth enabling, propose the change and
   wait for approval before editing config files. Adopting a newly-available
   option is part of the dependency update, not separate work: make the change
   - and any small cleanup it surfaces, such as fixing newly-flagged lint
   violations - on the dependency-update branch itself rather than deferring
   it to a follow-up issue. If the option is performance-related (e.g. a
   parallelism flag), benchmark it empirically across a range of values rather
   than assuming more is better.

---

## Mode 2: Review

1. Diff the branch against the default branch to identify version bumps in
   `pyproject.toml` and `uv.lock` - a lock-only refresh changes only the
   latter.

2. For each bumped package, apply the changelog review procedure above. Do not
   bump versions further.

---

## Verifying linter bumps

When bumping a linter (ruff, mypy, djlint, rumdl, etc):

- Clear the linter's cache before re-running checks. Stale caches from
  the previous version can make `just check` falsely report clean.
  For ruff: `ruff clean`. For mypy: `rm -rf .mypy_cache`.
- If preview rules are enabled (e.g. ruff `preview = true`), enumerate
  every new rule from the changelog and run the linter on the codebase
  to verify each one. Do not assume "didn't fire" without confirming
  on a freshly invalidated cache.
- Treat the post-bump linter run as the source of truth - any "ruff
  check / All checks passed" message that contradicts new rules in the
  changelog should be investigated, not trusted.

---

## Notes

- Missing new features or config options is a common failure mode - do not
  shortcut the changelog review.
- Flag major version bumps explicitly before proceeding.
- When a library adds inline types (look for "inline types", "py.typed", or
  "replaces typeshed" in the changelog), check whether the project has a
  `types-<package>` stub in dev deps and propose removing it. The typeshed
  stubs PyPI page usually states the recommended action explicitly.
- If `just check` fails after a bump, verify the failure is not pre-existing
  on the base branch before assuming the bump caused it (a quick
  `git stash && <linter> && git stash pop` confirms). A pre-existing failure
  is out of scope for the bump: say what an issue for it would contain and
  ask whether to file it or fix it on this branch, then continue.
