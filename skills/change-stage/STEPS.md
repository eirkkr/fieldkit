# The reviewer's answer at the steps stop

Reached from [SKILL.md](SKILL.md) step 2, state 3: the stage's steps are written and re-read, `Steps ready` is posted on the stage's issue, and the reviewer has not yet said to build. Forms are in `conventions/specs.md`, under the headings named. The reviewer's answer is one of four, or none of them: a message that is none says the stage is waiting for their word, and stops.

A message that only started the run (`/change-stage <n>`) and an answer to "resume this stage?" are not the word to build. Nor is "carry on", which is the word to start a stage. A message that says to build this stage's steps (`build it`, `yes, build`) is, even when it started the run.

An ending or a word to build that comes in the same message as changes to the steps or a step review is posted after the last `Steps ready` this run posts, so a new `Steps ready` never voids it. The changes or the review's fix then suggest nothing. With the word to build in the same message as changes to the steps, make the changes, post `Steps ready`, post the word, then build. With a step review in it, run the review and do not post the word: the reviewer has not seen the findings, so the word comes in their next message.

## A step review

A *fresh* agent is a subagent given only what is listed here, nothing from this conversation.

1. Run it at the agent and effort proposed or the reviewer's change ("Sizing a suggestion" in `GATE.md`). Give it the stage's steps, the brief, the notes, `conventions/specs.md` and the repository, and ask for (or run the skill the reviewer named):
   - each `Done when` that running or looking at something could not check;
   - each step that breaks the stage rules ("Stages" and "A stage's issue");
   - anything a builder from the steps alone would have to guess.
2. Reproduce each finding, then triage it: fix it by editing `## Steps`; edit it into the later stage that will handle it, with a comment there saying so; or list it as an issue to file.
3. Comment the findings and outcomes on the stage's issue as `## Review findings` ("Review"), `No findings.` when there are none. A round that fixed anything then comments what changed and posts `Steps ready` again, which voids older approvals and older `at steps` endings ("A stage's issue").
4. Show the reviewer each finding with its outcome. Look for an `at steps` ending newer than the newest `Steps ready` ("What is said at a gate"): one governs, so suggest nothing. Otherwise close the stop as "Review", "When it is offered" says: a fix is worth a suggested review, named with its size, reason, agent and effort ("Sizing a suggestion" in `GATE.md`), or say in one line that none is. Say what has not been reviewed. Stop.

Done when every finding has one of those outcomes and the round has its comment.

## A decline

The reviewer declines the suggested review of the steps, or says no more is needed.

1. Comment on the stage's issue `Review ended by the reviewer at steps (declined).` or `Review ended by the reviewer at steps (no more needed).`, with the choice of text "What is said at a gate" gives.
2. Suggest no review. Say what has not been reviewed, and stop.

## The word to build

Any clear yes to building, as above.

1. Comment on the stage's issue `Steps approved to build by @<login>.`, the login being the author of the change's `Plan approved.` comment.
2. Put the session on the stage's branch as `SKILL.md` step 2, state 2 says, then go to step 5, matching the step numbers in `git log` subjects against the steps as state 1 does. Steps renumbered since the commits were made (a commit's step number names a step whose text differs from the commit's subject): tell the reviewer, and stop.

Suggest no review. A decline, if the same message made one, was posted first, after the last `Steps ready`.

## Changes to the steps

1. Edit `## Steps` in the stage's issue.
2. Comment what changed and why.
3. Post `Steps ready` again, which voids older approvals and older `at steps` endings.
4. Close the stop with a suggested review of the steps, sized as above, or one line saying none is worth running; an `at steps` ending posted after this `Steps ready` governs and suggests nothing. Say what has not been reviewed. Stop, unless the message also gave the word to build: then post it and build (the opening paragraph).
