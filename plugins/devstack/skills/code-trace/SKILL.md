---
name: code-trace
description: Trace one real input (a CLI command, HTTP request, button tap or job) through the code step by step: which function runs, its file:line, the value at each step with a toy example, and where it touches the database, disk or network. Rendered as a numbered call trace, HTML when possible. Use when the user says "trace", "walk me through what happens when I run X", "follow this request", or is lost in a flow.
---

# Code trace

Make a flow concrete: pick one real input, follow it through the actual code, and show the value at every step. A trace with a toy value (`token = "abc123"`) teaches more than any abstract diagram.

## Pick the level the user needs

Users often climb these one at a time. Start where they are, and offer the next level in one line:

| Level | What it shows | When |
|---|---|---|
| 1. Flow | Boxes and decisions for the whole path, `file:line` under each | "draw a flowchart of this" |
| 2. Stages | Each stage in plain words: what it does and why | "I'm lost, what is stage 1 doing?" |
| 3. Toy example | One made-up value through real code, with table rows as they'd look | "use a toy example with our code" |
| 4. Call trace | Numbered calls from the entry point, indented by depth, value at each step | "draw and write the trace", "I must be passing through main.rs…" |

## Before drawing: read the code

1. **Find the entry point** for the input: the binary's `main` and its argument dispatch, the HTTP route table and middleware, the UI action handler, the job runner. Explain how the input reaches it if the user is unsure (e.g. "you type it by hand on the server; `device add` is a subcommand of the same binary, `main.rs:54`").
2. **Follow the calls** that matter, reading each function. Note `path:line` for each step. Skip logging, plain struct conversions and trivial getters; keep validation, branching, I/O and anything that changes state.
3. **Pick toy values** short enough to read (`abc123`, `u-111`, `d-222`), and say what the real ones look like (64 random characters). Compute real derived values where cheap (e.g. run `printf abc123 | shasum -a 256`), so the hash shown is real.
4. **Find the failure branches** (401, not found, validation error) and what triggers each.

## The call trace format (level 4)

- A header with the exact input: `$ ./app device add --name iPhone`, or `GET /v1/plan/today` with its headers.
- A one-line legend: indented = called by the step above; **value colour** = the value at that point; **I/O colour** = touches the database, disk or network.
- One numbered box per step: the **function** (`devices::add(…, "iPhone", Ios)`), its **location** (`devices.rs:74`) right-aligned, one plain sentence of what it does, and the **value** after it (`→ Platform::Ios`, `row: d-222 | u-111 | iPhone | 6ca13d52…`).
- Indent by call depth (2–4 levels; flatten deeper chains).
- End with the real output (what's printed, the HTTP response), filled with the toy values.
- Then, in chat, 3–5 bullets: the key idea (e.g. "it never talks to the running server; it opens the same SQLite file and exits"), and a C++/Python/TypeScript analogy if the user knows those languages ("the `match` is a `switch` on argv").

For levels 1 and 3, add a small table of "ways it fails" (input → why → result).

## Today vs proposed

When explaining a planned change, draw the new flow with **new code visually marked** (a coloured left border plus a legend "new code · everything else exists"), show which existing steps are reused (`reuse devices::add`), and add a short "later: expanding" strip if the design is meant to grow (more providers, more apps).

## Rendering

- **HTML when the client can show it:** an artifact page, the host's HTML preview tool, or a file in the scratchpad that the user opens. Start from `references/trace-template.html` (a self-contained page with light and dark colours); fill the steps, keep it narrow-screen friendly, and render or preview once to check before showing it.
- **Text fallback:** the same numbered, indented list in a code block, with `→ value` at the end of each line.
- Keep the chat text short. The trace carries the detail.

Don't change code while tracing. If the trace reveals a bug, say so and ask before fixing.
