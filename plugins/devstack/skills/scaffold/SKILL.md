---
name: scaffold
description: Bootstrap a new small web app with the devstack house defaults (TypeScript, Next.js App Router, plain CSS, node:sqlite, in-process scheduler, single Node 24 Docker container) and a private GitHub repo. Use when the user wants to start a new app or says /scaffold.
---

# Scaffold

Create a new app in one pass; write each file once. Ask only for the app name
(kebab-case, `<app>`; `<APP>` is its upper-snake form) if unknown. Follow `docs/plan.md`
if it exists. Do not run `create-next-app`. Dependencies: `next`, `react`, `react-dom`,
and dev `typescript`, `@types/node`, `@types/react`, `@types/react-dom`. Nothing else
without asking.

## Files

- `package.json`: private, `"type": "module"`, engines node `>=24`, scripts `dev`, `build`
  (`next build`), `start` (`node .next/standalone/server.js`), `typecheck` (`tsc --noEmit`).
- `tsconfig.json`: strict, bundler resolution, `src/` layout, alias `@/*` to `src/*`.
- `next.config.ts`: `{ output: "standalone" }`.
- `src/lib/db.ts`: `DatabaseSync` from `node:sqlite`; path from `<APP>_DB` (default
  `data/<app>.db`, `/data/<app>.db` in Docker); `mkdirSync` its folder; `PRAGMA
  journal_mode = WAL`; `CREATE TABLE IF NOT EXISTS` on first open; one connection cached
  on `globalThis` so dev HMR never reopens it.
- `src/lib/http.ts`: `fetchJson(url, {timeoutMs, retries})` with `AbortController`,
  retrying network errors, 5xx and 429 but never other 4xx; and `mapLimit(items, n, fn)`
  for bounded concurrency. No axios or p-limit.
- `src/lib/scheduler.ts`: `jobs = [{name, everyMs, run}]`, a sequential 5s tick that runs
  each due job, catching errors; per-job `{status: "ok"|"error", durationMs, at}` kept
  in memory. `src/app/api/health/route.ts` returns that map as JSON.
- `src/instrumentation.ts`: `register()` starts the scheduler only if
  `process.env.NEXT_RUNTIME === "nodejs"`, `<APP>_DISABLE` is not `1`, and a
  `globalThis` flag is unset (dynamic import, start once). `<APP>_DISABLE=1` serves the
  UI without jobs.
- `src/lib/llm.ts`: POST to `${LLM_BASE_URL}/chat/completions` (OpenAI-compatible) via
  `fetchJson`; key from `LLM_API_KEY` or `HF_TOKEN`; model `LLM_MODEL`; default base is
  the Hugging Face router. With no key it returns `null`; callers degrade, never break.
- `src/app/layout.tsx`, `page.tsx`: server components. Any page reading the DB exports
  `export const dynamic = "force-dynamic"`. Filters are a GET `<form>`.
- `src/app/refresh.tsx`: the only `"use client"` component, calls `router.refresh()` on
  an interval and renders nothing. Sparklines and charts are inline server-rendered SVG.
- `src/app/globals.css`: system fonts, CSS variables for color and spacing, dark
  variables under `prefers-color-scheme`. No Tailwind, shadcn, chart libs or animations.
- `Dockerfile` (exactly this shape):

```dockerfile
FROM node:24-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:24-slim
WORKDIR /app
ENV NODE_ENV=production HOSTNAME=0.0.0.0 PORT=3000 <APP>_DB=/data/<app>.db
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
VOLUME /data
EXPOSE 3000
CMD ["node", "server.js"]
```

- `.dockerignore`: `node_modules`, `.next`, `data`, `.git`, `.env*`.
- `.env.example`: every env var (`<APP>_DB`, `<APP>_DISABLE`, `LLM_BASE_URL`,
  `LLM_API_KEY`, `LLM_MODEL`, ...) with a one-line comment each.
- `.gitignore`: `node_modules`, `.next`, `data`, `.env*` except `.env.example`,
  `next-env.d.ts`. `public/.gitkeep` so the Dockerfile `COPY` works.
- `README.md`: what it is, local run, env var table, `docker build` and
  `docker run -v data:/data -p 3000:3000`, deploy note.

## Verify and publish

1. `npm install`, `npm run typecheck`, `npm run build`; fix failures.
2. If prototype code exists, make the first commit of it before rewriting so history
   keeps the prototypes.
3. `git init -b main`, commit `feat: scaffold <app>` (with the attribution Claude Code asks for, if any).
4. Ask before creating the remote, then `gh repo create <app> --private --source=. --push`. Never public unless told.
5. Report the repo URL and how to run. If `gh` or Docker is unavailable, skip that step
   and say so.
