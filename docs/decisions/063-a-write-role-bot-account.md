# 063 - Give Claude a write-role bot account

## Decision

Claude acts on GitHub as a separate bot account, a machine account under GitHub's terms, whose role on each repo is write, never admin. A personal repo invites the bot as a collaborator and uses a classic token; an organization repo can instead make the bot a member, give it write directly or through a team, and use a fine-grained token, as an option. [conventions/bot-account.md](../../conventions/bot-account.md) gives the two paths as steps, with the tokens, scopes and checks, and `scripts/setup-bot-account.sh` prints the chosen path's steps and checks the result.

## Reason

Claude uses whatever token `gh` holds, normally its user's own, so it can do anything the user can: delete a repo, edit protection rules, force-push. A role-limited account removes the repo-admin actions, whether Claude errs or its token leaks, and the cap sits in GitHub's role model, outside anything Claude can edit. It does not remove what write allows, such as pushing to an unprotected branch or pushing code that CI runs. Write, not a lower role, because it is the lowest role that can push a branch.

Rejected:

- **A fine-grained token on the user's own account.** It narrows the token but leaves the identity: the account still has admin, and any repo the token reaches is reached as an admin.
- **A fine-grained token on the bot everywhere.** GitHub's fine-grained tokens do not support a repository collaborator, so the bot could not reach a personal repo with one. Only the organization case works.
- **A GitHub App installed on the repos.** Per-repo permissions and short-lived tokens make it the strictest option, but it needs a private key and token-minting code in front of `gh`. The doc mentions it as the stricter option and does not cover it.
- **Moving every repo into an organization.** It would allow fine-grained tokens everywhere, but it moves repos and changes ownership to suit a token.
- **A classic token for organization repos too.** It works, but where the bot can be a member a fine-grained token is narrower, so the doc offers that instead.
- **A skill in place of the script.** The user runs the setup once, and a skill's description would load into every consumer session ([ADR 060](060-budget-the-always-loaded-context.md)).

## Consequences

- A classic token reaches every repo the bot can reach, so the role is the only limit, and it must stay at write.
- The bot can still push, force-push and delete on a default branch with no protection. GitHub's plans page lists protected branches for private repos under paid plans only, which suggests a private repo on a free plan stays open to the bot; the doc says that and does not recommend a plan.
- The fine-grained option was tried once against an organization's private repos on a free plan; the classic token for a personal repo is untried. The doc says which.
- GitHub's terms allow one free machine account per person, created by a human and used only for automated tasks, so the user creates the bot and it does nothing else.
- A bot account does nothing while the user's own token is readable on the same machine, and settings and hooks that refuse destructive commands are not yet written. Both are separate work: [keeping the user's token out of Claude's reach](https://github.com/eirkkr/fieldkit/issues/154), and [guarding destructive git and gh commands](https://github.com/eirkkr/fieldkit/issues/155).
