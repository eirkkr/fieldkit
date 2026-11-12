# A limited GitHub account for Claude

Claude runs `gh` and `git` with whatever token it finds, normally its user's own, so it can do anything its user can, including deleting a repo or editing its protection rules. A separate bot account whose role is Write, never Admin, takes the repo-admin actions out of reach. This doc covers making the bot and its token, protecting the default branch so the bot's pull requests need your approval, checking the setup, and running a command as the bot. It does not stop a Write-role bot pushing to a branch with no protection, or pushing a branch whose code CI then runs.

Claims about GitHub below link their page and were checked on 2026-10-30 or 2026-10-31.

## Which token

A classic token with the `repo` and `read:org` scopes, for every repo, personal or organization; [ADR 063](../docs/decisions/063-a-write-role-bot-account.md) says why not a fine-grained one. It reaches every repo the bot can reach, so the bot's role on each is what keeps it from admin actions. An organization that blocks classic tokens ([token policy](https://docs.github.com/en/organizations/managing-programmatic-access-to-your-organization/setting-a-personal-access-token-policy-for-your-organization)) cannot use this doc: check its Settings, Personal access tokens first.

`read:org` is there because `gh pr edit` fails without it, and with `repo` alone `gh pr checks --watch` prints the same scope error ([ADR 071](../docs/decisions/071-bot-token-includes-read-org.md)). A token made with `repo` alone needs the scope added: as the bot, open Settings, Developer settings, Personal access tokens, Tokens (classic), pick the token, tick `read:org`, and Update token. The same token string kept working after this was done once (2026-11-11), so the copy saved in step 7 should too; if `gh` refuses it, make a new token.

Tried with a classic token of `repo` alone against a personal repo and an organization's repo, including running Claude as the bot through `kit-claude`. After `read:org` was added to that token, `gh pr edit` was tried again on 2026-11-11 and worked; the other `gh` commands were not re-tried with both scopes.

## You need

- `gh`, the GitHub CLI, and a bash shell. In zsh, `read -rs -p "Bot token: " X` fails; write it as `read -rs "X?Bot token: "` in steps 6 and 7.
- To own the personal repos, or be an Owner of the organization, so you can invite the bot.

## Steps

Each step says what it should look like when it worked. Use a private browser window for the bot, so you stay logged in as yourself in the other.

### 1. Create the bot account

Sign up at github.com in the private window. Give the bot its own email address: GitHub's terms require a valid one for each account ([Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service), section B.2). A plus address such as `you+claude@example.com` arrives in your own inbox if your provider supports plus addressing, and is a different address to GitHub; this has not been tried here.

Turn on two-factor authentication for the bot: your profile picture at the top right, Settings, Password and authentication, Enable two-factor authentication ([configuring two-factor authentication](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/configuring-two-factor-authentication)). The bot's password and recovery codes are as worth protecting as your own.

Worked when: you can log in as the bot, and it asks for a second factor.

### 2. Give the bot access

**A personal repo.** As yourself, open the repo, then Settings, Collaborators, Add people, and pick the bot ([inviting collaborators](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-access-to-your-personal-repositories/inviting-collaborators-to-a-personal-repository)). A personal repo has one collaborator level, which can push and merge but not change settings or delete the repo; there is no role to choose ([permission levels](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-personal-account-settings/permission-levels-for-a-personal-account-repository)). As the bot, accept the invitation from its email. Repeat for each repo.

**An organization's repo.** As an owner, open the organization, then People, Invite member, and leave the role as Member, never Owner ([inviting users](https://docs.github.com/en/organizations/managing-membership-in-your-organization/inviting-users-to-join-your-organization)). An owner has "complete administrative access" to the organization ([roles in an organization](https://docs.github.com/en/organizations/managing-peoples-access-to-your-organization-with-roles/roles-in-an-organization)). As the bot, accept the invitation. Then, in each repo, open Settings, Collaborators and teams, Add people, pick the bot, and choose Write ([managing access to a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-teams-and-people-with-access-to-your-repository)). Also check the organization's Settings, Member privileges, Base permissions: it applies to every member on every repo, so it must not be Admin. If it is already No permission or Read, leave it ([base permissions](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/setting-base-permissions-for-an-organization)).

Worked when: the bot is listed as a collaborator, not pending, on a personal repo; on an organization's repo, the Collaborators and teams page lists the bot with Write.

### 3. Make the bot's token

Log in as the bot, then your profile picture at the top right, Settings, Developer settings, Personal access tokens, Tokens (classic), Generate new token, Generate new token (classic). Set an expiration you will remember to renew. Tick `repo` and `read:org` and nothing else; leave `workflow` unticked, so the bot cannot add or edit workflow files. Generate token, and copy it: it is shown once.

Worked when: the token is listed on the bot's token page.

### 4. Protect the default branch

A private repo on a free plan most likely cannot have this: see "Plan limits" in the reference. If so, skip the step and know that the bot can push, force-push and delete on the default branch.

Before the ruleset, add a `CODEOWNERS` file naming who may approve pull requests. Add `.github/CODEOWNERS` containing your username (more usernames, separated by spaces, to allow more people; each needs write access to the repo, and on a personal repo there are no teams) ([about code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)):

```text
* @<your-username>
```

Get it onto the default branch before turning on the ruleset (a ruleset that already exists refuses a direct commit, so use a pull request). GitHub reads the version on the pull request's base branch, so a bot's pull request should not be able to edit its way into the list (not tried here; [about code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)).

As yourself, open the repo, then Settings, Rulesets in the sidebar, New ruleset, New branch ruleset ([creating rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)). Set Enforcement status to Active and add the default branch as a target. Turn on Restrict deletions, Block force pushes and Require a pull request before merging, and under the pull request rule set Required approvals to 1, turn on Dismiss stale pull request approvals when new commits are pushed, and turn on Require review from Code Owners. Also turn on Require status checks to pass: add the checks your CI runs, set each one's source to GitHub Actions, and turn on Require branches to be up to date before merging ([available rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)). Then Add bypass, pick the Repository admin role, and set its mode to For pull requests only. Create. To change a ruleset that already exists, open it from the Rulesets list, change the same settings, and Save changes. Only an admin (on a personal repo, the owner) can manage rulesets, so the bot cannot lift it.

The result: the bot cannot push to the default branch, and cannot merge its own pull request until you approve it; with the stale-approval setting on, a later push by the bot withdraws your approval. You approve its pull requests. Your own pull requests still go through a pull request, but as an admin you can merge them without an approval. The bypass list takes roles, teams and apps, not individual users ([creating rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)), so on an organization repo anyone with the admin role gets the pass too. [ADR 063](../docs/decisions/063-a-write-role-bot-account.md) says why it is built this way. This gate has not been tried yet.

Three things this does not do:

- It covers the default branch only. The bot can still push, force-push and delete other branches, and a bot with Write can also push tags, so if pushing a tag runs a release workflow, add a ruleset that targets tags and restricts their creation, updates and deletion.
- The required checks still run code the bot can change, so a green check on a bot's pull request shows less than one on yours. Read the diff before approving, keep Settings, Actions, General on read-only default workflow permissions with "Allow GitHub Actions to create and approve pull requests" off, and leave auto-merge off.
- The pass covers only pull requests you open. A bot with Write can push to your open branch, so read a pull request's commit list before merging one of your own, and read closely any pull request that touches `CODEOWNERS`.

Worked when: the ruleset is listed as Active and `.github/CODEOWNERS` is on the default branch, or you have confirmed your plan does not offer rulesets. To see it hold, have the bot open a real pull request and look at it: GitHub should ask for your review and keep its merge button blocked. Do not try the merge on a throwaway pull request to find out; if the gate is missing, it merges.

### 5. Run the check script

```bash
.fieldkit/scripts/check-bot-account.sh <owner>/<repo>
```

In the kit itself the script is `scripts/check-bot-account.sh`; in a consumer repo the kit is reached through its `.fieldkit` link. The script asks for the bot's token without showing it; the token is never an argument, so it stays out of the process list. Paste it at the prompt: a `GH_TOKEN=...` prefix on the command is recorded in your shell history. If your shell already exports a `GH_TOKEN`, the script uses it without asking, so `unset GH_TOKEN` first. It only reads from GitHub and stores nothing.

| Line | Means |
| --- | --- |
| `pass: the token belongs to <login>` | The token works. `<login>` must be the bot, not you. |
| `pass: the token has the repo and read:org scopes` | A classic token with both scopes the doc asks for. GitHub lists them in the `X-OAuth-Scopes` header; `write:org` or `admin:org` stands in for `read:org`. |
| `note: the token is missing: <scopes>` | `<scopes>` is `repo`, `read:org` or `repo and read:org`. The token works for the rest, but `gh pr edit` fails without `read:org`. Fix the token in step 3. Exit status 0. |
| `note: GitHub sent no X-OAuth-Scopes header ...` | The check cannot read the scopes: a fine-grained token, for one, sends no such header, and the doc asks for a classic one. Exit status 0. |
| `note: could not read the token's scopes: ...` | The scope lookup failed, with GitHub's message; run the script again. Exit status 0. |
| `pass: <login> does not have admin on <repo>` | Good. Exit status 0. |
| `note: <login> cannot push to <repo>` | No admin, but no Write either: the invitation, the Write grant or the `repo` scope is missing. Exit status 0. |
| `fail: <login> has admin on <repo>` | On a personal repo, only the owner has admin, so this is your token, not the bot's. On an organization's, lower the bot's role to Write: check it is a Member, not an Owner, that no team gives it Admin, and that the base permission is not Admin. Exit status 1. |
| `note: ... is protected` | A branch protection rule or ruleset applies. The script cannot tell whether it would stop the bot; test 1 below does. |
| `note: ... has no branch protection rule or ruleset` | The bot can push to, force-push and delete the default branch. |
| `note: the ... lookup (repos/...) failed: ...` | That protection lookup was refused, with GitHub's message. For the ruleset lookup on a private repo, the likely reason is a plan without protection. |
| `note: the default branch name is empty or has characters this check does not look up` | Check its protection in the repo's Settings, Rulesets. |
| `note: the protection lookups gave answers this check cannot read` | Treat the default branch as unprotected until test 1 below is refused. |
| `GitHub refused the token (HTTP 401)` | Mistyped, expired or revoked. Make a new one. |
| `GitHub answered 404 Not Found for repos/...` | The token cannot see the repo. See below. |

Exit status 2 means the script stopped on an error, and its message says which. A failed protection lookup is only a note.

A 404 on the repo, when the name is right, usually means one of these:

- The token was made without the `repo` scope.
- The bot has not accepted its invitation, or has no access to the repo.
- The organization blocks classic tokens.

The script checks Admin, whether the bot can push, and which scopes a classic token has (tried 2026-11-12: GitHub sent `X-Oauth-Scopes: read:org, repo` for the bot's token). It does not check that the role is exactly Write.

Worked when: the exit status is 0 and the login on the first line is the bot's.

### 6. Test by hand

Run these in your own terminal with the bot's token. They use only `gh`. Test 2 leaves nothing behind but a closed pull request; if it stops partway, delete the leftover branch with `gh api -X DELETE repos/<owner>/<repo>/git/refs/heads/bot-check` before running again.

```bash
read -rs -p "Bot token: " GH_TOKEN; export GH_TOKEN; echo
gh api user -q .login   # must print the bot's login; if it prints yours, STOP and run: unset GH_TOKEN
R=<owner>/<repo>
B=$(gh api repos/$R -q .default_branch)
SHA=$(gh api repos/$R/git/ref/heads/$B -q .object.sha)
# 2. branch, commit, PR: should all work
gh api -X POST repos/$R/git/refs -f ref=refs/heads/bot-check -f sha=$SHA
gh api -X PUT repos/$R/contents/bot-check.txt -f message="bot check" -f content="$(printf hi | base64)" -f branch=bot-check
gh pr create -R $R --head bot-check --base $B --title "Bot check" --body "Throwaway, closing now."
gh pr close -R $R bot-check --delete-branch
# 3. an admin-only read: should be refused (403 or 404)
gh api repos/$R/hooks
```

Test 1 is separate, and only for a repo whose default branch is protected: on an unprotected one it succeeds, as a real commit that triggers any push workflow. Run it in the same terminal:

```bash
# 1. writing straight to the default branch: should be refused
gh api -X PUT repos/$R/contents/bot-check.txt -f message="bot check" -f content="$(printf hi | base64)" -f branch=$B
```

When you are done, run `unset GH_TOKEN`.

What a good result looks like:

1. On a protected branch, an error that names the rule or protection, and no new commit on the default branch. An error about `sha` is not a refusal: it means `bot-check.txt` already exists there. If the command succeeds, the protection does not cover the bot: delete `bot-check.txt` from the default branch in the web interface and check the ruleset.
2. Each command prints JSON or a URL, the pull request opens, and the close deletes the `bot-check` branch.
3. `HTTP 403` or `HTTP 404`. A list of webhooks, even an empty `[]`, means the token has Admin.

### 7. Start Claude as the bot

Keep the bot's token in a file only you can read, and start Claude, or another agent, through a script that loads it. The token is the limited credential, so it is fine for Claude to read it; anything with more power than that is not. The save command is for bash; in zsh, use `read -rs "t?Bot token: "`.

Once, to save the token (the `umask` makes a new file readable only by you, and the `rm` clears any older, wider file first; `gh` is given the `gh` directory the next command creates, empty, as its own settings folder):

```bash
mkdir -p ~/.config/bot-account/gh && chmod 700 ~/.config/bot-account
( umask 077; rm -f ~/.config/bot-account/token; read -rs -p "Bot token: " t; printf '%s' "$t" > ~/.config/bot-account/token; echo )
```

Then add this alias to `~/.bashrc` (or `~/.zshrc`) pointing at the kit's script, and open a new terminal. Use the absolute path of your kit checkout, which a consumer repo's `.fieldkit` link points to (a relative path works only from one directory):

```bash
# Start Claude as the GitHub bot account.
alias kit-claude=~/src/fieldkit/scripts/kit-claude.sh
```

`kit-claude` runs `claude` through the kit's `scripts/as-bot.sh`, which starts it with these settings, for that one command only; your own `gh` and git settings are unchanged:

- The token check refuses to start when the token file is missing or empty. Without that, `gh` would treat an empty `GH_TOKEN` as unset, and the session would run without the bot's token instead of failing (observed with `gh`).
- The `unset` line drops other GitHub tokens your shell may export, and any askpass program or injected git settings, which `gh`, git or other tools would otherwise use.
- `GH_HOST` and `GH_CONFIG_DIR` point `gh` at github.com and at an empty settings folder, so `gh` cannot find your stored login.
- `GIT_SSH_COMMAND=false` makes every SSH connection fail, so git cannot push with your SSH key.
- `GIT_CONFIG_COUNT=4` says four key and value pairs of git settings follow. Pair 0 has an empty value and clears any credential helper you use, such as a keychain holding your own login. Pair 1 makes `gh`, and so the bot's token, answer for github.com. Pairs 2 and 3 rewrite `git@github.com:` and `ssh://git@github.com/` remotes to HTTPS, so they work as the bot instead of failing. A remote through an SSH host alias is not rewritten, and fails.

`kit-claude` starts a session that acts as the bot. It refuses to start when the token is missing, as `as-bot.sh` does, and does not fall back to your login. `kit-claude --self` starts it as you instead of the bot, and every other argument goes to `claude` unchanged (`kit-claude --resume`, `kit-claude mcp list`). Plain `claude` still uses your own login.

Worked when, in a `kit-claude` session: asked to run `gh api user -q .login`, the session prints the bot's login, not yours; and `git config --get credential.https://github.com.helper` prints `!gh auth git-credential`. Commits still carry your name and email unless you also set `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL` and the `GIT_COMMITTER_` pair; "Who gets credit" in the reference says what that does to your profile.

Three more things:

- A token expires; when it does, make a new one and run the save-the-token commands above again.
- Do not put the token in a Claude `settings.json` `env` block, where it sits in plain text in a file that may be shared.
- This makes the bot the credential Claude uses by default; it is not a wall. Your own token is still stored on the same machine, and a session that wanted it could read the file, use your SSH agent or keys with `ssh` directly, point `GH_CONFIG_DIR` at your own `gh` settings, or let git fall back to a login in `~/.netrc` (see "Not covered here" in the reference).

## Reference

[bot-account-reference.md](bot-account-reference.md) holds what the roles and token allow, "Plan limits", "Who gets credit", "Terms" and "Not covered here". Read the section a step names; the steps above stand alone.
