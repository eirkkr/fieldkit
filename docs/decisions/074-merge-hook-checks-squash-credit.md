# 074 - The merge hook checks the squash credit lines

## Decision

`hooks/pretooluse-merge-message.py` refuses a `gh pr merge` whose message lacks a `Co-authored-by` line for each commit author who is not the PR's author, the rule `conventions/git.md` calls Squash credit.

- The hook runs when the command gives a subject or a body, since either replaces GitHub's own message. It asks `gh pr view [<PR>] [-R <repo>] --json author,commits,url` for the PR's author and each commit's author login. The PR is the command's selector, or the current branch's when the command names none; a flag's value, in any of the forms `gh` accepts (`-t text`, `-t=text`, `-ttext`, bundled as `-st text`), is never read as the selector. A PR of 100 commits or more may have been cut short by `gh pr view`, so its commits are read again from the REST list (`gh api --paginate repos/<owner>/<repo>/pulls/<N>/commits`), which GitHub caps at 250: a PR with that many is refused.
- A line counts when it is a `Co-authored-by:` trailer in the message's last paragraph, and every line of that paragraph is a trailer, which is how git reads them (a credit directly under `Closes #N`, or after body text with no blank line, is not one), whose address is `<id>+<login>@users.noreply.github.com` for that login, whatever name precedes it. Logins compare without regard to case. A commit author with no login needs no line.
- Only a refusal makes a second call per missing author, `gh api users/<login> -q .id`, so the message can spell out the line to add. If that call fails the line carries `<id>`, and the refusal says it is a placeholder to fill in.
- A `Co-authored-by:` line may run past the 72-column body wrap. Its name, login and a nine-digit id can't be wrapped, and without the exemption the hook would demand a line that `conventions.py`'s wrap rule then refused. `commit-msg` shares the exemption.
- In a repo that reaches the kit, a `gh pr merge` the hook can't check is refused: a lookup that fails, runs past 15 seconds (25 for one merge's lookups together), or returns something unreadable or of an unexpected shape, with `gh`'s own error in the refusal; a body or subject the shell rewrites (`$name`, `$(...)` other than `$(cat <<'EOF' ...)`, a backtick) for the body, and a `--body-file` that can't be read as UTF-8 or a `-` with no single heredoc; and an error anywhere in the check, which the hook catches, because it is registered with `|| true` and a crash would otherwise let the merge through. A subject the shell rewrites skips only the subject's own checks, and the credit check still runs. The reviewer fixes the cause and retries the same merge; nothing was pushed, so an approval of the head stands.
- `gh` runs without `CLICOLOR_FORCE` and `GH_FORCE_TTY`, which make it colour its JSON, and with `NO_COLOR` and `GH_PROMPT_DISABLED` set.

## Reason

The rule had no enforcement: the merge skill points at it, and a merge that skipped the read landed without credit. PR #190 and PR #222 did, each opened by the bot account with commits authored by a human. A squash commit on the default branch cannot be amended afterwards, so a miss is permanent.

**Why a hook, not CI.** The squash message is written at merge time, after every PR check has run. A workflow on `push` to the default branch could see a missing line, but only once the commit is public.

**Why matching on the login, not the id.** The address's `<id>+<login>` form carries the login, so the check needs no user lookup to decide; the id is fetched only to word a refusal. A merge that passes costs one `gh` call.

**Why fail closed.** A squash commit cannot be amended, so a merge the hook couldn't check is the outcome the hook exists to prevent. This differs from the hook's other checks, which let through a command they can't parse (ADR 047): those read only the command's text, which is always at hand, while this one depends on the network and on a message the hook has to read. The cost is that a slow or signed-out `gh`, or a body written with `$VAR`, stops a merge until the reviewer fixes it and retries. The refusal for an unreadable body says to pass it with `--body-file -` and a quoted heredoc, the form the merge skill uses.

**Why exempt the credit line from the wrap.** The rule is mandatory and its line is unbreakable, like the URL the wrap rule already exempts. A PR author `bot` and a commit author `christopher-montgomery` with a nine-digit id gives a 98-character line that the hook demanded and then refused, so such a PR could not be merged.

Alternatives rejected:

- **Computing the lines in the skill.** The skill already says to; this is the case where an agent skipped it.
- **A `push`-triggered workflow.** It reports after the commit is public and cannot fix it.

## Consequences

- Every merge through Claude that gives a subject or a body now pays one `gh` call, and a refused one pays a second.
- A merge made in GitHub's UI is outside the hook, as for every other message rule. The UI adds these trailers itself.
- A PR whose commits are all by its own author needs no line, and the hook makes no call beyond the one.
- Some commands are not checked. A `gh pr merge` giving neither subject nor body leaves the message to GitHub, and a flag with no value is left to `gh` to refuse. A merge run another way (`gh -R x pr merge`, `env gh pr merge`, `command gh pr merge`, `bash -c '...'`, `gh api` to the merge endpoint) is not recognised, and a `cd` the hook doesn't follow (`pushd`, `git -C`, a subshell) can leave it judging the wrong directory. The hook guards against an agent skipping the rule, not against a determined bypass.
- A body the hook refuses as unreadable adds friction where a literal `$` is meant (`--body 'costs $HOME'`). The refusal says how to pass it.
- This ADR narrows two earlier ones: [047](047-enforce-commit-messages.md), which let a merge with no `--subject` through, now checks credit on a body alone; and [062](062-a-push-voids-merge-approval.md), whose `=` caveat for `--match-head-commit` no longer applies.
- The hook needs `gh` on the PATH and signed in, which the merge skill needs already. Without it the merge is refused, not let through.
- A merge command that names a PR `gh` can't find is refused by the hook before `gh pr merge` would have refused it. The outcome is the same.
