# The reviewer's answer to a plan

Reached from [SKILL.md](SKILL.md) once a plan is published and the reviewer has answered. Forms are in `conventions/specs.md`, under the headings named.

Find the plan first: the issue named, else the open `change` issue with no approval comment (`gh issue list --label change --state open`). Several: ask.

## A review asked for

A *fresh* agent is a subagent given only what is listed here, nothing from this conversation.

1. Dispatch a fresh agent with the brief, the notes and `conventions/specs.md`, or run the skill the reviewer named. Ask it:
   - Can a test hold each requirement as written?
   - Does each stage meet the stage rules, and deliver what its line says?
   - What would an agent building from these alone have to guess?
   - What does the brief contradict: itself, the notes, the repo's ADRs?
2. Triage each finding against the repo: fix the brief or notes, or record why the finding is wrong. Where the brief or notes were edited, comment on the issue what changed and why, as "Changes asked for" step 1 does.
3. Post the round's findings and outcomes on the issue as `## Review findings` ("Review"), `No findings.` when there are none, so every round leaves its comment. Show the reviewer each finding with its outcome. Then look for the newest ending comment on the issue from an `OWNER`, `MEMBER` or `COLLABORATOR` author ("What is said at a gate"). One exists: suggest no review, and say what has not been reviewed. None, and something was fixed: suggest a review of what changed (the brief, or the notes alone) with the comment saying what changed, or say none is worth running. None, and nothing was fixed: say there is nothing to review. Stop.

## Changes asked for

1. Edit the brief; comment on the issue what changed and why.
2. Contracts or assumptions moved: post the notes again, whole, and hide the one before.
3. Show the reviewer the brief again. Then look for the newest ending comment, as "A review asked for" step 3 says. One exists: suggest no review, and say what has not been reviewed. None, and a requirement or stage changed: suggest a review of the edited brief and the comment saying what changed, with the reason, or say none is worth running. None, and nothing of that kind changed: say none is worth running. Stop.

An ending that comes with the change ("change X, no more reviews") is posted first, as "A review ended" says, then step 1 onward.

## A review ended

The reviewer declines the suggested reviews, or says no more is needed ("Review"). Alone, or with another ask: post the ending first, then do what else was asked, as that outcome says, and suggest no review.

1. Comment on the issue in the form "What is said at a gate" gives, `at plan`: `(declined)` for a no to suggestions, `(no more needed)` for word that enough has run; where the word does not say which, `(declined)` if no round has run (no `## Review findings` comment from a writer), else `(no more needed)`.
2. Say what has not been reviewed, and stop.

## Approved

Any clear yes is approval. An ending that comes with it ("looks good, no review needed") is posted first, as "A review ended" step 1 says, and the approval then runs as below.

1. Run the permission check ("Asking first, and approval") on your own login (`gh api user -q .login`):
   - `admin`: comment the approval line, naming that login.
   - Else: give the reviewer that section's command, `<n>` filled in, and stop. Steps 2-3 run once that comment exists, on the reviewer's word to continue.
2. Brief lists stages and no sub-issues exist yet: create each in order as a sub-issue (`gh issue create --parent <n>`), titled and filled as "A stage's issue" gives it; mark one blocked (`gh issue edit <stage> --add-blocked-by <other>`) where it cannot be built without the other. A change of one pull request gets none.
3. Report what was created.

Then stop, unless the approval also asked for the build: then start the `change-stage` skill.

## Turned down

On the reviewer's word to close it: close the issue as not planned, with a comment saying why. Close any stage sub-issues as not planned too.
