"""SubagentStart hook: give every subagent the devstack rules.

Subagents start with a fresh context, so the SessionStart rules don't reach them.
SubagentStart context must be JSON (hookSpecificOutput.additionalContext).
"""
import json
from pathlib import Path

RULES = Path(__file__).resolve().parent.parent / "rules" / "RULES.md"

PREFIX = (
    "You are a subagent. Where a rule says to ask the user or stop for approval, "
    "stop and report back to the agent that spawned you instead.\n\n"
)

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SubagentStart",
        "additionalContext": PREFIX + RULES.read_text(),
    }
}))
