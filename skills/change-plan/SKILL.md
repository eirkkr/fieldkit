---
name: change-plan
description: Plan a change - work too big for one pull request, or that leaves the reviewer a decision - or act on the reviewer's answer to a plan.
argument-hint: "[what the change is, or the issue that asks for it]"
---

# Plan a change

Forms for everything written here are in `conventions/specs.md`, under the heading each step names. `$ARGUMENTS`, if given, is what the change is about.

Reviewer has answered an already-published plan: go to [ANSWER.md](ANSWER.md).

## 1. Test that it is a change

Apply "When work is a change".

Done when the reviewer has been told which test the work meets, or that it meets none: then it is a branch and a PR, and this skill ends.

## 2. Ask

List what only the reviewer can decide, including (for a large, hard-to-undo change) whether to price it to decide whether to do it at all ("Planning to decide"). Run `gh issue list --label change --state open` for a change this one overlaps or waits on. Ask one question at a time, each with the answer you would pick, through the harness's question tool where it has one (choices as options, yours first, marked recommended). A skill named for the questions, in the conversation or else under `## Reviews` in the repo's `CLAUDE.md` (or the doc it points to), asks in your place, still one at a time.

Done when every question has the reviewer's answer, or their word that it stays open.

## 3. Draft

Write the brief ("The brief") for the reviewer, in plain words, and the first build notes ("The build notes") for the next agent. Run the plan past "What a plan tends to miss".

- A change fitting one pull request says so under Stages, no stage lines.
- A plan priced to decide ("Planning to decide") also has every stage's steps, as "A stage's issue" gives them, ready for its sub-issues.
- An existing issue asking for the change stays as is; the brief names it.
- Both published as written, every line readable by someone who never saw this conversation.

Done when every section of the brief is filled or says it is empty, every requirement is delivered by a stage or named as not yet specified, everything but the requirements fits one screen, and, for a plan priced to decide, every stage has its steps, each with a `Done when`.

## 4. Publish, and stop

1. File the issue with the `change` label (create the label if the repo lacks it), and `--blocked-by <n>` for a change it waits on.
2. Post the notes as its first comment.
3. Plan priced to decide: create each stage in order as a sub-issue (`gh issue create --parent <n>`), titled and filled as "A stage's issue" gives it, with its steps; mark one blocked (`gh issue edit <stage> --add-blocked-by <other>`) where it cannot be built without the other.
4. Show the reviewer the brief as published and the issue's URL.
5. Say the plan has not been reviewed; offer a review ("Review"): name it with the reason it is worth running here, or say why it is not.

Then stop. The reviewer's answer is the next step; [ANSWER.md](ANSWER.md) handles it.
