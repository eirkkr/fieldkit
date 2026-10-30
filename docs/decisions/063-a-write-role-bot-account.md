# 063 - Give Claude a write-role bot account

## Decision

Claude acts on GitHub as a separate bot account whose role on each repo is write, never admin. A personal repo invites the bot as a collaborator and uses a classic token with the `repo` scope and no `workflow` scope. An organization repo can instead make the bot a member and use a fine-grained token limited to the repos it works in, which is an option, not the default. [conventions/bot-account.md](../../conventions/bot-account.md) says how, and `scripts/setup-bot-account.sh` walks the user through it and checks the result.

## Reason

Claude uses whatever token `gh` holds, normally its user's own, so it can do anything the user can: delete a repo, edit protection rules, force-push. A role-limited account removes the admin-only actions in every case, whether Claude errs or its token leaks, and the cap sits in GitHub's role model, outside anything Claude can edit.

Rejected:

- **A fine-grained token on the user's own account.** It narrows the token but leaves the identity: the account still has admin, and any repo the token reaches is reached as an admin.
- **A fine-grained token on the bot everywhere.** GitHub's fine-grained tokens do not support a repository collaborator, so the bot could not reach a personal repo with one. Only the organization case works.
- **A GitHub App installed on the repos.** Per-repo permissions and tokens that expire after an hour make it the strictest option, but it needs a private key and token-minting code in front of `gh`. The doc names it as the upgrade, and it is left as work not yet specified.
- **Moving every repo into an organization.** It would allow fine-grained tokens everywhere, but it moves repos and changes ownership to suit a token.
- **A classic token on the bot everywhere.** It is what the personal-repo case uses, but where the bot can be an organization member a fine-grained token is narrower, so the doc offers it.

The script, not a skill, because the user runs it once, and a skill's description would load into every consumer session ([ADR 060](060-budget-the-always-loaded-context.md)).

## Consequences

- A classic token reaches every repo the bot can reach, so the role is the only limit. The doc says to keep it at write.
- The bot can still push, force-push and delete on a default branch with no protection. On private repos, protection needs a paid plan, so a private repo on a free plan stays open to the bot. The doc states this and does not recommend a plan.
- The fine-grained option and the repo endpoint's `permissions` field for both token kinds are untried against a real account. The doc marks both.
- A bot account does nothing while the user's own token is readable on the same machine, and settings and hooks that refuse destructive commands are not yet written. Both are separate work: keeping the user's token out of Claude's reach, and guarding destructive git and gh commands.
