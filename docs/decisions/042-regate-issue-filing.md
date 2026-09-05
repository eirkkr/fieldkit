# 042 - Re-gate filing an issue, unless the user asked for one

## Decision

Filing an issue goes back to being approval-gated, on the same narrow terms
[031](031-regate-pr-and-merge-invocation.md) set for opening a PR: the gate is
on *whether to file at all*, not on the draft. If the user asks for an issue -
"file an issue for that", "raise it" - that request is itself the approval, and
the issue is drafted and filed straight through with nothing shown for review
first. If instead the agent decides mid-task, unprompted, that a finding should
become an issue, it says what it would file and waits for a yes.

Commenting on an issue and editing either an issue or a comment stay
act-then-show, exactly as [038](038-ungate-issue-filing.md) left them. Closing
stays gated. `KIT.md`'s Always-on table splits its issue row accordingly,
`conventions/github.md` restates the rule, and `skills/kit-reconcile`'s
codebase-follow-up step goes back to proposing its issues rather than filing
them.

This amends 038, which ungated filing along with commenting and editing.

## Reason

038 argued that approving a drafted issue approves prose rather than the
decision, because "the decision was made earlier, when the finding was
surfaced and discussed". Acting on it showed that the earlier discussion it
assumed does not happen: a finding and the issue recording it arrive in the
same turn, so the first the human sees of either is a filed issue and a link.
The approval step 038 removed was not measuring wording. It was the only point
at which the human got to say what should happen to a finding.

What that costs is not cleanup - a wrong issue is still cheap to close. It is
that filing settles a question the human wanted open. An issue says "later,
separately, by someone with none of this context"; the alternative is often
"do it now, on this branch, while the context is here", and that alternative
disappears the moment the issue exists. Choosing between them is the human's
call, and it depends on things the agent cannot see: what else is queued, how
much appetite there is for scope today, whether the branch is nearly done.

This is the same correction 031 made for PRs, for the same reason. There, too,
ungating the draft was read as ungating the decision, and the two turned out to
be separable: the draft needs no pre-execution review, but the decision to act
unprompted needs a yes. Issues are the last action in the kit where those two
were still collapsed.

Alternatives rejected:

- **Gate the draft too**, showing the issue text for approval before filing.
  Rejected for the reason 038 gave and 031 upheld: the wording is correctable
  after the fact, and a review round trip per issue costs more than it catches.
  Approval is for whether the issue should exist.
- **Gate commenting and editing as well**, restoring 008's original grouping.
  Rejected - a comment adds to a thread the human already has; it forecloses
  nothing, which is the specific harm this ADR is about.
- **Keep filing ungated but require the alternative to be offered alongside**
  ("filed #N; say the word and I'll do it on this branch instead"). Rejected:
  it still spends the decision first and asks second, and it leaves the issue
  standing in the tracker while the question is reopened.

## Consequences

- `KIT.md`'s Always-on table replaces its combined issue row with two: filing
  is `ask first`, commenting and editing stay `act-then-show`. The existing
  clause about typing `/pr` or `/merge` being its own approval gains the same
  reading for a request to file an issue.
- `conventions/github.md`'s opening bullet splits the same way, keeping the
  close exception and the note that a `Closes #X` merge is already covered.
- Its "out-of-scope work -> file a narrow issue and defer" line becomes a
  choice put to the human rather than an instruction to file, since that line
  is where the foreclosing happens most often.
- `skills/kit-reconcile/SKILL.md` proposes its codebase follow-ups and files
  them on a yes, which is what it did before 038.
- Duplicate-checking (`gh issue list --search`) is no longer the only thing
  standing between a finding and a redundant issue, as 038 noted it had
  become. It stays worth doing before proposing one.
- The gate again relies on the agent distinguishing "the user asked for an
  issue" from "I decided to file one", with no stored state behind it - the
  same limitation 031 recorded for `/pr` and `/merge`, and the same signal
  that it is worth revisiting if it proves unreliable.
