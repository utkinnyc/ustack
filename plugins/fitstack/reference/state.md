# fitstack state log

Claude forgets between sessions, so fitstack keeps its memory in the JSON Lines file named
by `state_log` in the config (`AgentReferences/state.jsonl`). It holds what fitstack
recommended, what came of it, how the user felt, injuries, and goal progress over months
and years. Workouts themselves live in the logs and Strava, not here.

## Format

- One JSON object per line. Append only: never rewrite, reorder or delete lines. Create
  the file if it does not exist.
- Append with a single shell `>>` of one line per record.
- Every record has `date` (YYYY-MM-DD, the day it was written) and `type`.
- Records with an `id` can be updated by appending a new record with the same `id`. The
  latest one wins.

## Record types

**`checkin`**: readiness before a session, written by `fitcheck` from what is already
known (state, log and Strava notes, the user's messages). Include only fields that are
known; never invent a score. `source` is `user` (the user said it) or `inferred`.
```json
{"date":"2026-11-12","type":"checkin","status":"mild","pain":[{"area":"left knee","score":3,"note":"stairs"}],"energy":"low","minutes":60,"constraints":["ate heavy lunch"],"source":"user"}
```

**`plan`**: a workout fitstack recommended. `for` is the day it is meant for. `goal` names
the goal it serves. Strength targets are per set; endurance targets are what was
prescribed.
```json
{"date":"2026-11-12","type":"plan","id":"plan-2026-11-13-strength","for":"2026-11-13","sport":"strength","focus":"upper push","goal":"general strength","items":[{"exercise":"Chest press","sets":[{"weight":110,"reps":8},{"weight":110,"reps":8},{"weight":110,"reps":8}]}],"reason":"legs fresh for Saturday long run"}
{"date":"2026-11-12","type":"plan","id":"plan-2026-11-15-run","for":"2026-11-15","sport":"run","focus":"long run","goal":"marathon Nov 2027","target":{"distance_km":16,"pace":"7:00-7:20/km","hr_max":150},"reason":"build phase, +1 km on last long run"}
```

**`outcome`**: what actually happened to a plan, judged from the logs and Strava.
`status` is `as_planned`, `modified`, `substituted`, `skipped` (the user said so) or
`expired` (not done within 5 days of its day). `diffs` lists each difference from the
plan. `feedback` is the user's own words, if any.
```json
{"date":"2026-11-14","type":"outcome","plan_id":"plan-2026-11-13-strength","status":"modified","diffs":["Chest press set 3: 110x6 instead of 110x8"],"feedback":"last set felt heavy","source":"logs"}
```

**`injury`**: pain or a form problem that changes what can be trained. `status` is
`open` or `resolved`. Append a new record with the same `id` to update it.
```json
{"date":"2026-11-10","type":"injury","id":"inj-left-knee-2026-11","area":"left knee","movement":"barbell squat","cause":"knees caving in on squats","status":"open","restrictions":["no squat load increases","no jumping"]}
```

**`goal_progress`**: a snapshot of progress toward a goal, at least once a month.
```json
{"date":"2026-11-30","type":"goal_progress","goal":"marathon Nov 2027","metric":"longest run km","value":18.2,"source":"strava","milestone":"on track"}
```

**`meal`**: a logged meal, with estimated nutrition.
```json
{"date":"2026-11-12","type":"meal","time":"13:10","items":["chicken rice bowl"],"kcal":650,"protein_g":40,"carbs_g":75,"fat_g":18,"confidence":"medium"}
```

**`note`**: a lasting fact about the user's training life.
```json
{"date":"2026-11-12","type":"note","text":"Pool closed Mondays"}
```

## Reading

- At the start of a session, read the last 30 days of `checkin`, `plan`, `outcome`,
  `meal` and `note` records.
- Read all `injury` records regardless of age. Report any whose latest record is `open`.
- When assessing a goal, read all `goal_progress` records for that goal.
- A `plan` with no `outcome` is **pending**.

## Writing

- Only the user's own answers and fitstack's own plans, outcomes and estimates go here.
  Never copy workouts from the logs or Strava in full.
- How plans, outcomes and injuries are used is defined in
  [training-rules](training-rules.md).
