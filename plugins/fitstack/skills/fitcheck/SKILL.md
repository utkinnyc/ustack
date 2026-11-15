---
name: fitcheck
description: Automatic readiness check before every plan, without asking the user questions. Judges past plans against what was actually done, carries forward open injuries, reads pain and form notes from logs, Strava and the conversation, and flags anything unsafe. Called by `next`; use directly when the user asks whether they are fit to train or how their past plans went.
---

# Fitcheck

Rules: [agent-rules](../../reference/agent-rules.md), [training-rules](../../reference/training-rules.md)
section 1 and section 3, [state](../../reference/state.md).

**Ask the user nothing.** Work only from what fitstack already knows. Never invent a
score or a feeling.

## Inputs

- The gather output. If it is not in the conversation, invoke `gather`.
- The state log: the last 30 days, plus all `injury` records.
- The user's messages in this conversation.

## Steps

1. **Judge open plans** (training-rules section 3), including a plan for today:
   - Look in the gather output for a matching workout from the plan's day up to and
     including today, matched by sport and focus as the table in section 3 says.
   - Found → append an `outcome` record with the status from that table and the diffs.
     Add any notes on that workout as `feedback`.
   - Not found → still pending, or `expired` after 5 days.
   - The user said they skipped it → `skipped`.
   - A plan for today that is now done → report `done today: <plan id>`.
2. **Collect pain and form signals:**
   - Open `injury` records. They stay open, with their restrictions, unless the user
     said the area is better.
   - Notes in the gather output from the last 7 days that mention pain, soreness, a
     tweak, or bad form.
   - Anything the user said in this conversation.
   - A new signal → append an `injury` record (`open`) with only the fields that are
     known. The user says an area is better → append the same `id` with `resolved`.
3. **Collect other constraints** from the user's messages only: time available, sport
   later today, no gym or pool, travel, illness, sleep, energy.
4. **Classify** against training-rules section 1: **RED FLAG**, **moderate**, **mild**
   or **clear**. A pain signal with no score is handled as **mild** for that area, and
   says so.
5. **Write** one `checkin` record with only the known fields, `source` `user` or
   `inferred`.

## Output

```
FITCHECK: clear | mild | moderate | RED FLAG
pain: <area, score or "no score", since <date>, source> | none
assuming: <what was carried forward, e.g. "left knee still sore (open since Nov 10)"> | nothing
pending plan: <id>, pending since <the plan's `for` day> | none
outcomes: <plan id → status, key diff>, ... | none
done today: <plan id, or the workout logged today> | no
constraints: <from the user's messages> | none
```

For a RED FLAG, the first line after `FITCHECK` says which red flag and why.
