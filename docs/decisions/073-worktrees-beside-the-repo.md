# 073 - Worktrees beside the repo, made by a kit script

## Decision

A session's worktree is made by a kit script, not by `EnterWorktree`, at the session's first edit to a file git does not ignore:

- It lives beside the main checkout at `../<repo>-<description>`, `<repo>` being the main checkout's directory name, on a branch `<type>/<description>` cut from `origin/<default-branch>` with no upstream.
- The script, not a hook, checks the branch name, links `.fieldkit` where the main checkout has one, and runs the setup recipe the repo names.
- A repo names its setup recipe by having a `just worktree-setup` recipe. The script runs it in the new worktree; a repo without one is told so and the script exits 0. If the recipe fails, `just` cannot load the justfile, or a git hook fails once the worktree is made, the worktree stays, the path is still printed, and the exit code is 3; `--setup <path>` re-runs only the recipe.
- A session in a consumer repo runs `.fieldkit/scripts/new-worktree.sh <type> <description>`, through the symlink every consumer already has. In the kit it is `scripts/new-worktree.sh`. `--existing <branch>` makes the sibling for a branch that already exists, locally or only on origin.
- `/merge` removes the worktree it ran in, and a later sweep offers the other ended ones for removal on the reviewer's yes. Claude Code's own worktrees under `.claude/worktrees/` stay where they are.

If two repos map to the same path (`api` with `client-x` and `api-client` with `x` both give `../api-client-x`), creation stops at the existing path and says so.

### What this supersedes

- [ADR 069](069-configure-new-worktrees.md), Consequences: "the agent follows it with `EnterWorktree`, which uses these settings". For new work the agent runs the script. The two settings stay, since Claude Code's own worktrees (sub-agents, `claude --worktree`) still use them.
- [ADR 070](070-kit-claude-launcher.md), Reason: "the agent enters a worktree with `EnterWorktree`, then renames the branch to a conforming name, which the hook checks". The branch now has its name from the start, and the script checks it. The rename in `push` stays for Claude Code's own `worktree-*` branches.

## Reason

Prose has not kept worktrees from being made at a session's start, inside the repo, on `worktree-*` branches, without the repo's environment, and left behind. `EnterWorktree` with a `name` decides the location, the branch name and the contents of the checkout, so the first three cannot be fixed through it, and it does neither the setup nor the cleanup.

### Answers to 070's reasons for declining a creation hook

070 rejected a `WorktreeCreate` hook for two reasons. Both are met here by not using that hook:

- **it replaces Claude Code's own creation, "so the kit would own the base branch, the `.fieldkit` link and the cleanup".** The kit now owns them on purpose, and for a smaller surface: the base is explicit in the script's `git worktree add`, the link and environment are its steps, and cleanup is `/merge`. Claude Code's creation stays in use, untouched, for its own worktrees.
- **"the hook gets only a `name`, not the agent's description of the work".** The script is run by the agent, which passes the branch type and the description.

### Checks run on this layout

Run on Claude Code 2.1.323 in WSL2, in a session with permission mode `auto`, against a worktree made by hand: `git worktree add --no-track -b chore/spike-sibling ../fieldkit-spike-sibling origin/main`.

- **Entering a sibling.** `EnterWorktree` with `path` from the launch directory accepted it. From inside a session that had entered a worktree `EnterWorktree` made, it refused: "limited to worktrees managed by Claude Code (created under .claude/worktrees/ of this repository)". `ExitWorktree` `keep` works for both a path-entered and an `EnterWorktree`-made worktree, and the session can then enter another by `path`, including a managed one it left earlier. So a stage's hand-off must leave the previous worktree with `keep` before entering the next.
- **Editing in it.** Write, Bash and `git commit` in the sibling raised no permission prompt and no denial, and `git push --dry-run` targeted `origin/chore/spike-sibling`, because `--no-track` set no upstream. A real push was not run. The session was in `auto` permission mode, which may hide prompts a default-mode session would show, so the manual check below is what shows that no extra prompt appears (R7: a session can edit, commit and push in a new worktree with no prompt it would not get in the main checkout). Whether the repo's per-project permission settings still apply in a sibling, and whether a resumed session works there, were not tested.
- **Git's own checks.** The `commit-msg` hook, which lives in the shared `.git/hooks`, fired in the sibling and refused a bad subject. `scripts/enable-hooks.sh` refuses to run from a linked worktree, as its own message says; it needs no change, since it is run once from the main checkout.
- **Removal.** `ExitWorktree` `remove` removed a clean worktree the session made with `EnterWorktree`, and refused a path-entered one: "this session is not the owner". `git worktree remove` of a clean worktree succeeds whether or not the shell is inside it. The Bash tool then fails that one call (`getcwd: cannot access parent directories`) and resets to the launch directory for the next, so removal from inside is survivable.
- **Locks.** While a session is in a worktree it made with `EnterWorktree`, git shows `locked claude session <name> (pid N start T)`. `ExitWorktree` `keep` releases it. A path-entered sibling is never locked. `git worktree remove` of a locked tree refuses, with one `--force` too, and says `remove -f -f` overrides it.
- **A worktree session's git commands.** The harness refuses a git command from a worktree-isolated session that names a path outside its own worktree it cannot verify (`..`, a compound command), though a plain `git worktree add` with an absolute path ran. Making and removing siblings is therefore done from the main checkout, which is also where the plan has creation run.
- **Unwritable parent.** In a container with only the repo mounted, `git worktree add` into the parent failed (`could not create leading directories ... Permission denied`) after creating the branch, which stayed. The script must delete a branch it created when the add fails, and refuse an unwritable parent first.
- **The script's own cases.** `just test-new-worktree`, which `just check` runs, has 37 cases against throwaway repos: where the worktree goes and what it is cut from (the remote's tip, a default branch that is not `main`, one set in `fieldkit.defaultBranch`); each refusal case leaving nothing behind (a bad prefix or length, an uppercase, underscore or stray-hyphen description, an existing path, an existing branch locally or on origin, a parent inside another work tree, a submodule, an unwritable parent); a branch left by a failed add; `--existing` after a removal and for a branch only on origin; the setup recipe, with its output kept off stdout, whether it is a plain recipe, an alias or `[private]`, and not a longer recipe name taken for it; a justfile named in any case; a failing recipe, a justfile `just` cannot load, a failing link and a failing git hook (also among sixty worktrees, where a reader that stops at the first match loses the worktree to SIGPIPE), each exiting 3 with the worktree kept; a failed add never deleting a branch the user already had; `--setup`; the `.fieldkit` link; and the script run through a symlink with `CDPATH` set, or with `GIT_DIR` exported. Seventeen mutations of the script (removing a check, the fetch, the redirect of the recipe's output, and so on) were each caught by at least one case. Refusals no case covers: a type that is not lowercase letters, `--existing` with a branch that has no slash, a bare repository, a missing `origin/<default>`, a failed fetch, running outside a repository, and `--setup` on something that is not a directory.
- **Creating beside the kit.** From a session in the kit's worktree, `scripts/new-worktree.sh chore r7-check` made `../fieldkit-r7-check` and printed its path; `git worktree remove` and `git branch -D` cleaned it up. Nothing in that session showed the Bash sandbox on, so this does not check creation under the sandbox.
- **Not tested.** Creation under the Bash sandbox, and in a container with only the repo mounted (the script refuses an unwritable parent first, which the test suite holds with a read-only parent). Whether other tools scan a sibling was not tested; the markdown linter `rumdl` runs over the repo's own tree, which a sibling is outside.

### Manual check for R7

R7 is the requirement that a session can edit, commit and push in a new worktree with no permission prompt it would not get in the main checkout. In a default-permission-mode session in a repo that uses the kit, from the main checkout on the default branch: make a worktree by hand as above, `EnterWorktree` with its path, edit a tracked file, run a Bash command, `git commit`, and `git push`. Each should raise only the prompts the same action would in the main checkout. Run it once with a worktree made by hand and once with one made by `scripts/new-worktree.sh chore <description>`.

Run on 2026-11-14 (Claude Code 2.1.325, WSL2, default permission mode, from the main checkout on `main`) in three passes, the reviewer noting each prompt as the action ran: a control in the main checkout on a throwaway branch (`git switch -c`, `Edit`, `git commit`, `git push`), then a worktree made by hand with `git worktree add`, then one made by `scripts/new-worktree.sh chore r7-script`. Each of the last two ran `EnterWorktree` with the path, `Edit`, `Bash`, `git commit` and `git push` of a throwaway branch, and was removed with its branches afterwards. The control, the editing, the `Bash`, the commit and the push raised no prompt in any pass, nor did `ExitWorktree` or the cleanup. Only `EnterWorktree` with a path outside `.claude/worktrees/` prompted, in both passes and with the same text: "permission-root relocation to `<path>` — a model-supplied worktree outside .claude/worktrees/". The script's worktree behaved as the hand-made one.

R7 therefore holds for editing, committing and pushing, and does not hold as worded for entering: each `EnterWorktree` by path costs one confirmation, which the main checkout never asks. R7's wording is left as it is; stage 4 weighs the cost, and its rules and skills should say a session will be asked once on entering a sibling. Not checked: `EnterWorktree` by `name`, which makes its worktree inside `.claude/worktrees/` and may not prompt, and creation under the Bash sandbox.

Alternatives rejected:

- **Name the setup recipe in git config (`fieldkit.worktreeSetup`).** It is per clone, so every fresh clone must set it again, which the README already calls folklore for the fix command.
- **A `scripts/worktree-setup` file in the repo.** Version-controlled and free of `just`, but a script's name and place are as fixed as a recipe's, and every repo the kit serves already uses `just`.
- **A forwarding `just` recipe in each consumer to run the script.** Every consumer would add a recipe that only calls the script, and the rules could no longer give one command that works everywhere.
- **Keep `EnterWorktree` and fix it with prose.** Prose has failed.
- **A `WorktreeCreate` hook.** See 070's reasons above: it replaces Claude Code's creation and gets only a name.
- **One folder per repo for siblings.** A second path to remember for no gain.
- **Symlink the main checkout's `.venv`.** An editable install in it points at the main checkout's source.

## Consequences

- Stage 4 of [#121](https://github.com/eirkkr/fieldkit/issues/121) changes the rules, `push` and `change-stage` to this layout; until then `KIT.md` and `git.md` still say `EnterWorktree`, and `/merge` and the sweep described above are stages 2 and 5.
- `change-stage` cannot enter the next stage's sibling from inside the previous worktree: it leaves it with `keep` first, and runs creation from the main checkout. Its fallback of `git switch -c` in place would switch the previous stage's sibling, so stage 4 replaces it with the creation script.
- A repo in which `..` is not writable (a container with only the repo mounted) cannot use the layout, and is told so. Stage 3's script also refuses a parent that is inside another work tree, and a main checkout that is a submodule.
- If a Claude Code release lets a worktree session enter siblings, or locks siblings, revisit the hand-off and the removal rules.
