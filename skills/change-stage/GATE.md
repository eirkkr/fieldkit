# The reviewer's answer at a gate

Reached from [SKILL.md](SKILL.md) when a stage is at its gate and the reviewer has approved it or sent it back. Forms are in `conventions/specs.md`, under the headings named.

Find the stage's PR first - `gh pr list --head <branch>`, the branch being the one its issue names - and check that branch out. Done when the PR found closes this stage's issue.

## Sent back

1. Comment the exchange on the PR ("What is said at a gate").
2. Fix it on the stage's branch.
3. Run the review again (SKILL.md, step 6), and add its findings to the PR's findings comment.
4. Bring the PR body up to date, and `gh pr checks --watch`.
5. Show the reviewer the PR body again, and stop.

## Approved

1. Write down what the gate decided ("What is said at a gate"): on the PR, in the brief with its comment if the plan changed, in an ADR committed to the stage's branch if it outlasts the change.
2. File the listed issues the reviewer said yes to.
3. Merge through the `merge` skill.
4. Post the new build notes on the change's issue ("The build notes"): read the newest, carry it forward with what this stage built, post it whole.
5. Hide the notes comment before it. Its `id` is in `gh issue view <n> --json comments`:

   ```sh
   gh api graphql -f id=<comment id> -f query='mutation($id:ID!){minimizeComment(input:{subjectId:$id,classifier:OUTDATED}){minimizedComment{isMinimized}}}'
   ```

6. Report that the stage has merged. If something under the brief's Not yet specified can now be said in a line, propose it as a stage; on the reviewer's yes, add it to the brief with its comment and create its sub-issue.

Then stop, unless the approval also asked for the next stage: then start again at SKILL.md, step 1.
