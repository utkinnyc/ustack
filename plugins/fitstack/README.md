# fitstack

fitstack is a training partner for Claude Code. It reads your workout logs and Strava,
remembers what it recommended last time and whether you did it, and tells you what to do
next. It covers strength, running, cycling and swimming, all aimed at your goals, e.g.
"marathon by Nov 2027".

```
/fitstack:next
```

That one command covers the daily use. fitstack:

- **Plans for your goals.** It works backwards from each goal's date through monthly
  milestones, and balances several goals that compete for the same legs.
- **Remembers.** If you haven't done the last recommendation yet, it gives it back
  ("pending since Tuesday"), unless you ask for something else.
- **Learns.** It compares every plan with what you actually did, and adjusts. Patterns
  become personal rules, e.g. smaller bench steps if you keep missing reps.
- **Works around injuries.** Pain or bad form on a movement means no progression there.
  It builds the supporting muscles instead. Red-flag symptoms mean no workout and a
  recommendation to see a professional.
- **Doesn't quiz you.** There's no check-in questionnaire. It works from what it already
  knows and tells you what it's assuming, so you can correct it.

## Install

```
/plugin marketplace add utkinnyc/ustack
/plugin install fitstack@ustack
```

**Requirements**
- [Claude Code](https://claude.com/claude-code).
- Workout logs as Markdown files in one folder. Obsidian works well.
- Optional: the **Strava** connector for runs, rides and swims; the **Inkbox** connector
  for `text-me`; Apple Health, where your Claude app exposes it. fitstack works with
  whichever sources are available and tells you which ones it couldn't reach.

## Your fitstack folder

All your data lives in one folder that you own. fitstack never reads or writes outside
it.

```
fitstack/
  WorkoutLogs/                 ← daily logs: "Nov 12.md", "Nov 13.md", ...
  WorkoutMonthlyAggregated/    ← past months: "October 2026.md", ...
  AgentReferences/             ← created and kept up to date by fitstack
    config.md                  ← units, folder names
    goals.md                   ← your goals and dates
    milestones.md              ← monthly targets toward the goals
    state.jsonl                ← plans, outcomes, injuries, goal progress
    personal-rules.md          ← what fitstack has learned about you
```

Write logs however you like. A common format is an exercise name followed by one set
per line:

```
Shoulder press

90 x 9 (45 each side)
90 x 9
90 x 8
```

## First run

Open Claude Code in your fitstack folder (or give it the folder's path) and run
`/fitstack:next`. The `setup` skill:

1. Detects your log folders and units.
2. Asks once about your goals.
3. Takes a baseline from your recent training.
4. Proposes milestones, and writes them once you agree.

It never overwrites files that already exist. Then you get your first workout.

## Skills

| Skill | What it does |
|---|---|
| **`next`** | **Start here.** Decides your next workout, or a week plan, across all sports. |
| `setup` | First run: creates whatever is missing in `AgentReferences/`. Never overwrites. |
| `goals` | Shows, adds, changes or retires goals, and re-proposes milestones to match. |
| `fitcheck` | Checks past plans against what you did, carries forward injuries, flags red flags. Asks nothing. |
| `gather` | Fetches your workouts from the logs, Strava and Apple Health. |
| `strength` | Next lift session: from your history, on request ("chest day"), or a full-body default. |
| `run` · `ride` · `swim` | Analyze recent sessions and recommend the next one. |
| `rehab` | Works around pain and form problems: what to avoid, what to strengthen, what to swap. |
| `text-me` | Texts you the plan over iMessage, via Inkbox. |
| `nutrition` | Under development. |

You can call any skill directly, e.g. `/fitstack:run` to ask about your last run.

**Agent:** `data-gatherer` fetches the raw data in its own context, so your logs don't
flood the conversation. It is read-only (enforced by its tool list) and keeps no state.

## How it fits together

```
next ─┬─ setup        (first run only)
      ├─ gather ──── data-gatherer agent (logs, Strava, Apple Health)
      ├─ fitcheck     (past plans → outcomes, injuries, red flags)
      ├─ strength · run · ride · swim   (+ rehab when there's pain)
      └─ text-me      (only if you ask)
```

Every sport skill has the same shape: inputs (your data, fitcheck, goals), analysis
(the training rules, applied to your pattern) and one fixed recommendation block. The
shared rules are in [`reference/`](reference/):

- `agent-rules.md`: what every skill and agent must follow (folder boundary, writes,
  honest data).
- `training-rules.md`: safety, goals, the feedback loop, personal rules, load and
  progression.
- `state.md`: the state log's record types.
- `config.md`: the folder layout and data sources.
- `skill-format.md`: the shape every sport skill follows.

## Privacy and safety

- **Nothing personal is in this repo.** Your logs, goals and history stay in your
  folder.
- fitstack never edits your workout logs, and never pushes or syncs your notes.
- It labels estimates as estimates, and never fills in data a source doesn't have.
- fitstack is a training partner, not a clinician. It never diagnoses. For red-flag
  symptoms, it stops and recommends a doctor or physiotherapist.

## Status

Being tested. Nutrition tracking is not built yet, and Apple Health
depends on the app running Claude exposing it. Issues and suggestions are welcome.

## Adding a skill

Create `skills/<name>/SKILL.md` and open a PR; the version is bumped for you (see the
[root README](../../README.md#contributing)). A sport skill should follow [`skill-format.md`](reference/skill-format.md).
