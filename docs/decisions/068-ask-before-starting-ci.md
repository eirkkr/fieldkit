# 068 - Starting CI by hand is asked first

## Decision

Where CI runs only when started (a recipe that re-runs or dispatches it, [065](065-manual-ci-skips-until-re-run.md)), the agent asks the human before starting it, naming the PR and head. A yes covers that head; a push voids it. A typed `/merge` approves the merge, not the start. The full local check no longer covers starting CI. The rule lives in `KIT.md`.

This amends [064](064-agents-run-the-local-check-before-review.md), whose `KIT.md` line had the readiness run also start CI.

## Reason

Starting CI spends runner minutes and cannot be undone. A consumer repo saw a retry loop around its start recipe run about 45 minutes on one head. Whether a head is worth that cost is the human's call, as with merging.

Rejected:

- **Keep starting CI with the readiness run.** Spends minutes on work the human has not yet read, and on a head a review may change.
- **Ask only on a retry.** The first start costs the same, and the agent cannot tell a retry from a first start across sessions.

## Consequences

- One extra question per head in a repo with manual CI; repos where CI runs on push are unaffected.
- A repo may tighten this further in its own `CLAUDE.md`, as it may any kit rule.
