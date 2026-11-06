# Bot account reference

Background for [bot-account.md](bot-account.md): read the section a step points to, not the whole file.

## What the roles allow

Read and Triage cannot push; Write can ([repository roles for an organization](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/repository-roles-for-an-organization)). Only Admin can delete or transfer a repo, change its settings, or manage branch protection rules and rulesets. A personal repo has no roles to choose from: its collaborators can push and merge, and only the owner can delete or archive the repo, change its settings, or invite collaborators ([permission levels for a personal repository](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-personal-account-settings/permission-levels-for-a-personal-account-repository)).

What Write still allows, beyond pushing and opening pull requests ([repository roles](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/repository-roles-for-an-organization), not tried here): create, update and delete Actions secrets and variables (it cannot read a secret back, but code it pushes runs in pull request checks, which can use any secret those workflows are given); edit or delete other people's comments, including yours; transfer issues; create and edit releases; and dismiss Dependabot and code scanning alerts. Only Admin can delete an issue.

What the token leaves out: `workflow` (so no editing workflow files, which GitHub's scope page describes as its purpose), `project` (so `gh project` should fail), `read:org` (so some organization lookups, such as requesting a team as reviewer, may fail), `write:packages` and `gist` ([scopes](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps); none of this tried here). Whether `repo` covers reading code scanning alerts is not documented. Add a scope only if you use the feature, and each one widens what a leaked token can do.

What Write does not stop is pushing, force-pushing and deleting on a branch with no protection. A protected branch blocks force pushes and deletion by default ([about protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)), and an unprotected one has no such rule.

## Token scopes

`workflow` "grants the ability to add and update GitHub Actions workflow files" ([scopes for OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps)); without it the bot can still push a branch whose code CI runs.

A GitHub App installed on the repos is stricter still; this doc does not cover it (see [ADR 063](../docs/decisions/063-a-write-role-bot-account.md)).

## Plan limits

GitHub's plans page lists protected branches under "Advanced tools and insights in private repositories" for Pro and Team, does not list them for Free, and gives a free organization "unlimited private repositories with a limited feature set" ([GitHub's plans](https://docs.github.com/en/get-started/learning-about-github/githubs-plans)). That suggests a private repo on a free plan cannot have a ruleset or branch protection rule, so the bot can push to its default branch; the page does not say so outright, so this is inferred. Public repos are not affected. Without server-side protection, the only guards are local hooks and settings, which Claude can work around (see "Not covered here").

## Who gets credit

What lands on a profile's contribution graph follows the account an action is made under, and for commits the author email, not who pushed. GitHub's rules, checked on 2026-10-31 ([contributions on your profile](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference), [why contributions are not showing up](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/managing-contribution-settings-on-your-profile/why-are-my-contributions-not-showing-up-on-my-profile)): a commit counts only if its author email is linked to the account and it is on the default branch (or `gh-pages`) of a standalone repo; opening an issue, proposing a pull request and submitting a review also count, for the account that did them.

| What happens in an `as-bot` session | Credited to | Why |
| --- | --- | --- |
| A commit Claude makes | You, if git's `user.email` is yours (it is unless you set `GIT_AUTHOR_*`) | The commit stores its author; the pusher is not recorded. Tried: GitHub's API shows this branch's commits as authored by the user's account. |
| A pull request, issue or comment Claude opens with `gh` | The bot | It is made under the bot's login. |
| You approving or commenting on the bot's pull request | You | It is made under your login. |
| Squash-merging the bot's pull request | The bot, not you | The squash commit's author is whoever opened the pull request, and you are not on it. Tried on three squash merges in a public repo (vercel/next.js pull requests 100961, 100947 and 100935), where the pull request opener was credited although a bot had written the commit. The kit's `merge` skill squashes. |
| Rebase-and-merging it | The original commit authors (you) and whoever merged | GitHub's page says rebased commits credit "the original authors of the commit and the person who rebased the commits". Not tried here. |
| A merge commit | The merge commit, to whoever merges; the commits inside keep their authors | Tried on a public repo that merges with merge commits (cli/cli pull request 14879): the merge commit was authored by the merger. The inner commits keeping their authors is how git works. |

So with squash merges, which this kit uses, the commit that reaches the default branch is the bot's even when the work in it was committed under your email. To have it count for you, open the pull request yourself from the bot's pushed branch, or merge another way. To make the bot's commits the bot's, set `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL` and the `GIT_COMMITTER_` pair for `as-bot`. Contributions can take up to 24 hours to appear. Not tried: a merged pull request made end to end through `as-bot`.

## Terms

GitHub's terms allow a machine account: one "set up by an individual human who accepts the Terms on behalf of the Account, provides a valid email address, and is responsible for its actions", "used exclusively for performing automated tasks". "You may maintain no more than one free machine account in addition to your free Personal Account." ([GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service), section B.3.) So create the bot yourself, use it only for Claude's work, and keep to one free bot per person.

## Not covered here

- Settings and hooks that refuse destructive commands before they run: [Guard destructive git and gh commands with settings and hooks](https://github.com/eirkkr/fieldkit/issues/155).
- Keeping the user's own token out of Claude's reach, without which a bot account is not a wall: [Keep the user's own GitHub token out of Claude's reach](https://github.com/eirkkr/fieldkit/issues/154).
