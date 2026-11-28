---
name: plan
description: Before building a feature, fix or change, write a short plan to docs/plan.md — the goal restated, the check that proves it's done, non-goals, and numbered steps that each say what part of the request they serve and how they're verified — then stop for the user's yes. No code. Use when the user describes something to build or change, asks for a plan, says "how would you do this", or says /plan.
---

# Plan

Turn a request into a plan the user can approve or correct in under a minute. Write no code in this skill.

## 1. Look only as far as needed

Read the README, the manifest (`package.json`, `Cargo.toml`, `pyproject.toml`, `Package.swift`, …) and the files the request obviously touches. Cite what you found as `path:line`. No exploratory sweeps. If `devstack:distinguished-engineer` already produced a design doc, plan from it.

If the change is small (one file, obvious approach), skip the file: give a one-line plan and its check in chat, and hand to `devstack:build`.

## 2. Write `docs/plan.md`

Under 60 lines. Overwrite the previous plan for a new piece of work; edit in place while iterating on this one.

```markdown
# <short title>

**Goal:** <the request in one or two sentences, in the user's terms>
**Done when:** <the check: a command, test or observable result>

**Non-goals:** <at least two things this deliberately won't do>

**Approach:** <one paragraph>. Considered: <the other approach and why not>.

## Steps
1. [ ] <one action> — serves: <part of the goal> — check: `<command or what to look at>`
2. [ ] ...

## Files
- `path` — create | change — <why>

## Open questions
- <question> — default: <your pick, so a plain "yes" settles it>   (or "none")
```

Rules for steps:
- **Checks use the app when they can.** If the repo has `.claude/skills/verify-*` (from `devstack:verify`), write checks as its control commands.
- **One action, one check each.** "Add the `users` table — check: `npm test -- users` passes." Not "handle edge cases".
- **Every step serves part of the goal.** If a step serves none, cut it. Refactors and cleanups don't go in unless the goal needs them.
- **Order so each check can run** when its step is done. Tests that prove the goal come early, not at the end.
- **No code in the plan** beyond a signature or a type where the shape is the decision. A plan longer than the code it describes has written the code instead.
- New dependencies go under Open questions, with the reason and the standard-library alternative.
- More than about a day of work: plan the first slice only, and list the rest under Non-goals as "later".

## 3. Ask, then stop

Give the path, the goal and the "done when" in two lines, the open questions with defaults, and ask: **"Yes to build, or what should change?"**

Stop. Don't scaffold or code until the user says yes. On changes, edit `docs/plan.md` and ask again.

On a yes, hand off: `devstack:build` for one agent, `devstack:orchestrate` when the steps split into independent parts for parallel agents, `devstack:scaffold` first for a brand-new web app.
