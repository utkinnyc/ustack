---
name: review
description: Pre-ship self-review of the current change in any repo — a trace table mapping every changed file to the part of the request it serves (reverting what serves none), the plan's "done when" check, the project's own typecheck, lint, test and build, then a short safety checklist (secrets, new dependencies, env vars). Fixes what it finds and reports what it skipped. Use before shipping, after devstack:build, or when the user says "review this", "is this ready", or /review.
---

# Review

A fast check that the change does what was asked, only what was asked, and works. Read only what changed: `git status`, `git diff --stat <base>...HEAD` and the working tree, where `<base>` is the branch this one was cut from (usually `main`). For a deep bug hunt across the diff, suggest the built-in `/code-review` after this.

## 1. The goal

Take the goal and "done when" check from `docs/plan.md`, or from the user's request in this conversation. If neither exists, ask the user what the change is for before reviewing.

## 2. Trace table

One row per changed file (per hunk if a file mixes concerns):

| File | Serves | Verdict |
|---|---|---|
| `src/db.ts` | "store the user's settings" | ✅ |
| `src/utils.ts` | nothing: reformatting | ↩︎ reverted |
| `README.md` | documents the new env var | ✅ |

- **Serves nothing, and you made it:** revert it.
- **Serves nothing, and the user made it** (or you're unsure): leave it, and list it under "Needs you".
- **Serves the goal but goes beyond it** (an extra option, an abstraction used once, a feature not asked for): simplify it to what the goal needs.

## 3. Checks

1. **The "done when" check.** Run it and show the output. Failing → the review is `blocked`, whatever else passes.
2. **The project's own checks**, from whatever it defines (`package.json` scripts, `Makefile`, `cargo`, `pytest`, `swift test`, CI workflow): typecheck, lint, tests, build, in that order. Stop and fix at the first failure. Don't add tooling just to run it; record what doesn't exist as skipped.
3. Never silence an error (`any`, `@ts-ignore`, disabling a rule, skipping a test) without a one-line reason in the code.

## 4. Safety

- **Secrets:** nothing that looks like a key, token, password or private URL in the diff (`git diff <base>...HEAD | grep -iE 'key|token|secret|password'`, then read the hits). `.env` files are git-ignored.
- **Dependencies:** anything added was approved by the user. If not, flag it with the built-in alternative.
- **Env vars:** every new one is documented (e.g. `.env.example`) and fails fast with a clear message if required.
- **Personal data:** no real IPs, hostnames, emails or phone numbers in docs or tests; use placeholders.

## 5. Stack checks (only for apps made with `devstack:scaffold`)

Network calls go through `fetchJson` (timeout, retries, no retry on 4xx except 429); the app still runs with the LLM off; SQLite via `node:sqlite` in WAL mode at the `<APP>_DB` path, never inside the image; pages that read the DB export `dynamic = "force-dynamic"`; nothing slow runs in a request (background work is a scheduler job from `instrumentation.ts`); forms and links work without JS; `output: "standalone"` is still set if the Dockerfile or `next.config.ts` changed.

## 6. Report

Reply in this shape, nothing more:

```
REVIEW: pass | fixed | blocked
Goal: <one line> — done when: <check> → passed | failed
Trace: <n files, all traced | n reverted | n need you>  (table above)
Ran: <checks>
Fixed: <one line each, or "nothing">
Skipped: <check and why>
Needs you: <decisions only the user can make, or "nothing">
```

`blocked` means something fails that you couldn't fix. Say what, and stop.
