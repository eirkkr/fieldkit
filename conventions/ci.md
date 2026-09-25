# CI conventions

## Pin everything a workflow runs on

Nothing a workflow depends on changes without a commit saying so
([ADR 048](../docs/decisions/048-pin-ci-by-commit.md)).

- **Actions:** the full commit SHA, with the version as a trailing comment:

  ```yaml
  - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0
  ```

  Not `@v4`, which moves with every 4.x release, and not `@v4.4.0`, since a
  tag can be re-pointed. A commit can't. Dependabot and Renovate both update
  this form, comment included.
- **Runners:** a versioned image such as `ubuntu-24.04`, never `-latest`.
- **Tools a job installs:** through uv, at an exact version - from the
  lockfile where the repo has one (a dev dependency, `uv sync --locked`, and
  `setup-uv`'s `activate-environment: true` to put it on `PATH`), otherwise
  `uv tool install rust-just@1.58.0`. Never a vendor's install script: it puts
  a third-party host on every run, and installs whatever release is current.
- **One tool, one version:** where a tool is pinned in several places - the
  lockfile, a Dockerfile, a workflow - every site names the same version, and
  they are raised together.

Find an action's commit from its release tag - this resolves annotated tags
too:

```bash
gh api repos/<owner>/<action>/commits/<tag> -q .sha
```

Upgrading means editing the pin: change the SHA and its comment together.

## Workflows run the repo's own recipes

- Each job runs a `just` recipe - the same command a developer runs locally.
  The logic lives in the recipe, not in the workflow's `run:`.
- `just lint` runs the linters and is what the lint job runs; `just check` runs
  everything, `lint` included, for local use.
- Each check runs in exactly one job, so a failure is reported once.
- A recipe longer than a line or two calls a script in `scripts/`.
- A check prints a line for each result, prefixed with its recipe name
  (`check-branch-name: ...`), on success as well as failure - so a pass is
  visible, and a log says which check spoke.

## Triggers and input

- Workflows run on `on: pull_request` with no draft filter: every PR runs
  every check ([ADR 011](../docs/decisions/011-wip-on-branches.md) keeps
  unfinished work on branches, not in draft PRs). Add
  `types: [..., edited]` only for a check that reads the PR's title or body,
  so a retitled PR is checked again.
- PR text - the title, body or branch name - reaches a script through `env:`,
  never interpolated as `${{ }}` into `run:`. It is user input, and
  interpolated it runs as shell.
