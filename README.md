# ustack

A Claude Code plugin marketplace.

## Install

```
/plugin marketplace add utkinnyc/ustack
/plugin install <plugin>@ustack
```

To pick up updates, run `/plugin marketplace update ustack`.

## Plugins

| Plugin | What it does |
|---|---|
| [fitstack](plugins/fitstack/) | A training partner that plans your next workout from your logs, Strava and goals. |

Each plugin's README covers its setup and skills.

## Contributing

**Add a plugin:**
1. Create `plugins/<name>/.claude-plugin/plugin.json`, `plugins/<name>/skills/`, and
   a `README.md`.
2. Add an entry to the `plugins` array in `.claude-plugin/marketplace.json`.
3. Add a row to the table above.

**Change a plugin:** bump `version` in its `plugin.json`, so installed copies update.
