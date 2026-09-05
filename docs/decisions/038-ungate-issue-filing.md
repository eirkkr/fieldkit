# 038 - Make filing and editing issues act-then-show, not gated

## Decision

Filing an issue, commenting on one, and editing either drop out of the
approval-gated list. The agent files the issue or comment, then surfaces what
it filed so the wording can be corrected. `KIT.md`'s Always-on section and
`conventions/github.md` are updated to match, and `skills/kit-reconcile`'s
codebase-follow-up step files its issues instead of listing them and asking.

Closing an issue stays gated - it ends a thread someone may still be relying
on. Opening a PR and merging keep the gates
[031](031-regate-pr-and-merge-invocation.md) put back on them.

This amends [008](008-outward-irreversible.md), which established the
issue/comment gate, and resolves the note in
[029](029-ungate-pr-body-edits.md) that left it untouched.

## Reason

Every neighbouring action has already moved this way - committing and pushing
([008](008-outward-irreversible.md)), creating a branch, and revising an open
PR's description ([029](029-ungate-pr-body-edits.md)) - on the reasoning that
they are cheap to amend or discard. An issue belongs with them: it is
editable, closable and deletable by whoever owns the repo, so a wrong one
costs a moment's cleanup rather than anything irreversible.

The gate also did not buy what it looked like it bought. Approving a drafted
issue approves prose, not the decision; the decision was made earlier, when
the finding was surfaced and discussed. By the time a draft is shown, the
judgment about whether the issue should exist is already done, so the approval
step measures wording that could be edited afterwards anyway - at the cost of
a round trip per issue, at the moment the context is freshest.

Alternatives rejected:

- **Keep the gate for issues in repos with outside readers.** The audience
  argument is what 008 gated on, but it does not survive the amendability
  point: an issue read by someone else is still corrected in place, and the
  agent has no clean signal for which repos qualify.
- **Ungate closing too.** Closing is the one issue action that isn't a
  correction away from harmless - it silently ends a thread for everyone
  watching it.

## Consequences

- `KIT.md`'s outward/irreversible clause no longer names issues and comments;
  it names closing an issue, and a new bullet states the act-then-show rule
  for filing, commenting and editing.
- `conventions/github.md`'s "Show a draft and wait for approval ... confirm
  first" line is replaced with the act-then-show model, carrying the close
  exception.
- The close gate doesn't reach the automatic close a merge performs: a PR
  body carrying `Closes #X` closes `X` on merge, and merging is already
  gated in its own right, so nothing is confirmed twice.
- Duplicate-checking (`gh issue list --search`) becomes more load-bearing:
  with no human reading the draft first, that search is the only thing
  standing between a fresh finding and a redundant issue.
- Issues filed in a repo we don't own are unaffected by this ADR. A
  third-party repo's AI policy still has to be checked before anything is
  filed there; that gate is tracked separately and is not ungated here.

> Amended by [042](042-regate-issue-filing.md): filing an issue is gated
> again when the user did not ask for one, on 031's terms - the gate is on
> whether to file, not on the draft. The ungating this ADR gave commenting
> and editing stands, and so does its argument that the wording does not
> need approving; what did not survive is the claim that the decision to
> file had already been made by the time a draft existed.
