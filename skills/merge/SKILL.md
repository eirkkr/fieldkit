---
name: merge
description: Merge the current branch's pull request via squash merge
---

# Merge a pull request via a delegated agent

If there's no open PR for this branch yet - including uncommitted or
unpushed work - follow `skills/pr/SKILL.md` first (which itself follows
`skills/push/SKILL.md` if needed to get the branch pushed). This `/merge`
invocation is implicit approval for both; they're already ungated
act-then-show, so there's nothing to ask before doing them.

Check the PR is actually mergeable before drafting anything: `gh pr view
--json
number,title,state,mergeable,statusCheckRollup,baseRefName,headRefName,url`.
If it's not open, has conflicts, or has checks failing or still pending,
stop and report what's blocking it. Calling `/merge` is approval to merge
once CI is green - not approval to merge regardless of what CI says.

Once it's clean, decide the squash subject and body yourself: read `git log
<base>..<branch>` and `git diff <base>...<branch>` for the whole change set,
not just the latest commit. Synthesize a subject + body summarizing the
whole change, not a concatenation of commit messages. For `Closes #X`, don't
read a number off the PR body or infer one - ask GitHub what this PR
actually closes: `gh pr view --json closingIssuesReferences -q
'.closingIssuesReferences[].number'`. Use only a number it returns; if it
returns nothing, omit the line entirely rather than substituting the PR's
own number.

Launch the `merge` subagent (`subagent_type: merge`) in the foreground with
the drafted subject and body. The agent takes them as given, re-verifies
mergeability defensively, merges, and cleans up the branch locally - it
doesn't rediscover, diff, or draft any of it itself. Relay its report.
