## Review gates (kit overlay - overrides the above)

Where this section and anything above it disagree, this section wins.

The `review-gated` schema ends every stage with a review gate: a task whose text contains `REVIEW GATE`. The guardrail above - "keep going through tasks until done or blocked" - does **not** apply across one. A gate is a full stop, and reaching it is a successful outcome, not an interruption.

At a review gate:

- Do NOT tick the gate's checkbox. Only the human closes it.
- Do NOT start the next stage, however small its first task looks.
- Confirm the stage is green first (run the repo's test command). A gate reached on a red tree is not reached.
- Commit each task on its own as you go, with the task number in the subject. The note's record links every commit on the branch so the stage can be walked commit by commit.
- Open a PR for the stage's branch - every gate, not just the first, and not a draft. The stage is one branch and one PR, so opening it is part of reaching the gate and needs no approval.
- Write the review note into `tasks.md`, indented under the gate's checkbox, before reporting. Then show its brief - the brief only - in your reply.
- Stop and wait.

The note's two parts, the brief and the record, are the schema's: step 3's `openspec instructions apply --change "<name>" --json` returns their shape in its instruction field. Write every item of both.

If the reviewer sends the stage back, fix it within that stage and rewrite the note. Do not open the next stage to carry the fix. The links do not need rewriting - both ends stay valid as fixes land.

When the reviewer approves, record `git rev-parse --short HEAD` under **Reviewed at**, tick the box, and merge the PR. That commit is the record of the tree they signed off, kept because the squash-merge discards the branch holding it.

Then stop and report that the stage has merged. Approval is not a request for the next stage: start it only when the human asks, by invoking this skill again or by saying so - in the approval itself ("approved, carry on with stage 3") or later.

The next stage, once asked for, starts on a fresh branch cut from the default branch - never continued on the merged one, and never stacked on a branch still under review.

The final stage is the whole-change review. Its closing task stops the same way, except that it iterates: present the change, take feedback, revise, present again, until the reviewer says they are satisfied. Only then is the change complete. Its gate then closes and merges like any other stage's; archiving follows in a PR of its own, cut from the default branch.

How its note and its tasks differ from an ordinary gate's is in that same instruction, under L3.

That instruction is the schema's own statement of every rule here, and the one place the note is specified. This section repeats only the stops, because the generated steps above were written for a schema without gates.
