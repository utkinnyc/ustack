---
name: gather
description: Fetch the user's recent workouts from their workout logs, Strava and Apple Health through the read-only data-gatherer agent, so raw data stays out of the conversation. Use when a plan or analysis needs training history, or when the user asks for a training summary.
---

# Gather

Rules: [agent-rules](../../reference/agent-rules.md), [config](../../reference/config.md).

1. **Find the fitstack folder** and read the config (see config). If the config is
   missing, invoke `setup`, then continue.
2. **Spawn the `data-gatherer` agent** (it may be listed as `fitstack:data-gatherer`).
   Its prompt contains, in this order:
   - The full text of agent-rules (agent-rules rule 2).
   - The fitstack folder's absolute path.
   - `daily_logs` and `monthly_logs`: the config's values as absolute paths.
   - `focus`, only if the caller named a sport or an exercise (e.g. "runs, with splits
     and heart rate", "squat"). A time span ("last 30 days", "this week") or "all
     workouts" is not a focus: pass no focus, and the agent uses its default window.
   - In test mode (agent-rules rule 5): `today`, and `strava_snapshot` as an absolute
     path, from `test-mode.md`.
3. **If the agent tool is unavailable,** do the agent's steps yourself (see
   `../../agents/data-gatherer.md`) and keep the same output format.
4. **Return the agent's output.**
   - **Called by another skill:** return it unchanged.
   - **The user asked directly:** show every workout, set and note as the agent gave
     them. You may lay them out for reading (e.g. a table), but drop nothing and change
     no value. After the workouts, add:
     - **Data notes**, in plain words, from the agent's SOURCES and STATS: sources that
       could not be fetched, ignored files (by name), strength sessions without sets (by
       date), and unmerged same-day pairs. Omit a note that does not apply.
     - **One line** on the biggest thing to act on.
   - **Add no numbers of your own.** No totals, counts, averages or trends the agent did
     not return. If you must give one, mark it `(calc)` (agent-rules rule 4).
