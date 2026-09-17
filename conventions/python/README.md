# Python conventions

Language-specific conventions for Python repos.

## Load on Demand

Read the matching file before the action; don't load it otherwise.

| Before...                             | Read                                          |
| ------------------------------------- | --------------------------------------------- |
| Writing or editing Python source      | .fieldkit/conventions/python/code.md          |
| Setting up a project or managing deps | .fieldkit/conventions/python/setup.md         |
| Writing or reviewing tests            | .fieldkit/conventions/python/testing.md       |

Bumping dependencies, or reviewing bumps already in a diff, goes through the
`update-deps` skill where the repo has enabled it
(`.fieldkit/scripts/enable-python.sh`).
