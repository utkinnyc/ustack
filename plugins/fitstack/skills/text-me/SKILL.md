---
name: text-me
description: Send the user today's workout card over iMessage via Inkbox. Called by `card` when the user chose to get every workout by text; use directly when the user asks to text, message or send them the plan.
---

# Text me

Rules: [agent-rules](../../reference/agent-rules.md), [config](../../reference/config.md).

1. Read `imessage_to` from the config. If it is `none` or missing and the user asked
   for a text, ask once for the number and save it to the config. When `card` called
   you, never ask: send nothing. Only ever send to that number.
2. **The message is the card**, exactly as `card` showed it (see
   [card](../card/SKILL.md)). If the user asked for a text and there is no card in this
   conversation, invoke `card` for the latest `plan` in the state log first.

3. **Dry run** (agent-rules rule 5): do not send, and do not save a number to the
   config. Show the message and the number it would go to under `WOULD WRITE`, then
   stop.
4. Send with the Inkbox `inkbox_imessage_send` tool, reusing the existing conversation
   with that number if one is listed.
5. If the send fails with `imessage_awaiting_inbound`, return that to the caller (`card`
   tells the user, in one line, to text `START` to the agent's line). A `pending` status
   counts as sent.
