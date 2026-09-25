# 045 - Run push, pr and merge inline; retire their agents

## Decision

The `push`, `pr` and `merge` skills run their git and `gh` commands in the
main agent, in the same turn that drafts what those commands carry. The
`agents/push`, `agents/pr` and `agents/merge` worker agents are removed, and
with them the last skill-agent pair [ADR 016](016-skill-agent-pair.md)
describes.

Nothing about *what* the skills decide or *when* they may run changes:

- The skill still decides the branch, commit message, file list, PR title
  and body, and squash message ([ADR 027](027-push-decisions-move-to-caller.md),
  [030](030-ungate-merge.md)).
- [ADR 031](031-regate-pr-and-merge-invocation.md) still governs whether
  `pr` and `merge` may be invoked at all.
- `merge` still waits out pending CI and never merges past a failing check
  ([ADR 032](032-merge-waits-out-pending-ci.md)).

## Reason

[ADR 015](015-mechanical-subagent-boundary.md)'s test for delegating a git
step was: it is ungated, and there is enough real work to justify the
isolation. The work it had in mind was reading the diff, choosing a branch
name and drafting a message, on a cheaper model. Later decisions moved that
work out of the agents one piece at a time. 027 gave every push decision to
the caller, and 030 did the same for the squash message. 033 kept `pr`'s
agent only by moving `gh pr create` into it, conceding that what was left was
"too thin to earn a subagent hop". By 015's own test, none of the three still
earned one. Each agent ran commands whose every argument the caller had
already decided.

What the hop cost showed up in one long consumer-repo session, which
dispatched eleven of these agents (eight push, two pr, one merge):

- **Cold starts.** About 14k tokens each, on the cheap model - the one cost
  the design anticipated, and the smallest.
- **Wake-ups on the expensive side.** The agents ran in the background, so
  each dispatch meant the main agent polled for the commit to land, as the
  push skill required. It then verified the result, as the skill also
  required, because the report was "unverified". Then it woke twice more:
  once for the agent's hand-back message and once for its completion
  notice. Each wake-up re-reads the whole session context on the main
  model, which in a long session costs far more than the haiku tokens the
  delegation saved. That was about twenty extra turns in one session.
- **Duplicated checks.** Since the skill told the caller to verify the
  outcome itself, the agent's report carried nothing the caller used, and
  the merge agent re-checked mergeability the skill had just checked.
- **Noise for the human.** Each of those wake-ups surfaced as a near-empty
  message saying the report matched what had already been checked, and the
  human asked about it. That question is what prompted this decision.

Running inline also removes a race. The push skill had to poll because a
background commit could land after the turn ended, racing the `Stop` hook
that measures formatter drift against the commit the turn started from
([ADR 035](035-measure-the-fixer-not-the-transcript.md)). An inline commit
lands before the turn ends, so there is nothing to poll for.

Alternatives rejected:

- **Keep the agents, drop the verification step.** Removes the duplicated
  checks but not the wake-ups, which are the main cost, and leaves the
  caller trusting a report it has no reason to prefer over `git log`.
- **Keep the agents, run them in the foreground.** Would remove the polling
  and the extra wake-ups, but foreground dispatch is not reliably available
  (in the session above every dispatch ran in the background, whatever the
  skill asked for), and it would still pay a cold start to run commands
  whose arguments are already fixed.
- **Keep only `merge`'s agent, for the CI wait.** The wait is one
  `gh pr checks --watch` call. It blocks the main agent's turn for up to its
  timeout, which is the same wait the human was already making for the
  agent's report.

## Consequences

- `skills/push`, `skills/pr` and `skills/merge` carry their own command
  steps: the steps that were in the agents, moved across, minus the checks
  the skill had already made.
- `agents/` ships nothing. `scripts/link-agents.sh` stays in `just install`,
  because its pruning pass is what removes the `push`, `pr` and `merge`
  links it made in `~/.claude/agents` on machines that installed them. It
  now tolerates an empty `agents/`.
- The test in 015 still stands for any future delegation: a subagent earns
  its hop only when it isolates real work - reading, deciding, exploring -
  and not when it runs commands whose arguments are already fixed.
  KIT.md's rule that subagents are for context isolation, not for a cheaper
  model on a small task, says the same.
- [016](016-skill-agent-pair.md) and [033](033-pr-agent-opens-the-pr.md) are
  superseded. [027](027-push-decisions-move-to-caller.md) and
  [030](030-ungate-merge.md) are amended: their decisions stand, but the
  agent they hand to no longer exists.
