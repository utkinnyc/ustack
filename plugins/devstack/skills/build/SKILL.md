---
name: build
description: Carry out an approved plan one step at a time — make the change for a step, run that step's check, show the result, tick it off, and only then move on — touching nothing the plan doesn't need, and stopping to ask when the work would go beyond the plan. Ends by running the plan's "done when" check. Use after the user approves a plan (docs/plan.md or a one-line plan in chat), or says "build it", "go ahead", "implement the plan", or /build.
---

# Build

Turn an approved plan into a working change, with proof at every step. For many independent parts in parallel, use `devstack:orchestrate` instead.

## Before the first step

1. **Read the plan:** `docs/plan.md`, or the one-line plan the user approved in chat. No approved plan → run `devstack:plan` first. (A one-line fix the user asked for directly counts as its own plan.)
2. **Restate in one line** the goal and the "done when" check.
3. **Check the starting state:** `git status`. If there are uncommitted changes you didn't make, leave them alone and say so. Make sure the project's checks already pass (or note which ones fail before you start, so you don't chase them later).

## Each step

1. **Make the change the step names**, and nothing else. Match the surrounding code's style. No drive-by renames, reformatting or refactors.
2. **Run the step's check** and show the command and the relevant lines of output.
3. **Pass:** tick the step in `docs/plan.md` (`[x]`) and continue.
4. **Fail:** find the root cause before changing anything (see `devstack:debug`). Don't stack fixes. If two fixes fail for the same reason, stop and tell the user what assumption looks wrong.

## When the plan doesn't fit

Stop and ask, with your recommendation, when the work needs something the plan didn't agree:
- a file, dependency, schema change or API change not in the plan;
- a different approach than the one agreed;
- changing behaviour outside the goal (including "while I'm here" fixes).

Small, obvious necessities (an import, a type the step plainly needs) are fine; mention them in the step's result. Anything you notice but don't need goes in a "Noticed, not changed" list for the end.

## Finish

1. **Run the plan's "done when" check** and show the output.
2. **Run the project's own checks** (tests, typecheck, lint, build — whatever the repo defines).
3. **Remove only what your change made unused** (imports, helpers). Leave older dead code alone and list it.
4. Report:

```
BUILT: <goal in one line>
Done when: <check> → passed | failed (<why>)
Steps: <n of m done>
Changed: <files, one line each>
Noticed, not changed: <list, or "nothing">
Next: devstack:review
```

Don't commit or push unless the user asked; `devstack:ship` does that after review.
