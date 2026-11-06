# Claude Guidance (Generic)

Where these rules conflict with the repo's own docs, flag it briefly before proceeding.

## Always-on

- Act-then-show by default: make the change, surface it, correct after. Ask first for the table's marked actions, anything else outward-facing or irreversible, and any new convention or design decision, even a local one.
- Git and GitHub actions go through the `push`, `pr` and `merge` skills, never raw `git commit`, `git push`, `gh pr create` or `gh pr merge`, even mid-task. Read-only inspection (`git status`, `git diff`, `git log`) and actions no skill covers stay direct; for those read the matching doc below.

| Action | Approval | Notes |
| --- | --- | --- |
| Committing and pushing | act-then-show | each coherent piece as it lands |
| Force-pushing a branch with an open PR | ask first | even when git.md's checks show nothing lost |
| Revising an open PR's title/body | act-then-show | keep it true as the branch grows |
| Filing an issue | ask first | unless the user asked for one, or a change's plan files it (`conventions/specs.md`) |
| Commenting on or editing an issue | act-then-show | surface what was filed |
| Closing an issue | ask first | except a `Closes #X` PR's close on merge |
| Branching off a non-default branch | ask first | explain why; off the default branch needs none |
| Opening a PR | ask first | unless the user typed `/pr`, or it is a change stage's gate PR |
| Merging | ask first | unless the user typed `/merge`; needs CI |

- Approval settles whether to act, not what the draft says: once given (a yes, or the `/pr`, `/merge` or issue request itself), draft and go straight to it.
- Merging needs CI: a failed check, a conflict or a missing required review stops it (report; never `--admin` or edit a ruleset unless the user asks). A running check is waited out; a green one merges with no further sign-off.
- Approval covers one head: the short SHA named when asking, or the head at a typed `/merge`. Any push that adds or rewrites a commit voids it (a fix, a rebase, anyone's): stop, report, ask again. The one exception is this PR's gate approval commits (`change-stage` skill's GATE.md).
- Commit onto the current branch, even if its existing work looks unrelated.
- A gate on a *follow-up* never holds the action before it: land the push, then ask.
- A finding is *small* when fixing it costs less than filing an issue, or slightly more. Fix a small unrelated one on the branch, act-then-show, in its own commit named in the PR description. Any other finding becomes an issue: say what it would say, file on a yes.
- Route lessons worth keeping by scope: generic ones to the shared conventions kit, repo-specific ones to that repo's docs.
- Fix the cause before suppressing (`# type: ignore`, `# noqa`, tool exclusion). Suppress only when the tool is wrong about the file's context (generated, vendored).
- Recommend on correctness; effort, churn and consistency are costs stated beside it ("X is more correct; switching costs Y"). When costs are high enough to matter, give both options. Consistency only decides between equally correct options.
- Delegate to a subagent to isolate context (large throwaway exploration), not to save on a small task: a fresh subagent re-pays context. One that may edit files, a reviewer's mutation probe included, gets `isolation: "worktree"`.
- Re-derive any count or claim about a file's contents from the tree as you write it into an ADR, spec, issue or commit message. Reading part of a file is not reading it: never claim what a document "never addresses" from a partial read.

### Linting and formatting

- Lint once, at readiness: while iterating, match surrounding style by eye, no linters. Before handing work over (a PR to open, `/pr` included; a stage's gate), run the repo's full local check and fix what it reports in its own commit via `push`. `/merge` is no handover: a fix would void the approved head.
- That run also covers starting CI; rerun only if code changed since. Run more of what CI runs only where the repo's docs ask; ask first for a slow recipe.
- Run tests for correctness feedback: the repo's canonical command, quiet, short tracebacks, fail-fast on the narrowest relevant selection while iterating, then the full suite before declaring done.

### Reviewing and auditing

- Green CI covers only machine-enforced rules; audit review-enforced conventions (ordering, spacing, doc accuracy) by hand against the diff.
- When a branch adds or changes a convention, audit existing code for violations and fix docs still teaching the old pattern.
- Fix pre-existing convention violations in files you edit; never extend them. A fix that isn't *small* (usually spanning modules) becomes an issue.
- Read an artifact edited many times end to end, as a document, before calling it finished: each edit can be right while the whole drifts from its stated goal. This pass comes last.

## Load on Demand

Read the matching file before the action, and only then.

| Before... | Read |
| --- | --- |
| A git action `push`/`pr`/`merge` don't cover (rebase, tag, amend) | .fieldkit/conventions/git.md |
| A GitHub action `pr`/`merge` don't cover (issues, comments, PR edits) | .fieldkit/conventions/github.md |
| Writing an issue, ADR, spec or convention doc, or an exemption list | .fieldkit/conventions/records.md |
| Recording a design decision (ADR) | .fieldkit/conventions/decisions.md |
| Starting work too big for one PR, or that leaves the user a decision | .fieldkit/conventions/specs.md |
| Building a feature that calls an LLM | .fieldkit/conventions/ai.md |
| Writing or editing a CI workflow, or a check or lint recipe | .fieldkit/conventions/ci.md |
| Setting up, checking or running Claude as a bot account (a limited GitHub account) | .fieldkit/conventions/bot-account.md |
