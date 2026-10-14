# Python project setup and dependencies

Conventions for scaffolding a Python project and managing its dependencies with uv.

## Project setup

Initialise new projects with uv commands rather than hand-authoring `pyproject.toml`:

```sh
uv init <name>          # scaffold pyproject.toml, .python-version, README
uv add <pkg>            # add a runtime dependency (resolves latest)
uv add --dev <pkg>      # add a dev dependency (resolves latest)
uv sync                 # create/update the lockfile and venv
```

Commit `pyproject.toml`, `uv.lock`, and `.python-version`. Do not edit `pyproject.toml` or `uv.lock` by hand after initial setup - use `uv add` / `uv remove` so the lockfile stays consistent.

`.python-version` records the exact Python patch the project uses (e.g. `3.14.4`). Create or update it with `uv python pin <version>`. This is the specific version developers and CI should run; `requires-python` in `pyproject.toml` is the broader compatibility range.

**Always use the latest available versions** when setting up a project - the latest stable Python minor and the latest release of each dependency. `uv add` resolves the latest by default; after it runs, tighten the version range in `pyproject.toml` to follow the pinning convention below. Check the installed Python version with `uv run python --version` and use that patch in `requires-python`.

## Dependencies

After `uv add` installs a package, set its version range in `pyproject.toml` based on the installed version. Do not hand-edit `pyproject.toml` directly; use `uv add "pkg>=X.Y,<Z"` to update a constraint.

The minimum is the minor of the installed release (drop the patch); the maximum depends on the package:

- **Dependencies (major >= 1):** cap at the next major. `>=X.Y,<X+1` - e.g. installed `pytest 9.1.1` → `>=9.1,<10`
- **Dependencies (major == 0):** cap at the next minor - 0.x semver treats the minor as the breaking-change boundary. `>=0.Y,<0.Y+1` - e.g. installed `rumdl 0.2.26` → `>=0.2,<0.3`
- **`requires-python`:** pin to the latest installed minor and cap at the next minor. `>=X.Y,<X.Y+1` - e.g. installed Python `3.14.4` → `>=3.14,<3.15`

Common mistakes to avoid:

- `>=9.1.1,<10` - patch in the floor; use `>=9.1,<10`
- `>=9,<10` - major in the floor; use `>=9.1,<10`
- `>=0.2.26,<0.3` - patch in the floor for a 0.x package; use `>=0.2,<0.3`
- `>=0.9,<1` - capping a 0.x package at major; use `>=0.9,<0.10`
- `>=3.11` - an old Python version with no upper bound; use `>=3.14,<3.15`

## Version pins the dependency tooling does not manage

`uv tree --outdated` sees only project and dev dependencies. The pins below sit outside it and go stale silently, grouped by what moves them.

### Moved by a dependency update

- **`[build-system] requires`** - the build backend is not a dependency of the project, so it never appears in the tree. `uv_build` versions with uv itself, and an upper bound below the installed uv makes every `uv` command warn. Raise it with uv's own minor, following the 0.x rule above.
- **Tools pinned in a Dockerfile or CI** - a `COPY --from=ghcr.io/...` line, an action's `version:` input, a service container's image.

### Moved by an interpreter update

The Python version moves in a change of its own, after the dependencies are current: support for a new Python arrives in packages' newer releases, and with them current, any failure after the update belongs to Python.

- **Full version** - `.python-version`, and any base image tag naming the Python version (with its digest). Every Python update raises them. An image using `uv python install` has no Python pin of its own. A base image's OS release (`trixie` is Debian 13) moves when a newer one is out.
- **Minor only** - `requires-python`, the `Programming Language :: Python :: X.Y` classifier, and tool targets such as ruff `target-version` and mypy `python_version`.

### Pins that must agree

Where the same tool or version is pinned in more than one place, pin it to the same version everywhere and raise them together. A site that follows the latest release drifts from one pinned exactly, and nothing compares them.

A repo can record its pin sites, and which must agree, in `docs/version-pins.md`. `update-deps` checks it against the tree, and `update-python` adds the sites a Python update finds.

## Python in a Docker image

Follow Astral's [standalone example](https://github.com/astral-sh/uv-docker-example/blob/main/standalone.Dockerfile):

- **Builder stage** on `debian:trixie-slim` with uv copied in: `uv python install` (with `UV_PYTHON_INSTALL_DIR=/python`, `UV_PYTHON_PREFERENCE=only-managed`), then `uv sync --frozen`.
- **Runtime stage** on the same image and digest: copy `/python` and the app, install `ca-certificates` (for TLS verification), `netbase` and `tzdata`, and run as an unprivileged user with a home directory - gunicorn writes its control socket there. No uv.

`.python-version` is then the only full-version Python pin. Two details:

- Put `--mount=type=cache,target=/root/.cache/uv` on every uv step; `UV_LINK_MODE=copy` is for that mount. Without it, uv's cache ships in the image.
- The standalone builds include pip, whose vendored packages image scanners flag. Removing it takes `pip uninstall --break-system-packages pip`, as the interpreter is marked externally managed (PEP 668).
