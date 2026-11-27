---
name: transcripts-to-skills
description: Mine the user's past Claude Code conversations (and T3Code threads) for repeated workflows, hard-won fixes, and preferences, then turn them into new skills or improvements to existing ones in their plugin marketplace, delivered as a PR. Tracks what has already been processed so each run only reads what's new. Use this whenever the user says "go through my transcripts", "make skills out of what I did", "process transcripts into skills", "do you see more transcripts now", "what skills could we make from my sessions", or asks to turn a conversation, session or workflow into a skill or plugin.
---

# Transcripts to skills

Turn what the user actually did, and corrected, into skills that make the next session better. The source is their own transcripts. The output is a reviewed PR to their skills repo, not files dropped into `~/.claude/skills`.

## 1. Find what's new

Use the bundled script (`scripts/transcripts.py`, run with `python3 -I`):

```sh
T=<this skill>/scripts/transcripts.py
python3 -I $T list --new          # sessions with human messages not yet processed
python3 -I $T t3                  # T3Code threads, if the user works there (read-only DB)
python3 -I $T users <id…> --since ledger   # only what the user typed, since the last run
```

- Transcripts live at `~/.claude/projects/<project>/<session>.jsonl`. Subagent sidechains are skipped.
- T3Code threads that run Claude are the same Claude Code sessions under `~/.claude/projects/`, so read them there; the T3 database only helps map titles to sessions.
- Forked or continued sessions repeat earlier messages. Deduplicate by text and timestamp.
- If this is the first run (no ledger), read everything, oldest first.

## 2. Spot skill candidates from the user's side

Read the user messages first; they're short and show intent. Look for:

- **Workflows repeated** across sessions or steps the user walked through by hand (deploying, shipping an app, a review routine).
- **Corrections**, the most valuable signal: "you should have described the trade-off", "don't be so verbose", "don't touch the server", "push it to my plugin, not there". These become rules inside the relevant skill, with the reason.
- **Questions the user had to ask** ("what does this command do?", "why are we copying this?"). The skill should answer them up front next time.
- **Failures and their fixes** (exact error text → cause → fix).

Skip one-offs (a single question about a gadget, a quick lookup). Mention them in the report so the user can overrule.

## 3. Get the details from the assistant side

For each candidate, dump just the relevant window:

```sh
python3 -I $T dump <id> --since 2026-11-26T21:00 --until 2026-11-26T23:00 > <scratchpad>/<topic>.md
```

Then read the real artifacts the session produced (scripts, config, PRs in the user's repos). They're the verified version; the chat may show intermediate attempts that failed.

## 4. New skill or an edit?

List the existing skills in the target plugin and read the ones that overlap. Prefer **extending** an existing skill when the topic fits its description. Create a new skill when the material has its own trigger phrases and would bloat another skill. Typical result of a run: one or two new skills and several small edits.

Write with the `skill-creator` guidance in mind:
- a "pushy" description listing the phrases that should trigger it;
- the why behind each rule, kept short;
- generic placeholders (`<app>`, `<host>`, `com.<prefix>.<app>`) instead of the user's specifics;
- long templates or scripts in `references/` or `scripts/`, tested (`bash -n`, a dry run) before committing;
- nothing you can't trace to a transcript or a verified artifact. Don't invent tips.

## 5. Privacy check (the skills repo may be public)

Before committing, grep the changed files for everything personal you saw in the transcripts: IP addresses, domains, Team IDs, emails, phone numbers, street addresses, hostnames, tokens, the user's name in paths. Replace each with a placeholder. Report that the scan came back clean.

## 6. Ship and record

1. On a branch in the marketplace repo: add or edit the skills, update the plugin README's command list and table, and the plugin and marketplace descriptions if the scope changed. **Check for a version-bump workflow** (e.g. `.github/workflows/version-bump.yml`) before touching `version`: if one exists, don't bump by hand; give the PR a conventional title instead (`feat(<plugin>): …` for new skills, so it's a minor bump). Bump by hand only when there's no automation.
2. Commit, push, and open a PR (or add to an open one on the same topic and comment on what changed).
3. Mark what was processed: `python3 -I $T mark --all` (or just the sessions read), so the next run starts from here.
4. Report briefly: a table of new and changed skills, what each came from, what you skipped and why, and the PR link.
