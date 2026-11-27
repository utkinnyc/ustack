---
name: debug
description: Find and fix the root cause of a bug, failing test, crash or wrong output — reproduce it, read the whole error, trace back to the first place the system does something wrong, write a failing test, then make one fix and prove it. After two failed fixes, stop and test the assumption behind them. Use when the user reports a bug, pastes an error or stack trace, says "this is broken", "why does X happen", "the test fails", "it worked yesterday", or /debug.
---

# Debug

No fix before the root cause. A fix for a cause you haven't found usually moves the bug, or hides it.

## 1. Reproduce

- **Read the whole error**, every line of the stack trace and the log around it, not just the last line.
- **Make it happen on demand** with one command (a test, a `curl`, a script). Show the command and the failing output. If it won't reproduce, gather more evidence (logs, inputs, versions) before guessing; say what you still need from the user.
- **What changed?** `git log --oneline -15`, `git diff`, dependency or config changes. If it worked before and the range is long, `git bisect` with the reproduction command.

## 2. Find where it first goes wrong

Trace the bad value backwards from where it surfaced to where it was produced. At each boundary (function, process, network call, database), check the value: is it already wrong coming in? The root cause is the **first** place the system does something it shouldn't. Read the code there and cite it as `path:line`.

Compare with something similar that works (another endpoint, the previous version, the docs' example) and list the differences.

## 3. One hypothesis at a time

State it plainly: "The token is read before the env file loads, so it's empty." Test it with the smallest experiment that could prove it wrong (a print, a breakpoint, a one-line change you'll revert). Change one thing at a time. Wrong → a new hypothesis, not a second change on top.

## 4. Fix

1. **Write a test that fails** because of the bug (or, where a test isn't practical, a command whose output shows it).
2. **Make one fix** at the root cause. Not a guard, retry, `try/catch` or default value where the symptom appeared, unless the root cause is outside your control; then say so and fix as close to it as you can.
3. **Run the test** and the project's other checks. Show the output.
4. If the same mistake exists elsewhere, list the places, and fix them only if the user wants.

## 5. When fixes keep failing

If two fixes based on the same assumption fail, **stop**. Write the assumption down ("the config is loaded once at startup") and test it directly before trying anything else. After three failed fixes, tell the user: what you tried, what each showed, and what you now think is wrong with the design. Don't try a fourth on your own.

## Report

```
BUG: <symptom, one line>
Cause: <root cause> at path:line  (verified | inferred)
Fix: <what changed>
Proof: <test or command> → passes
Also affected: <other places, or "none found">
```
