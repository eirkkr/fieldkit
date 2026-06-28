# Python project setup and dependencies

Conventions for scaffolding a Python project and managing its dependencies with
uv. See [README.md](README.md) for the index.

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
  `>=0.Y,<0.Y+1` - e.g. installed `pymarkdownlnt 0.9.38` → `>=0.9,<0.10`
- **`requires-python`:** pin to the latest installed minor and cap at the next
  minor. `>=X.Y,<X.Y+1` - e.g. installed Python `3.14.4` → `>=3.14,<3.15`

Common mistakes to avoid:

- `>=9.1.1,<10` - patch in the floor; use `>=9.1,<10`
- `>=9,<10` - major in the floor; use `>=9.1,<10`
- `>=0.9.38,<0.10` - patch in the floor for a 0.x package; use `>=0.9,<0.10`
- `>=0.9,<1` - capping a 0.x package at major; use `>=0.9,<0.10`
- `>=3.11` - an old Python version with no upper bound; use `>=3.14,<3.15`
