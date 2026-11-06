# 064 - Agents run the local check once, before review

## Decision

Agents still don't run formatters or linters while iterating. When the work is ready for the human's review or approval - a PR to open, a stage at its gate - the agent runs the repo's full local check once and fixes what it reports, as a plain commit. Before starting CI on GitHub, it runs locally what CI runs, where the repo has a recipe for it. The rule lives in `KIT.md`.

This supersedes [007](007-agents-dont-run-linters.md), which kept the agent out of lint entirely and left the pass to the human and CI.

## Reason

007 weighed lint churn - run, parse, fix, re-run over cosmetic findings - against a style slip reaching CI, and chose the slip. Its premise was that CI ran on every push and the human ran the tools. A consumer has since moved CI to run only when started, where a lint failure found there costs a started run and a fix commit after the reviewer has already read the diff.

Churn comes from running the tool repeatedly, not from running it at all. One run at the end, on work the agent judges done, costs one pass; the loop stays out of the iteration. And a reviewer, human or agent, should not spend attention on lint a tool would have caught.

Rejected:

- **Keep 007.** Right while CI was automatic and free to fail; wrong once a failed run is paid for and the diff is already being read.
- **Run lint on every edit or turn.** The churn 007 removed. The auto-fix hook it left as an opt-in stays that.
- **Leave the local run of CI's suites to the human.** The agent knows when the work is ready; asking after the fact adds a round trip, and a run that only confirms is cheaper than one that discovers.

## Consequences

- The check runs once per readiness point, not per commit. A fix it prompts is a plain commit; a later push that changes code makes the next readiness point run it again.
- "Full local check" is the repo's recipe, and which CI-only suites to run beforehand is the repo's call - some are slow or destructive and are asked about first. A repo names them in its own docs.
- Tests are unchanged: the agent runs them throughout, concise and fail-fast.
