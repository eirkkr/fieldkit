---
name: merge
description: Merge the current branch's pull request via squash merge
---

# Merge a pull request via a delegated agent

If there's no open PR for this branch yet - including uncommitted or
unpushed work - follow `skills/pr/SKILL.md` first (which itself follows
`skills/push/SKILL.md` if needed to get the branch pushed). Reaching this
skill already means merging is approved - either the user typed `/merge`
directly, or the caller asked and got a yes first - and that covers opening
the PR and pushing along the way too, so there's nothing further to ask
before doing them.

Check the PR is actually mergeable before drafting anything: `gh pr view
--json
number,title,state,mergeable,statusCheckRollup,baseRefName,headRefName,url`.
If it's not open or has conflicts, stop and report what's blocking it -
waiting doesn't fix either. Checks still running is not a stop condition
here: draft as normal and let the `merge` subagent wait for them. Reaching
this skill is approval to merge once CI is green - not approval to merge
regardless of what CI says, and not approval to skip waiting for it.

Once it's clean, decide the squash subject and body yourself. Start from
context already in hand plus `git log <base>..<branch>` for the branch's
full run of commit messages, not just the latest one - that's usually
enough to synthesize a subject + body summarizing the whole change, not a
concatenation of the commits. Only fall back to `git diff <base>...<branch>`
when the commit messages and your own context don't add up to a clear
picture of the whole change. For `Closes #X`, don't
read a number off the PR body or infer one - ask GitHub what this PR
actually closes: `gh pr view --json closingIssuesReferences -q
'.closingIssuesReferences[].number'`. Use only a number it returns; if it
returns nothing, omit the line entirely rather than substituting the PR's
own number.

Launch the `merge` subagent (`subagent_type: merge`) in the foreground with
the drafted subject and body. The agent takes them as given, re-verifies
mergeability defensively, waits out any still-running checks, merges once
they're green, and cleans up the branch locally - it doesn't rediscover,
diff, or draft any of it itself. This can take a few minutes if CI is still
running; relay its report once it lands (merged, or blocked - a failing
check, or checks still running past the wait window).
