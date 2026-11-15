# devstack

devstack is a personal software factory for Claude Code: plan, scaffold, review and
ship small web apps fast, with the same stack and habits every time. It is opinionated
and meant to be tuned over time.

```
/devstack:plan      # design note in docs/plan.md, then wait for a yes
/devstack:scaffold  # new app + private GitHub repo
/devstack:review    # pre-ship self-review
/devstack:ship      # review, commit, push, open a PR
```

## The stack

- TypeScript, Next.js (App Router), plain CSS. No Tailwind, shadcn or animations.
  Server components first, minimal client JS.
- One container: Node 24 slim image, `next build` with `output: "standalone"`, SQLite
  via the built-in `node:sqlite` on a mounted volume, background jobs started from
  `instrumentation.ts`.
- Railway (or any Docker host), deployed from GitHub Actions.

## Habits

- Private GitHub repos. Small conventional commits (`feat:`, `fix:`, `docs:`), each ending
  with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- Frugal with tokens: no exploratory reading, write files once, prefer built-ins over
  dependencies, ask before adding one, be conservative when in doubt.

## Install

```
/plugin marketplace add utkinnyc/ustack
/plugin install devstack@ustack
```

**Requirements:** [Claude Code](https://claude.com/claude-code), Node 24, Docker, and the
`gh` CLI signed in. The deploy workflow needs a `RAILWAY_TOKEN` repo secret.

## Skills

| Skill | What it does |
|---|---|
| `plan` | Writes a short design note to `docs/plan.md`, gets a yes, then stops. |
| `scaffold` | Bootstraps the app, Dockerfile, config files and a private repo. |
| `review` | Typecheck, lint, build, then a short ship checklist; fixes what it finds. |
| `ship` | Runs `review`, commits, pushes, opens a PR; includes a deploy workflow template. |
