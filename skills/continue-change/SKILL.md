---
name: continue-change
description: Resume a task-list-driven change (an OpenSpec change, or any tasks.md/checklist-style plan) - work the next task group, push incrementally, and end with a handoff summary the next session can pick up cold
argument-hint: "[change-name]"
---

# Resume a change, leaving a clean handoff

Pick up an in-progress change and work it forward, structured so the
session can be `/clear`'d at any point without losing state - the next
session re-runs this same skill and continues from the handoff summary.

## Select the change

If `$ARGUMENTS` names a change, use it. Otherwise infer from conversation
context; if that's ambiguous, list candidates and ask.

In an OpenSpec repo (`openspec/` present), prefer `openspec status --change
"<name>" --json` to find its `tasks.md` and read progress; `openspec list
--json` enumerates active changes. Without OpenSpec, find the change's own
plan/checklist file (`tasks.md`, `TODO.md`, or whatever the repo uses) and
read progress from its `- [ ]`/`- [x]` boxes directly.

Read the change's own docs (proposal/design/spec, or equivalent) if this
session hasn't seen them yet - don't re-derive settled decisions from the
diff.

## Work the next group

Take the next unchecked group of tasks (not just the next single task) as
one unit of work: implement it, then check off every task in it. Don't
jump ahead to a later group before the current one is checked off.

## Push incrementally

Commit and push at each group boundary (via this kit's `push` skill, or by
hand following `conventions/git.md`), not only at the very end. A session
that gets cut off mid-change should still leave pushed, working state -
the next session resumes from the branch, not from a lost local diff.

## Hand off

Stop at a natural boundary: a group finishes, context runs low, the user
asks, or a task turns out to need a decision only they can make. On
stopping, always close with a handoff summary in this shape, so a fresh
session (with none of this one's context) can continue immediately:

```text
Groups completed: <ids/names>, next up: <id/name>
Branch: <branch> (pushed, commit <sha>)

Judgement calls / surprises worth knowing: <anything decided without
asking, anything that turned out to be a no-op or diverged from the plan>

Anything the next session should watch out for: <open questions,
known follow-ups>
```

Keep it terse and concrete - file paths, task numbers, commit SHAs - not
prose a reader has to decode. This is the only continuity between
sessions; write it for someone who wasn't here.
