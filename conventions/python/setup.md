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

`uv tree --outdated` sees only project and dev dependencies. The pins below sit outside it and go stale silently, so they are checked by hand. What moves each one decides which group it is in.

### Moved by a dependency update

- **`[build-system] requires`** - the build backend is not a dependency of the project, so it never appears in the tree. `uv_build` versions with uv itself, and an upper bound below the installed uv makes every `uv` command warn. Raise it with uv's own minor, following the 0.x rule above.
- **Tools pinned in a Dockerfile or CI** - a `COPY --from=ghcr.io/...` line, an action's `version:` input, a service container's image.

### Moved by an interpreter update

The Python version moves in a change of its own, after the dependencies are current. Support for a new Python arrives in packages' newer releases, so with dependencies current first, the move hits fewer blockers and any failure after it belongs to Python.

- **Full version** - `.python-version`, and a base image tag naming the Python version, with its digest where the image is pinned by one. Every move raises them, patch or minor. An image that installs Python with `uv python install` reads `.python-version` and has no Python pin of its own. A base image tag also names an OS release (`-slim-trixie` is Debian 13), which can move on its own when a newer one is out.
- **Minor only** - `requires-python`, the `Programming Language :: Python :: X.Y` classifier, and tool targets such as ruff `target-version` and mypy `python_version`. Only a move to a new minor raises them.

### Pins that must agree

Where the same tool or version is pinned in more than one place, pin it to the same version everywhere and raise them together. One site pinned exactly while another follows the latest release will drift, and nothing compares them - the exactly-pinned one is the copy that quietly falls behind.

A repo can record its pin sites, and which must agree, in `docs/version-pins.md`. `update-deps` checks it against the tree, and `update-python` adds the sites an interpreter move finds.

## Python in a Docker image

Build the image the way Astral's [standalone example](https://github.com/astral-sh/uv-docker-example/blob/main/standalone.Dockerfile) does:

- **A builder stage** on a slim Debian image (`debian:trixie-slim`), with uv copied in (`COPY --from=ghcr.io/astral-sh/uv:X /uv /uvx /bin/`). `uv python install` reads `.python-version` into a fixed directory (`UV_PYTHON_INSTALL_DIR=/python`, `UV_PYTHON_PREFERENCE=only-managed`), then `uv sync --frozen` builds the venv.
- **A runtime stage** on the same Debian image and digest, copying `/python` and the app with its venv from the builder, and running as an unprivileged user created with a home directory - gunicorn 26 writes its control socket there, and logs a permission error on every start without one. It carries no uv.

The Dockerfile then names no Python version, so `.python-version` is the one full-version Python pin, for local runs and the image alike. The slim Debian image lacks what the official Python image adds on top of it: install `ca-certificates` in the runtime stage for anything that verifies TLS, and `netbase` and `tzdata` alongside it.

Two details the layout depends on:

- **A cache mount on every uv step:** `RUN --mount=type=cache,target=/root/.cache/uv`, with `UV_LINK_MODE=copy`, since uv can't hard-link into a mount. Without the mount, uv's cache is written into the layer and ships in every image built from it.
- **The standalone builds include pip**, in the interpreter's own `site-packages`, though nothing in the image uses it. Image scanners report the CVEs of the packages pip vendors. The interpreter is marked externally managed (PEP 668), so removing pip takes `pip uninstall --break-system-packages pip`.
