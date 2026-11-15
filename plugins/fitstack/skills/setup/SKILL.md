---
name: setup
description: First-run setup for fitstack. Creates whatever is missing in the fitstack folder's AgentReferences (config, goals, milestones, state log, personal rules), detecting what it can and asking only for the rest. Never overwrites existing files. Called by `next` and `gather` when any of these files is missing; use directly when the user wants to set up or re-check fitstack.
---

# Setup

Rules: [agent-rules](../../reference/agent-rules.md), [config](../../reference/config.md),
[state](../../reference/state.md), [training-rules](../../reference/training-rules.md)
section 2.

## Principles

- **Only fill gaps.** Check each file in `AgentReferences/`. A file that exists is read,
  never overwritten, and its step is skipped. Running setup again only creates what is
  still missing. To change existing goals, use the `goals` skill.
- **Detect before asking.** Ask only for what cannot be found in the folder or Strava.
- **At most two question rounds** in total: one AskUserQuestion round, and one plain
  follow-up only if a goal still has no target or date.
- **Works with no data.** If there are no logs and Strava is unavailable, setup still
  completes. It writes no baselines, and the first plan uses the no-history defaults.
- **Test mode** (agent-rules rule 5): with `strava_snapshot`, read the athlete profile
  from the snapshot's `get_athlete_profile.json` instead of calling Strava. With
  `dry_run`, create no folder or file; list every file and its full content under
  `WOULD WRITE`, and continue the steps as if they had been written.

## Steps

1. **Find the fitstack folder** as config describes. Create `AgentReferences/` if it
   does not exist.

2. **Detect the config values:**
   - `daily_logs`: a folder of files named like `Nov 12.md` (e.g. `WorkoutLogs`).
   - `monthly_logs`: a folder of files named like `October 2026.md` (e.g.
     `WorkoutMonthlyAggregated`). If none exists, use `none`.
   - `distance_units`: from the Strava athlete profile, if Strava is available.
   - `weight_unit`: from the logs, if they state `lb` or `kg`.
   - `goals`, `milestones`, `state_log`, `personal_rules`: the default paths in config.
   - `meal_photos`: `none`. `imessage_to` and `text_plans`: from the question below.

3. **Ask one AskUserQuestion round**, skipping any question already answered by a file
   or by detection:
   - **Goals** (multi-select): e.g. "Run a marathon", "Long bike ride", "Get stronger",
     "General fitness". Ask the user to add the target and date in their own words
     (e.g. "marathon by Nov 2027", "200 km ride by June").
   - **Weight unit**, if not detected: lb or kg.
   - **Distance units**, if not detected: metric or imperial.
   - **Week starts**: Monday or Sunday.
   - **Texts**: "Text you each workout?" Options: "Yes (type your number in Other)" and
     "No". A number → `imessage_to: <number>`, `text_plans: always`. No →
     `imessage_to: none`, `text_plans: never`, and never ask again.

   If a chosen goal still has no target or no date, ask once in plain text. A goal with
   no date is allowed; it gets no milestones.

4. **Write `config.md`** with the template from config, using detected and answered
   values.

5. **Write `goals.md`**, one block per goal, nearest date first:

   ```markdown
   # Goals

   ## Marathon
   - target: finish a marathon
   - by: 2027-11
   - priority: 1
   ```

   Priority follows training-rules section 2: the goal with the nearer date is 1.

6. **Gather.** Invoke `gather` with the default window.

7. **Create `state.jsonl`** if missing. Append one `goal_progress` baseline per goal,
   only from measured data in the gather output (e.g. longest run, longest ride, a
   lift's best set). A goal with no matching data gets no baseline. Never write past
   plans or invented history.

8. **Draft `milestones.md`** for each dated goal. Work backwards from the date
   through the phases in training-rules section 2, starting from the baseline and
   growing within the load rules in section 5 (10% a week, a cutback every 4th week).
   One row per month:

   ```markdown
   # Milestones

   | Month   | Marathon (by 2027-11) | 200 km ride (by 2027-06) |
   |---------|-----------------------|--------------------------|
   | 2026-12 | long run 20 km        | long ride 80 km          |
   ```

   Write it now with `status: draft` under the heading, so training can use it and
   setup does not run again for it. Do not show it. The user reviews it when they ask
   ("show milestones"); once they agree, change the line to `status: agreed`. If they
   want changes, adjust and show it again.

9. **Create `personal-rules.md`** if missing, with only a header and one line saying
   rules are added from patterns across at least 3 comparable sessions (training-rules
   section 4).

10. **Hand back** to the calling skill, so a first `next` still ends with a workout.
    Report nothing yourself: `card` adds one line (e.g. `Set up ✓ Goals saved. Say
    "show milestones" to review the plan to May 2027.`). If setup was run directly, reply
    with only that line.
