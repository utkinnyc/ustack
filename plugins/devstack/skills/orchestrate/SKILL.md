---
name: orchestrate
description: Run a large build as one serial foundation step plus many subagents working in parallel git worktrees, then merge everything back in dependency order and prove it with an end-to-end smoke test. Covers splitting the plan into workstreams, an AGENTS.md ownership map, launching and monitoring background agents, resuming after usage limits, pre-push secret checks, a notes file for the author, merge sequencing, integration, read-only review agents, and worktree cleanup. Use this whenever the user says "use subagents", "run these in parallel", "execute the plan", "step 0 then N agents", "orchestrate", "merge these branches", "what order should I merge", or hands over an implementation plan with many independent parts.
---

# Orchestrate

Turn a plan into working code using many agents at once, without them colliding, and leave the user with something they can review and trust.

## Shape: F0 → parallel workstreams → integration

1. **F0, the foundation (one agent, serial).** It fixes everything the others build against: shared types and interfaces, the database schema and migrations, the API contract, the folder layout, and an `AGENTS.md` that says which folders each workstream owns and which checks must pass (e.g. build, test, lint, format). Keep it small, and verify its checks yourself before fanning out.
2. **Workstreams A, B, C… (many agents, parallel).** Each one:
   - gets its own **git worktree and branch** (e.g. `phase0/a-database`) created from F0, because several agents can't commit to one branch at once;
   - touches only the folders `AGENTS.md` gives it;
   - codes against F0's interfaces, using fakes for the rest;
   - finishes when its own checks pass and its "done when" is met.

   Mark the few that must wait for another (e.g. "F starts after A").
3. **Integration (serial).** Merge, fix the seams between the pieces, and pass one end-to-end gate.

If the user asks what a worktree is, explain it simply: another checkout of the same repo in a sibling folder, on its own branch, sharing one `.git`.

## Running the agents

- Launch the workstream agents **in the background, in one batch**, and report as each one finishes ("7 of 9 done; B and H still running").
- Give every agent the same rules: stay in your folders, don't touch servers or production, don't run paid LLM calls, show "Not supported yet" rather than leaving a broken screen, and commit to your own branch.
- **Watch for shared-environment traps:**
  - a shared build cache or target dir (e.g. Cargo `target/`) causes lock contention or stale builds; give each worktree its own if builds clash;
  - broad `.gitignore` rules can silently hide source folders (`data/` also matches `Data/` on case-insensitive disks), so check `git status --ignored` when files go missing;
  - one-time GUI approvals (e.g. Xcode plugin trust) block command-line builds; tell the user or use the documented flag to skip them.
- **Usage limits:** if agents stop partway, they resume cleanly as long as nothing was half-committed. Say what happened and resume when the user is back.
- If an agent finds a bug in another workstream's area, pass it to that owner rather than fixing it across boundaries.
- **Builders, then one integrator.** For a feature split across agents (e.g. "app sign-in" and "CLI login"), give every builder the same short shared design: shared helper names, types and routes. When they're all back, launch one integrator agent. It merges the branches, removes duplicates (the same helper written twice), wires the pieces together, removes stale docs, reviews security, and runs every build plus an end-to-end test. Then open the PR.

## Before pushing anything

- Scan for secrets and personal data: keys, tokens, `.env` files, server IPs, phone numbers, addresses. Replace real IPs and hosts in docs with placeholders. Known public test values (like AWS's `AKIA…EXAMPLE`) are fine.
- If the user says "commit whatever state it's in, broken or not", do exactly that, and write down what's broken.
- **Check the size before opening a PR.** Run `git diff --stat` and split the result into generated, tests, docs and hand-written code. If the hand-written part is more than a few hundred lines or spans every area, say so first and offer **stacked PRs, one per area** (backend, apps, web, CLI). Each must build and pass tests on its own, and the last must match the full branch exactly. Better still, design the feature to live in one module first (see `devstack:app-login`, "Keep it in one place").
- **Write PR bodies to a file and pass `--body-file`.** Never build them inline in a shell command. Backticks in the text run as commands: one inline body once started a real TestFlight upload.
- **Stacked PRs can merge into a dead branch.** If the parent merges first and the child is then merged, the child lands in the parent's branch, not `main`. Turn on **Automatically delete head branches** (`gh api -X PATCH repos/<owner>/<repo> -f delete_branch_on_merge=true`), so GitHub retargets children to `main`. If the parent has already merged, rebase onto `main` instead of stacking. To clean up old branches, pass them all to one `git push origin --delete b1 b2 …`. Don't give a pipe the user might paste across two lines.
- Run subagents **one after another** when they edit the same files, and build the second PR on the first.
- **Before force-pushing a stacked branch, check it's still open** (`gh pr view N --json state`). The user may have merged it while you worked. GitHub also refuses to change the base of a PR that's part of a stack, so rebase onto `main` instead.
- Write a **notes file for the author** (e.g. `NOTES_FOR_AUTHOR.md`): a table of branches with test counts, the recommended review and merge order, known seams integration must fix, and decisions or actions waiting on the user. Say what you verified yourself and what you're taking on the agents' word.

## Merging

Propose the order in a table (branch, why it goes here) and wait for a go-ahead:

- Foundation first; **CI next**, so every later merge gets checked; then in dependency order (storage before the things that use it); the widest-touching branch late; independent ones (e.g. a separate Swift package) anywhere.
- **Use normal merges, not squash.** Every branch sits on F0's commits; squashing F0 makes git see them as different, and every other branch conflicts.
- Expect conflicts mainly in dependency manifests and lockfiles. Keep both sides' dependencies and let the tool regenerate the lock.
- Run build and tests **after each merge**, so a failure points at one branch. If a test is flaky, rerun it several times and find out whether it's noise or a real bug (e.g. ordering that breaks after a relaunch).
- Merge in a separate worktree if the user's main checkout has uncommitted edits. Never discard edits that aren't yours.

## Integration gate

Prove the whole thing works before building on top of it. A small CLI that talks to the backend exactly like the real clients is ideal: it tests without device tooling and stays useful for debugging. Use a **fake LLM** (canned, free) for the end-to-end smoke test, and ask before any real paid run.

## Reviews

When asked for a review, launch several **read-only** reviewer agents, each with one angle (bugs, security and guardrails, deploy gaps, simplification, test gaps). They change nothing and write findings to one dated file (e.g. `docs/REVIEW-YYYY-MM-DD.md`). The user decides what to act on.

## After merging

- Every change goes through a branch and a PR for the user to review and merge, unless they say otherwise.
- **Every change goes in a temporary worktree** (the user's rule), even a one-line PR. Create it with `git worktree add <tmp>/<repo>-wt-<name> -b <branch> origin/main`, or from the parent branch for a follow-up. Edit, commit, push and open the PR from there, then remove the worktree and the local branch. To update an open PR, make a fresh worktree on its branch. Other sessions share the main checkout: if you switch its branch, their commits land on your branch. Before pushing, check `git log origin/main..HEAD` for commits you didn't make.
- **Keep one checkout.** The user works in the original repo folder, on `main`. Delete each worktree as soon as its branch is merged or pushed, without being asked. Before deleting: confirm every branch is merged or pushed, move any git-ignored local state (`.env`, local data) back into the main checkout, then `git worktree remove` and `git worktree prune`. Delete a shared build cache too (it can be tens of GB) after checking nothing like `CARGO_TARGET_DIR` points at it, and warn that the next build is slow. Report the space freed.
- Background servers you started stop at the tool's time limit, so say so and give the command to run them manually.
