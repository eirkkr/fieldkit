# 065 - Manual CI skips on a push and runs on a re-run

## Decision

`conventions/ci.md` gains a "Manual CI" section, an option for a repo that wants CI only when started. Each workflow triggers on `pull_request` with its job gated on `github.run_attempt > 1`: a push skips it, and a re-run runs it, with the result replacing the skipped entry on the PR. A check on the PR's own text runs for real when that text changes. The default stays every check on every PR.

The `merge` skill treats a `skipping` check as not passed where a repo's CI works this way.

## Reason

A consumer repo that wanted CI only when ready to merge, to spend runner minutes once per PR, tried `workflow_dispatch` first. A dispatch run starts fine, but its check runs never appear on the PR: both jobs passed on a test PR, and neither the PR page nor `gh pr checks` listed them, though the API did. A `pull_request` workflow whose jobs are skipped on a push shows a grey entry on the PR, uses no runner, and a re-run keeps its checks on the PR. The same test PR showed the cycle: skipped on a push, passed after a re-run on the same entry, skipped again on the next push.

A check that reads the PR's title or body is the one exception worth making. It is short, and what it reads changes on an edit, not a push, so it runs for real on `opened`, `reopened` and `edited` and skips on `synchronize`, the event a push to the PR's branch fires, in a workflow of its own so an edit leaves the other jobs' passes alone. This follows `ci.md`'s rule to trigger on `edited` for such a check. Its job gate is `github.run_attempt > 1 || github.event.action != 'synchronize'`. Nothing is measured here beyond the test PR: no minutes were counted, and the claim is that a skipped job is given no runner.

This makes the default of [011](011-wip-on-branches.md), CI on every PR, optional; the default itself is unchanged.

Rejected:

- **`workflow_dispatch`.** Its results never reach the PR.
- **Commit statuses posted by each job.** They do show on the PR, but give no "not run" marker, and need a script and a permission.
- **A label that starts CI.** Adds a trigger the re-run button already is, and has to be removed and added again for each push.
- **Making `skipping` a fail.** A skipped job is legitimate in a repo that skips on path filters, so the `merge` skill cannot treat it as not passed everywhere.

## Consequences

- Nothing enforces the merge rule without branch protection. A skipped check is not failing, so a PR can look clear without CI; the rule lives in the repo's own docs. The `merge` skill finds a repo that works this way by `github.run_attempt > 1` in its workflows, and stops on a `skipping` check there; elsewhere a skipped job is legitimate and does not stop it.
- A re-run reuses the original merge ref, so if the base branch moved since the push it tests the earlier merge.
