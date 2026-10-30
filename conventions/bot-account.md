# A limited GitHub account for Claude

Claude runs `gh` and `git` with whatever token it finds, normally its user's own, so it can do anything its user can, including deleting a repo or editing its protection rules. A separate bot account whose role is write, never admin, takes the repo-admin actions out of reach. It does not stop a write-role bot pushing to a branch with no protection, or pushing a branch whose code CI then runs. Claims about GitHub below link their page and were checked on 2026-10-30.

## Which token

The token depends on who owns the repo, because GitHub's fine-grained tokens do not support a repository collaborator ([managing personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens), which lists "contributing to repositories as an outside collaborator or repository collaborator" as unsupported).

| The repo is owned by | The bot is | Token |
| --- | --- | --- |
| A personal account | A collaborator with the write role | Classic, `repo` scope, no `workflow` scope |
| An organization (optional) | An organization member with write on the repo | Fine-grained, with the repo selected |

- The fine-grained option has two preconditions: the bot is a member of the organization, not an outside collaborator, and the organization allows fine-grained tokens (it can require an owner to approve each one). Neither has been tried against a real organization, so treat this row as untried.
- A classic token reaches every repo the bot can reach, so the bot's role is its only limit.
- A GitHub App installed on the repos is stricter still, with per-repo permissions and tokens that expire after an hour. It needs a private key and token-minting code in front of `gh`, and this doc does not cover it.

## What the write role leaves out

On a personal repo, a collaborator can push, merge pull requests and manage issues. Only the owner can delete or archive the repo, change its settings, invite collaborators, or merge on a protected branch without the required approvals ([permission levels for a personal account repository](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-personal-account-settings/permission-levels-for-a-personal-account-repository)). In an organization the same split holds: deleting a repo, changing its settings, and managing branch protection rules and rulesets are admin-only, and write cannot push to a protected branch that requires a pull request ([repository roles for an organization](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/repository-roles-for-an-organization)).

What write does not stop is the bot pushing, force-pushing and deleting on a branch that has no protection. A protected branch blocks force pushes and deletion by default, and an unprotected one has no such rule ([about protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)).

## Token scopes

- **Classic:** `repo` only. Leave `workflow` off: it is what lets a token add or change workflow files, and without it the bot cannot edit workflow files directly, though it can still push a branch whose code CI runs ([scopes for OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps), which says `workflow` "grants the ability to add and update GitHub Actions workflow files").
- **Fine-grained:** select only the repos the bot works in, and set Contents, Pull requests and Issues to read and write. Give it no Administration permission.

## Protecting the default branch

Protect the default branch with a ruleset or a branch protection rule that requires a pull request and blocks force pushes and deletion. Only an admin can edit it, so a write-role bot cannot lift it.

Where it is available depends on the plan. GitHub's plans page lists protected branches under "Advanced tools and insights in private repositories" for Pro and Team, does not list them for Free, and describes Free as "unlimited public repositories with a full feature set" ([GitHub's plans](https://docs.github.com/en/get-started/learning-about-github/githubs-plans)). That suggests private repos on a free plan have no server-side protection, so the bot could push to their default branch, but the page does not say so outright: check your plan before relying on either reading. Without server-side protection, the only guards are local hooks and settings, which Claude can work around (see "Not covered here").

## Not covered here

- Settings and hooks that refuse destructive commands before they run: [Guard destructive git and gh commands with settings and hooks](https://github.com/eirkkr/fieldkit/issues/155).
- Keeping the user's own token out of Claude's reach, without which a bot account protects nothing: [Keep the user's own GitHub token out of Claude's reach](https://github.com/eirkkr/fieldkit/issues/154).

## Setting up and checking

`.fieldkit/scripts/setup-bot-account.sh owner/name` (`scripts/` in the kit itself) prints the steps for creating the bot, inviting it and making a token, then checks the token against a repo with read-only calls. The bot's token goes in `GH_TOKEN`, never an argument, so it stays out of the process list and shell history. It exits 0 when the token does not have admin on the repo, 1 when it does, and 2 on a usage error, no token, an invalid token, an API error, or a missing `gh`.

The script checks admin only: not that the role is exactly write, and not which scopes a classic token has. It shows whether the default branch has a protection rule or a ruleset, and cannot show that the protection would stop this bot without pushing to it.

Two things here are untried: that a fine-grained token on an organization member can reach an organization repo, and that the repo endpoint returns `permissions` for both kinds of token.
