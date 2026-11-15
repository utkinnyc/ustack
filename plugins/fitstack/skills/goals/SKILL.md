---
name: goals
description: View or change the user's fitstack goals — add a goal, change a target or date, reprioritise, mark one achieved, or drop one — and re-propose milestones to match. Use when the user wants to set, add, update, enhance, change or remove a goal, or asks what their goals and milestones are.
---

# Goals

Rules: [agent-rules](../../reference/agent-rules.md), [config](../../reference/config.md),
[state](../../reference/state.md), [training-rules](../../reference/training-rules.md)
sections 2, 5 and 7.

## Principles

- **Change only what the user asked.** Every other goal stays exactly as it is.
- **Never lose history.** A dropped or achieved goal moves to `## Past goals`; it is
  not deleted. `goal_progress` records are never rewritten.
- **Ask at most once.** If a new or changed goal has no target, ask once in plain text.
  A goal with no date is allowed; it gets no milestones.
- **Test mode** (agent-rules rule 5): with `dry_run`, write nothing. Show each file's
  full new content under `WOULD WRITE`.

## Steps

1. **Find the fitstack folder** and read the config. If the config or `goals.md` is
   missing, invoke `setup` instead and stop; setup creates the first goals.
2. **Read** `goals.md`, `milestones.md` and all `goal_progress` records in the state log.
   If the user only asked what their goals are, show them with this month's milestone
   and the latest progress, and stop.
3. **Work out the change**, one or more of:
   - **Add**: a new goal with a target and, if given, a date (`YYYY-MM`).
   - **Change**: a goal's target, date or both.
   - **Achieve** or **drop**: move it to `## Past goals` with `status: achieved` or
     `status: dropped` and the date.
   - **Reprioritise**: the user's order wins. Otherwise apply training-rules section 2:
     the goal with the nearer date is priority 1; undated goals come after dated ones.
4. **Baseline.** For a new goal, or a changed goal whose metric changed, invoke `gather`
   with the goal's sport or exercise as the focus. Append one `goal_progress` record from
   measured data only (e.g. the fastest 10K-length run, a lift's best set). No matching
   data → no baseline, and say so.
5. **Write `goals.md`** with the change applied, in the format setup uses, nearest date
   first:

   ```markdown
   # Goals

   ## 10K under 55 min
   - target: run 10 km in under 55:00
   - by: 2027-03
   - priority: 1

   ## Past goals

   ## 5K
   - target: run 5 km without stopping
   - by: 2026-09
   - status: achieved 2026-09-20
   ```

6. **Re-propose milestones** for every goal that was added or whose target or date
   changed: work backwards from the date through the phases in training-rules section 2,
   from the baseline, within the load rules in section 5. Keep the other goals' columns
   as they are; drop the columns of past goals. Show the proposal and write
   `milestones.md` only once the user agrees.
7. **Report** in a few lines: the goals before and after, the new priority order, and
   what changes in training (e.g. "runs now lead; strength drops to 2 sessions a week").
   Append a `note` record describing the change (e.g. `"Added goal: 10K under 55 min by
   2027-03"`).
