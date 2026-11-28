#!/usr/bin/env python3
"""Check every plugin in the marketplace. Prints one line per problem; exits 1 if any.

- marketplace.json, plugin.json and hooks.json parse, and each plugin source exists
- each SKILL.md has frontmatter whose name matches its folder and a description <= 500 chars
- every `plugin:name` reference points to an existing skill or agent
- rules files a hook prints stay under the hook context cap
- shell scripts pass `bash -n` (and shellcheck, if installed); Python scripts compile
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAX_DESCRIPTION = 500
MAX_RULES = 9000  # hook output is capped at 10,000 characters; keep headroom
FRONTMATTER = re.compile(r"\A---\nname: (.+)\ndescription: (.+)\n(?:.*\n)*?---\n")
REFERENCE = re.compile(r"`([a-z]+stack):([a-z0-9-]+)`")

problems: list[str] = []


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def load_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError) as e:
        problems.append(f"{rel(p)}: invalid JSON ({e})")
        return {}


marketplace = load_json(ROOT / ".claude-plugin/marketplace.json")
plugins = [ROOT / p["source"] for p in marketplace.get("plugins", [])]
for p in plugins:
    if not (p / ".claude-plugin/plugin.json").exists():
        problems.append(f"{rel(p)}: listed in marketplace.json but has no .claude-plugin/plugin.json")

names: set[str] = set()
for p in plugins:
    load_json(p / ".claude-plugin/plugin.json")
    if (p / "hooks/hooks.json").exists():
        load_json(p / "hooks/hooks.json")
    names |= {f"{p.name}:{a.stem}" for a in (p / "agents").glob("*.md")}
    for skill in sorted((p / "skills").glob("*/SKILL.md")):
        names.add(f"{p.name}:{skill.parent.name}")
        m = FRONTMATTER.match(skill.read_text())
        if not m:
            problems.append(f"{rel(skill)}: frontmatter must start with name: and description:")
            continue
        if m.group(1) != skill.parent.name:
            problems.append(f"{rel(skill)}: name '{m.group(1)}' doesn't match folder '{skill.parent.name}'")
        if len(m.group(2)) > MAX_DESCRIPTION:
            problems.append(f"{rel(skill)}: description is {len(m.group(2))} chars (max {MAX_DESCRIPTION})")

for p in plugins:
    for doc in sorted(p.rglob("*.md")):
        if "evals" in doc.parts:
            continue
        for plugin, name in REFERENCE.findall(doc.read_text()):
            ref = f"{plugin}:{name}"
            if ref not in names:
                problems.append(f"{rel(doc)}: `{ref}` is not a skill or agent in this marketplace")
    for rules in p.glob("rules/*.md"):
        if len(rules.read_text()) > MAX_RULES:
            problems.append(f"{rel(rules)}: {len(rules.read_text())} chars (max {MAX_RULES})")
    for script in sorted(p.rglob("*.sh")):
        r = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
        if r.returncode:
            problems.append(f"{rel(script)}: bash -n failed: {r.stderr.strip()}")
        elif shutil.which("shellcheck"):
            r = subprocess.run(["shellcheck", "-S", "warning", str(script)], capture_output=True, text=True)
            if r.returncode:
                problems.append(f"{rel(script)}: shellcheck warnings (run shellcheck {rel(script)})")
    for script in sorted(p.rglob("*.py")):
        try:
            compile(script.read_text(), str(script), "exec")
        except SyntaxError as e:
            problems.append(f"{rel(script)}:{e.lineno}: does not compile: {e.msg}")

print("\n".join(problems) if problems else f"ok: {len(plugins)} plugins, {len(names)} skills and agents")
sys.exit(1 if problems else 0)
