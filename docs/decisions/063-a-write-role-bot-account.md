# 063 - Give Claude a write-role bot account

## Decision

Claude acts on GitHub as a separate bot account, a machine account under GitHub's terms, whose role on each repo is write, never admin. One classic token with the `repo` scope serves every repo; it has no `workflow` scope, so the bot cannot add or edit workflow files. A personal repo invites the bot as a collaborator; an organization repo makes the bot a member with write on the repo. The default branch is protected by a ruleset that requires a pull request, one approval from a code owner that is dismissed when new commits are pushed, and the CI's required checks accepted from GitHub Actions only, with the owner's admin role allowed to bypass it for pull requests only, so the bot's pull requests need the owner's approval and it cannot merge its own. Claude runs as the bot through `scripts/as-bot.sh`, which reads the token from `~/.config/bot-account/token` and sets `GH_TOKEN` and points git's credentials at `gh`. [conventions/bot-account.md](../../conventions/bot-account.md) gives the steps, with the token, scope and checks, and `scripts/check-bot-account.sh` checks the bot's token against a repo.

## Reason

Claude uses whatever token `gh` holds, normally its user's own, so it can do anything the user can: delete a repo, edit protection rules, force-push. A role-limited account removes the repo-admin actions, whether Claude errs or its token leaks, and the cap sits in GitHub's role model, outside anything Claude can edit. It does not remove what write allows, such as pushing to an unprotected branch or pushing code that CI runs. Write, not a lower role, because it is the lowest role that can push a branch (Read and Triage cannot), and not Maintain, which adds repository management the bot does not need.

The approval gate exists because the bot, with Write, could otherwise open a pull request and merge it itself once the checks pass. Code owner review limits whose approval counts to the people listed, which the bot is not. Stale approvals are dismissed because the bot, with Write, could otherwise push a different commit after being approved. Required checks are pinned to GitHub Actions because any account with write access can post a commit status by hand.

Rejected:

- **A fine-grained token on the user's own account.** It narrows the token but leaves the identity: the account still has admin, and any repo the token reaches is reached as an admin.
- **A fine-grained token on the bot.** It is narrower, but it reaches one owner only and, per GitHub, cannot reach a repo where the bot is a collaborator ([managing personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)). A session holds one token, so it could not work on a personal repo and an organization's repos together. Dropped to keep one path.
- **A GitHub App installed on the repos.** Per-repo permissions and short-lived tokens make it the strictest option, but it needs a private key and token-minting code in front of `gh`. The doc names it as the stricter option and does not cover it.
- **No approval requirement.** The bot could open a pull request and merge it itself once the checks pass, so the only stop would be an instruction to ask.
- **Required approvals alone, without code owners.** The bot has Write, so its approval of the user's pull requests would count, and the user could not approve their own.
- **Naming the user in the bypass list.** GitHub's bypass list takes roles, teams and apps, not individual users ([creating rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)), so the admin role is used; on a personal repo that is only the owner.
- **Moving every repo into an organization.** It would allow fine-grained tokens everywhere, but it moves repos and changes ownership to suit a token.
- **A skill in place of the script.** The user runs the check rarely, and a skill's description would load into every consumer session ([ADR 060](060-budget-the-always-loaded-context.md)).

## Consequences

- The classic token reaches every repo the bot can reach, so the role is the only limit, and it must stay at write.
- An organization that blocks classic tokens is not served by this doc.
- The checks still run code the bot can change, so a green check on a bot's pull request shows less than one on the user's, and the user reads the diff before approving. Read-only default workflow permissions, no "create and approve pull requests" and no auto-merge keep what that code can reach small.
- The approval gate has not yet been tried.
- With squash merges, which the kit uses, the commit that reaches the default branch is credited to whoever opened the pull request, so a bot-opened pull request puts the bot's name on it even when the commits inside carry the user's email. The doc's "Who gets credit" gives the cases and the ways round it.
- The bot can still push, force-push and delete on a default branch with no protection. GitHub's plans page lists protected branches for private repos under Pro and Team and not Free, which suggests a private repo on a free plan stays open to the bot; the doc says that and does not recommend a plan.
- The classic token was tried against a personal repo and an organization's repo, running Claude as the bot. The doc says so.
- GitHub's terms allow one free machine account per person, created by a human and used only for automated tasks, so the user creates the bot and it does nothing else.
- A bot account is not a wall while the user's own token is readable on the same machine, and settings and hooks that refuse destructive commands are not yet written. Both are separate work: [keeping the user's token out of Claude's reach](https://github.com/eirkkr/fieldkit/issues/154), and [guarding destructive git and gh commands](https://github.com/eirkkr/fieldkit/issues/155).
