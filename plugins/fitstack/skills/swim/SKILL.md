---
name: swim
description: Analyze the user's recent swims and recommend the next swim session — technique drills, intervals, or a continuous-distance build. Use when the user asks about swimming, a swim they did, or what swim to do next.
---

# Swim

Follows [skill-format](../../reference/skill-format.md): inputs, analysis,
recommendation. Gather focus: "swims".

## Analysis

- Sessions per week, total distance `(calc)`, and the longest continuous freestyle
  distance. If the data cannot tell continuous from interval swimming, say so in
  `NOTES` instead of guessing.
- Compare against this month's swim milestone.
- How past swim plans went (`outcome` records).

## Recommendation

- **No swim history:** a baseline session. 5 min easy, then freestyle as far as is
  comfortable, rest, and repeat 3 times. Tell the user to log the distance.
- **Building to continuous distance:** mostly intervals with short rest that add up to
  more than the current continuous best (e.g. 8–10 × 50 m with 20–30 s rest), then one
  continuous swim about 10–20% longer than the current best.
- **Every session:** 2–3 technique drills (catch-up, side kick, bilateral breathing).
- Give distance per set and rest.
