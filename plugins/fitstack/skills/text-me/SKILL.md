---
name: text-me
description: Send the user a short text of today's workout (or any fitstack result) over iMessage via Inkbox. Use when the user asks to text, message or send them the plan.
---

# Text me

Rules: [agent-rules](../../reference/agent-rules.md), [config](../../reference/config.md).

1. Read `imessage_to` from the config. If it is `none` or missing, ask for the number
   and save it to the config. Only ever send to that number.
2. Format briefly: a title line with an emoji, then numbered items. Today only: no
   last-session numbers, no explanations.

```
Back Day 💪

1. Lat Pulldown: 135×8, 135×8, 135×7, then 130 for max reps
2. Low Row: 120×10, then 140×8 ×3
3. Rear Delt Fly: 70×10, 80×8, 85×6
4. Dead Hang: 30 sec ×3
```

3. Send with the Inkbox `inkbox_imessage_send` tool, reusing the existing conversation
   with that number if one is listed.
4. If the send fails with `imessage_awaiting_inbound`, ask the user to text `START` to
   the agent's line. Report a `pending` status as sent but unconfirmed.
