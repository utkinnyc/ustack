---
name: strength
description: Plan the next strength session from the user's lift history, a specific request (e.g. "chest day", "something with dumbbells"), or a full-body default when there is no history. Use when the user wants a lifting or gym workout.
---

# Strength

Follows [skill-format](../../reference/skill-format.md): inputs, analysis,
recommendation. Gather focus: "strength". Weights use the config's `weight_unit`.

## Analysis

- **Pattern:** for each exercise, the last session's sets, and whether past plans for
  it were done as planned, more, or less (`outcome` records).
- **Pick the session:**
  1. **Requested:** the user named a muscle group, exercise or equipment → build that.
  2. **History:** the muscle group trained longest ago that today's constraints allow.
     Rotation: legs, push (chest, shoulders, triceps), pull (back, biceps), with core
     added to any day. After a heavy meal, skip core and bent-over work. Before a long
     run or ride tomorrow, no heavy legs.
  3. **No history:** a full-body beginner session (see below).

## Recommendation

- 3–5 exercises in total, counting core, hangs and carries. Warm-up and cool-down
  moves do not count. If more would fit, pick the ones that serve the goal and the
  day's focus. For each exercise with history, set targets per training-rules section
  6 (or the user's personal rules), with the last session in parentheses:
  `Shoulder press: 95x8, 95x8, 95x7  (last: 90x9, 90x9, 90x9)`.
- Exercises affected by an open injury or bad form are held or reduced, never
  progressed (training-rules section 1). Add work for the supporting muscles.
- Leg days for a runner always include calf raises and one single-leg exercise.
- **No history:** 2–3 sets of 8–12 at moderate weights the user picks: goblet squat,
  dumbbell bench press, one-arm row, Romanian deadlift, plank, calf raises. Tell them to
  log weights so the next session can progress.
