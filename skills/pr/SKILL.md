---
name: pr
description: Draft and open a pull request for the current branch
argument-hint: "[short summary of the change, optional]"
---

# Open a pull request via a delegated agent

If there's uncommitted work, or the branch isn't pushed yet - including
still being on the default branch, with no branch to open a PR from at all -
follow `skills/push/SKILL.md` first: decide the branch, commit message, and
file list, and dispatch its `push` subagent. Pushing is already
ungated/act-then-show regardless of how this skill was reached, so there's
nothing to ask separately before doing it.

Decide the title and body yourself, from context already in hand plus
`conventions/git.md`/`conventions/github.md`'s conventions - read
`git log <base>..HEAD` / `git diff <base>...HEAD` yourself if you need the
branch's full change set to pin them down:

- Title: Conventional Commits format, under 70 characters.
- Body: 1-3 bullet summary points plus a test plan checklist.
- Add `Closes #X` only when the brief or the branch's work names a tracked
  issue, and only after confirming `X` is an issue, not a PR - issues and
  PRs share one number space, and `gh issue view <N>` returns a *PR* just as
  happily, so it proves nothing. Use `gh api repos/{owner}/{repo}/issues/<N>
  -q '.pull_request.url // "issue"'` - any output but `issue` means `N` is a
  PR number, so the line is wrong. With no number in hand, omit the line
  entirely; don't go looking for one to fill the slot.

Launch the `pr` subagent (`subagent_type: pr`) in the foreground with the
title and body stated explicitly, plus `$ARGUMENTS` for whatever extra
context was given. The agent takes them as given, and assumes the branch is
already pushed - it doesn't rediscover, diff, push, or second-guess any of
it. It runs `gh pr create` itself - don't run it here, and don't read its
report as a draft awaiting a second dispatch. Relay that report (the PR
link, title, and body - or an existing PR's URL if one was already open on
this branch, in which case there was nothing to create).

Everything handed to the agent as title or body is published verbatim, so
keep directives out of it - "don't add X", "use the wording below", notes
about what not to do - or they end up in the PR for everyone to read. Those
belong in the surrounding prompt, not inside the text being posted. Read the
body back after it's opened (`gh pr view --json body`), which is also what
catches it when this goes wrong.

Reaching this skill already means opening the PR is approved - either the
user typed `/pr` directly, or the caller asked and got a yes first. So the
agent opens it straight away, with no review of the draft in between;
surfacing the link, title, and body afterward is what lets it be corrected
if it's off.
