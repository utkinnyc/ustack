---
name: review
description: Pre-ship self-review of the current app: typecheck, lint, build, then a short checklist for errors, secrets, env vars, SQLite path, blocking work and no-JS behavior. Fixes what it finds and reports what was skipped. Use before shipping, or when the user says /review.
---

# Review

A fast self-review before code leaves the machine. Fix problems directly; do not just
list them. Stay frugal: read only changed files (`git diff --stat main...HEAD` and
`git status`), not the whole repo.

## 1. Mechanical checks

Run what `package.json` defines, in this order, stopping to fix at the first failure:

1. `npm run typecheck` (or `npx tsc --noEmit` if the script is missing)
2. `npm run lint`, if a lint script exists. Do not add a linter just for this.
3. `npm run build`

If a script does not exist, record it as skipped. Never silence an error with `any`,
`@ts-ignore` or by disabling a rule, except with a one-line reason.

## 2. Checklist

Check each against the changed files and fix what fails:

- **Network calls.** Every `fetch` or external call checks `res.ok`, has a timeout
  (`AbortSignal.timeout(...)`), and handles failure without crashing the page or job.
- **Secrets.** No keys, tokens or passwords in the repo or git history of this change.
  Check with `git diff main...HEAD` and a grep for `key`, `token`, `secret`. `.env` is in
  `.gitignore`.
- **Env vars.** Every `process.env.X` in the code appears in `.env.example` with a
  comment. Required ones fail fast with a clear message at startup.
- **SQLite path.** The database path comes from an env var (e.g. `DATABASE_PATH`) that
  defaults to a file under the mounted volume (`/data`), never inside the image or
  `.next`. Schema creation is idempotent (`CREATE TABLE IF NOT EXISTS`).
- **Request path.** Nothing slow or blocking runs in a request: no long loops, big
  synchronous file work or polling. Background work lives in `instrumentation.ts` jobs
  and catches its own errors so one failure does not kill the process.
- **Works without JS.** Forms use real `<form>` with server actions, navigation uses
  `<a>`, content renders in server components. Client components are only for what truly
  needs state; each has a one-line reason.
- **Dependencies.** Anything added this change was approved by the user. If not, flag it
  and suggest the built-in alternative.
- **Docker.** If the Dockerfile or `next.config.ts` changed, confirm `output:
  "standalone"` is still set and the image still starts the server from `server.js`.

## 3. Report

Reply in this shape, nothing more:

```
REVIEW: pass | fixed | blocked
Ran: typecheck, lint, build
Fixed: <one line each, or "nothing">
Skipped: <check and why, e.g. "docker build: Docker not running">
Needs you: <decisions only the user can make, or "nothing">
```

`blocked` means something fails that you could not fix. Say what and stop.
