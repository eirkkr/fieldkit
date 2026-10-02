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
infer a number - take every number from two sources. Ask GitHub what this
PR closes: `gh pr view --json closingIssuesReferences -q
'.closingIssuesReferences[].number'`. And read the PR body's own
closing-keyword lines (`Closes #X`, `Fixes #X`, `Resolves #X`), keeping
only those that pass
`gh api repos/{owner}/{repo}/issues/<N> -q '.pull_request.url // "issue"'`
(any output but `issue` means `N` is a PR). GitHub's answer can be empty at
merge time though the body names an issue, and an issue it has not linked
stays open on merge, so the footer is what closes it. Write each as
`Closes #X`. With no number from either, omit the line rather than
substituting the PR's own number.

The message follows `conventions/git.md`'s Commits rules, with `(#<PR>)`
ending the subject and counting toward its 72. A `!` title's
`BREAKING CHANGE:` line comes over from the PR body into the squash body.
The kit's merge-message hook refuses a merge that doesn't, saying what to
fix.

Then merge, in this turn:

1. If any checks are still running, wait for them: `gh pr checks --watch
   --fail-fast --interval 15`, with a Bash timeout up to the 600000ms
   maximum. If every check passes, continue. If one fails, stop and report
   which - never merge on anything less than every check finished and
   passed. If the wait times out first, stop and report that CI is still
   running; `/merge` can be run again later.
2. Push the branch if local commits aren't on the remote yet.
3. Run `gh pr merge <PR> --squash` with the drafted subject and body - the
   body through `--body-file -` and a heredoc, so it keeps its line breaks.
4. Clean up locally: switch to the default branch (`gh repo view --json
   defaultBranchRef -q .defaultBranchRef.name`), force-delete the merged
   branch (`git branch -D <branch>` - a squash merge isn't recognised as
   merged by plain `-d`), and `git pull --prune`.
5. Report the PR number and URL, and that it merged and was cleaned up - or
   what is still blocking it.

These steps run here rather than in a subagent
([ADR 045](../../docs/decisions/045-inline-git-skills.md)).
