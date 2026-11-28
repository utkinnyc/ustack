---
name: verify
description: Give agents a way to prove their changes work in the real app — a control CLI (reusing the app's own CLI) plus a Feature Map — for backends, CLIs, web, iOS, watchOS, tvOS and Android. Modes - create (set it up), maintain (catch up with new features), use (verify a change and show evidence). Use when the user says "verify", "prove it works", "test it in the app", "set up verification", "control the app", or a change can't be checked by unit tests alone.
---

# Verify

An agent that can drive the app can check its own work. Set that up once per app, keep it current, and use it as the "done when" check in `devstack:build` and `devstack:review`.

```
create   ──▶ control CLI (JSON out)  +  docs/features/ (Feature Map)  +  .claude/skills/verify-<app>/SKILL.md
maintain ──▶ update all three for what changed since the last run
use      ──▶ run the check, show the output, screenshot or recording as evidence
```

Pick the mode from the request. If the repo has no `.claude/skills/verify-*` yet, it's `create`.

## create

1. **Detect the app.** Read the manifests and entry points, cite `path:line`. One repo can have several surfaces:

   | Found | Surface |
   |---|---|
   | server entry, routes, `Dockerfile` | backend |
   | `bin` in `package.json`, `[[bin]]` in `Cargo.toml`, `[project.scripts]`, `cmd/` | CLI |
   | `next`, `vite`, `react`, `index.html` | web |
   | `*.xcodeproj`, `project.yml`, `Package.swift` with app targets | iOS / iPadOS / watchOS / tvOS / macOS |
   | `build.gradle(.kts)`, `AndroidManifest.xml` | Android |

2. **Find the app's CLI.** Reuse it; never build a second one beside it.
   - **Found:** add only what's missing (below), as subcommands or flags in the CLI's own language and style.
   - **Not found:** stop and tell the user. Offer two options: they add one, or you create a small one in the codebase's language. Wait for the answer.

3. **Agree the commands.** Propose this set, trimmed to the surfaces found, and wait for a yes:

   | Group | Commands |
   |---|---|
   | Health | `doctor` (is everything needed installed and running; what to do if not) |
   | Lifecycle | `up`, `down`, `reset` (seed a dev database, test user) |
   | Core actions | one per main thing a user does (`send`, `add`, `login`, …) |
   | Inspect | `state` or `snapshot` (what's on screen / in the DB, as JSON), `screenshot <file>`, `logs` |
   | Platform | `launch`, `open-url <deep link>`, `tap`, `type`, `record <file>`, `trace` (where the platform allows) |

   How to drive each platform, and its limits, is in `references/platforms.md`. The properties every command needs are in `references/cli-design.md`: JSON output, `--dry-run` on anything destructive, errors that say what to do, refusal to touch production.

4. **Build it** with `devstack:build`: one command per step, each checked by running it and showing its JSON.

5. **Write the Feature Map** (`references/feature-map.md`): `docs/features/README.md` lists every user-facing feature with a link to one file each (what it does, how a user reaches it, the control commands that drive it, gotchas). Build it from the routes, screens and CLI commands in the code, not from memory.

6. **Write the project skill** `.claude/skills/verify-<app>/SKILL.md`: when to use it, how to run `doctor` and `up`, the command list, and a pointer to `docs/features/README.md`. This is how every later session and subagent finds the tooling. Claude Code asks permission before writing under `.claude/`; if that's declined, save the file elsewhere and tell the user where.

7. **Prove the verifier.** Run `doctor`, then each command once, and show the outputs. Record today's commit in `docs/features/README.md` as `Last verified: <sha>`. Hand to `devstack:ship`.

## maintain

1. `git log <last verified sha>..HEAD --stat` to find new or changed routes, screens and commands.
2. Update the matching Feature Map files and add control commands for new features. Delete entries for removed features.
3. Run `doctor` and each command touched. Update `Last verified`.
4. Report what drifted and what you changed, in a short table.

## use

1. Read `.claude/skills/verify-<app>/SKILL.md` and the Feature Map entry for the feature at hand.
2. `doctor`, then `up` if needed.
3. Drive the change end to end through the control commands. For UI, take a screenshot (or a recording for a flow) before and after.
4. Show the evidence: commands, the relevant JSON, image paths. Label anything not checked.
5. If a control command is missing or broken, fix it as part of the change (it's shared infrastructure), or say so.

## Rules

- Dev and test environments only. Commands that would hit production refuse unless an explicit flag is passed, and you never pass it without the user's yes.
- Secrets come from env files or the keychain, never from the Feature Map or the skill.
- Keep it small: a command earns its place by being used to verify something.
