# 030 - Ungate merging; caller drafts the squash message

## Decision

`agents/merge-prep` is renamed to `agents/merge` (matching `/merge`, per
[016](016-skill-agent-pair.md)'s pattern) and its model drops to `haiku`.
`skills/merge/SKILL.md` now does the heavy lifting: if the branch isn't
merge-ready (uncommitted work, unpushed, or no PR open yet), it follows
`skills/pr/SKILL.md` first, which itself follows `skills/push/SKILL.md` -
`/merge` is treated as implicit approval for both, since they're already
ungated. It then checks the PR's mergeability and CI status itself, and -
only once that's clean - drafts the squash subject and body (reading the
branch's full diff, resolving `Closes #X` from GitHub's own answer). The
`merge` agent takes that draft as given, re-verifies mergeability/CI
defensively, and runs `gh pr merge --squash` and the local branch cleanup
itself, with no human review step in between.

Merging is no longer approval-gated. It is conditioned on CI: a red or
still-running check blocks it outright, but a green one merges immediately.
This is the last gate in the `push`/`pr`/`merge` trio to fall, following
[028](028-ungate-pr-creation.md) (PR creation) and
[029](029-ungate-pr-body-edits.md) (PR body edits). It amends
[008](008-outward-irreversible.md) and [011](011-wip-on-branches.md), which
established and then relocated the merge gate, and resolves the "worth
revisiting wholesale" note [029](029-ungate-pr-body-edits.md) left open.

## Reason

Same trust extension already granted twice this session, applied to the one
step it hadn't reached yet: the human has decided the agent's drafted
output doesn't need a pre-action review, squash messages included. What's
left standing isn't a human-approval gate at all - it's a machine-checkable
precondition. [011](011-wip-on-branches.md) named CI status as the actual
thing the merge gate was protecting ("human approval at merge is what
confirms CI is green"); having the agent query
`statusCheckRollup`/`mergeable` directly and refuse to proceed on anything
but green is a more reliable version of that same confirmation, not a
weaker one - a human clicking approve was never independently re-checking
CI either.

Alternatives rejected:

- **Keep a lightweight approval step for the squash message specifically,
  separate from the CI check.** Explicitly ruled out - "don't need human to
  review draft commit" was stated plainly, not conditionally.
- **Have the skill run `gh pr merge` itself**, mirroring how `skills/pr`
  runs `gh pr create` directly rather than delegating creation to its
  agent. Rejected for the opposite reason `pr` was built that way: merge
  benefits from its defensive mergeability/CI re-check, the merge call, and
  the local branch cleanup all happening in one tool-call boundary, the same
  shape `push` already uses for commit+push+optional PR edit. Splitting the
  re-check into the agent and the merge call into the skill would recreate
  the seam [015](015-mechanical-subagent-boundary.md) warned an approved
  draft executed by a second party opens up - except here there's no
  approval step for it to undermine, so there's no reason to introduce the
  split at all.

## Consequences

- `CLAUDE.md`'s outward/irreversible gate list no longer mentions merging;
  the only gate concept left there is agreeing direction first on a
  genuinely new convention or design decision, which is unrelated to git or
  GitHub actions. The whole `push`/`pr`/`merge` trio is now act-then-show,
  conditioned only on mechanical checks (tree sanity, dedupe, CI/mergeable),
  never on a human sign-off.
- A bad squash message or an unwanted merge is no longer caught by a human
  glance before it happens. Recourse is the same after-the-fact correction
  this session's other ungatings already lean on: `git revert` on `main`,
  or `gh pr edit`-style fixes where still applicable.
- The CI/mergeability check is the only thing left between a `/merge`
  invocation and an actual squash-merge to `main`, so it has to stay an
  unconditional, hard-coded blocker rather than a judgment call. Both
  `skills/merge/SKILL.md` and `agents/merge/AGENT.md` check it - once each,
  so a check-then-merge race (CI flips red in the gap) is the one scenario
  this doesn't fully cover. Accepted: the same narrow race a synchronous
  human-approval gate wouldn't have caught either.
