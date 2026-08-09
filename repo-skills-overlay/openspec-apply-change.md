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
- Write the review note into `tasks.md`, indented under the gate's checkbox,
  before reporting. Then show the same note in your reply.
- Stop and wait.

The note covers, in order: **what changed** since the previous gate, per file
or behaviour; **departures from the plan** and why ("none" if none); **how to
verify**, as exact commands plus any manual step; **look closely at**, naming
the judgement calls and what you are least sure of; and **not done yet**, the
known gaps later stages cover. Complete, not long.

If the reviewer sends the stage back, fix it within that stage and rewrite
the note. Do not open the next stage to carry the fix.

The final stage is the whole-change review. Its closing task stops the same
way, except that it iterates: present the change, take feedback, revise,
present again, until the reviewer says they are satisfied. Only then is the
change complete, and only then may it be archived.

`openspec instructions apply --change "<name>" --json` returns the schema's
own statement of these rules in its instruction field. Follow it; this
section exists because the generated steps above were written for a schema
without gates.
