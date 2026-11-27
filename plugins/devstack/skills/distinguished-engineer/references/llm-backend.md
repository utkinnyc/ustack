# Backends driven by an LLM

The answers that came up while designing an app shaped like "capture something → an LLM processes it in the background → store the results → the apps read them".

## Two layers

```
┌─ app (the product) ─────────────────────────────┐
│ domain models, API routes, MCP tools, prompts,   │
│ job handlers, integrations                       │
└──────────────── uses ↓ ─────────────────────────┘
┌─ platform ──────────────────────────────────────┐
│ config, DB pool + migrations, time, users,       │
│ devices, sign-in, tokens, job queue + worker,    │
│ agent runner, MCP server shell, run/cost records │
└─────────────────────────────────────────────────┘
```

- **The one rule:** the platform never imports from the app. The app plugs in through a few interfaces, e.g. `JobHandler` (one per job kind), `ToolSet` (its tools) and the HTTP services.
- **Keep app details out of the platform.** Job payloads are `kind: String` plus JSON, so the queue doesn't know what an input or a workout is; the app turns the payload into its own typed struct. Tool names, the system prompt, the MCP server name, plugin paths and sign-in policy (e.g. owner-only) are all app settings.
- **Two model files:** `system` (users, devices, jobs, agent runs, tool calls) and the domain (`fitness`, …). Keep each enum next to the struct that uses it.
- **Layers are two crates, or two modules.** Crates per area only pay off for teams, long builds or publishing.
- **Reuse:** the platform could serve another app. Build it for this one, keep the rule strict, and only pull it out when a second app really exists. One server per app, sharing a library, beats one server hosting many apps.
- **Names, if asked:** this is layered architecture and separation of concerns ("platform vs product"), i.e. software architecture. It isn't systems engineering, and it isn't low-level (close-to-hardware) work. **Ports and adapters:** the port is the interface the core defines (the socket), and an adapter is the implementation plugged in at startup (the plug).

## Data model

- **Raw inputs are the source of truth** and never change.
- The LLM writes **loose results**: a short text summary plus a JSON blob in whatever shape it likes. Strict per-set or per-item schemas fight messy real-world logs.
- Keep strict structure only for things with a lifecycle (goals, injuries, plans, jobs), plus the few numbers that charts and goals need.
- New needs (embeddings, other data sources, video analysis) get **new tables in new migrations**. Never edit a migration that has already been applied in production.

## Jobs

- **A queue in SQLite**, not RabbitMQ, Redis or SQS, while there's one server. Saving an input and enqueuing its job commit in one transaction, with no outbox pattern and no extra service to run. A broker wouldn't cover budgets, per-job tool tokens, cost records, dedup keys or the status the app polls anyway.
- Rust queue libraries (apalis, effectum) were pre-1.0 or quiet, and bring their own tables and retry model. The queue itself is ~200 lines, so keep your own.
- **Concurrency:** async tasks, not threads. The real limit is the LLM processes (a few hundred MB each, plus rate limits), so set it from server RAM and add per-user fairness (at most one running job per user).
- **Heartbeat and leases** only matter with more than one worker process.

## Models and cost

- **Pick the model per job kind:** a small model (Haiku) for high-volume extraction, a mid model (Sonnet) for estimates, the big one (Opus) for planning and hard vision. Most of the saving comes from parsing.
- **Other providers** fit as another adapter behind the agent-runner port. Tool calling and the CLI's features don't carry over for free, so say what's lost.
- **Whose Claude account:** the Agent SDK terms don't allow offering claude.ai login or subscription limits to other users without Anthropic's approval, or storing their claude.ai tokens. A personal subscription token is fine for the owner alone. Once other people use the app, switch to an API key, optionally the user's own. Check the current docs before quoting this.
  - Plugins, skills and MCP servers work the same with an API key. Only claude.ai connectors need a claude.ai login.
  - With an API key, add per-user rate limits (runs per day, checked before a run starts, 429 when over) and a monthly spend cap in the Console.

## Ports and processes

- The MCP tool server is a second listener in the same process, bound to `127.0.0.1`, so the LLM subprocess can reach it and the internet can't. That works the same on a VPS. Use stdio only if you accept a new process per run.
- Reverse proxy to `127.0.0.1:<port>` over plain HTTP is normal. The port numbers are arbitrary; a Unix socket also works.

## Logs

One JSON line per request with a request ID, route template, status and duration makes a failing request easy to find. Free hosted log portals with a small agent on the server include Grafana Cloud's free tier and Axiom's free tier. Say these limits come from memory and check current pricing. Skip self-hosting Loki or Elasticsearch on a small box.
