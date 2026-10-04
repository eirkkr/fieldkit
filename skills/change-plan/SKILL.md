---
name: change-plan
description: Plan a change - work too big for one pull request, or that leaves the reviewer a decision - or act on the reviewer's answer to a plan.
argument-hint: "[what the change is, or the issue that asks for it]"
---

# Plan a change

The form of everything written here is in `conventions/specs.md`, under the heading each step names. `$ARGUMENTS`, if given, is what the change is about.

When the reviewer has answered a plan already published, go to [ANSWER.md](ANSWER.md).

## 1. Test that it is a change

Apply "When work is a change".

Done when the reviewer has been told which test the work meets - or that it meets none, in which case it is a branch and a PR, and this skill ends.

## 2. Ask

List what only the reviewer can decide, and `gh issue list --label change --state open` for a change this one overlaps or waits on. Ask one question at a time, each with the answer you would pick. A skill named for the questions - in the conversation, else under `## Change skills` in the repo's `CLAUDE.md` - asks in your place.

Done when every question has the reviewer's answer, or their word that it stays open.

## 3. Draft

Write the brief ("The brief") for the reviewer, in plain words, and the first build notes ("The build notes") for the next agent. Run the plan past "What a plan tends to miss".

- A change that fits one pull request says so under Stages, and has no stage lines.
- An existing issue that asks for the change stays as it is. The brief names it.
- Both are published as written: every line reads to someone who never saw this conversation.

Done when every section of the brief is filled or says it is empty, every requirement is delivered by a stage or named as not yet specified, and everything but the requirements fits one screen.

## 4. Publish, and stop

1. File the issue with the `change` label, creating the label if the repo lacks it, and `--blocked-by <n>` for a change it waits on.
2. Post the notes as its first comment.
3. Show the reviewer the brief as published and the issue's URL.
4. Say the plan has not been reviewed, and offer a review ("Review"): name it with the reason it is worth running here, or say why it is not.

Then stop. The reviewer's answer is the next step, and [ANSWER.md](ANSWER.md) handles it.
