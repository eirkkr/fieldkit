# 054 - A change is an issue, and a stage is a pull request

## Decision

Retire OpenSpec and the `review-gated` schema. A change keeps nothing about itself in the repository's files: it is planned, built and reviewed on GitHub, and what it leaves in the repository is code, tests, docs and ADRs.

Each thing a change writes has one home and one reader:

- **The change is an issue**, labelled `change`. Its body is the brief, and it is all the reviewer reads to approve the plan: why, what they get, the decisions made, the decisions that are theirs, and one line per stage. One screen. The brief always says the plan as it now stands, and every edit to it is paired with a comment on the issue saying what changed, why, and where that was decided. The body is the plan; the comments under it are how the plan got there.
- **The build notes are a comment on that issue, written afresh at every gate.** They are the agent's, and they hold the change's current state: the interfaces as built, each requirement with the test that holds it, stopgaps still to remove, assumptions not yet tested. Each gate posts the notes whole as a new comment and hides the one before it as outdated, so the latest comment is the only one an agent reads and the earlier ones stay as the history. They are never polished for a human, and they have a size cap - notes that outgrow it mean the change should be split.
- **A stage is a sub-issue of the change, and one pull request closes it.** The sub-issue is created with the plan, holding the stage's one line. Its steps are written into it when the stage starts, from the repository as it then is, not when the change is planned. Anything an earlier stage finds that changes a later one is a comment on the later stage's issue. A change small enough to be one stage has no sub-issues: it is an issue and a PR.
- **A change or a stage that waits on another is marked blocked by it.** Stages run in the order of the change's sub-issues, and that order alone says nothing about need. A stage is marked blocked only by a stage it cannot be built without, in its own change or another, so the stages left unmarked are the ones free to be reordered or dropped. When a blocker closes, what waited on it is re-read against the repository before it starts.
- **A step is a commit.** Its body says why, and anything the step needed that the stage's plan did not anticipate.
- **Reviewer agents read every stage before the human does.** They start with no build context and read the stage's diff against the repo's conventions, the change's requirements, and the plain-language rule for everything a human will read. Each finding is reproduced before it is acted on, then sorted: fixed in this stage, left as a comment on the later stage that will handle it, or listed in the PR as an issue to file. Findings are inline comments on the PR.
- **The PR body is the reviewer's page.** The stage in a few sentences; what changed from the plan they approved, or one line saying nothing did; the choices the agent made that they could overturn, when there are any; and one thing to try, saying whether the agent ran it. Every command in it was run as written.
- **A decision made at a gate is written down where it will be found.** The exchange is a comment on the PR. If it changes the plan, the change's brief is edited, with its comment linking that PR. If it outlasts the change, it is an ADR.
- **The final stage is still the whole-change review**, in three directions: requirements unmet, things built unasked, requirements no test holds. Its findings are the closing comment on the change's issue, together with anything the change showed the process itself got wrong.
- **Behaviour is described once**, by tests and docs. A requirement becomes a named test. There are no delta specs, no living specs and no archive.

Unchanged: the stage is the unit of merge and ends green and independently mergeable ([041](041-stage-is-the-merge-unit.md)); a gate is a full stop, and approving it starts nothing ([049](049-approval-does-not-start-the-next-stage.md)); what a change writes is divided by its reader ([052](052-divide-a-change-by-reader.md)).

This supersedes [021](021-adopt-openspec-centralised-via-kit.md), [022](022-openspec-skills-model-discoverable.md) and [034](034-review-gated-openspec-schema.md), and replaces the mechanics of 041, 049 and 052 while keeping their rules.

## Reason

The evidence is ten changes in one consumer repo, six of them review-gated, read back after the fact.

**Most of what a change wrote had no reader.** One eight-stage change produced about 3,150 lines of change artifacts for 1,350 lines of source and 3,525 of tests. The pull request that landed its 1,530-line plan drew no comments and no reviews. Its `tasks.md` reached 1,440 lines, of which about 290 were the plan and the rest review notes. The reviewer reported reading neither the living specs nor the delta specs, ever, and not using the note's "look closely at" item.

**The detailed plan did not hold, and keeping it true was most of the work.** Each of that change's first five stages recorded departures from a design written days earlier, and the first stage's review reversed a decision the design had recorded. Every departure meant correcting the design and the later tasks by hand; the final review corrected them again, and the next commit archived them. Another change was planned in full, paused, and rewritten before most of it was built, going from 46 tasks to 73. A third has waited unstarted while the model it targets changed under it. Detail written ahead of the stage that needs it is written twice.

**The bookkeeping existed because facts git already held were written into files.** The commit list, `Reviewed at`, `Change based at`, the recorded check states and the rule for remapping all of them after a rebase are copies of what a pull request knows about itself. On one stage's branch, four of eleven commits existed only to maintain the note. 034 defined that note, and 041 and 052 each reshaped it.

**What the reviewer did at gates was decide.** The send-backs on record are questions about behaviour - why one fault should end a run at all, whether a placement window belongs to a block or a component, whether a fixture should hold real material - plus requests for plainer wording, and one verify command that turned out to match nothing. None of that needs a record of every commit. All of it needs a short page that says what is theirs to decide.

**The findings came from independent review, which nothing required.** At several gates a fresh agent read the branch and found what the building agent had not: values stored that should have been refused, an input that crashed a page, tests that were missing. Where that did not happen, a final review found five convention faults that seven approved stages had let through. The independent pass is made a rule and moved to every stage, where a finding is cheapest to fix.

**Behaviour was described three times.** The living specs, the repo's own docs and the tests covered the same ground, a whole stage of one change was spent bringing the docs into line, and nothing outside the spec tooling read the living specs.

**Moving only the review note into the PR was considered first, and rejected as too small.** It removes the bookkeeping and leaves the up-front task plan, the delta specs and the archive, which are the larger costs.

**Keeping the build notes in a file deleted by the final stage was rejected.** It is easier to edit and to search, but it puts agent-only text back into every stage's diff, which is what the reviewer asked to be rid of.

**Editing one build-notes comment in place was rejected.** It keeps the issue's thread shortest, but an edit replaces the whole comment, so one bad write loses the change's state with nothing beneath it, and how the notes stood at each gate survives only in GitHub's edit history, which nobody reads. **Appending only what each stage changed was rejected too:** the next agent would have to read every comment and work out which lines still hold, which is the accumulated note this ADR removes. A whole copy per gate costs a longer thread and gives both a single place to read and a history.

**Leaving the brief's history to GitHub's edit history was rejected**, for the reason given for the notes: it records that the text changed, not why, and nobody opens it. **Never editing the brief was rejected too:** a plan corrected only in comments beneath it is acted on, uncorrected, by whoever reads the body alone. So the body is edited and each edit is announced.

**A checklist of stages in the issue body was rejected for sub-issues.** A sub-issue gives the stage's plan somewhere to be written when the stage starts, gives a later stage somewhere to receive what an earlier one found, and is closed by its PR without anyone ticking a box.

**Marking every stage blocked by the one before it was rejected.** It needs no judgement, but a chain says only what the order already says, and it has to be re-linked whenever a stage is split or moved - one change here went from seven stages to ten. Marking only real needs records something the order does not: which later stages a reviewer can reorder or drop between gates, and which stage in one change is waiting on a stage in another, as one here did.

**Keeping "look closely at" was considered.** It did once name the thing a gate was then sent back on. But it is the building agent reporting on itself to a reader who does not open it; the reviewer agents cover the same ground independently, and the choices the reviewer could overturn are asked as choices.

**Keeping the full task plan as the default was rejected.** [specs.md](../../conventions/specs.md) argues that pricing every part of a change is how to find out whether to do it. That holds for a decision that is large and hard to undo, and it stays available for one. As the default it bought plans that were rewritten before they were built.

## Consequences

- **The history of a change is on GitHub, not in git.** A clone no longer carries it, a search of the repository no longer finds it, and edits to an issue are not reviewed diffs. Looking back over past changes - the work this ADR is itself the result of - reads issues and pull requests through `gh` rather than files: `gh issue list --label change --state all` finds them, and each one's stage PRs hold what departed, what review found and what was decided.
- **That lookback depends on the gate being written down.** The build notes say how the change stood at each gate, not what happened at it; that record is the stage PRs and their comments. A gate conversation held only in a terminal leaves nothing behind, and recording its outcome on the PR is what replaces the note that used to capture it.
- **The change's issue carries one build-notes comment per gate**, all but the last collapsed as outdated.
- **No change is priced task by task before it starts** unless someone asks for that. The stage list is the estimate.
- **Nothing enforces a spec format.** That behaviour is written down at all now rests on tests and docs being kept, and on the final review's check that every requirement has a test.
- **More issues.** A five-stage change is six issues and five PRs.
- **Review costs tokens at every gate**, accepted for what it has been finding.
- **The reviewer agents' "file it" findings are listed, not filed.** Filing an issue stays ask-first, so they are filed on a yes at the gate. Creating a change's own issue and its stage sub-issues needs the exemption stage PRs already have.
- **The kit drops its npm footprint and everything built to carry OpenSpec**: `package.json` and its lockfile, the install, enable and refresh scripts, `repo-skills/` with its six vendored skills, `repo-skills-overlay/` and its check, and `schemas/review-gated/`. One kit skill and a rewritten `conventions/specs.md` replace them.
- **A consumer's in-flight changes finish under the schema they started with.** Its `openspec/` directory, lint exclusions and skill symlinks are removed once the last one is archived; the living specs go with them, after anything the docs lack is moved across.
