# Python project setup and dependencies

Conventions for scaffolding a Python project and managing its dependencies with
uv.

## Project setup

Initialise new projects with uv commands rather than hand-authoring
`pyproject.toml`:

```sh
uv init <name>          # scaffold pyproject.toml, .python-version, README
uv add <pkg>            # add a runtime dependency (resolves latest)
uv add --dev <pkg>      # add a dev dependency (resolves latest)
uv sync                 # create/update the lockfile and venv
```

Commit `pyproject.toml`, `uv.lock`, and `.python-version`. Do not edit
`pyproject.toml` or `uv.lock` by hand after initial setup - use `uv add` /
`uv remove` so the lockfile stays consistent.

`.python-version` records the exact Python patch the project uses (e.g.
`3.14.4`). Create or update it with `uv python pin <version>`. This is the
specific version developers and CI should run; `requires-python` in
`pyproject.toml` is the broader compatibility range.

**Always use the latest available versions** when setting up a project - the
latest stable Python minor and the latest release of each dependency. `uv add`
resolves the latest by default; after it runs, tighten the version range in
`pyproject.toml` to follow the pinning convention below. Check the installed
Python version with `uv run python --version` and use that patch in
`requires-python`.

## Dependencies

After `uv add` installs a package, set its version range in `pyproject.toml`
based on the installed version. Do not hand-edit `pyproject.toml` directly;
use `uv add "pkg>=X.Y,<Z"` to update a constraint.

The minimum is the minor of the installed release (drop the patch); the
maximum depends on the package:

- **Dependencies (major >= 1):** cap at the next major.
  `>=X.Y,<X+1` - e.g. installed `pytest 9.1.1` → `>=9.1,<10`
- **Dependencies (major == 0):** cap at the next minor - 0.x semver treats
  the minor as the breaking-change boundary.
  `>=0.Y,<0.Y+1` - e.g. installed `rumdl 0.2.26` → `>=0.2,<0.3`
- **`requires-python`:** pin to the latest installed minor and cap at the next
  minor. `>=X.Y,<X.Y+1` - e.g. installed Python `3.14.4` → `>=3.14,<3.15`

Common mistakes to avoid:

- `>=9.1.1,<10` - patch in the floor; use `>=9.1,<10`
- `>=9,<10` - major in the floor; use `>=9.1,<10`
- `>=0.2.26,<0.3` - patch in the floor for a 0.x package; use `>=0.2,<0.3`
- `>=0.9,<1` - capping a 0.x package at major; use `>=0.9,<0.10`
- `>=3.11` - an old Python version with no upper bound; use `>=3.14,<3.15`

## Version pins the dependency tooling does not manage

`uv tree --outdated` reports project and dev dependencies. Several pins sit
outside that view and go stale silently, so a dependency update has to look
at them by hand:

- **`[build-system] requires`** - the build backend is not a dependency of
  the project, so it never appears in the tree. `uv_build` versions with uv
  itself, and an upper bound below the installed uv makes every `uv` command
  warn. Raise it with uv's own minor, following the 0.x rule above.
- **Tool versions pinned in a Dockerfile or CI** - a `COPY --from=ghcr.io/...`
  line, a base image tag, an action's `version:` input, a service container's
  image.
- **`.python-version`** - the exact patch developers and CI run, which
  `requires-python` only brackets.

Where the same tool is pinned in more than one place, pin it to the same
version everywhere and raise them together. One site pinned exactly while
another follows the latest release will drift, and nothing compares them -
the exactly-pinned one is the copy that quietly falls behind.
