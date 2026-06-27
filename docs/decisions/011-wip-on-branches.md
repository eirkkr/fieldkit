# 011 - WIP on branches; gate PR creation, not drafts

## Decision

Drafts are dropped entirely. Work in progress lives on a branch: commits and
branch pushes are ungated act-then-show. A PR is opened only once the work is
judged ready for review, and opening it needs human approval - the agent
surfaces a GitHub compare link (`.../compare/main...branch`) and a short
summary, then waits. CI runs on every PR (the lint workflow no longer filters on
`draft` or listens for `ready_for_review`), since a PR now exists only when the
work is ready. The pre-merge message gate stays.

This amends [008](008-outward-irreversible.md): drafts are gone, branch pushes
join act-then-show, and the ready-for-review gate is relocated onto PR creation.

## Reason

Draft status was only ever the CI gate, which made "no CI" the default for every
PR and forced a draft-then-ready dance plus an approval step before CI ran at
all. Moving WIP onto the branch removes draft state outright: the PR itself
becomes the readiness signal, so 008's ready-for-review gate relocates naturally
onto PR creation. Same protection 008 wanted - a human confirms the work is
ready before it goes out for review - with one gated step instead of two and no
draft state to manage.

Branch pushes stay ungated: they are reversible, enable backup, and let the
agent produce the compare link used at the readiness checkpoint. The diff is
surfaced via that link rather than dumped into the terminal - cheaper, and the
human reviews it on GitHub.

The pre-merge message gate is kept for two reasons: the repo has no
branch-protection required checks, so human approval at merge is what confirms CI
is green; and it is where the synthesised squash message is verified.

Alternatives rejected:

- **WIP suppression label / `[skip ci]` marker.** Earlier candidates for gating
  CI on an open PR; unnecessary once WIP lives on the branch with no PR, so CI
  only ever runs on ready work.
- **No PR-creation gate (rely on the pre-merge gate alone).** A PR requests human
  review and can notify reviewers; relocating 008's existing gate here is cheap
  and stops the agent asserting readiness unilaterally, which was the explicit
  concern.
- **Branch protection with required checks instead of the pre-merge gate.** Would
  automate the CI-green confirmation and is worth adopting per-repo, but it is not
  in place here, and the squash-message check needs the gate regardless.

## Consequences

- Lifecycle: branch + commits + push (ungated) -> open PR (gated, readiness) ->
  pre-merge message (gated, CI + message). Two gates, both at meaningful points.
- 008's "first push opens a PR as an early checkpoint" is lost. Replaced by
  surfacing the compare link and summary on the branch before opening the PR -
  the checkpoint moves earlier and stays local until the work is ready.
- CI runs only on ready work, so WIP pushes don't burn runs - the branch-WIP
  model recovers the run-saving the draft gate gave, without the draft churn.
- A consumer repo with expensive CI inherits the same model for free; if it wants
  CI on open-but-unready PRs suppressed, a WIP label is the documented fallback.
- 008's principle (gate on outward or irreversible actions) stands; only its
  draft-PR and ready-for-review specifics are amended here.
