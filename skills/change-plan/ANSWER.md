# The reviewer's answer to a plan

Reached from [SKILL.md](SKILL.md) once a plan is published and the reviewer has answered. Forms are in `conventions/specs.md`, under the headings named.

Find the plan first: the issue named, else the open `change` issue with no approval comment (`gh issue list --label change --state open`). With several, ask.

## A review asked for

A *fresh* agent is a subagent given only what is listed here, and nothing from this conversation.

1. Dispatch a fresh agent with the brief, the notes and `conventions/specs.md`, or run the skill the reviewer named. Ask it:
   - Can a test hold each requirement as written?
   - Does each stage meet the stage rules, and deliver what its line says?
   - What would an agent building from these alone have to guess?
   - What does the brief contradict - in itself, in the notes, or in the repo's ADRs?
2. Triage each finding against the repo: fix the brief or the notes, or record why the finding is wrong.
3. Show the reviewer each finding with its outcome, and stop.

## Changes asked for

1. Edit the brief, and comment on the issue what changed and why.
2. If the contracts or assumptions moved, post the notes again, whole, and hide the one before.
3. Show the reviewer the brief again, offer a review if a requirement or a stage changed, and stop.

## Approved

Any clear yes is approval.

1. Comment the approval line ("Asking first, and approval"), the login being the reviewer's: `gh api user -q .login`.
2. Where the brief lists stages, create each in order as a sub-issue (`gh issue create --parent <n>`), titled and filled as "A stage's issue" gives it, and mark one blocked (`gh issue edit <stage> --add-blocked-by <other>`) where it cannot be built without the other. A change of one pull request gets none.
3. Report what was created.

Then stop, unless the approval also asked for the build: then start the `change-stage` skill.

## Turned down

Close the issue as not planned, with a comment saying why, on the reviewer's word to close it.
