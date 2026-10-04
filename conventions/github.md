# GitHub and external actions

- An issue or comment that missed is edited in place. Closing is harder to take back: it ends a thread someone may still be relying on. A merge closes the issues its PR resolves.
- PRs: mechanics live in [git.md](git.md). Once open, keep the title and body in sync as the branch grows - revise it directly when it drifts, keeping the author's wording where it still holds. The description is what reviewers read and what the squash message is built from.
- Before filing an issue, check for duplicates/broader scope: `gh issue list --search "<2-3 keywords>"`.
- Out-of-scope work doesn't get bundled in. It becomes an issue or its own branch, depending on what else is queued.
- In a public repo, don't name a private one. Issue text, PR descriptions, comments, and commit messages are as public as the code, and a `owner/repo#123` cross-reference or a `github.com` URL names it as plainly as prose does. Refer to it by role instead - "a consumer repo", "a Python consumer". The substance of a worked example - the finding, the numbers, the file names - is fine; the repo's identity is what stays out.

## Issues

- Titles: imperative mood, no trailing period, ~72-character soft limit. Optionally prefix with the primary component when it adds clarity (e.g. `API:`, `Docs:`); the prefix list is per-repo and grows with the codebase.
- Use the bug template for anything broken, the feature template for new functionality. File refactors, chores, and docs without a template.
- Keep the description focused on the specific finding - a narrow, well-described issue is more actionable than a broad one.
