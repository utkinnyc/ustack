#!/usr/bin/env python3
"""Set the version of every plugin a PR changes to main's version, bumped once.

The bump comes from the PR (labels win over the title):
  label "major" / "minor" / "patch"
  title "feat!: ..." or "fix!: ..." (any type with "!")  -> major
  title "feat: ..." or "feat(scope): ..."                -> minor
  anything else                                          -> patch

The target is always computed from main, so running it again changes nothing, and
retitling a PR (e.g. fix: -> feat:) moves the bump to match.
Prints a one-line summary for the commit message and the status check.
"""
import json
import os
import re
import subprocess
import sys


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def bump_kind(title, labels):
    for kind in ("major", "minor", "patch"):
        if kind in labels:
            return kind
    if re.match(r"^\w+(\([^)]*\))?!:", title):
        return "major"
    if re.match(r"^feat(\([^)]*\))?:", title):
        return "minor"
    return "patch"


def bump(version, kind):
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if not m:
        sys.exit(f"version {version!r} on main is not MAJOR.MINOR.PATCH")
    major, minor, patch = map(int, m.groups())
    return {
        "major": f"{major + 1}.0.0",
        "minor": f"{major}.{minor + 1}.0",
        "patch": f"{major}.{minor}.{patch + 1}",
    }[kind]


def main():
    kind = bump_kind(os.environ.get("PR_TITLE", ""), json.loads(os.environ.get("PR_LABELS") or "[]"))
    changed = git("diff", "--name-only", "origin/main...HEAD").split()
    plugins = sorted({p.split("/")[1] for p in changed if p.startswith("plugins/") and p.count("/") >= 2})
    report = []
    for name in plugins:
        path = f"plugins/{name}/.claude-plugin/plugin.json"
        if not os.path.exists(path):
            continue  # plugin removed in this PR
        try:
            main_version = json.loads(git("show", f"origin/main:{path}"))["version"]
        except subprocess.CalledProcessError:
            report.append(f"{name}: new plugin, version kept")
            continue
        with open(path) as f:
            data = json.load(f)
        target = bump(main_version, kind)
        if data.get("version") != target:
            data["version"] = target
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
                f.write("\n")
        report.append(f"{name} {main_version} -> {target} ({kind})")
    print("; ".join(report) or "no plugin changes")


if __name__ == "__main__":
    main()
