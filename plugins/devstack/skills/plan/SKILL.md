---
name: plan
description: Before coding a new app or feature, write a short design note to docs/plan.md and get the user's yes, then stop. Use when the user describes something to build, asks for a plan or design, or says /plan.
---

# Plan

Think before building. The output is one short file the user can approve or correct in
under a minute. Write no code in this skill.

## Flow

1. **Look only as far as needed.** If the repo exists, read `README.md`, `package.json`
   and the files the request obviously touches. No exploratory sweeps. New app: read
   nothing.
2. **Write `docs/plan.md` once**, under 60 lines, with these sections:
   - **Goal**: one or two sentences, what the user gets.
   - **Non-goals**: what this deliberately will not do. Always list at least two.
   - **Data flow**: request or job in, what is read or written (SQLite tables, external
     calls), response out. A short bullet chain or ASCII sketch.
   - **Files**: each file to create or change, one line each, with its purpose.
   - **Open questions**: things only the user can answer. Each with your default, so a
     plain "yes" settles it. Write "none" if there are none.
3. **Apply the stack defaults** unless the user said otherwise, and say so rather than
   asking: TypeScript, Next.js App Router, plain CSS, server components first, SQLite
   via `node:sqlite` on the volume, background work from `instrumentation.ts`, single
   Docker container.
4. **Be conservative.** Prefer built-ins to dependencies. If the plan needs a new
   dependency, list it under Open questions with the reason and the stdlib alternative.
5. **Ask for approval.** Tell the user the path, summarize the plan in at most three
   lines, list the open questions with defaults, and ask: "Yes to build, or what should
   change?"
6. **Stop.** Do not scaffold or code until the user says yes. On changes, edit
   `docs/plan.md` in place and ask again. On a yes, hand off: new app means `scaffold`,
   existing app means start building from the Files list.

## Rules

- One plan file, kept up to date. Do not create a second plan or a changelog.
- Small scope wins. If the plan is over about a day of work, split it and plan the
  first slice only; put the rest under Non-goals as "later".
- Commit `docs/plan.md` with the first feature commit using `docs:` if it stands alone.
