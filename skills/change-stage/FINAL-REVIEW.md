# A change's final review

Reached from [SKILL.md](SKILL.md) when every stage of a change built in stages is closed. The rules are in `conventions/specs.md`, "The final review". A *fresh* agent is a subagent given only what a step lists, and nothing from this conversation.

If the brief's Not yet specified still holds work, tell the reviewer and stop: the change has stages left to plan.

If the reviewer has not asked for the final review, offer it - saying what it would read and why that is or is not worth it for this change - ask whether to close the change, and stop. Close it on their yes.

When they ask for it:

1. Gather the change: for each stage closed by a PR, `gh issue view <stage> --json closedByPullRequestsReferences`, then `gh pr diff <pr>`. A stage closed as not planned was dropped, and has none.
2. Dispatch fresh agents over those diffs, with the brief's requirements, one for each direction: requirements unmet; things built that no requirement asked for; requirements no test holds. A fourth reads them against the repo's conventions.
3. Re-read every issue the change cites in code, comments and docs: open, and about the thing cited.
4. Reproduce each finding, then triage it: one more stage to fix it, or an issue to file.
5. Post the findings on the change's issue under `## Final review`, with anything the change showed the process got wrong. Where a mechanical check would have caught a mistake, propose the check.
6. Tell the reviewer what is left: each stage proposed and each issue to file, or that nothing is. On their yes to a stage, add it to the brief with its comment and create its sub-issue. With nothing left, ask whether to close the change, and close it on their yes.

Done when every requirement in the brief has been reported as met with a named test, or as a finding, and the reviewer has been asked.
