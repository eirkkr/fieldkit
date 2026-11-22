# 075 - The reviewer ends the review loop

## Decision

A review is suggested at every stop and never run unasked, and the suggestion repeats after each fix until the reviewer ends it.

- **At each stop** (a plan published, a PR at its gate, a fix made) the agent names every review worth running with its reason, or says in one line that none is, and says what has not been reviewed.
- **After a fix** it suggests a review of the fix, or says none is worth running, or, when no finding was fixed, that there is nothing to review.
- **The reviewer ends it** by declining, or by saying no more is needed. The ending covers that gate only (a PR at its gate, or a published plan awaiting its answer); every stop still says what has not been reviewed, and a review the reviewer asks for afterwards still runs.
- **The ending is a comment**, `Review ended by the reviewer at PR (declined).` or `at plan`, `(no more needed)` in place of `(declined)` for word that enough has run. Where the word does not say which, no round run means `declined`, else `no more needed`. The newest such comment from an `OWNER`, `MEMBER` or `COLLABORATOR` author governs, so a second ending replaces the first.
- **Every round posts a `## Review findings` comment**, `No findings.` when it found none, on the PR or on the issue for a plan. A round is one run of a review, its parallel axes counting as one.
- **The PR body's Review line is derived**, never copied: `Review: Not run.` or `Review: <n> round(s) run.`, the count from the findings comments, followed once ended by `Ended by the reviewer (declined).` or `(no more needed).`, from the newest ending comment.
- **A message with two asks records the ending first**, then does the rest: a change asked for is a send-back, an approval is approval, a review asked for runs, and none of them suggests another review.

## Reason

[ADR 054](054-a-change-is-an-issue.md) made review offered, not run, because its first trial ran it eleven times. 054's rule already put a stop after a fix ("a fix made after either"), but the skills built from it showed the findings and stopped, so a fix made on a reviewer's finding went unreviewed unless the reviewer thought to ask. And nothing let the reviewer stop being asked, so an offer at every fix could only nag or be suppressed for good.

The loop closes both while keeping 054's reason: nothing runs unasked, the reviewer decides each round, and one word ends the suggestions.

Why the choices above:

- **The comments are the state, the Review line is derived**, over a line that carries the count and the ending. Three writers touch the line (the stage's PR when it is opened, `push` when a body goes stale, and `GATE.md`), and a run can die between a comment and a rewrite. A line recounted from the comments on every rewrite cannot be left stale by any of them, and nothing reads it as the state.
- **An empty round still posts a comment**, or the count would miss a review that found nothing, and a decline after it would read as made before any round.
- **The newest ending from a trusted author governs**, because the repository is public and anyone can post a comment that begins with the same words.
- **An ending covers one gate**, over lasting until the next push, because a new gate is a new thing to look at and the reviewer can end it again in a word.
- **The reviewer's own word chooses `declined` or `no more needed`**, with the round count only breaking a tie, over a count alone. The change this belongs to, [Review loop, step pause and a record for every stage](https://github.com/eirkkr/fieldkit/issues/173), later records each suggested review's answer, and "declined" and "said enough" are separate answers there; the line should carry what the reviewer said.

## Consequences

- A reviewer who wants no suggestions says so once per gate.
- Every stop of the loop uses one shape: the review, then its reason, or one line saying none is worth running. The final review's offer is a separate offer and keeps its own wording.
- A PR can merge with `Review: Not run. Ended by the reviewer (declined).`, which says what happened more plainly than `Not run.` did.
- The Review line no longer says whether the last review covers the PR's current head, as "on the PR as it now stands" did. Each stop says what has not been reviewed instead, so a fix made after the last round is named there, not on the line.
- The stop after a stage's steps, and the record of who did what, are separate decisions, made by the later stages of that change.
