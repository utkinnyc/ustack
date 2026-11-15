---
name: run
description: Analyze the user's recent runs (pace, heart rate, volume, long run, trends) and recommend the next run — easy, long, tempo, intervals or rest. Use when the user asks about a run they did, their running progress, or what run to do next.
---

# Run

Follows [skill-format](../../reference/skill-format.md): inputs, analysis,
recommendation. Gather focus: "runs, with splits and heart rate".

## Analysis

- Weekly distance for the last 3–4 weeks and the change week to week (flag more than
  10%). Mark these `(calc)`.
- Longest run, compared with this month's milestone.
- Easy-run pace at similar heart rate: improving, flat, or slipping.
- How past run plans went (`outcome` records): did the user hold the target pace and
  distance?
- If the user asked about one run: splits, pacing (even, faded, negative split), heart
  rate drift, and one thing to do differently.

## Recommendation

- Pick the type from the week so far: **easy** (conversational), **long** (weekend, +1–2
  km over the last long run, within the 10% rule), or one **quality** session a week
  once the goal's phase allows it (tempo or strides).
- Give distance or duration and a target effort first, with pace as a guide.
- Cutback week (every 4th week): about 25% less volume.
