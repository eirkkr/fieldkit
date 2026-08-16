---
name: openspec-apply-change
description: Implement tasks from an OpenSpec change. Use when the user wants to start implementing, continue implementation, or work through tasks.
allowed-tools: Bash(openspec:*)
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.6.0"
---

Implement tasks from an OpenSpec change.

**Store selection:** If the user names a store (a store is a standalone OpenSpec repo registered on this machine) or the work lives in one, run `openspec store list --json` to discover registered store ids, then pass `--store <id>` on the commands that read or write specs and changes (`new change`, `status`, `instructions`, `list`, `show`, `validate`, `archive`, `doctor`, `context`). Other commands do not take the flag. Hints printed by commands already carry the flag; keep it on follow-ups. Without a store, commands act on the nearest local `openspec/` root.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, run `openspec list --json` to get available changes and use the **AskUserQuestion tool** to let the user select

   Always announce: "Using change: <name>" and how to override (e.g., `/opsx:apply <other>`).

2. **Check status to understand the schema**
   ```bash
   openspec status --change "<name>" --json
   ```
   Parse the JSON to understand:
   - `schemaName`: The workflow being used (e.g., "spec-driven")
   - `planningHome`, `changeRoot`, and `actionContext`: planning scope and edit constraints
   - Which artifact contains the tasks (typically "tasks" for spec-driven, check status for others)

3. **Get apply instructions**

   ```bash
   openspec instructions apply --change "<name>" --json
   ```

   This returns:
   - `contextFiles`: artifact ID -> array of concrete file paths (varies by schema - could be proposal/specs/design/tasks or spec/tests/implementation/docs)
   - Progress (total, complete, remaining)
   - Task list with status
   - Dynamic instruction based on current state

   **Handle states:**
   - If `state: "blocked"` (missing artifacts): show message, suggest using openspec-continue-change
   - If `state: "all_done"`: congratulate, suggest archive
   - Otherwise: proceed to implementation

4. **Read context files**

   Read every file path listed under `contextFiles` from the apply instructions output.
   The files depend on the schema being used:
   - **spec-driven**: proposal, specs, design, tasks
   - Other schemas: follow the contextFiles from CLI output

5. **Show current progress**

   Display:
   - Schema being used
   - Progress: "N/M tasks complete"
   - Remaining tasks overview
   - Dynamic instruction from CLI

6. **Implement tasks (loop until done or blocked)**

   For each pending task:
   - Show which task is being worked on
   - Make the code changes required
   - Keep changes minimal and focused
   - Mark task complete in the tasks file: `- [ ]` → `- [x]`
   - Continue to next task

   **Pause if:**
   - Task is unclear → ask for clarification
   - Implementation reveals a design issue → suggest updating artifacts
   - Error or blocker encountered → report and wait for guidance
   - User interrupts

7. **On completion or pause, show status**

   Display:
   - Tasks completed this session
   - Overall progress: "N/M tasks complete"
   - If all done: suggest archive
   - If paused: explain why and wait for guidance

**Output During Implementation**

```
## Implementing: <change-name> (schema: <schema-name>)

Working on task 3/7: <task description>
[...implementation happening...]
✓ Task complete

Working on task 4/7: <task description>
[...implementation happening...]
✓ Task complete
```

**Output On Completion**

```
## Implementation Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 7/7 tasks complete ✓

### Completed This Session
- [x] Task 1
- [x] Task 2
...

All tasks complete! Ready to archive this change.
```

**Output On Pause (Issue Encountered)**

```
## Implementation Paused

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 4/7 tasks complete

### Issue Encountered
<description of the issue>

**Options:**
1. <option 1>
2. <option 2>
3. Other approach

What would you like to do?
```

**Guardrails**
- Keep going through tasks until done or blocked
- Always read context files before starting (from the apply instructions output)
- If task is ambiguous, pause and ask before implementing
- If implementation reveals issues, pause and suggest artifact updates
- Keep code changes minimal and scoped to each task
- Update task checkbox immediately after completing each task
- Pause on errors, blockers, or unclear requirements - don't guess
- Use contextFiles from CLI output, don't assume specific file names

**Fluid Workflow Integration**

This skill supports the "actions on a change" model:

- **Can be invoked anytime**: Before all artifacts are done (if tasks exist), after partial implementation, interleaved with other actions
- **Allows artifact updates**: If implementation reveals design issues, suggest updating artifacts - not phase-locked, work fluidly

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
- At a change's first gate, open a draft PR for the branch if none is open.
  It is the surface the note points at, and a draft asks nothing of anyone.
- Write the review note into `tasks.md`, indented under the gate's checkbox,
  before reporting. Then show the same note in your reply.
- Stop and wait.

The note covers, in order: **review this stage**, the PR's file view
(`/pull/<n>/files/<base>..HEAD`) and `git diff <base>..HEAD`, both written
out, where `<base>` is the previous gate's recorded commit; **what changed**
since the previous gate, per file or behaviour; **departures from the plan**
and why ("none" if none); **how to verify**, as exact commands plus any
manual step; **look closely at**, naming the judgement calls and what you are
least sure of; **not done yet**, the known gaps later stages cover; and
**reviewed at**, left marked awaiting approval. Complete, not long.

If the reviewer sends the stage back, fix it within that stage and rewrite
the note. Do not open the next stage to carry the fix. The links do not need
rewriting - both ends stay valid as fixes land.

When the reviewer approves, record `git rev-parse --short HEAD` under
**Reviewed at** and only then tick the box. That commit is the base the next
gate's links run from.

The final stage is the whole-change review. Its closing task stops the same
way, except that it iterates: present the change, take feedback, revise,
present again, until the reviewer says they are satisfied. Only then is the
change complete, and only then may it be archived. Once they are satisfied,
take the PR out of draft and bring its description up to the finished change.

`openspec instructions apply --change "<name>" --json` returns the schema's
own statement of these rules in its instruction field. Follow it; this
section exists because the generated steps above were written for a schema
without gates.
