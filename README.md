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

**Change a plugin:** open a PR to `main` (direct pushes are blocked). A workflow bumps
the `version` of every plugin the PR changes, so installed copies update, and the PR
can't merge until its `version-bump` check passes. The PR title picks the bump:

| PR title | Bump | Use for |
|---|---|---|
| `fix: ...`, `docs: ...`, anything else | patch, 1.1.0 → 1.1.1 | fixes and wording |
| `feat: ...` | minor, 1.1.0 → 1.2.0 | something new that changes nothing for existing users |
| `feat!: ...`, `fix!: ...` | major, 1.1.0 → 2.0.0 | something users rely on changed or was removed |

A `major`, `minor` or `patch` label on the PR overrides the title.
