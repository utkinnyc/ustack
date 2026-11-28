---
name: lean
description: Make a codebase small enough for one developer to read: measure where the lines are, then cut in reviewable PRs (unused code, extra crates or packages, hand-written plumbing the framework already provides, duplicate tests, wordy comments). Also runs file-by-file trimming sessions. Use when the user says the code is too big, "too many lines/tests/comments", "can we delete this", "make it lean", or wants to go through a folder file by file.
---

# Lean

Every line is a line someone has to read. For a solo developer or a small team, optimise for a codebase one person can hold in their head, not for team-scale process.

## 1. Measure, then describe (read-only)

- Count non-blank, non-comment lines from git-tracked files, excluding generated code. Show a table per module with code and tests counted separately. Recount after each PR and update the README's size table through a PR when asked.
- For "what is each part doing", run **one read-only subagent per module in parallel**, then give a short flowchart of how they connect and a table: module → lines → what it does → verdict (keep / shrink / delete / merge / replace with a library). Change nothing until the user says so. "Don't delete or restructure anything right now" means exactly that.
- Explain *why* it got big (e.g. built by parallel agents, one crate each with a frozen shared core, so it got fakes and swappable traits). That tells the user which cuts are safe.

## 2. What to cut

| Smell | Cut |
|---|---|
| A crate or package per area in a one-person project | Merge into a few crates with modules. Keep only the boundaries that matter (e.g. platform vs app, see `devstack:distinguished-engineer`) |
| A trait with exactly one real implementation | Use the concrete type. Keep traits only where tests need a fake (clock, LLM runner) |
| A hand-written fake of a real dependency that's cheap to run (an in-memory "database" next to SQLite) | Test against the real thing (`sqlite::memory:`) and delete the fake and its tests |
| Hand-written middleware or parsing the framework already ships (request logging, rate limits, typed headers, body limits, extractors) | Use the framework's and its ecosystem's standard piece (e.g. tower-http `TraceLayer`, `tower_governor`, axum `FromRequest` derive). Turn off default features you don't need |
| Request structs of plain `String`s validated by hand | Typed fields (`InputId`, enums, `Timestamp`), so the deserializer checks them |
| Two error types with conversions between them | One error type that renders itself |
| Methods nothing in production calls, unused config fields, unused enum values | Delete, along with their tests |
| Tooling that isn't used yet (eval harnesses, test kits) | Delete; keep any data files worth keeping |
| A file whose job has gone away | Delete the file, don't leave a stub |

Recommend, but let the user pick. When they say "using the framework's piece is always better, what's wrong with adding a dependency", take a well-used library over hand-written code.

## 3. Tests: each behaviour once

- **Test at the API** (real HTTP, real database). Drop lower-level copies of the same check: the same idempotency test at the repo, the API and e2e is three tests for one fact.
- **One happy-path test plus one table of bad inputs per endpoint or tool**, not one test per bad field.
- **Unit tests only for tricky logic** that's hard to reach through the API (timezone and day boundaries, ID ordering, signing against published test vectors, backoff, stream parsing), plus one end-to-end smoke test.
- The PR gets a **coverage table**: behaviour → the one test that covers it.
- While a part is being rebuilt and isn't known to work yet, the user may say to delete its tests outright ("we have no idea if the thing even works"). Do it, and note what's untested.
- Report bugs the cut uncovers (e.g. tests that only passed on the fake) instead of quietly fixing them.

## 4. Comments: only what isn't obvious, in one line

- Delete comments that restate the code or the name, section banners, file headers longer than ~3 lines, and docstrings on functions whose name says it all.
- Keep one short line for a non-obvious *why*: `# No MemoryDenyWriteExecute: the claude CLI's JIT would crash.`
- Apply this to every comment you write or touch in any PR, not only in cleanup PRs.

## 5. File-by-file sessions

When the user says "let's look at the X folder" or "we'll interactively edit and understand it, no commit until I say":

1. Go one file at a time. For each file: what it does in a few bullets, then which parts are needed, which can be deleted, and which the framework or standard library already does.
2. Answer syntax questions as they come up, in their languages (see `devstack:explain`).
3. Apply only what they pick ("only trim comments", "delete AuthError, move token here"). Edit the working tree, build and test, and don't commit until they say "create the PR".
4. **Be honest about lines.** Say whether code was removed or just moved into named helpers ("`run` went from 160 to 60 lines; the file only lost 23"). A split that improves readability is still worth doing, so say which kind of gain it is.
5. Leave callers (clients, other apps) alone unless asked. If there are no clients yet, say the API can change freely.

## 6. Shipping the cuts

- One PR per kind of cut (delete X, fewer tests, crates → modules, http cleanup), each building and passing tests on its own, made in a temporary worktree (see `devstack:orchestrate`).
- Run subagents **one after another** when they rewrite the same files. Parallel runs produce PRs that conflict line by line.
- In each PR description, give lines before and after, and what's knowingly untested.
