# Python project setup and dependencies

## Project setup

Initialise projects with uv, not a hand-written `pyproject.toml`:

```sh
uv init <name>          # scaffold pyproject.toml, .python-version, README
uv add <pkg>            # add a runtime dependency (resolves latest)
uv add --dev <pkg>      # add a dev dependency (resolves latest)
uv sync                 # create/update the lockfile and venv
```

Commit `pyproject.toml`, `uv.lock` and `.python-version`. After setup, change dependencies only with `uv add` / `uv remove`, never by editing `pyproject.toml` or `uv.lock`, so the lockfile stays consistent.

`.python-version` records the exact patch (e.g. `3.14.4`) that developers and CI run; set it with `uv python pin <version>`. `requires-python` is the broader compatibility range.

Set a project up on the latest stable Python minor and the latest release of each dependency. `uv add` resolves the latest; afterwards tighten the range in `pyproject.toml` per the pinning convention below, taking the Python version from `uv run python --version`.

## Dependencies

After `uv add` installs a package, set its range from the installed version with `uv add "pkg>=X.Y,<Z"`. The minimum is the installed release's minor (no patch); the maximum depends on the package:

- **Dependencies (major >= 1):** cap at the next major, `>=X.Y,<X+1`: installed `pytest 9.1.1` → `>=9.1,<10`
- **Dependencies (major == 0):** cap at the next minor, since 0.x treats the minor as the breaking boundary, `>=0.Y,<0.Y+1`: installed `rumdl 0.2.26` → `>=0.2,<0.3`
- **`requires-python`:** the installed minor, capped at the next, `>=X.Y,<X.Y+1`: installed Python `3.14.4` → `>=3.14,<3.15`

Common mistakes to avoid:

- `>=9.1.1,<10` - patch in the floor; use `>=9.1,<10`
- `>=9,<10` - major in the floor; use `>=9.1,<10`
- `>=0.2.26,<0.3` - patch in the floor for a 0.x package; use `>=0.2,<0.3`
- `>=0.9,<1` - capping a 0.x package at major; use `>=0.9,<0.10`
- `>=3.11` - an old Python version with no upper bound; use `>=3.14,<3.15`

## Version pins the dependency tooling does not manage

`uv tree --outdated` sees only project and dev dependencies. The pins below sit outside it and go stale silently, grouped by what moves them.

### Moved by a dependency update

- **`[build-system] requires`** - the build backend never appears in the tree. `uv_build` versions with uv itself, and an upper bound below the installed uv makes every `uv` command warn. Raise it with uv's minor, by the 0.x rule above.
- **Tools pinned in a Dockerfile or CI** - a `COPY --from=ghcr.io/...` line, an action's `version:` input, a service container's image.

### Moved by an interpreter update

Python moves in a change of its own, after the dependencies are current: new-Python support arrives in packages' newer releases, so with them current a failure after the update belongs to Python.

- **Full version** - `.python-version`, and any base image tag naming the Python version (with its digest). Every Python update raises them. An image using `uv python install` has no Python pin of its own. A base image's OS release (`trixie` is Debian 13) moves when a newer one is out.
- **Minor only** - `requires-python`, the `Programming Language :: Python :: X.Y` classifier, and tool targets such as ruff `target-version` and mypy `python_version`.

### Pins that must agree

A tool or version pinned in more than one place takes the same version everywhere, raised together: a site following the latest release drifts from one pinned exactly, and nothing compares them.

A repo can record its pin sites, and which must agree, in `docs/version-pins.md`. `update-deps` checks it against the tree, and `update-python` adds the sites a Python update finds.

## Python in a Docker image

Follow Astral's [standalone example](https://github.com/astral-sh/uv-docker-example/blob/main/standalone.Dockerfile):

- **Builder stage** on `debian:trixie-slim` with uv copied in: `uv python install` (with `UV_PYTHON_INSTALL_DIR=/python`, `UV_PYTHON_PREFERENCE=only-managed`), then `uv sync --frozen`.
- **Runtime stage** on the same image and digest: copy `/python` and the app, install `ca-certificates` (for TLS verification), `netbase` and `tzdata`, and run as an unprivileged user with a home directory - gunicorn writes its control socket there. No uv.

`.python-version` is then the only full-version Python pin. Two details:

- Put `--mount=type=cache,target=/root/.cache/uv` on every uv step (`UV_LINK_MODE=copy` is for that mount), or uv's cache ships in the image.
- The standalone builds include pip, whose vendored packages image scanners flag. Remove it with `pip uninstall --break-system-packages pip` (the interpreter is externally managed, PEP 668).
