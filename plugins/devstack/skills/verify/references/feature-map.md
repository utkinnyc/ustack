# Feature Map

A compact index of what the app does and how to drive it. Agents read the one entry they need instead of exploring the codebase. Build it from the code (routes, screens, CLI commands), not from memory.

## `docs/features/README.md`

```markdown
# <app> features

Last verified: <commit sha>

| Feature | Surfaces | What it does |
|---|---|---|
| [Sign in](sign-in.md) | web, iOS | Apple sign-in, session per device |
| [Logs](logs.md) | CLI, iOS, Watch | add, list and delete entries |
```

## One file per feature: `docs/features/<feature>.md`

```markdown
# Logs

Add, list and delete log entries.

## Sub-features
- add: from the CLI (`app log add`), the iPhone's + button, the Watch's dictation.
- list: newest first, paged by 50.

## How a user gets there
iPhone: Logs tab → + . Watch: open the app, tap Log. CLI: `app log add "<text>"`.

## Driving it
control up
control cli log add "test entry"        # → {"ok": true, "id": "…"}
control state logs --limit 1            # → the entry above
control ios open-url app://logs         # then: control ios screenshot /tmp/logs.png

## Gotchas
- The Watch syncs through the phone; allow ~5 s before checking `state`.
```

Keep each file under about 40 lines. When a feature is removed, delete its file and its row.
