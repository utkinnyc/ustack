# Sport skill format

Every sport skill (`strength`, `run`, `ride`, `swim`, and any added later) has the same
three parts: inputs, analysis, recommendation. `next` combines their output, so the
recommendation block is always the same shape.

## 1. Inputs

Follow [agent-rules](agent-rules.md) first, including test mode (rule 5).

- **The user's request**, if any (e.g. "chest day", "a short run").
- **From `next`**, when it called the skill: the day type and constraints.
- **Gather output** for this sport. If it is not already in the conversation, invoke
  `gather` with the skill's focus (e.g. focus "runs").
- **Fitcheck result.** If it is not already in the conversation, invoke `fitcheck`.
- **Goals, milestones, personal rules and state**, read as described in
  [config](config.md) and [state](state.md).

## 2. Analysis

- Apply the rules in the order of [training-rules](training-rules.md) section 0: red
  flags, then pain and injury, then personal rules, then defaults.
- Look at the user's pattern for this sport: recent sessions, and the `outcome` records
  of past plans (did they do what was planned, more, or less?).
- Place the session in the goal's current phase, and check this month's milestone.
- Use only numbers from the gather output. Mark anything computed as `(calc)`. If data
  is missing, say what is missing; do not fill it in.

## 3. Recommendation

Return this block:

```
SESSION: <sport> · <type, e.g. long run / upper push> · for <YYYY-MM-DD>
GOAL: <goal it serves> · phase <base/build/peak/taper or n/a> · milestone <on track / behind / ahead / none>
WHY:
- <1–3 bullets: what in the data and rules led here>
WARM-UP: <from training-rules section 8>
MAIN:
- <exercise or segment with targets>  (last: <last session's numbers>)
COOL-DOWN: <from training-rules section 8>
NOTES: <form cue, fuelling, rehab swaps, missing data; or "none">
PLAN: <the `plan` record for the state log, as one JSON line>
```

- Called by `next`: return the block. `next` presents it and writes the plan record.
- Called directly by the user: present the block (without the `PLAN` line), then append
  the plan record to the state log yourself.
- If the user asked about past sessions, add up to three analysis bullets after the
  block.
