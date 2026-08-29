## Review gates (kit overlay - overrides the above)

Where this section and anything above it disagree, this section wins.

The `review-gated` schema ends every stage with a review gate: a task whose
text contains `REVIEW GATE`. The guardrail above - "keep going through tasks
until done or blocked" - does **not** apply across one. A gate is a full
stop, and reaching it is a successful outcome, not an interruption.

At a review gate:

- Do NOT tick the gate's checkbox. Only the human closes it.
- Do NOT start the next stage, however small its first task looks.
- Confirm the stage is green first (run the repo's test command). A gate
  reached on a red tree is not reached.
- Commit each task on its own as you go, with the task number in the
  subject. The gate's note links those commits so the stage can be walked
  task by task.
- Open a PR for the stage's branch - every gate, not just the first, and not
  a draft. The stage is one branch and one PR, so opening it is part of
  reaching the gate and needs no approval.
- Write the review note into `tasks.md`, indented under the gate's checkbox,
  before reporting. Then show the same note in your reply.
- Stop and wait.

The note covers, in order: **review this stage**, the PR's file view
(`/pull/<n>/files`) and `git diff <default-branch>...HEAD`, both written out,
followed by one line per task giving its number, subject and commit URL - the
PR holds exactly this stage, so there is no range to assemble and no base
commit to carry; at a first gate also `Change based at <commit>`, from
`git merge-base <default-branch> HEAD`, carried forward unchanged in every
later note because the final review needs it; **what changed**
since the previous gate, per file or behaviour; **departures from the plan**
and why ("none" if none); **how to verify**, as exact commands plus any
manual step; **look closely at**, naming the judgement calls and what you are
least sure of; **not done yet**, the known gaps later stages cover; and
**reviewed at**, left marked awaiting approval. Complete, not long.

If the reviewer sends the stage back, fix it within that stage and rewrite
the note. Do not open the next stage to carry the fix. The links do not need
rewriting - both ends stay valid as fixes land.

When the reviewer approves, record `git rev-parse --short HEAD` under
**Reviewed at**, tick the box, and merge the PR. That commit is the record of
the tree they signed off, kept because the squash-merge discards the branch
holding it. The next stage then starts on a fresh branch cut from the default
branch - never continued on the merged one, and never stacked on a branch
still under review.

The final stage is the whole-change review. Its closing task stops the same
way, except that it iterates: present the change, take feedback, revise,
present again, until the reviewer says they are satisfied. Only then is the
change complete. Its gate then closes and merges like any other stage's;
archiving follows in a PR of its own, cut from the default branch.

Its note opens with two diffs: this stage's own PR, exactly as any stage's
note gives it, then the whole change from the `Change based at` commit -
mostly already merged, so `git log --oneline <base>..<default-branch>` and
`git diff <base>...<default-branch>` rather than a PR view, naming the base
commit and the merged stages' PR numbers. The
stage walks the diff *before* correcting the artifacts, since the walk turns
up artifact-shaped findings; reconciles code against the artifacts in three
directions - unmet, unasked-for, and met only by construction; and re-reads
every issue the change references for still open, still about the thing
cited.

`openspec instructions apply --change "<name>" --json` returns the schema's
own statement of these rules in its instruction field. Follow it; this
section exists because the generated steps above were written for a schema
without gates.
