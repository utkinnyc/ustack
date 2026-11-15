---
name: card
description: The last step of every fitstack workout. Turns the decided session into a short card of exercises and targets, shows only that card, and texts it to the user if they set that up. Called by `next` and by the sport skills; use directly when the user asks to see today's plan again or asks "why" about it.
---

# Card

Rules: [agent-rules](../../reference/agent-rules.md), [config](../../reference/config.md).

The user wants the workout and nothing else. You only present and deliver. Never change
the session: no adding, dropping or re-ordering exercises, and no changing targets.

## Input

From the calling skill: the session (every exercise or segment with its targets, after
any `rehab` swaps), whether it is a pending plan and since which day, and any pain or
injury restriction that shaped it.

## The card

```
<Session name> <emoji>

1. <Exercise>: <set>, <set>, <set>
2. <Exercise>: <set>, <set>, <set>
3. <Endurance segment>: <distance or time> at <pace or effort>

⚠ <one line, only if pain or an injury shaped the session>
```

- **Title:** the session in 2–4 words, one emoji (e.g. `Back Day 💪`, `Easy Run 🏃`).
  For a pending plan, add `(pending since <day>)`, e.g. `Easy Run 🏃 (pending since Nov 13)`.
- **Strength:** every set written out, `<weight>x<reps>`, e.g.
  `1. Lat pulldown: 135x10, 140x8, 140x8`. Add `each side` when it applies. Holds are
  times: `Dead hang: 30s, 30s, 25s`. Bodyweight: `BW x12`.
- **Endurance:** one line per segment: distance or time, then pace, heart rate or
  effort, e.g. `1. Easy run: 4 km at 7:00–7:30/km, HR under 150`.
- **⚠ line:** at most one, and only when pain, an injury or form shaped the session,
  e.g. `⚠ Lower back: no squats or deadlifts. Stop anything that hurts.`
- **Nothing else.** No reasons, assumptions, last-session numbers, warm-up, cool-down,
  alternatives, data notes, goal or milestone status, or questions.

## The reply

Your whole reply is the card. The only other lines allowed:

- **Red flag** (training-rules section 1): no card. Two lines: what the flag is, and to
  see a doctor or physiotherapist.
- **First run** (setup just ran): one line after the card, e.g. `Set up ✓ Goals saved.
  Say "show milestones" to review the plan to May 2027.`
- **Already trained today** (the session is for tomorrow): `Done today ✓` as the first
  line, and the title starts with `Tomorrow:`, e.g. `Tomorrow: Back Day 💪`.
- **Texting not yet confirmed** (step 2 below): one line saying how to start it.
- **Test mode** (agent-rules rule 5): the `TEST MODE` line first, and the `WOULD WRITE`
  section last. These are for testing, not the user.

## Steps

1. **Show the card** as above.
2. **Text it** if the config has `text_plans: always` and an `imessage_to` number:
   invoke `text-me` with the card exactly as shown. Do not mention the text if it was
   sent. If it fails with `imessage_awaiting_inbound`, add one line: `Text START to
   <the agent's number> once to get your workouts by text.` If `text_plans` is `never`
   or missing, send nothing and say nothing.

## Follow-ups

- **"why" / "details":** answer in at most 5 short bullets from the plan's `reason` and
  the decision already made in this conversation (or the latest `plan` record in the
  state log). Then stop.
- **"show milestones" / "warm-up?":** show just that, briefly.
- **"text me":** invoke `text-me` with the last card.

## Week plan

One line per day, no more:

```
Week of Nov 16 📅

Mon: Easy run 5 km
Tue: Upper push
Wed: Rest
...
```
