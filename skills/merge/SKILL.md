---
name: merge
description: Merge the current branch's pull request via squash merge
---

# Merge a pull request

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
here: draft as normal, and wait for them below. Reaching
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

Then merge, in this turn:

1. If any checks are still running, wait for them: `gh pr checks --watch
   --fail-fast --interval 15`, with a Bash timeout up to the 600000ms
   maximum. If every check passes, continue. If one fails, stop and report
   which - never merge on anything less than every check finished and
   passed. If the wait times out first, stop and report that CI is still
   running; `/merge` can be run again later.
2. Push the branch if local commits aren't on the remote yet.
3. Run `gh pr merge --squash` with the drafted subject and body.
4. Clean up locally: switch to the default branch (`gh repo view --json
   defaultBranchRef -q .defaultBranchRef.name`), force-delete the merged
   branch (`git branch -D <branch>` - a squash merge isn't recognised as
   merged by plain `-d`), and `git pull --prune`.
5. Report the PR number and URL, and that it merged and was cleaned up - or
   what is still blocking it.

These steps run here rather than in a subagent
([ADR 045](../../docs/decisions/045-inline-git-skills.md)).
