# 029 - Make PR title/body edits act-then-show too

## Decision

The approval gate on revising an open PR's title/body - introduced in
[026](026-pr-description-sync-on-push.md) and explicitly kept when
[028](028-ungate-pr-creation.md) ungated PR *creation* - is dropped. When
`skills/push/SKILL.md` finds a PR's description has gone stale, it drafts
the revision and hands it straight to the `push` subagent to apply via
`gh pr edit`; there's no pending-approval branch left in that flow.
`conventions/git.md` and `conventions/github.md` drop their "wait for
approval" language for this edit. `CLAUDE.md`'s gate list narrows to
merging alone - the last gate standing in the `push`/`pr`/`merge` trio.

## Reason

Same extension of trust 028 already made for PR creation, now applied one
step further: the human has decided the agent can be trusted to write a
correct PR title/body without a pre-application review, for edits as much
as for the initial draft. 026's original worry - an unattended rewrite
silently dropping context the human wrote by hand - is a real risk this ADR
accepts rather than mitigates; recourse is the same the rest of this
workflow already relies on: a wrong edit is corrected after the fact
(`gh pr edit` again, or GitHub's own edit history to recover prior text).

Alternatives rejected:

- **Keep the gate specifically when the existing body looks human-edited**
  (e.g. diverges structurally from the agent's own template). Adds a
  judgment call with no clean signal, and doesn't match what was actually
  asked - the human's trust wasn't conditional on that distinction.

## Consequences

- The `push` flow collapses to a single pass with no wait state: draft (if
  the PR looks stale), dispatch, agent applies. `skills/push/SKILL.md` no
  longer has a "surface and wait" tail.
- Merging is now the only gated action left across `push`, `pr`, and
  `merge`. If that also stops being wanted, the "gate" framing this trio's
  ADRs have carried since [008](008-outward-irreversible.md) is worth
  revisiting wholesale rather than amending piecemeal again.
- The issue/comment gate `conventions/github.md` states separately is
  untouched - this decision is scoped to PR title/body edits, not issues or
  comments.

> Amended by [030](030-ungate-merge.md): merging drops its gate too,
> resolving the "worth revisiting wholesale" note above - the `push`/`pr`/
> `merge` trio is now fully act-then-show.

<!-- -->

> Amended by [038](038-ungate-issue-filing.md): the issue/comment gate this
> ADR left explicitly untouched is dropped too, apart from closing an issue.
