---
name: challenge
description: Read-only adversarial review of a plan, design or diff — restate what it's meant to do, then try to break it (wrong assumptions, missing cases, failure modes, security, scope beyond the request), keeping only findings proven by running something or pointing at specific lines. Reports; changes nothing. Use when the user says "challenge this", "poke holes", "what could go wrong", "devil's advocate", "is this plan sound", "try to break it", or wants a second opinion before building or merging.
---

# Challenge

Try to break the plan or change before reality does. You report; you don't fix. The user decides what to act on.

## 1. Frame

- **What to challenge:** what the user named; else `docs/plan.md` if the work hasn't started; else the branch diff (`git diff <base>...HEAD` plus the working tree).
- **Restate its intent** in one or two lines: what it's meant to achieve, and for whom. If you can't tell, ask before going further. A finding only counts if it breaks *that* intent.

## 2. Attack

Go through these angles; skip what doesn't apply:

| Angle | Ask |
|---|---|
| Premises | What does this assume is true? Which assumption, if wrong, sinks it? |
| Inputs | Empty, huge, duplicated, malformed, concurrent, retried, out of order? |
| Failure | What happens when the network, disk, database or a dependency fails midway? Is anything lost or done twice? |
| Security | Untrusted input reaching a shell, query, file path or model; secrets in logs; missing auth checks |
| Scope | Anything built that the request didn't ask for? Anything asked for that's missing? |
| Simpler | Is there a much smaller way to meet the same goal? |
| Reversibility | What's hard to undo (data migrations, published APIs, IDs)? Is there a way back? |

For a big change, you may run several **read-only** subagents in parallel, one angle each, and merge their findings.

## 3. Prove each finding

A finding needs evidence, or it's dropped:
- for code: a command, test or input that shows the failure, with its output; or the exact `path:line` and the input that reaches it;
- for a plan: the specific step or assumption, and the concrete case that breaks it.

Rerun anything a subagent claims. Merge findings that share one root cause. Drop style nits and "could be cleaner" unless it hides a bug.

## 4. Report

```
CHALLENGE: <what was reviewed>
Intent: <one or two lines>

Findings (most serious first)
1. <what breaks> — evidence: <command/output or path:line + case> — impact: <what the user would see>
2. ...

Dropped: <n unproven ideas, one line each, so the user can overrule>
Verdict: sound | sound with fixes | rethink   — <one line why>
```

Change nothing. If the user wants fixes, hand to `devstack:build` (or `devstack:plan` if it's a rethink).
