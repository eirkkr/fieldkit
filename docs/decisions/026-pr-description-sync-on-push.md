# 026 - Keep PR descriptions in sync, gated on approval

## Decision

When `/push` targets a branch that already has an open PR, `commit-push`
checks whether the PR description still describes the branch, and drafts a
revision when it doesn't. The agent never applies it: the draft comes back in
its report, `skills/push` surfaces it, and `gh pr edit` runs only after
approval.

This reverses `conventions/github.md`'s "update title and body directly - no
pre-approval needed for those edits", and with it the corresponding line in
[008](008-outward-irreversible.md)'s consequences. The rest of 008's model -
which actions are gated, which are act-then-show - is untouched.

## Reason

A branch that grows after its PR opens leaves the description behind. Nothing
in the workflow noticed: the PR body was written once at creation time, and
the next thing to read it closely was `merge-prep`, synthesising a squash
message from a description that no longer matched the diff. The push is the
moment the drift happens, so it's the moment to catch it - and `commit-push`
already has the diff loaded to do the comparison for free.

Editing was gated rather than made act-then-show, unlike the push itself,
because a PR body is not purely machine-generated state. Reviewers read it,
the squash message is built from it, and the human may have written parts of
it by hand. An agent rewriting it unattended can silently drop that - the
failure is invisible precisely because the artefact still looks well-formed.
That's the same shape as the outward-facing actions 008 already gates, so the
carve-out 008 granted for PR-body edits doesn't hold up.

Alternatives rejected:

- **Let the agent edit the body directly** (the status quo ante). Consistent
  with pushes being ungated, but a push is reversible and a clobbered
  human-written description isn't recoverable from git.
- **Catch it at merge instead, in `merge-prep`.** Later and worse: the drift
  has to be fixed while a merge is waiting on it, and `merge-prep` would have
  to reconstruct scope the pushing agent had in hand.
- **Regenerate the body from scratch on every push.** No staleness check
  needed, but it discards the human's wording by design - the exact loss the
  gate exists to prevent.

## Consequences

- A push onto a branch with an open PR can now end in an approval prompt. It
  fires only when the description has actually drifted, so a routine
  fixup-and-push still ends silently. The prompt follows the push and gates
  only the `gh pr edit` - it must not be read as making the push itself
  gated, a misreading this ADR's first draft immediately provoked.
- `commit-push` gains a `gh pr view` call per push. Negligible next to the
  diff reads it already does.
- Staleness is a judgement call the agent makes, so it will sometimes propose
  a rewrite that isn't warranted. Cheap to decline, and the failure mode
  points the safe way.

> Amended by [027](027-push-decisions-move-to-caller.md): the staleness
> check and draft move from `commit-push` (now `agents/push`) to
> `skills/push` - the caller already holds the diff, so it judges directly
> instead of delegating to the agent's copy of the same comparison. The gate
> itself (approval before `gh pr edit`; the push never gated) is unchanged.
