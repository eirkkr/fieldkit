# 042 - Re-gate filing an issue, unless the user asked for one

## Decision

Filing an issue is approval-gated again, on the terms
[031](031-regate-pr-and-merge-invocation.md) set for opening a PR: the gate is
on *whether to file at all*, not on the draft. A request for an issue is
itself the approval and files straight through; an issue the agent decides on
unprompted is described first and filed on a yes.

Commenting and editing stay act-then-show and closing stays gated, as
[038](038-ungate-issue-filing.md) left them. `KIT.md`'s Always-on table splits
its issue row, `conventions/github.md` restates the rule, and
`skills/kit-reconcile` proposes its codebase follow-ups rather than filing
them.

This amends 038.

## Reason

038 argued that approving a drafted issue approves prose rather than the
decision, because "the decision was made earlier, when the finding was
surfaced and discussed". Acting on it showed that earlier discussion does not
happen: a finding and the issue recording it arrive in the same turn, so the
first the human sees of either is a filed issue and a link. The step 038
removed was not measuring wording - it was the only point at which the human
got to say what should happen to a finding.

The cost is not cleanup, since a wrong issue is cheap to close. It is that
filing settles a question the human wanted open. An issue says "later,
separately, by someone with none of this context", where the alternative is
often "do it now, on this branch, while the context is here" - and that
alternative disappears the moment the issue exists. Which one fits depends on
what else is queued and how much appetite there is for scope today, none of
which the agent can see.

This is the correction 031 made for PRs, for the same reason: ungating the
draft was read as ungating the decision, and the two are separable. Issues
were the last action in the kit where they were still collapsed.

Alternatives rejected:

- **Gate the draft too.** Rejected for the reason 038 gave and 031 upheld: the
  wording is correctable afterwards, and a review round trip per issue costs
  more than it catches.
- **Gate commenting and editing as well**, restoring 008's grouping. Rejected
  - a comment adds to a thread the human already has, so it forecloses
  nothing, which is the harm this ADR is about.
- **Keep filing ungated but offer the alternative alongside** ("filed #N; say
  the word and I'll do it on this branch instead"). Rejected: it still spends
  the decision first and asks second, leaving the issue standing while the
  question is reopened.

## Consequences

- `KIT.md`'s Always-on table replaces its combined issue row with two: filing
  is `ask first`, commenting and editing stay `act-then-show`. The clause
  about `/pr` and `/merge` being their own approval reads the same way for a
  request to file an issue.
- `conventions/github.md`'s opening bullet splits the same way, and its
  "out-of-scope work -> file a narrow issue and defer" line becomes a choice
  put to the human - that line is where the foreclosing happens most often.
- `skills/kit-reconcile/SKILL.md` proposes its codebase follow-ups and files
  them on a yes, which is what it did before 038.
- Duplicate-checking (`gh issue list --search`) is no longer the only thing
  standing between a finding and a redundant issue, as 038 noted it had
  become. It stays worth doing before proposing one.
- The gate relies on the agent distinguishing "the user asked for an issue"
  from "I decided to file one", with no stored state behind it - the same
  limitation 031 recorded, and the same signal that it is worth revisiting if
  it proves unreliable.
