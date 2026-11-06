# CI conventions

## Pin everything a workflow runs on

Nothing a workflow depends on changes without a commit saying so ([ADR 048](../docs/decisions/048-pin-ci-by-commit.md)).

- **Actions:** the full commit SHA, with the version as a trailing comment:

  ```yaml
  - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0
  ```

  Not `@v4` (moves with every 4.x release) or `@v4.4.0` (a tag can be re-pointed; a commit can't). Dependabot and Renovate update this form, comment included.
- **Runners:** a versioned image such as `ubuntu-24.04`, never `-latest`.
- **Base images:** `FROM` names tag and digest, `debian:trixie-slim@sha256:<digest>` (`docker buildx imagetools inspect` prints it). The digest records the build but freezes OS security fixes, so add Dependabot's `docker` ecosystem to refresh it. Where a skill owns an image's version, as `update-python` does Python's, ignore Dependabot's version updates for it. Dependabot reads `FROM` only; `COPY --from=` images stay with the skills' sweep.
- **Tools a job installs:** through uv at an exact version: from the lockfile where the repo has one (a dev dependency, `uv sync --locked`, `setup-uv`'s `activate-environment: true` to reach `PATH`), else `uv tool install rust-just@1.58.0`. Never a vendor's install script, which adds a third-party host to every run and installs whatever is current.
- **One tool, one version:** a tool pinned in several places (lockfile, Dockerfile, workflow) names the same version in each, raised together.

Find an action's commit from its release tag (resolves annotated tags too):

```bash
gh api repos/<owner>/<action>/commits/<tag> -q .sha
```

To upgrade, change the SHA and its comment together.

## Workflows run the repo's own recipes

- Each job runs a `just` recipe, the command a developer runs locally; the logic lives in the recipe, not the workflow's `run:`. A recipe longer than a line or two calls a script in `scripts/`.
- `just lint` runs the linters and is what the lint job runs; `just check` runs everything, `lint` included, locally.
- Each check runs in exactly one job, so a failure is reported once.
- A check prints a line per result, prefixed with its recipe name (`check-branch-name: ...`), on success too, so a pass is visible and a log says which check spoke.
- A script running several tools catches each result - `if tool ...; then echo "<recipe>: tool passed"; else echo "<recipe>: tool failed" >&2; status=1; fi` - and exits once, at the end. Bare under `set -e`, the first failure exits with no prefixed line and the later tools never run.

## Shell scripts

- **Tools:** shellcheck lints, shfmt formats ([ADR 061](../docs/decisions/061-shellcheck-and-shfmt.md)). `just lint` runs both; `just fix` runs `shfmt --write`.
- **Pins:** the `shellcheck-py` and `shfmt-py` packages, as dev dependencies with a lockfile, else `uvx --from shfmt-py@<version> shfmt`. shfmt-py numbers its own releases: 4.2.0 ships shfmt 3.14.1.
- **Style:** in `.editorconfig`, under `root = true` so a file above the clone can't merge in. The indent is each repo's; start from the kit's four spaces with indented `case` arms (`indent_size = 4`, `switch_case_indent = true`). A script matching no section gets shfmt's default, tabs. A slash anchors a glob to the root, so `[{*.sh,hooks/*}]` misses `scripts/*.sh`: give each pattern its own section.
- **Config:** an empty `.shellcheckrc` at the root, so a `~/.shellcheckrc` can't change the result.
- **Files:** `git ls-files`, selected by first-line shebang, which catches an extensionless hook and skips a Markdown code block.
- **Suppressions:** `# shellcheck disable=SCxxxx` on the one line, beside a comment saying why.

## Triggers and input

- Workflows run on `on: pull_request` with no draft filter, so every PR runs every check ([ADR 011](../docs/decisions/011-wip-on-branches.md) keeps unfinished work on branches), unless the repo chooses [Manual CI](#manual-ci). Add `types: [..., edited]` only for a check that reads the PR's title or body, so a retitled PR is rechecked.
- PR text (title, body, branch name) is user input: pass it to a script through `env:`, never interpolated as `${{ }}` into `run:`, where it runs as shell.

## Manual CI

For a repo that wants CI only when started, not on every push ([ADR 065](../docs/decisions/065-manual-ci-skips-until-re-run.md)).

- **State the merge rule in the repo's own docs:** a merge needs `pass` for every job; a `skipping` check is not a pass. Nothing enforces this without branch protection. The `merge` skill finds such a repo by `github.run_attempt > 1` in `.github/workflows/*.yml`, so keep that gate in each job's `if:` and name the files `.yml`.
- **Trigger on `pull_request` and gate each job `if: github.run_attempt > 1`.** A push is attempt 1: the PR shows the job skipped and no runner is used. A re-run (the PR's button, or `gh run rerun <id>`) has `run_attempt` above 1, so the job runs and its result replaces the skipped entry. `gh run rerun --failed` skips skipped jobs. A push starts a new run, skipped again, so a pass belongs to its head. `workflow_dispatch` is no option: its check runs don't appear on the PR.
- **One workflow per job, under a shared filename prefix** such as `check-*.yml`, so each re-runs alone and a glob finds them all.
- **A check on the PR's text (title, body, branch name) runs for real when that text changes.** Give it its own workflow on `opened`, `reopened`, `edited` and `synchronize`, with `if: github.run_attempt > 1 || github.event.action != 'synchronize'` on the job: it runs on open and edit, skips on a push unless re-run, and an edit leaves other jobs' passes alone.
- **A re-run reuses the original merge ref.** If the base moved since the push, push again first.
