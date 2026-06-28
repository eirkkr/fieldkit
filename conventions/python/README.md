# Python conventions

Language-specific conventions for Python repos. `@`-import this file in a Python
repo as an index to the detail files, which you read on demand for the task at
hand. Several of the linked rules have no automated enforcement and rely on
review.

## Load on Demand

Read the matching file before the action; don't load it otherwise. Paths are
relative to the consumer repo root, via the `.fieldkit` symlink.

| Before...                             | Read                                          |
| ------------------------------------- | --------------------------------------------- |
| Writing or editing Python source      | .fieldkit/conventions/python/code.md          |
| Setting up a project or managing deps | .fieldkit/conventions/python/setup.md         |
| Writing or reviewing tests            | .fieldkit/conventions/python/testing.md       |
