# 032 - Merge waits out pending CI instead of stopping

## Decision

`agents/merge/AGENT.md` and `skills/merge/SKILL.md` no longer treat a
still-running check the same as a failing one. Only "PR not open," "has
conflicts," or "a check failed" stop the flow outright. A still-running
check instead makes the `merge` agent wait: `gh pr checks --watch
--fail-fast --interval 15`, bounded by a single Bash call's timeout (up to
the 600000ms max). If every check passes within that window, the agent
merges and cleans up in the same run, with no second `/merge` needed. If a
check fails, it stops and reports which one, same as before. If the wait
itself times out before CI resolves, it stops and reports that CI is still
running, rather than looping indefinitely - the caller can invoke `/merge`
again once it's expected to be done.

`conventions/git.md`'s squash-merge mechanics line is updated to match: a
red check or conflicts block outright, a still-running one is waited out.

This amends [030](030-ungate-merge.md), which had the agent check CI once
and stop on anything but green, including "still pending."

## Reason

Queued/running CI was the single most common reason `/merge` didn't
complete on the first call - not because anything was wrong, just because
the pipeline hadn't finished yet. That forced a second `/merge` (or a
manual poll-and-retry) for what's really one logical action: land this PR
once its checks pass. `gh pr checks --watch` already does exactly that kind
of polling natively, so there's no need to build a custom poll loop - one
command blocks until the outcome is known, and the agent acts on it
directly.

This doesn't touch the CI gate itself, which [011](011-wip-on-branches.md)
and [030](030-ungate-merge.md) already established as the one
unconditional, hard-coded blocker in this flow: a red check still stops the
merge exactly as before. Only the handling of "not resolved yet" changes,
from "stop" to "wait for resolution, then act on it."

Alternatives rejected:

- **Use GitHub's native auto-merge** (`gh pr merge --auto`), letting
  GitHub itself merge once required checks pass, rather than watching from
  the agent side. Rejected for this repo: `gh api repos/{owner}/{repo}`
  shows `allow_auto_merge: false`, a repository setting that's off by
  default and would need to be flipped first - a shared, persistent
  infrastructure change to make for what a client-side watch loop already
  achieves without touching repo settings. `gh pr checks --watch` needs
  no such prerequisite and works the same in any repo.
- **Poll indefinitely** rather than bounding the watch call. Rejected -
  a hung or unusually slow pipeline would otherwise leave the agent blocked
  with no way to report back; bounding it and letting the caller retry is
  the same shape [030](030-ungate-merge.md) already accepted for the
  check-then-merge race (best-effort, not a guarantee).

## Consequences

- A `/merge` called while CI is still running now typically completes the
  merge in the same invocation instead of requiring the caller to check
  back and call it again - the common case gets faster, not just more
  correct.
- If CI takes longer than a single Bash call's timeout allows, the agent
  still stops and reports rather than merging on an unresolved state; nothing
  bypasses the CI gate itself.
- `conventions/git.md`'s "a red or still-running check blocks it outright"
  line no longer describes actual behavior for "still-running" and is
  corrected.

> Completed by [039](039-always-on-gate-table.md): `KIT.md` carried the same
> "still-running blocks outright" line and was missed here; it is corrected
> there.
