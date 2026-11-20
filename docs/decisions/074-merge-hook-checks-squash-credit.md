# 074 - The merge hook checks the squash credit lines

## Decision

`hooks/pretooluse-merge-message.py` refuses a `gh pr merge` whose message lacks a `Co-authored-by` line for each commit author who is not the PR's author, the rule `conventions/git.md` calls Squash credit.

- The hook asks `gh pr view [<PR>] --json author,commits` for the PR's author and each commit's author login. The PR is the command's selector, or the current branch's when the command names none.
- A line counts when it is a `Co-authored-by:` trailer whose address is `<id>+<login>@users.noreply.github.com` for that login, whatever name precedes it. Logins compare without regard to case. A commit author with no login needs no line.
- Only a refusal makes a second call, `gh api users/<login> -q .id`, so the message can spell out the line to add.
- A lookup that fails, times out (15 seconds) or returns something unreadable refuses the merge, saying the PR's authors couldn't be read. The reviewer fixes `gh` and retries.

## Reason

The rule had no enforcement: the merge skill points at it, and a merge that skipped the read landed without credit. Two merges in the repo's history did, each a PR the bot account opened with commits authored by a human. A squash commit on the default branch cannot be amended afterwards, so a miss is permanent.

**Why a hook, not CI.** The squash message is written at merge time, after every PR check has run. A workflow on `push` to the default branch could see a missing line, but only once the commit is public.

**Why matching on the login, not the id.** The address's `<id>+<login>` form carries the login, so the check needs no user lookup to decide; the id is fetched only to word a refusal. A merge that passes costs one `gh` call.

**Why fail closed.** A squash commit cannot be amended, so a merge the hook couldn't check is the outcome the hook exists to prevent. This differs from the hook's other checks, which let through a command they can't parse (ADR 047): those read only the command's text, which is always at hand, while this one depends on the network. The cost is that a slow or signed-out `gh` stops a merge until the reviewer fixes it and retries.

Alternatives rejected:

- **Computing the lines in the skill.** The skill already says to; this is the case where an agent skipped it.
- **A `push`-triggered workflow.** It reports after the commit is public and cannot fix it.

## Consequences

- Every merge through Claude now pays one `gh` call, and a refused one pays a second.
- A merge made in GitHub's UI is outside the hook, as for every other message rule. The UI adds these trailers itself.
- A PR whose commits are all by its own author needs no line, and the hook makes no call beyond the one.
- The hook needs `gh` on the PATH and signed in, which the merge skill needs already. Without it the merge is refused, not let through.
- A merge command that names a PR `gh` can't find is refused by the hook before `gh pr merge` would have refused it. The outcome is the same.
