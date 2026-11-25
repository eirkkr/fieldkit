# 076 - A stage stops after its steps

## Decision

A stage stops once its steps are written and re-read, and its branch is cut only on the reviewer's word to build.

- **Every stage stops.** The stop comes after the steps are written and before the branch is cut, for every stage, including a stage of a plan priced to decide, whose steps were written before approval: they are re-read against the repository, corrected where it has moved, and the stage then stops like any other.
- **The word to build is a clear yes to building** (`build it`, `yes, build`). The word that starts a stage ("carry on"), a message that only started the run, an approval of the plan or of the previous stage, and an answer to "resume this stage?" are not it.
- **Two comments on the stage's issue mark the stop.** `Steps ready` says the steps are written and re-read; `Steps approved to build by @<login>.` is the word, written by the agent on the reviewer's word. Each is matched on its first line, and the newest of each from an `OWNER`, `MEMBER` or `COLLABORATOR` author governs. A new `Steps ready` voids older approvals and older `at steps` endings.
- **A review of the steps is suggested at the stop**, sized like any other. A fresh agent reads the steps, the brief, the notes and the repository, and reports each `Done when` that nothing could check, each step that breaks the stage rules, and anything a builder from the steps would have to guess.
- **A decline at the stop covers it alone.** `Review ended by the reviewer at steps (declined).` (or `(no more needed).`) ends suggestions at the steps stop only, and a plan-stage ending does not cover it.
- **A stage that is assigned, has `Steps ready`, no later approval and no pull request is waiting** for the word, and a later run says so. A stage with no commit carrying one of its step numbers is never resumed into a build without it.

## Reason

[ADR 049](049-approval-does-not-start-the-next-stage.md) kept approval from starting the next stage, but it left the start itself to a few words ("carry on with stage 3"), and nothing then stopped the agent between writing the stage's steps and building them. The reviewer's check on the steps came, if at all, as a review of the diff they had already produced. Reading the steps is cheaper than reading that diff, and a wrong step is cheapest to catch before anything is built from it.

Why the choices above:

- **Every stage, over only risky ones.** What makes a stage risky is often what the steps would show, so a rule that waits for a risk the agent has already judged waits for the wrong thing. The stop costs the reviewer a word; revisit after several stages have run under it.
- **"Carry on" is not the word**, over reading it as one. It means start the stage, and the stage's steps are the first thing it produces. If the same word also meant build, the stop would never be a stop.
- **The word is a comment**, over the agent remembering it. A run can end between the word and the first commit, and the next run has only the issue to read.
- **A newer `Steps ready` voids older approvals**, because an approval is of the steps as they stood. The agent edits the steps only to fix them, so the reviewer sees the corrected ones before anything is built from them.
- **A decline names its stop**, over covering the whole change. A decline of a plan review says nothing about steps that did not exist yet, and a reviewer who wanted none at either can say so at each in a word.
- **A plan priced to decide stops too**, over building from its steps as written: its steps were written before the repository moved, and that is the case the re-read exists for.

## Consequences

- The reviewer says one more thing per stage, usually "build it", after it has the steps in front of them.
- A bare yes can mean two things when one stage waits at its gate and another waits for the word to build, so the agent asks which and acts on neither.
- A stage that was building when a run died is told apart from one waiting: a commit carrying a step number and no newer `Steps ready` means building.
- The rule stands in `conventions/specs.md` ("A stage's issue", "Review") and the `change-stage` skill (`SKILL.md` step 4 and `STEPS.md`), and the always-loaded `KIT.md` carries a row for the word to build.
- The stop applies to a stage the agent builds from written steps. A change that is one pull request has its steps in a comment on its own issue and stops the same way.
