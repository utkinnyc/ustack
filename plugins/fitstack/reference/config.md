# fitstack config

All of the user's fitstack data lives in one folder, the **fitstack folder** (e.g. an
Obsidian folder named `fitstack`). Nothing personal lives in this plugin, and nothing
outside that folder is used (see [agent-rules](agent-rules.md)).

## Finding the fitstack folder

Use the first that applies:

1. A folder path the user gave in this conversation.
2. The current working directory, if it contains `AgentReferences/config.md`.
3. Otherwise, ask the user once for the folder's path.

The config is always `<fitstack folder>/AgentReferences/config.md`. Every path in it is
relative to the fitstack folder.

## Expected layout

```
<fitstack folder>/
  AgentReferences/
    config.md              ← this config
    goals.md               ← the user's goals
    milestones.md          ← monthly milestones toward the goals
    state.jsonl            ← fitstack's memory (see state.md)
    personal-rules.md      ← rules learned for this user (see training-rules.md)
  WorkoutLogs/             ← daily log files, e.g. "Nov 12.md"
  WorkoutMonthlyAggregated/ ← one file per past month, e.g. "October 2026.md"
```

## If the config is missing

The `setup` skill creates it, detecting what it can and asking only for the rest. It
writes `AgentReferences/config.md` with this template. Unknown values are `none`.

```markdown
# fitstack config

- distance_units: metric | imperial
- weight_unit: lb | kg                      # used when a log line states no unit
- week_starts: monday | sunday              # for weekly volume
- daily_logs: WorkoutLogs
- monthly_logs: WorkoutMonthlyAggregated
- goals: AgentReferences/goals.md
- milestones: AgentReferences/milestones.md
- state_log: AgentReferences/state.jsonl
- personal_rules: AgentReferences/personal-rules.md
- meal_photos: <folder> | none
- imessage_to: <phone> | none
```

## Workout log lifecycle

- **Daily files** (`daily_logs`): one file per training day, named like `Nov 12.md`, with
  no year. They hold the current month, and the previous month until it is aggregated.
- **Monthly files** (`monthly_logs`): after a month ends, its daily files are compacted
  into `<Month YYYY>.md`, e.g. `October 2026.md`, with each day under a heading like
  `## October 1`.
- **Which to read:** for a month that has a monthly file, read the monthly file and
  ignore that month's daily files. For any other month, read the daily files.
- **Month files inside `daily_logs`** (e.g. `WorkoutLogs/November 2026.md`) are not part
  of this layout. Ignore them, and tell the user, because they duplicate the daily
  files.
- **`## Summary` sections** in monthly files are written by an AI, not logged by the
  user. They are derived figures. Never use them as source data.
- Log format is free-form. Sets are usually written `weight x reps`, with optional
  notes, but users write them in many ways.

## Data sources

Any source may be unavailable on a given run: a connector is not set up, a tool is
missing, a file does not exist yet. Report which sources were missing, continue with the
rest, and never fill in what a missing source would have said.

- **Workout logs:** the daily and monthly files above.
- **Strava** (connector, read-only): runs, rides, swims, court sports, sometimes
  strength sessions, with notes and descriptions.
- **Apple Health** (only when the app running fitstack exposes Apple Health tools):
  workouts, heart rate, and calories.
- **Goals and milestones:** `goals` and `milestones`. Read them every run.
- **State log:** `state_log`; see [state](state.md).
- **Personal rules:** `personal_rules`; see [training-rules](training-rules.md).
