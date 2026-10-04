# The reviewer's answer at a gate

Reached from [SKILL.md](SKILL.md) once a stage's PR is open and the reviewer has answered. Forms are in `conventions/specs.md`, under the headings named.

## Sent back

1. Comment the exchange on the PR ("What is said at a gate").
2. Fix it on the stage's branch.
3. Run the review again (SKILL.md, step 6) and bring the PR body up to date.
4. Show the reviewer the PR body again, and stop.

## Approved

1. Write down what the gate decided ("What is said at a gate"): on the PR, in the brief with its comment if the plan changed, in an ADR if it outlasts the change.
2. Merge through the `merge` skill.
3. Post the new build notes on the change's issue ("The build notes"): read the newest, carry it forward with what this stage built, post it whole.
4. Hide the notes comment before it. Its `id` is in `gh issue view <n> --json comments`:

   ```sh
   gh api graphql -f id=<comment id> -f query='mutation($id:ID!){minimizeComment(input:{subjectId:$id,classifier:OUTDATED}){minimizedComment{isMinimized}}}'
   ```

5. Report that the stage has merged.

Then stop. The next stage starts when the reviewer asks for it, in the approval itself or later.
