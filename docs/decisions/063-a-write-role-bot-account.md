# 063 - Give Claude a write-role bot account

## Decision

Claude acts on GitHub as a separate bot account, a machine account under GitHub's terms, whose role on each repo is write, never admin. One classic token with the `repo` scope serves every repo. A personal repo invites the bot as a collaborator; an organization repo makes the bot a member with write on the repo. Claude runs as the bot through a script that sets `GH_TOKEN` and points git's credentials at `gh`. [conventions/bot-account.md](../../conventions/bot-account.md) gives the steps, with the token, scope and checks, and `scripts/check-bot-account.sh` checks the bot's token against a repo.

## Reason

Claude uses whatever token `gh` holds, normally its user's own, so it can do anything the user can: delete a repo, edit protection rules, force-push. A role-limited account removes the repo-admin actions, whether Claude errs or its token leaks, and the cap sits in GitHub's role model, outside anything Claude can edit. It does not remove what write allows, such as pushing to an unprotected branch or pushing code that CI runs. Write, not a lower role, because it is the lowest role that can push a branch.

Rejected:

- **A fine-grained token on the user's own account.** It narrows the token but leaves the identity: the account still has admin, and any repo the token reaches is reached as an admin.
- **A fine-grained token on the bot.** It is narrower, but it reaches one owner only and, per GitHub, cannot reach a repo where the bot is a collaborator. A session holds one token, so it could not work on a personal repo and an organization's repos together. Dropped to keep one path.
- **A GitHub App installed on the repos.** Per-repo permissions and short-lived tokens make it the strictest option, but it needs a private key and token-minting code in front of `gh`. The doc mentions it as the stricter option and does not cover it.
- **Moving every repo into an organization.** It would allow fine-grained tokens everywhere, but it moves repos and changes ownership to suit a token.
- **A skill in place of the script.** The user runs the check rarely, and a skill's description would load into every consumer session ([ADR 060](060-budget-the-always-loaded-context.md)).

## Consequences

- The classic token reaches every repo the bot can reach, so the role is the only limit, and it must stay at write.
- An organization that blocks classic tokens is not served by this doc.
- The bot can still push, force-push and delete on a default branch with no protection. GitHub's plans page lists protected branches for private repos under Pro and Team and not Free, which suggests a private repo on a free plan stays open to the bot; the doc says that and does not recommend a plan.
- The classic token was tried against a personal repo; an organization's repos with a classic token are untried. The doc says so.
- GitHub's terms allow one free machine account per person, created by a human and used only for automated tasks, so the user creates the bot and it does nothing else.
- A bot account does nothing while the user's own token is readable on the same machine, and settings and hooks that refuse destructive commands are not yet written. Both are separate work: [keeping the user's token out of Claude's reach](https://github.com/eirkkr/fieldkit/issues/154), and [guarding destructive git and gh commands](https://github.com/eirkkr/fieldkit/issues/155).
