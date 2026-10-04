# A change's final review

Reached from [SKILL.md](SKILL.md) when every stage of the change is closed. A *fresh* agent is a subagent given only what a step lists. The rules are in `conventions/specs.md`, "The final review".

1. Find where the change began: the commit before its first stage's merge. `git diff <that>...<default>` is the whole change.
2. Dispatch fresh agents over that diff, with the brief's requirements, one for each direction: requirements unmet; things built that no requirement asked for; requirements no test holds. A fourth reads the diff against the repo's conventions.
3. Re-read every issue the change cites in code, comments and docs: open, and about the thing cited.
4. Reproduce each finding, then triage it: fix it, or list it as an issue to file. A fix is one more stage - add it as a sub-issue and build it through SKILL.md.
5. Post the findings on the change's issue, with anything the change showed the process got wrong. Where a mechanical check would have caught a mistake, propose the check.
6. Ask the reviewer to close the change.

Done when every requirement in the brief has been reported as met with a named test, or as a finding, and the reviewer has been asked.
