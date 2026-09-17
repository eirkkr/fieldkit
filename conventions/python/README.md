# Python conventions

Language-specific conventions for Python repos.

## Load on Demand

Read the matching file before the action; don't load it otherwise.

| Before...                             | Read                                          |
| ------------------------------------- | --------------------------------------------- |
| Writing or editing Python source      | .fieldkit/conventions/python/code.md          |
| Setting up a project or managing deps | .fieldkit/conventions/python/setup.md         |
| Writing or reviewing tests            | .fieldkit/conventions/python/testing.md       |

Dependency bumps, and reviews of bumps in a diff, go through the `update-deps`
skill where enabled (`.fieldkit/scripts/enable-python.sh`).
