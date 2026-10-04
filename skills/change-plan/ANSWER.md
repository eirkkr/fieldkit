# The reviewer's answer to a plan

Reached from [SKILL.md](SKILL.md) once a plan is published and the reviewer has answered. Forms are in `conventions/specs.md`, under the headings named.

## Changes asked for

Edit the brief, comment on the issue what changed and why, show the reviewer the brief again, and stop.

## Approved

1. Comment the approval line ("Asking first, and approval").
2. Create each stage in order as a sub-issue (`gh issue create --parent <n>`), its body as "A stage's issue" gives it.
3. Mark a stage blocked (`gh issue edit <stage> --add-blocked-by <other>`) where it cannot be built without the other.
4. Report the stages created.

Then stop. A stage starts when the reviewer asks for one.

## Turned down

Close the issue as not planned, with a comment saying why, on the reviewer's word to close it.
