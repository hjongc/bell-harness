# Away run procedure

## Deadline

Resolve the agreed return time to a dated deadline in its timezone before starting. Run `date` before each item and compare the current time to that deadline. At or after the deadline, start no new item and report. If the time passes during an item, finish its checks, review and commit, then push the branch if authorized. Open its pull request only if the checks and review passed and it is within budget. Apply the same failure handling below and report without starting another item.

## Each item

1. **Choose the base.** Use a separate branch per item named for the work, such as `feat/<topic>`, `fix/<topic>` or `refactor/<topic>`. Start independent items from the project integration branch. If the item depends on an unmerged branch, base it on that branch and name the dependency and base in the pull request. Keep existing working changes out of the item. When a link in `~/.claude/skills` or `~/.agents/skills` resolves into the checkout, follow Separate folder below.
2. **Set the scope.** Follow the approved roadmap spec if there is one. For a `todo` requirement, use the `spec` skill to write a spec that cites the approved requirement ID and preserves its acceptance criteria. The requirement supplies approval within its scope, so continue without a separate spec approval prompt. Set `Size budget: net +<n> lines` before implementing any self-written spec, including an audit fix. Record the expected file scope, checks and approval gates. Park any gap that would require a new product decision or an action on the approval list that the requirement does not name.
3. **Implement and check.** Keep the acceptance criteria in view. On the item branch, link the spec and move a tracked requirement to `in-progress` while working. Include its proposed `done` status and any applicable roadmap checkbox in the change to verify. Run `scripts/check` or the project check and the spec's done condition against the full change. Save the real command output. Finalize the completion updates only after the checks and review pass.
4. **Get a fresh review.** Give a fresh reviewer only the requirement, the spec and the complete diff against the chosen base, including new files. For a roadmap item or audit without a requirements row, give the corresponding source task or observed finding as the requirement. Ask whether the acceptance criteria are met and whether a smaller change would suffice. Count lines added and removed against that base. Net size is additions minus removals. Report the counts and the applicable budget in this format (use `n/a` when an existing approved spec has no budget):

   ```text
   Review: PASS|FAIL -- acceptance: <met|unmet: which> -- smaller change: <none|description> -- size: +<added> -<removed> (budget +<n>)
   ```

   A failed review or a net size above budget gets no pull request. If a fresh reviewer is unavailable, park the item without self-approving. Keep the work on its branch and record the branch name, the verdict or review blocker, the next choices and what was done in `docs/plans/blocked.md`. Leave its requirement and roadmap entry open.
5. **Commit and open the pull request.** Split commits by meaning. Follow the project preflight before pushing. Push the branch when authorized, then open a regular pull request. Its body names the source requirement or finding, links the spec, includes the actual check commands and output, and appends the review verdict and size. For stacked work, target the dependency branch and name it in the body. The user merges. If `gh auth status` fails or `gh` is unavailable, push the verified branch if allowed, list it as awaiting a pull request and ask about opening it on return.

Keep the three-failure rule from the skill. Record the last error and continue with independent work. Avoid starting another item that depends on a parked result.

## Separate folder

Use `git worktree add <folder> -b <branch> <base>` with a folder outside the checkout, without `-b` for an existing branch. Copy Git-ignored inputs that the checks read, such as a private term list, into it before the first check. Run the following in the original folder before the item, and again before opening its pull request. If the output differs, open no pull request and park the item. Write `docs/plans/blocked.md` in the original folder only after that comparison.

```sh
git branch --show-current
git rev-parse HEAD
git status --porcelain --untracked-files=all
git diff HEAD --binary | git hash-object --stdin
git -c core.quotePath=false ls-files -o --exclude-standard | git hash-object --no-filters --stdin-paths
```

After the branch is pushed or parked, run `git worktree remove <folder>`, which keeps the branch and refuses while uncommitted work exists.

## Audit and requirement gaps

Inspect entry points, recent changes, tests and decision records for reproducible bugs, avoidable work and code that can shrink without changing behavior. Verify the finding with a failing check, measured waste or concrete redundant paths. Work one finding per branch and pull request, using the same scope, size budget, checks and review. Park findings that need a product decision. After a full pass finds no grounded change, record questions about actual gaps in the requirements and planning docs in `docs/plans/blocked.md`.
