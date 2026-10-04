---
name: change-plan
description: Plan a change as a GitHub issue - questions, brief, build notes, review, approval, stage issues
argument-hint: "[what the change is, or the issue that asks for it]"
---

# Plan a change

Read `conventions/specs.md` first: it says what a change is, and what its brief, build notes and stage issues must contain. This skill is how one gets written. `$ARGUMENTS`, if given, is what the change is about.

Being asked to plan a change is the approval to file its issue. Nothing here builds anything.

## 1. Check it is a change

Apply the three tests in `conventions/specs.md`. If a single PR could be opened for the work now without asking anything, say so and stop - it is ordinary work. Otherwise say which test it met.

## 2. Read before asking

- The code, docs and ADRs in the area, enough to ask questions the repo cannot answer.
- `gh issue list --label change --state open --json number,title` for a change this one overlaps or must wait on.
- The repo's `CLAUDE.md` for a `## Change skills` heading, and the conversation for a skill named for this run.

## 3. Ask

Ask the reviewer what only they can decide, one question at a time, each with the answer you would pick. With a skill named for the questions, invoke it instead. Stop asking when what is left can be settled by reading the code.

## 4. Draft the brief and the first build notes

Write both to the form in `conventions/specs.md`. Keep the two readers apart: the brief is the reviewer's and is in plain words; the notes are the next agent's.

- A decision that would outlast the change is an ADR, written now.
- If the change comes from an existing issue, leave that issue as it is. The brief names it, and the reviewer is asked to close it with the change.
- Both are published as written. Every line is for a reader who never saw this conversation.

## 5. Have the plan reviewed

Dispatch a subagent with no context from this conversation. Give it the draft brief, the draft notes and `conventions/specs.md`, and nothing else. Ask it:

- Can a test hold each requirement as written?
- Does each stage meet the stage rules, and deliver what its line says?
- What would an agent building stage 1 from these alone have to guess?
- What does the brief contradict - in itself, the notes, or the repo's ADRs?

With a skill named for plan review, invoke it as well. Check each finding against the repo before acting on it, and fix the draft.

## 6. Publish, and stop

1. Create the `change` label if the repo lacks it: `gh label list --search change`, then `gh label create change --description "A change planned and built in stages"`.
2. `gh issue create --label change --title "<title>" --body-file <brief>`, with `--blocked-by <n>` for a change it waits on.
3. `gh issue comment <n> --body-file <notes>` - the first build notes.
4. Show the reviewer the brief as published and the issue's URL, and what the plan review found. Then stop and wait.

## 7. On the reviewer's answer

- **Changes asked for:** edit the brief with `gh issue edit <n> --body-file`, comment what changed and why, and stop again.
- **Approved:**
  1. `gh issue comment <n> --body "Plan approved by @$(gh api user -q .login)."`
  2. Create each stage, in order: `gh issue create --parent <n> --title "Stage <k> - <name>" --body-file <stage>`, the body holding the stage's one line and the requirements it delivers.
  3. Mark a stage blocked only where it cannot be built without another: `gh issue edit <stage> --add-blocked-by <other>`.
  4. Report the stages created. Do not start one: approval of a plan is not a request to build it.
- **Turned down:** `gh issue close <n> --reason "not planned" --comment "<why>"`, once the reviewer has said to close it.
