# Claude Guidance (Generic)

Where these rules conflict with the repo's own docs, flag it briefly before proceeding.

## Always-on

- Default act-then-show: change, surface, correct after. Ask first for the table's marked actions, anything else outward-facing or irreversible, and any new convention or design decision, even local.
- Git and GitHub actions go through the `push`, `pr`, `merge` skills, never raw `git commit`, `git push`, `gh pr create`, `gh pr merge`, even mid-task. Read-only inspection (`git status`, `git diff`, `git log`) and actions no skill covers stay direct; for those read the matching doc below.

| Action | Approval | Notes |
| --- | --- | --- |
| Committing and pushing | act-then-show | each coherent piece as it lands |
| Force-pushing a branch with an open PR | ask first | even when git.md's checks show nothing lost |
| Revising an open PR's title/body | act-then-show | keep true as branch grows |
| Filing an issue | ask first | unless user asked, or a change's plan files it (`conventions/specs.md`) |
| Commenting on or editing an issue | act-then-show | surface what was filed |
| Closing an issue | ask first | except a `Closes #X` PR's close on merge |
| Branching off a non-default branch | ask first | explain why; off default needs none |
| Opening a PR | ask first | unless user typed `/pr`, or it is a change stage's gate PR |
| Merging | ask first | unless user typed `/merge`; needs CI |
| Removing other worktrees at `/merge` | ask first | the sweep's yes; the merge's own worktree needs none |
| Starting CI by hand (a repo's recipe that re-runs or dispatches it) | ask first | name PR and head; a yes covers that head; `/merge` does not cover it |

- Approval settles whether to act, not what the draft says. Once given (a yes, or the `/pr`, `/merge` or issue request itself), draft and go straight to it.
- Merging needs CI. Failed check, conflict or missing required review stops it: report, never `--admin` or edit a ruleset unless asked. Running check: wait. Green: merge, no further sign-off.
- Approval covers one head: the short SHA named when asking, or the head at a typed `/merge`. Any push adding or rewriting a commit voids it (a fix, a rebase, anyone's): stop, report, ask again. Sole exception: this PR's gate approval commits (`change-stage` GATE.md).
- Commit onto the current branch, even if its work looks unrelated.
- New work from the default branch: before the first edit to a non-ignored file, run `.fieldkit/scripts/new-worktree.sh <type> <description>` from the main checkout, then `EnterWorktree` the path it prints. Failure or refused entry: tell the reviewer; at exit 3 enter it, otherwise stop. In a worktree or on a non-default branch: stay.
- A gate on a *follow-up* never holds the action before it: land the push, then ask.
- A finding is *small* when fixing costs less than filing an issue, or slightly more. Small and unrelated: fix on the branch, act-then-show, own commit, named in the PR description; on a change's stage PR, only in files the stage already touches. Any other finding becomes an issue: say what it would say, file on a yes.
- Route lessons worth keeping by scope: generic to the shared conventions kit, repo-specific to that repo's docs.
- Fix the cause before suppressing (`# type: ignore`, `# noqa`, tool exclusion). Suppress only when the tool is wrong about the file's context (generated, vendored).
- Recommend on correctness; state effort, churn and consistency as costs beside it ("X is more correct; switching costs Y"). When costs are high enough to matter, give both options. Consistency decides only between equally correct options.
- Delegate to a subagent to isolate context (large throwaway exploration), not to save on a small task: a fresh subagent re-pays context. One that may edit files, a reviewer's mutation probe included, gets `isolation: "worktree"`.
- Re-derive any count or file-contents claim from the tree as you write it into an ADR, spec, issue or commit message. Partial read is not reading: never claim what a document "never addresses" from one.

### Linting and formatting

- Lint once, at readiness. While iterating, match surrounding style by eye, no linters. Before handover (PR to open, `/pr` included; a stage's gate), run the repo's full local check, fix what it reports in its own commit via `push`. `/merge` is no handover: a fix would void the approved head.
- Run more of CI only where the repo's docs ask; ask first for a slow recipe.
- Run tests for correctness feedback: repo's canonical command, quiet, short tracebacks, fail-fast on the narrowest relevant selection while iterating, full suite before declaring done.

### Reviewing and auditing

- Green CI covers only machine-enforced rules. Audit review-enforced conventions (ordering, spacing, doc accuracy) by hand against the diff.
- A branch that adds or changes a convention: audit existing code for violations, fix docs still teaching the old pattern.
- Fix pre-existing convention violations in files you edit; never extend them. A fix that isn't *small* (usually spanning modules) becomes an issue.
- Read an artifact edited many times end to end, as a document, before calling it finished: every edit can be right while the whole drifts from its stated goal. Last pass.

## Load on Demand

Read the matching file before the action, and only then.

| Before... | Read |
| --- | --- |
| A git action `push`/`pr`/`merge` don't cover (rebase, tag, amend) | .fieldkit/conventions/git.md |
| A GitHub action `pr`/`merge` don't cover (issues, comments, PR edits) | .fieldkit/conventions/github.md |
| Writing an issue, ADR, spec or convention doc, an exemption list, or editing KIT.md or a skill | .fieldkit/conventions/records.md |
| Recording a design decision (ADR) | .fieldkit/conventions/decisions.md |
| Starting work too big for one PR, or that leaves the user a decision | .fieldkit/conventions/specs.md |
| Building a feature that calls an LLM | .fieldkit/conventions/ai.md |
| Writing or editing a CI workflow, or a check or lint recipe | .fieldkit/conventions/ci.md |
| Setting up, checking or running Claude as a bot account (a limited GitHub account) | .fieldkit/conventions/bot-account.md |
