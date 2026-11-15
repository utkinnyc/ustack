# ustack

Utkarsh's Claude Code skills, packaged as a plugin marketplace.

## Install

```
/plugin marketplace add utkinnyc/ustack
/plugin install fitstack@ustack
```

## Plugins

### fitstack — fitness and training

Start with `/fitstack:next`. It gathers your data, runs a fitcheck without asking you
questions, gives back any pending plan, or picks the next session and calls the right
sport skill.

| Skill | What it does |
|---|---|
| `next` | Decides your next workout (or week) across all sports |
| `setup` | First run: creates missing config, goals, milestones, state and personal rules |
| `fitcheck` | Judges past plans, carries forward injuries, flags red flags; asks nothing |
| `gather` | Fetches workout logs, Strava and Apple Health (via the `data-gatherer` agent) |
| `strength` | Next lift session: from history, on request, or full-body default |
| `run` / `swim` / `ride` | Analyze recent sessions and recommend the next one |
| `rehab` | Works around pain and form problems: what to avoid, add and swap |
| `nutrition` | Under development |
| `text-me` | Sends the plan over iMessage via Inkbox |

Agent: `data-gatherer` is read-only and stateless; it returns every workout by date.

Shared rules live in `plugins/fitstack/reference/`.

**Personal setup.** Nothing personal is stored in this repo. All your data lives in one
fitstack folder (e.g. in Obsidian). The config, goals, milestones, state log and
personal rules are in its `AgentReferences/` folder, and fitstack never reads outside
it. Needs the Strava connector for cardio data and the Inkbox connector for `text-me`.

## Adding a skill

Drop a folder with a `SKILL.md` into `plugins/<plugin>/skills/`, bump `version` in
`plugins/<plugin>/.claude-plugin/plugin.json`, and push. Then run
`/plugin marketplace update ustack` to pick it up.

## Adding a plugin

Create `plugins/<name>/.claude-plugin/plugin.json` and `plugins/<name>/skills/`, then add an
entry to the `plugins` array in `.claude-plugin/marketplace.json`.
