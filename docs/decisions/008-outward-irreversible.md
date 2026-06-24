# 008 - Gate on outward or irreversible actions

## Decision

Agents seek approval only before actions that are outward-facing or
irreversible: creating or editing issues or comments, marking a PR ready for
review, and squash-merging to main (with its message). Local, pre-merge work -
creating branches, editing docs and code, committing, and pushing draft PRs -
is act-then-show: do it, surface it (the diff or PR), and correct after. First
push is a review checkpoint, not a gate. The principle is stated once in
`CLAUDE.md` and applied in `conventions/workflow.md` and `conventions/git.md`.

## Reason

Pre-approval on every step (the branch name, each doc edit) added round-trips
for little safety: local pre-merge work is cheap to amend or revert with git, so
the gates mostly cost turns. Gating only the outward and irreversible points
keeps protection where mistakes are costly - public artefacts, and the shared
`main` branch every consumer pulls - while taking friction off reversible local
work.

Alternatives rejected:

- **Gate each step** (branch creation, doc text before editing). High friction,
  and the gated steps are trivially reversible, so the gate mostly bought
  round-trips, not safety.
- **No gates, review only after merge.** A merge to `main` is irreversible and
  propagates to every consumer, and outward actions (issues, review requests)
  reach other people - those genuinely need a stop.

## Consequences

- Wrong-but-local outcomes (a misnamed branch, an off doc edit) are corrected
  after the fact rather than prevented. Accepted: cheaper than gating every step.
- The pre-merge message is the single substantive review point; the agent drafts
  it proactively so it is not an extra round-trip.
- A genuinely new convention or design decision still has its direction agreed
  first, in discussion, since redoing it is costly - the one place pre-agreement
  is kept.
- `conventions/github.md` already matched this model (draft PRs need no approval;
  the gates are ready-for-review and the pre-merge message), so only `CLAUDE.md`,
  `workflow.md`, and `git.md` changed.
