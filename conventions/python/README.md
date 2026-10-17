# Python conventions

Language-specific conventions for Python repos.

## Load on Demand

Read the matching file before the action; don't load it otherwise.

| Before... | Read |
| --- | --- |
| Writing or editing Python source | .fieldkit/conventions/python/code.md |
| Setting up a project, managing deps, or writing a Dockerfile | .fieldkit/conventions/python/setup.md |
| Writing or reviewing tests | .fieldkit/conventions/python/testing.md |

Dependency bumps, and reviews of bumps in a diff, go through the `update-deps` skill where enabled (`.fieldkit/scripts/enable-python.sh`). Updating the Python interpreter to a newer patch or minor goes through `update-python`.
