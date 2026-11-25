# The reviewer's answer at a gate

Reached from [SKILL.md](SKILL.md) when a stage is at its gate and the reviewer has answered. Forms are in `conventions/specs.md`, under the headings named.

Find the stage's PR first - `gh pr list --head <branch>`, the branch being the one its steps name - and put the session on it: by the "On yes" procedure of `SKILL.md`'s "Stage assigned, no open PR" line (skip its question and its step 5). Done when the PR found closes this stage's issue.

## A review asked for

A *fresh* agent is a subagent given only what is listed here, nothing from this conversation.

1. Run what the reviewer asked for: the skills they named, else the axes of "Review" they chose, each as a fresh agent, in parallel, at the agent and effort proposed or the reviewer's change ("Sizing a suggestion").
   - **Conventions.** Give it `git diff origin/<default>...HEAD` and the repo's convention docs. It reports each place the diff breaks one, and each thing a person will read that is not in plain words.
   - **Requirements.** Give it the same diff, the stage's steps and the brief's requirements. It reports each requirement the stage claims and misses, each with no test behind it, and each thing built that none asked for.
2. Reproduce each finding, then triage: fix it here as a commit; edit it into the later stage that will handle it, with a comment there saying so; or list it as an issue to file.
3. Comment the findings and outcomes on the PR as `## Review findings` ("Review"), `No findings.` when there are none, so every round leaves its comment; rewrite the Review line from the comments ("The PR body").
4. `gh pr checks --watch`. Show the reviewer the findings and outcomes, then close the stop as "Review", "When it is offered" says, looking for the newest ending comment on the PR ("What is said at a gate"): a fix made here is what a suggested review would read, named with its size, reason, agent and effort ("Sizing a suggestion"). Stop.

Done when every finding has one of those three outcomes, the round has its comment and the full check passes.

## Sent back

Any answer asking for something to change is this one. An ending that comes with it ("fix X, no more reviews") is recorded first, by "A review ended" steps 1 and 2, and the fix follows. A review asked for in the same message runs after the fix, as "A review asked for".

1. Fix it on the stage's branch, as plain commits.
2. Comment on the PR what was asked and what changed ("What is said at a gate"); bring the PR body up to date, its Review line rewritten from the comments ("The PR body").
3. `gh pr checks --watch`.
4. Show the reviewer what changed, then close the stop as "Review", "When it is offered" says, looking for the newest ending comment on the PR ("What is said at a gate"). A fix of more than wording is worth a suggested review, which reads the fix's diff and is named with its size, reason, agent and effort ("Sizing a suggestion"); a rewording is not. Stop.

## A review ended

The reviewer declines the suggested reviews, or says no more is needed ("Review"). With another ask in the same message, do steps 1 and 2, then that other outcome, and skip step 3: nothing is suggested, and a review the reviewer asked for still runs, as "A review asked for".

1. Comment the ending on the PR, in the form and with the choice of text "What is said at a gate" gives.
2. Rewrite the PR body's Review line from the comments ("The PR body").
3. Suggest no review. Say what has not been reviewed, and stop.

Done when the ending is a comment on the PR and the Review line carries it. A run that dies after step 1 is repaired by the next rewrite of the line, which recounts from the comments.

## Approved

Any clear yes is approval, and the word to merge. An ending that comes with it ("looks good, no review needed") is recorded first, by "A review ended" steps 1 and 2, and the approval then runs as below.

1. Write down what the gate decided ("What is said at a gate"): on the PR; in the brief with its comment if the plan changed; in an ADR committed to the stage's branch if it outlasts the change. Rewrite the PR body's Review line from the comments ("The PR body"), so a run that died after an ending still merges with it recorded.
2. File the issues the reviewer said yes to.
3. Merge through the `merge` skill. Step 1's ADR commit and, for a staged change, the commit that sets **Reviewed at** and ticks the box are the only pushes the approval survives: the approved sha is the head they leave. A fix the reviewer asked for is not one of them.

Change of one pull request: the merge closes the change. Report it, stop.

Change built in stages, carry on:

4. Post the new build notes on the change's issue ("The build notes"): read the newest, carry it forward with what this stage built, post whole.
5. Hide the notes comment before it. Its `id` is in `gh issue view <n> --json comments`:

   ```sh
   gh api graphql -f id=<comment id> -f query='mutation($id:ID!){minimizeComment(input:{subjectId:$id,classifier:OUTDATED}){minimizedComment{isMinimized}}}'
   ```

6. Report the stage has merged. Something under the brief's Not yet specified can now be said in a line: propose it as a stage; on the reviewer's yes, add it to the brief with its comment and create its sub-issue.
7. That was the last stage: offer the final review ("The final review") with its size, agent and effort ("Sizing a suggestion"), ask whether to close the change.

Then stop, unless the approval also asked for the next stage: then start again at SKILL.md, step 1.

## Sizing a suggestion

Applies to every stop that suggests a review (a plan published, the steps written, a PR at its gate, a fix made, the final review's offer), not only to an answer at a gate. A suggestion names the review, its size, its reason, and the agent and effort proposed, so the reviewer can change either before it runs. A review the reviewer asks for that no suggestion proposed is sized the same way.

**The size.** Count a first review of a plan over the brief and the notes, of steps over the steps, of a PR over its diff, and of the final review over the diffs it reads, summed. Count a later review over the lines changed since the last one. Then:

- *Small*: at most 50 changed lines, at most two requirements, and no choices beyond a rename or a rewording.
- *Large*: over 300 changed lines, or five or more requirements, or three or more files that change what an agent does.
- *Medium*: anything else.

Where the signals disagree, the larger size wins.

**The agent and effort.**

| Size | Agent | Effort |
| --- | --- | --- |
| Small | Sonnet | medium |
| Medium | Opus | medium |
| Large | Opus | high |

A review run through a skill names the skill and the effort it is run at. A skill that takes no effort of its own is run by a subagent of the size's model, dispatched at that effort. A review's parallel axes count as one review, each run at the size's agent and effort. The reviewer may change the agent or the effort before the review runs.

`xhigh`, `max` and `code-review ultra` are proposed only when the reviewer asks for them.
