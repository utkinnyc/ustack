---
name: rehab
description: Adjust training around pain, a minor injury or a form problem — what to avoid, what to strengthen instead, and gentle mobility for the area. Use when the user reports pain, soreness, a tweak, an injury or bad form, or when fitcheck reports pain or an open injury.
---

# Rehab

Follow [training-rules](../../reference/training-rules.md) section 1 strictly; it
overrides everything here. Also: [agent-rules](../../reference/agent-rules.md),
[state](../../reference/state.md).

1. If the fitcheck result is not in this conversation, invoke `fitcheck` first.
2. **Red flag:** no exercise. Say why and recommend a doctor or physiotherapist. Stop.
3. **Moderate (4–6/10):** rest that area. Suggest easy movement for the rest of the
   body only. Suggest getting it checked if it persists.
4. **Mild (≤ 3/10), or an open injury or form problem:**
   - List what to avoid today: exercises and sports that load the area.
   - Hold or reduce the load on the affected movement; never progress it.
   - Add work for the supporting muscles (e.g. knee → glutes, hips, core; shoulder →
     upper back, rotator cuff), and one form cue for the movement.
   - Give 3–4 gentle, pain-free mobility or activation exercises for the area, with
     sets, reps or holds.
   - Tell the caller which planned exercises to swap, and what to swap them for.
5. Say plainly: this helps recovery and works around pain but does not cure it. Pain
   lasting more than 3 days → reduce volume and get it checked.
6. Look at the state log for the same area. If it keeps coming back, say so.

Return: `AVOID: ...`, `ADD: ...`, `SWAP: ...`, and the advice line.
