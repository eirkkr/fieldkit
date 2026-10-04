# The reviewer's answer to a plan

Reached from [SKILL.md](SKILL.md) once a plan is published and the reviewer has answered. Forms are in `conventions/specs.md`, under the headings named.

Find the plan first: the issue named, else the open `change` issue with no approval comment (`gh issue list --label change --state open`). With several, ask.

## Changes asked for

Any answer short of approval with no conditions is this one.

1. Edit the brief, and comment on the issue what changed and why.
2. If the contracts or assumptions moved, post the notes again, whole, and hide the one before.
3. If a requirement or a stage changed, run the fresh review again (SKILL.md, step 4).
4. Show the reviewer the brief again, and stop.

## Approved

1. Comment the approval line ("Asking first, and approval"), the login being the reviewer's: `gh api user -q .login`.
2. Create each stage the brief lists, in order, as a sub-issue (`gh issue create --parent <n>`), titled and filled as "A stage's issue" gives it. A change of one stage gets its one.
3. Mark a stage blocked (`gh issue edit <stage> --add-blocked-by <other>`) where it cannot be built without the other.
4. Report the stages created.

Then stop, unless the approval also asked for the first stage: then start the `change-stage` skill.

## Turned down

Close the issue as not planned, with a comment saying why, on the reviewer's word to close it.
