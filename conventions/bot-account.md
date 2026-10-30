# A limited GitHub account for Claude

Claude runs `gh` and `git` with whatever token it finds, normally its user's own, so it can do anything its user can, including deleting a repo or editing its protection rules. A separate bot account whose role is Write, never Admin, takes the repo-admin actions out of reach. It does not stop a Write-role bot pushing to a branch with no protection, or pushing a branch whose code CI then runs.

Claims about GitHub below link their page and were checked on 2026-10-30.

## Decide your path

| The repos are owned by | Path | The bot is | Token |
| --- | --- | --- | --- |
| Your personal account | A | A collaborator on each repo | Classic, `repo` scope only |
| An organization | B | An organization member, with Write on each repo | Fine-grained, for the organization, with the repos selected |

The token type follows the owner because GitHub's fine-grained tokens do not support contributing "to repositories where the user is an outside or repository collaborator" ([managing personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)). So on path B the bot has to be a member of the organization, not a collaborator on its repos. A fine-grained token also reaches one owner only, so repos owned by two organizations need a token for each.

Path B was tried once, with a fine-grained token on private repos in an organization on a free plan. Path A, with a classic token, is untried.

## You need

- `gh`, the GitHub CLI, and a bash shell. In zsh, `read -rs -p "Bot token: " X` fails; write it as `read -rs "X?Bot token: "` in steps 6 and 7, and use `~/.zshrc` in step 7.
- To own the repos (path A), or to be an Owner of the organization (path B): inviting the bot, making a team and approving the token all need one.

## Steps

Each step says what it should look like when it worked. Use a private browser window for the bot, so you stay logged in as yourself in the other.

### 1. Create the bot account

Sign up at github.com in the private window. Give the bot its own email address: GitHub's terms require a valid one for each account ([Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service), section B.2). A plus address such as `you+claude@example.com` arrives in your own inbox if your provider supports plus addressing, and is a different address to GitHub; this has not been tried here.

Turn on two-factor authentication for the bot: your profile picture at the top right, Settings, Password and authentication, Enable two-factor authentication ([configuring two-factor authentication](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/configuring-two-factor-authentication)). The bot's password and recovery codes are as worth protecting as your own.

Worked when: you can log in as the bot, and it asks for a second factor.

### 2. Give the bot access

**Path A, a personal repo.** As yourself, open the repo, then Settings, Collaborators, Add people, and pick the bot ([inviting collaborators](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-access-to-your-personal-repositories/inviting-collaborators-to-a-personal-repository)). A personal repo has one collaborator level, which can push and merge but not change settings or delete the repo; there is no role to choose ([permission levels](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-personal-account-settings/permission-levels-for-a-personal-account-repository)). As the bot, accept the invitation from its email. Repeat for each repo.

**Path B, an organization.** First make the bot a member: as an owner, open the organization, then People, Invite member, and leave its role as Member, never Owner ([inviting users](https://docs.github.com/en/organizations/managing-membership-in-your-organization/inviting-users-to-join-your-organization)). An owner has "complete administrative access" to the organization ([roles in an organization](https://docs.github.com/en/organizations/managing-peoples-access-to-your-organization-with-roles/roles-in-an-organization)). As the bot, accept the invitation. As an owner, also check Settings, Member privileges, Base permissions: it applies to every member on every repo of the organization, so it must not be Admin. Lowering it also changes what every human member can reach, so if it is already No permission or Read, leave it ([base permissions](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/setting-base-permissions-for-an-organization)).

Then give it Write on each repo, one of two ways:

- **Through a team, for several repos.** Create a team (Teams, New team, for example `bots`) ([creating a team](https://docs.github.com/en/organizations/organizing-members-into-teams/creating-a-team)) and add the bot to it. In each repo, open Settings, Collaborators and teams, Add teams, pick the team, and choose the Write role. A later repo then needs one step, and every bot on the team gets the same role.
- **Directly, for one repo.** In the repo, open Settings, Collaborators and teams, Add people, pick the bot, and choose Write ([managing access to a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-teams-and-people-with-access-to-your-repository)).

Worked when: on path A, the bot is listed as a collaborator, not pending. On path B, the repo's Collaborators and teams page lists the bot, or its team, with Write.

### 3. Make the bot's token

Log in as the bot, then your profile picture at the top right, Settings, Developer settings, Personal access tokens. Set an expiration you will remember to renew.

**Path A, a classic token.** Tokens (classic), Generate new token, Generate new token (classic). Tick `repo` and nothing else; leave `workflow` unticked, so the bot cannot add or edit workflow files. Generate token, and copy it: it is shown once.

**Path B, a fine-grained token.** Fine-grained tokens, Generate new token, then:

- **Resource owner:** the organization. Left as the bot itself, the token reaches none of the organization's private repos.
- **Repository access:** Only select repositories, and pick every repo the bot works in.
- **Permissions:** under repository permissions, set Contents, Issues and Pull requests to Read and write. Leave Administration and the rest at no access (Metadata switches to Read-only by itself).

Generate token, and copy it. If the organization requires approval, an owner must now approve the token: the organization's Settings, Personal access tokens, Pending requests, the token, Approve ([managing token requests](https://docs.github.com/en/organizations/managing-programmatic-access-to-your-organization/managing-requests-for-personal-access-tokens-in-your-organization)). Until then it cannot reach anything that is not public: "an organization owner must approve the token before it can be used to access any resources that are not public", so a private repo looks missing to it. An owner can also block fine-grained tokens for the whole organization ([token policy](https://docs.github.com/en/organizations/managing-programmatic-access-to-your-organization/setting-a-personal-access-token-policy-for-your-organization)); then a classic token made as in path A may work for its repos, unless the organization restricts classic tokens too on the same page. It reaches every repo the bot can reach, which includes every repo the base permission opens to members.

Worked when: the token is listed on the bot's token page. On path B, an owner sees it under the organization's Settings, Personal access tokens, Active tokens, not Pending requests.

### 4. Protect the default branch

A private repo on a free plan most likely cannot have this: see "Plan limits" below. If so, skip the step and know that the bot can push, force-push and delete on the default branch.

As yourself, open the repo, then Settings, Rulesets in the sidebar, New ruleset, New branch ruleset ([creating rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)). Set Enforcement status to Active, add the default branch as a target, and turn on Restrict deletions, Block force pushes, and Require a pull request before merging ([available rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)). Create. Only an admin (on a personal repo, the owner) can manage rulesets, so the bot cannot lift it.

Three things this does not do. It applies to you too, unless you add yourself to the ruleset's bypass list. It does not stop the bot merging its own pull request: with no approvals required, it can open one and merge it at once; setting Required approvals to 1 stops that, and then you approve each of the bot's pull requests yourself; on an organization repo, add yourself to the bypass list too, or your own pull requests need someone else's approval. And it covers branches only: a bot with Write can also push tags, so if pushing a tag runs a release workflow, add a ruleset that targets tags and restricts their creation, updates and deletion.

Worked when: the ruleset is listed as Active, or you have confirmed your plan does not offer it.

### 5. Run the check script

```bash
.fieldkit/scripts/setup-bot-account.sh <owner>/<repo>
```

In the kit itself the script is `scripts/setup-bot-account.sh`. In a consumer repo the kit is reached through its `.fieldkit` link, as above. You have done steps 1 to 4, so answer `s` when it asks who owns the repo to skip its short copy of them. It then asks for the bot's token without showing it; the token is never an argument, so it stays out of the process list. Paste it at the prompt: a `GH_TOKEN=...` prefix on the command is recorded in your shell history. It only reads from GitHub and stores nothing.

| Line | Means |
| --- | --- |
| `pass: the token belongs to <login>` | The token works. `<login>` must be the bot, not you. |
| `note: <repo> is owned by ...` | Which path applies. If it is not the one you followed, you made the wrong kind of token. |
| `pass: <login> does not have admin on <repo>` | Good. Exit status 0. |
| `note: <login> cannot push to <repo>` | No admin, but no Write either: the invitation, team, token approval or `repo` scope is missing. Exit status 0. |
| `fail: <login> has admin on <repo>` | On path A, only the owner has admin, so this is your token, not the bot's. On path B, lower its role to Write: check it is a Member, not an Owner, that no team gives it Admin, and that the base permission is not Admin. Exit status 1. |
| `note: ... is protected` | A branch protection rule or ruleset applies. The script cannot tell whether it would stop the bot; test 1 below does. |
| `note: ... has no branch protection rule or ruleset` | The bot can push to, force-push and delete the default branch. |
| `note: the ... lookup (repos/...) failed: ...` | That protection lookup was refused, with GitHub's message. For the ruleset lookup on a private repo, the likely reason is a plan without protection. |
| `note: the default branch name is empty or has characters this check does not look up` | Check its protection in the repo's Settings, Rulesets. |
| `note: the protection lookups gave answers this check cannot read` | Treat the default branch as unprotected until test 1 below is refused. |
| `GitHub refused the token (HTTP 401)` | Mistyped, expired or revoked. Make a new one. |
| `GitHub answered 404 Not Found for repos/...` | The token cannot see the repo. See below. |

Exit status 2 means the script stopped on an error, and its message says which. A failed protection lookup is only a note.

A 404 on the repo, when the name is right, usually means one of these:

- Path B: the token is still pending an owner's approval (step 3).
- Path B: the token's resource owner is the bot, not the organization.
- Path B: the repo was not picked under Only select repositories.
- Path A: the classic token was made without the `repo` scope.
- Either path: the bot has not accepted its invitation, or is not yet on the team with access.

The script checks Admin and whether the bot can push: not that the role is exactly Write, and not which scopes a classic token has.

### 6. Test by hand

Run these in your own terminal with the bot's token, one at a time. They use only `gh`, and when every command succeeds they leave nothing behind but a closed pull request. If a run stops partway, delete the leftover branch with `gh api -X DELETE repos/<owner>/<repo>/git/refs/heads/bot-check` before running again.

```bash
read -rs -p "Bot token: " GH_TOKEN; export GH_TOKEN; echo
gh api user -q .login   # must print the bot's login; if it prints yours, STOP and run: unset GH_TOKEN
R=<owner>/<repo>
B=$(gh api repos/$R -q .default_branch)
SHA=$(gh api repos/$R/git/ref/heads/$B -q .object.sha)
# 1. writing straight to the default branch: refused only if the branch is protected. SKIP this on a repo without protection: it succeeds, as a real commit that triggers any push workflow
gh api -X PUT repos/$R/contents/bot-check.txt -f message="bot check" -f content="$(printf hi | base64)" -f branch=$B
# 2. branch, commit, PR: should all work
gh api -X POST repos/$R/git/refs -f ref=refs/heads/bot-check -f sha=$SHA
gh api -X PUT repos/$R/contents/bot-check.txt -f message="bot check" -f content="$(printf hi | base64)" -f branch=bot-check
gh pr create -R $R --head bot-check --base $B --title "Bot check" --body "Throwaway, closing now."
gh pr close -R $R bot-check --delete-branch
# 3. an admin-only read: should be refused (403 or 404)
gh api repos/$R/hooks
unset GH_TOKEN
```

What a good result looks like:

1. On a protected branch, an error that names the rule or protection, and no new commit on the default branch. An error about `sha` is not a refusal: it means `bot-check.txt` already exists there. If the command succeeds, the protection does not cover the bot: delete `bot-check.txt` from the default branch in the web interface and check the ruleset.
2. Each command prints JSON or a URL, the pull request opens, and the close deletes the `bot-check` branch.
3. `HTTP 403` or `HTTP 404`. A list of webhooks, even an empty `[]`, means the token has Admin. On path B this tests the token's permissions, not the bot's role; the script's admin check covers the role.

### 7. Run Claude as the bot

Keep the bot's token in a file only you can read, and start Claude through a small wrapper that loads it. The token is the limited credential, so it is fine for Claude to read it; anything with more power than that is not. These commands are for bash; in zsh, save the token with `read -rs "t?Bot token: "` and put the function in `~/.zshrc`.

Once, to save the token (the `umask` makes the file readable only by you; `gh` is given the empty `gh` directory below as its own settings folder):

```bash
mkdir -p ~/.config/claude-bot/gh && chmod 700 ~/.config/claude-bot
( umask 077; read -rs -p "Bot token: " t; printf '%s' "$t" > ~/.config/claude-bot/token; echo )
```

Then add this to `~/.bashrc`, and open a new terminal:

```bash
claude-bot() {
    local t
    t="$(cat ~/.config/claude-bot/token)" && [ -n "$t" ] || { echo "claude-bot: no bot token" >&2; return 1; }
    GH_TOKEN="$t" \
        GH_HOST=github.com \
        GH_CONFIG_DIR="$HOME/.config/claude-bot/gh" \
        GIT_SSH_COMMAND=false \
        GIT_CONFIG_COUNT=4 \
        GIT_CONFIG_KEY_0=credential.helper GIT_CONFIG_VALUE_0= \
        GIT_CONFIG_KEY_1=credential.https://github.com.helper GIT_CONFIG_VALUE_1='!gh auth git-credential' \
        GIT_CONFIG_KEY_2=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_2=git@github.com: \
        GIT_CONFIG_KEY_3=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_3=ssh://git@github.com/ \
        claude "$@"
}
```

What each part does, for this one session only (your own `gh` and git settings are unchanged):

- The first line refuses to start when the token file is missing or empty. Without that, `gh` would treat an empty `GH_TOKEN` as unset and fall back to your own stored login (observed with `gh`).
- `GH_HOST` and `GH_CONFIG_DIR` point `gh` at github.com and at an empty settings folder, so it cannot find your stored login at all.
- `GIT_SSH_COMMAND=false` makes every SSH connection fail, so git cannot push with your SSH key.
- `GIT_CONFIG_COUNT=4` says four key and value pairs of git settings follow. Pair 0 has an empty value and clears any credential helper you use, such as a keychain holding your own login. Pair 1 makes `gh`, and so the bot's token, answer for github.com. Pairs 2 and 3 rewrite `git@github.com:` and `ssh://git@github.com/` remotes to HTTPS, so they work as the bot instead of failing. A remote through an SSH host alias is not rewritten, and fails.

`claude-bot` starts a session that acts as the bot, and plain `claude` still uses your own login. Worked when: asked to run `gh api user -q .login`, the session prints the bot's login, not yours; and `git config --get credential.https://github.com.helper` prints `!gh auth git-credential`. Commits still carry your name and email unless you also set `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL` and the `GIT_COMMITTER_` pair.

- A token expires; when it does, make a new one and run the save-the-token commands above again.
- Do not put the token in a Claude `settings.json` `env` block, where it sits in plain text in a file that may be shared.
- This makes the bot the credential Claude uses by default; it is not a wall. Your own token is still stored on the same machine, and a session that wanted it could read the file (see "Not covered here").

## Reference

### Why Write

Write is the lowest repository role that can push: Read and Triage cannot ([repository roles for an organization](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/repository-roles-for-an-organization)). Maintain adds repository management the bot does not need, and only Admin can delete or transfer a repo, change its settings, or manage branch protection rules and rulesets. A personal repo has no roles to choose from: its collaborators can push and merge, and only the owner can delete or archive the repo, change its settings, or invite collaborators ([permission levels for a personal repository](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-personal-account-settings/permission-levels-for-a-personal-account-repository)).

What Write does not stop is pushing, force-pushing and deleting on a branch with no protection. A protected branch blocks force pushes and deletion by default ([about protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)), and an unprotected one has no such rule.

### Token scopes

- `workflow` "grants the ability to add and update GitHub Actions workflow files" ([scopes for OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps)); without it the bot can still push a branch whose code CI runs. A classic token reaches every repo the bot can reach, so the bot's role is its only limit.

A GitHub App installed on the repos is stricter still, with per-repo permissions and short-lived tokens. It needs a private key and token-minting code in front of `gh`, and this doc does not cover it.

### Plan limits

GitHub's plans page lists protected branches under "Advanced tools and insights in private repositories" for Pro and Team, does not list them for Free, and gives a free organization "unlimited private repositories with a limited feature set" ([GitHub's plans](https://docs.github.com/en/get-started/learning-about-github/githubs-plans)). That suggests a private repo on a free plan cannot have a ruleset or branch protection rule, so the bot can push to its default branch; the page does not say so outright, so this is inferred. Public repos are not affected. Without server-side protection, the only guards are local hooks and settings, which Claude can work around (see "Not covered here").

### Terms

GitHub's terms allow a machine account: one "set up by an individual human who accepts the Terms on behalf of the Account, provides a valid email address, and is responsible for its actions", "used exclusively for performing automated tasks". "You may maintain no more than one free machine account in addition to your free Personal Account." ([GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service), section B.3.) So create the bot yourself, use it only for Claude's work, and keep to one free bot per person.

### Not covered here

- Settings and hooks that refuse destructive commands before they run: [Guard destructive git and gh commands with settings and hooks](https://github.com/eirkkr/fieldkit/issues/155).
- Keeping the user's own token out of Claude's reach, without which a bot account protects nothing: [Keep the user's own GitHub token out of Claude's reach](https://github.com/eirkkr/fieldkit/issues/154).
