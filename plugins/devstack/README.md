# devstack

devstack is a personal software factory for Claude Code: shape the product, design the
system, build it with parallel agents, ship it to a VPS and Apple devices, and learn the
stack along the way. Its web-app skills use the same stack and habits every time. It is opinionated
and meant to be tuned over time.

```
/devstack:product-manager       # brainstorm the product: who, why, scope, decision log
/devstack:distinguished-engineer # technical design and a parallel build plan
/devstack:orchestrate            # F0 + parallel worktree agents + merge plan
/devstack:explain                # learn a codebase or concept, with analogies
/devstack:selfhost               # VPS + Cloudflare + Caddy runbook (you run the commands)
/devstack:apple-ship             # signing, devices, TestFlight, App Store
/devstack:resume                 # Typst resume + tailoring to a job description
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
| `product-manager` | Acts as your PM: frames the product, asks one topic at a time, keeps a decision log, writes the product doc after the brainstorm. |
| `distinguished-engineer` | Acts as a principal engineer: data model, stack, contracts, auth, CI/CD, secrets, agent guardrails, and an F0 + parallel workstreams build plan. |
| `orchestrate` | Runs a plan as one foundation step plus parallel agents in git worktrees, then merges in dependency order and passes an end-to-end smoke test. |
| `explain` | Teaches a codebase or concept briefly, grounded in the code, with C++/Python/TypeScript analogies, a reading order and diagrams. |
| `selfhost` | Step-by-step VPS setup and deploys: SSH keys, ufw, Cloudflare DNS, Caddy, systemd. Never touches the server itself. |
| `apple-ship` | Gets iPhone/Watch/TV apps onto devices and TestFlight: developer account, signing, Developer Mode, bundle IDs. |
| `resume` | Resume as Typst code: measured one-page layout, crisp honest bullets, tailoring and fit checks against a job description. |
| `plan` | Writes a short design note to `docs/plan.md`, gets a yes, then stops. |
| `scaffold` | Bootstraps the app, Dockerfile, config files and a private repo. |
| `review` | Typecheck, lint, build, then a short ship checklist; fixes what it finds. |
| `ship` | Runs `review`, commits, pushes, opens a PR; includes a deploy workflow template. |
