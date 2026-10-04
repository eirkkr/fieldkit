# The reviewer's answer at a gate

Reached from [SKILL.md](SKILL.md) when a stage is at its gate and the reviewer has answered. Forms are in `conventions/specs.md`, under the headings named.

Find the stage's PR first - `gh pr list --head <branch>`, the branch being the one its steps name - and check that branch out. Done when the PR found closes this stage's issue.

## A review asked for

A *fresh* agent is a subagent given only what is listed here, and nothing from this conversation.

1. Run what the reviewer asked for: the skills they named, else the axes of "Review" they chose, each as a fresh agent, in parallel.
   - **Conventions.** Give it `git diff origin/<default>...HEAD` and the repo's convention docs. It reports each place the diff breaks one, and each thing a person will read that is not in plain words.
   - **Requirements.** Give it the same diff, the stage's steps and the brief's requirements. It reports each requirement the stage claims and misses, each with no test behind it, and each thing built that none asked for.
2. Reproduce each finding, then triage it: fix it here as a commit; edit it into the later stage that will handle it, with a comment there saying so; or list it as an issue to file.
3. Comment the findings and their outcomes on the PR ("Review"), and bring the PR body's Review line up to date.
4. `gh pr checks --watch`. Show the reviewer the findings and their outcomes, and stop.

Done when every finding has one of those three outcomes and the full check passes.

## Sent back

Any answer that asks for something to change is this one.

1. Fix it on the stage's branch, as plain commits.
2. Comment on the PR what was asked and what changed ("What is said at a gate"), and bring the PR body up to date. A review that ran before the fix no longer covers it: the Review line says so.
3. `gh pr checks --watch`.
4. Show the reviewer what changed. Offer a review again where the fix is more than wording, with the reason, and stop.

## Approved

Any clear yes is approval, and the word to merge.

1. Write down what the gate decided ("What is said at a gate"): on the PR, in the brief with its comment if the plan changed, in an ADR committed to the stage's branch if it outlasts the change.
2. File the issues the reviewer said yes to.
3. Merge through the `merge` skill.

For a change of one pull request, the merge closes the change. Report it, and stop.

For a change built in stages, carry on:

4. Post the new build notes on the change's issue ("The build notes"): read the newest, carry it forward with what this stage built, post it whole.
5. Hide the notes comment before it. Its `id` is in `gh issue view <n> --json comments`:

   ```sh
   gh api graphql -f id=<comment id> -f query='mutation($id:ID!){minimizeComment(input:{subjectId:$id,classifier:OUTDATED}){minimizedComment{isMinimized}}}'
   ```

6. Report that the stage has merged. If something under the brief's Not yet specified can now be said in a line, propose it as a stage; on the reviewer's yes, add it to the brief with its comment and create its sub-issue.
7. If that was the last stage, offer the final review ("The final review") and ask whether to close the change.

Then stop, unless the approval also asked for the next stage: then start again at SKILL.md, step 1.
