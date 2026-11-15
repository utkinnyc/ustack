---
name: next
description: Decide the user's next workout across strength, running, cycling and swimming, from their logs, Strava, goals, past plans and anything they said. Use when the user asks what's next, what to do today, wants a workout or a week plan, or says /next.
---

# Next

The entry point of fitstack. Sport skills propose sessions; you decide.

Read first: [agent-rules](../../reference/agent-rules.md), [config](../../reference/config.md),
[training-rules](../../reference/training-rules.md), [state](../../reference/state.md),
[skill-format](../../reference/skill-format.md).

## Flow

1. **Set up.** Find the fitstack folder. If any of `config.md`, `goals.md`,
   `milestones.md`, `state.jsonl` or `personal-rules.md` is missing from
   `AgentReferences/`, invoke `setup` first. Then read the config, goals, milestones and
   personal rules, and the state log as described in state.
2. **Gather.** Invoke `gather` with the default window. If the user asked about a
   specific sport or exercise, pass it as the focus.
3. **Fitcheck.** Invoke `fitcheck`. It asks the user nothing. If it reports a **RED
   FLAG**: no workout. Invoke `card` with the red flag, and stop.
4. **Decide what comes next**, in this order (training-rules section 3):
   0. **Today's training is already done** (fitcheck reports `done today`, or the gather
      output has a workout today that fully covers what today called for) → plan
      tomorrow's session instead, with `for` set to tomorrow, unless the user asked
      for a second session today. Tell `card` it is for tomorrow.
   1. **The user asked for something specific or different** → that. Build it in the
      context of their state, goals and recent training. Honor it unless it breaks
      training-rules section 1; if it breaks another rule, note which one in the plan's
      `reason` (the user sees it if they ask "why"). Any pending plan stays pending.
   2. **A plan is pending** (fitcheck lists it) → give it again as "pending since
      <the plan's `for` day>" (training-rules section 3). If fitcheck's pain or
      constraints affect it, adjust it.
   3. **Otherwise** → pick the day type from training-rules: the default week (section
      5), the goal's phase (section 2), personal rules, and fitcheck's constraints.
5. **Get the session.** Invoke the matching sport skill (`strength`, `run`, `ride` or
   `swim`) with the day type and constraints. If fitcheck found pain or an open injury,
   also invoke `rehab` and apply its `AVOID`, `ADD` and `SWAP`.
6. **Remember.** Append the `plan` record. For an adjusted pending plan, use the same
   `id`. Put the reasoning in its `reason` (the sport skill's `WHY`, fitcheck's
   assumptions, rehab's changes), so "why" can be answered later.
7. **Present with `card`.** Invoke `card` with the session (after rehab's swaps), the
   pending day if it is a pending plan, and any pain or injury restriction. Your reply
   is only card's output: no reasons, data notes, assumptions or summaries of the steps
   above. `card` also texts the user if they set that up.

## Week plan

When the user asks for a week: repeat steps 4.3–5 for each day, keeping the load rules
across days. Append one `plan` record per day, then invoke `card` with the week.
