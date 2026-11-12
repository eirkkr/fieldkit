# 071 - The bot's token carries read:org

## Decision

The bot's classic token has the `repo` and `read:org` scopes, still without `workflow`. A token made to the old instructions is `repo` only; its scopes are edited in GitHub's settings, not remade. The skills run `gh pr edit` with no fallback.

This amends [063](063-a-write-role-bot-account.md), which gave the token the `repo` scope only.

## Reason

With a `repo`-only token, `gh pr edit` fails: it sends a GraphQL query that asks for organization and login fields, and GitHub answers "Your token has not been granted the required scopes" (the `login` field needs `read:org`; `name` and `slug` need `read:org` or `read:discussion`). `gh pr checks --watch` prints the same error. The kit worked round it with a REST call, `gh api -X PATCH`, written into two skills and two docs. Tested on 2026-11-11: after `read:org` was added to the bot's existing classic token, `gh pr edit <n> --body-file <file>` succeeded, with no new token and no other change. The scope list was the only thing forcing the workaround.

The cost is that a leaked token can also read organization membership. The `repo` scope already reaches far more than that, and the role, not the scope list, is what keeps the bot from admin actions.

Rejected:

- **Keep the REST workaround.** Every skill that edits a pull request carries a branch for a failure the token's scopes cause, and a reader of the docs learns a second way to do an edit `gh` already does.
- **Keep the workaround as a one-line fallback for `repo`-only tokens.** It leaves the old text in the skills for a case the doc now tells the reader to fix at the token.
- **`read:discussion` in place of `read:org`.** It covers `name` and `slug` but not `login`, which the query also asks for; not tried.

## Consequences

- A `repo`-only token still fails at `gh pr edit`, with the scope error above, until its scopes are edited; the other `gh` commands the skills use worked with it.
- `scripts/check-bot-account.sh` still does not check which scopes a classic token has, so a `repo`-only token passes it.
