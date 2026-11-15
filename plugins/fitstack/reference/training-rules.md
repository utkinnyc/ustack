# Training rules (shared by all fitstack skills)

Sport skills propose sessions; `next` decides. fitstack is a training partner, not a
clinician.

## 0. Which rule wins

When rules conflict, the higher one wins:

1. **Red flags** (section 1).
2. **Pain, injury and form** (section 1).
3. **Personal rules** from the user's `personal_rules` file (section 4).
4. **Defaults** in sections 5–8.

## 1. Pain, injury, form and red flags

**Red flags: no workout today; recommend a doctor or physiotherapist.** Apply this if the
user reports any of:

- Chest pain, pressure, fainting, unusual breathlessness, or palpitations.
- Numbness, tingling or weakness in a limb, or pain shooting down a leg or arm.
- Swelling, heat or redness at a joint, or a pop or giving way at the time of injury.
- Pain that is sharp, getting worse, waking them at night, or lasting more than ~2 weeks.
- Pain 7/10 or above, or pain that makes them limp.
- Fever or illness below the neck (chest cold, stomach bug).

**Moderate pain (4–6/10):** rest or very easy movement for that area only. Suggest getting
it checked if it persists.

**Mild pain (≤ 3/10), not a red flag:**
- Avoid loading the painful area; train the rest of the body.
- Gentle, pain-free range of motion is fine. Pain during an exercise means stop that
  exercise.
- Pain lasting more than 3 days → reduce volume and suggest getting it checked.

**Injury or poor form** (an open `injury` record, or the user mentions pain or bad form on
a movement):
- Never progress the affected movement or area. Hold its load, or reduce it.
- Build the muscles that support it instead. For example, a knee or squat-form problem →
  glutes, hips and core. A shoulder problem → upper back and rotator cuff. Good form
  comes from those getting stronger.
- Give one form cue for the movement when it returns.
- Resume progression only after 3 pain-free sessions at the held load, and then in
  smaller steps than usual. Mark the injury `resolved` once the user confirms it.

**Always:**
- Never assume pain has gone. An open injury keeps its restrictions until the user says
  it is better. Do not ask before every session; say what is being assumed (e.g.
  "Treating left knee as still sore") so the user can correct it.
- Never diagnose. Say "this could be" or "worth getting checked", not "you have X".
- Say plainly that exercise can help recovery and work around pain, but it does not
  cure it.

## 2. Goals drive every recommendation

- Every `plan` names the goal it serves. If a session serves no goal, say so and why
  (e.g. recovery).
- **Dated goals** (e.g. marathon by Nov 2027): work backwards from the date through
  phases: base, build, peak, taper (about 2–3 weeks before an endurance event). The
  milestones file holds one target per month. If it is missing or does not cover a goal,
  propose milestones and write them once the user agrees.
- **Several goals** (e.g. a 200 km ride and a marathon): the goal with the nearer date
  sets the priority. The other is maintained with 1–2 sessions a week. Running, cycling
  and leg strength share the same legs, so count them together (section 5).
- **Nutrition** supports the same goals: fuel around long endurance sessions, enough
  protein for strength goals. Nutrition numbers are always estimates.
- At the end of each month, or the first session after it, write one `goal_progress`
  record per goal.

## 3. Learning from outcomes

**Judge every outcome.** At the start of a session, for each pending plan whose day has
passed, look in the logs and Strava for a workout of that sport between the plan's day
and today that no other plan has claimed:
- Found → write an `outcome` record (`as_planned`, `modified` or `substituted`).
- Not found, and the plan's day was 5 days ago or less → still pending.
- Not found, and more than 5 days ago → write an `outcome` with status `expired`.

**Pending plans carry forward.**
- A pending plan is the next workout. Give it again, saying "pending since <day>",
  unless the user asks for something specific. `<day>` is always the plan's `for` day
  (the day it was meant to be done), never the `date` it was written. A plan written
  Nov 12 for Nov 13 is "pending since Nov 13".
- Re-check it against today's fitcheck first. If new pain or constraints affect it,
  adjust it (and append the adjusted plan with the same `id`).
- **The user's request wins.** If the user asks for something specific or different
  ("chest day", "something easy", "not running today"), give them that, built in the
  context of their state, goals and recent training. The pending plan stays pending
  for later; it is not cancelled.
- An expired plan is not given again. Plan fresh.

**Adjust from the outcome:**
- `as_planned`, and the user did not say it was too hard → progress as normal
  (section 6).
- `modified` downward (fewer reps, less weight, shorter, slower) → repeat the achieved
  level next time; do not progress.
- `modified` upward (more than planned, felt easy) → take the next step.
- `substituted` or `skipped` → find out why if the user says. Reschedule the session; do
  not stack it on top of the next one.

## 4. Personal rules (rules that evolve)

The defaults below fit most people. The user's `personal_rules` file holds what fitstack
has learned about this user. It overrides the defaults.

- Add a personal rule only from a pattern: the same result in at least 3 comparable
  sessions, not a single day.
- Examples: missed reps after 3 of the last 4 bench increases → bench steps are +2.5 lb.
  Long runs on Saturdays are always skipped → schedule them on Sundays.
- Tell the user when a rule is added, changed or removed.
- Personal rules can never relax section 1.
- Format, one block per rule:

```markdown
## Bench press steps
- rule: Increase bench press by +2.5 lb, not +5 lb.
- why: missed target reps in 3 of the last 4 sessions after a +5 lb step.
- evidence: outcomes plan-2026-10-02-strength, plan-2026-10-16-strength, plan-2026-11-06-strength
- since: 2026-11-14
```

## 5. Load across the week

Weeks start on the config's `week_starts` day.

- **Default week**, adjusted to the user's goals, current phase and personal rules: run
  3x (two easy, one long), ride 1x long (weekend), swim 1–2x, lift 2–3x, one mobility
  session. Drop sports that serve none of the user's goals.
- Legs are shared by running, cycling, leg day, and court sports (pickleball and tennis
  count as hard leg days).
- No hard leg session the day before or the day after a long run or long ride.
- No two hard run days back to back. About 80% of running is easy (conversational).
- Grow weekly run volume by at most 10% per week. Every 4th week, cut back ~25%.
- Several hard days in a row, a sharp drop in performance, or poor sleep → easy or rest.

## 6. Progression

- **Strength:** set each target one small step above the last session (+5 lb, or +1–2
  reps). If the last session hit every target rep, raise the weight.
- **Endurance:** progress one variable at a time: distance, or duration, or intensity.

## 7. Milestones

- Compare the current month against the milestones file and say on track, behind or
  ahead.
- Behind by one month: hold volume and repeat the month. Never double up to catch up.
- Behind by two or more months, or pain lasting more than 3 days: move the goal date
  back rather than forcing volume.

## 8. Warm-up and cool-down

- **Before every session:** 5–8 min dynamic warm-up (leg swings, walking lunges, high
  knees, A-skips; arm circles before swims or presses). No long static holds beforehand.
- **After every session:** 5 min static stretching, 30–45 s per position. Runs: calves,
  hamstrings, hip flexors, glutes. Swims: shoulders, lats. Rides: hip flexors, quads.
- **Once a week, on an easy day:** 20–30 min mobility or yoga.
- Calf raises and single-leg strength work prevent more running injuries than stretching.
