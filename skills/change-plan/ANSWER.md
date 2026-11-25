# The reviewer's answer to a plan

Reached from [SKILL.md](SKILL.md) once a plan is published and the reviewer has answered. Forms are in `conventions/specs.md`, under the headings named.

Find the plan first: the issue named, else the open `change` issue with no approval comment (`gh issue list --label change --state open`). Several: ask.

## A review asked for

A *fresh* agent is a subagent given only what is listed here, nothing from this conversation.

1. Dispatch a fresh agent with the brief, the notes and `conventions/specs.md`, or run the skill the reviewer named, at the agent and effort proposed or the reviewer's change ("Sizing a suggestion" in `skills/change-stage/GATE.md`). Ask it:
   - Can a test hold each requirement as written?
   - Does each stage meet the stage rules, and deliver what its line says?
   - What would an agent building from these alone have to guess?
   - What does the brief contradict: itself, the notes, the repo's ADRs?
2. Triage each finding against the repo: fix the brief or notes, or record why the finding is wrong. Where the brief or notes were edited, comment on the issue what changed and why, as "Changes asked for" step 1 does.
3. Post the round's findings and outcomes on the issue as `## Review findings` ("Review"), `No findings.` when there are none, so every round leaves its comment. Show the reviewer each finding with its outcome. Then close the stop as "Review", "When it is offered" says, looking for the newest ending comment on the issue ("What is said at a gate"): what a suggested review would read is what changed, the brief or the notes alone, with the comment saying what changed, named with its size, reason, agent and effort ("Sizing a suggestion" in `skills/change-stage/GATE.md`). Stop.

## Changes asked for

An ending that comes with the change ("change X, no more reviews") is posted first, by "A review ended" step 1, then step 1 here.

1. Edit the brief; comment on the issue what changed and why.
2. Contracts or assumptions moved: post the notes again, whole, and hide the one before.
3. Show the reviewer the brief again, then close the stop as "Review", "When it is offered" says, looking for the newest ending comment on the issue ("What is said at a gate"). A changed requirement or stage is worth a suggested review of the edited brief and the comment saying what changed, named with its size, reason, agent and effort ("Sizing a suggestion" in `skills/change-stage/GATE.md`); anything less is not. Stop.

## A review ended

The reviewer declines the suggested reviews, or says no more is needed ("Review"). With another ask in the same message, do step 1, then that other outcome, and skip step 2: nothing is suggested, and a review the reviewer asked for still runs, as "A review asked for".

1. Comment the ending on the issue, in the `at plan` form and with the choice of text "What is said at a gate" gives.
2. Suggest no review. Say what has not been reviewed, and stop.

## Approved

Any clear yes is approval. An ending that comes with it ("looks good, no review needed") is posted first, by "A review ended" step 1, and the approval then runs as below.

1. Run the permission check ("Asking first, and approval") on your own login (`gh api user -q .login`):
   - `admin`: comment the approval line, naming that login.
   - Else: give the reviewer that section's command, `<n>` filled in, and stop. Steps 2-3 run once that comment exists, on the reviewer's word to continue.
2. Brief lists stages and no sub-issues exist yet: create each in order as a sub-issue (`gh issue create --parent <n>`), titled and filled as "A stage's issue" gives it; mark one blocked (`gh issue edit <stage> --add-blocked-by <other>`) where it cannot be built without the other. A change of one pull request gets none.
3. Report what was created.

Then stop, unless the approval also asked for the build: then start the `change-stage` skill.

## Turned down

On the reviewer's word to close it: close the issue as not planned, with a comment saying why. Close any stage sub-issues as not planned too.
