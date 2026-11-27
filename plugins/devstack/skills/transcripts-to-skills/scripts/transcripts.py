#!/usr/bin/env python3
"""Read Claude Code transcripts so they can be mined for skills.

Subcommands:
  list   [--since ISO] [--new]         sessions with dates, size, user-message count, first message
  users  SESSION... [--since ISO]      only what the human typed (no tool results, commands, agent reports)
  dump   SESSION [--since ISO] [--until ISO] [--max N]
                                       user + assistant text and one line per tool call, as Markdown
  mark   SESSION... | --all            record sessions as processed up to their last message
  t3     [--since ISO]                 T3Code threads (read-only), if ~/.t3/userdata/statev2.sqlite exists

SESSION is a session id or any unique prefix of one. The ledger lives at
~/.claude/transcript-skills-ledger.json and maps session id -> last processed timestamp,
so `list --new` and `users --since ledger` show only what is new since the last run.
"""
import argparse, glob, json, os, re, sqlite3, sys

HOME = os.path.expanduser("~")
PROJECTS = os.path.join(HOME, ".claude", "projects")
LEDGER = os.path.join(HOME, ".claude", "transcript-skills-ledger.json")
T3_DB = os.path.join(HOME, ".t3", "userdata", "statev2.sqlite")

NOISE = (  # human-looking messages that are really harness or agent output
    "This session is being continued", "Background task completed", "Background command",
    "[Request interrupted", "Caveat:",
)
AGENT_REPORT = re.compile(r"^(I've |I built|I picked up|## Workstream|All \d+ |`[^`]+` is built|The `)")


def sessions():
    out = []
    for f in glob.glob(os.path.join(PROJECTS, "*", "*.jsonl")):
        out.append((os.path.basename(f)[:-6], os.path.basename(os.path.dirname(f)), f))
    return out


def find(prefix):
    hits = [s for s in sessions() if s[0].startswith(prefix)]
    if len(hits) != 1:
        sys.exit(f"session prefix {prefix!r} matched {len(hits)} sessions")
    return hits[0]


def records(path):
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def text_of(content):
    if isinstance(content, str):
        return content
    return "\n".join(x.get("text", "") for x in content if isinstance(x, dict) and x.get("type") == "text")


def human_messages(path, since=""):
    for m in records(path):
        if m.get("type") != "user" or m.get("isMeta") or m.get("isSidechain"):
            continue
        ts = m.get("timestamp", "")
        if ts <= since:
            continue
        t = text_of(m.get("message", {}).get("content", "")).strip()
        if not t or t.startswith("<") or any(n in t[:200] for n in NOISE) or AGENT_REPORT.match(t):
            continue
        yield ts, t


def load_ledger():
    try:
        return json.load(open(LEDGER))
    except (OSError, ValueError):
        return {}


def cmd_list(a):
    ledger = load_ledger()
    rows = []
    for sid, proj, f in sessions():
        msgs = list(human_messages(f, a.since or ""))
        if a.new:
            msgs = [m for m in msgs if m[0] > ledger.get(sid, "")]
        if not msgs:
            continue
        rows.append((msgs[0][0], sid, proj, os.path.getsize(f), msgs))
    for first, sid, proj, size, msgs in sorted(rows):
        proj = proj.replace(HOME.replace("/", "-"), "~")
        print(f"{sid[:8]}  {first[:10]}..{msgs[-1][0][:10]}  {size/1e6:6.1f}MB  {len(msgs):4d} msgs  {proj}")
        print(f"          > {msgs[0][1][:150].replace(chr(10), ' ')}")


def cmd_users(a):
    ledger = load_ledger()
    for p in a.session:
        sid, _, f = find(p)
        since = ledger.get(sid, "") if a.since == "ledger" else (a.since or "")
        print(f"== {sid[:8]}")
        for ts, t in human_messages(f, since):
            print(f"  {ts[:16]} | {t[:a.width].replace(chr(10), ' / ')}")


def cmd_dump(a):
    sid, _, f = find(a.session)
    n = 0
    for m in records(f):
        ts = m.get("timestamp", "")
        if m.get("type") not in ("user", "assistant") or m.get("isMeta"):
            continue
        if (a.since and ts < a.since) or (a.until and ts > a.until):
            continue
        c = m.get("message", {}).get("content", "")
        for it in ([{"type": "text", "text": c}] if isinstance(c, str) else c):
            if not isinstance(it, dict):
                continue
            if it.get("type") == "text" and it["text"].strip() and not it["text"].lstrip().startswith("<"):
                print(f"\n### {m['type']} {ts[:16]}\n{it['text'][:a.max]}")
            elif it.get("type") == "tool_use":
                i = it.get("input", {})
                s = i.get("command") or i.get("file_path") or i.get("description") or ""
                print(f"  [{it.get('name')}] {str(s)[:200]}")


def cmd_mark(a):
    ledger = load_ledger()
    targets = sessions() if a.all else [find(p) for p in a.session]
    for sid, _, f in targets:
        last = max((m.get("timestamp", "") for m in records(f)), default="")
        ledger[sid] = last
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    json.dump(ledger, open(LEDGER, "w"), indent=1, sort_keys=True)
    print(f"marked {len(targets)} session(s) in {LEDGER}")


def cmd_t3(a):
    if not os.path.exists(T3_DB):
        sys.exit("no T3Code database found")
    db = sqlite3.connect(f"file:{T3_DB}?mode=ro", uri=True)
    q = """select t.thread_id, t.title, min(m.created_at), max(m.created_at), count(*)
           from orchestration_v2_projection_threads t join orchestration_v2_projection_messages m
           on m.thread_id = t.thread_id and m.role = 'user'
           where m.created_at > ? group by t.thread_id order by 3"""
    for tid, title, first, last, n in db.execute(q, (a.since or "",)):
        print(f"{tid[:20]:20}  {first[:10]}..{last[:10]}  {n:4d} msgs  {title[:70]}")
    print("\nT3Code threads that run Claude are also Claude Code sessions; read those with `users`/`dump`.")


p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sub = p.add_subparsers(dest="cmd", required=True)
s = sub.add_parser("list"); s.add_argument("--since"); s.add_argument("--new", action="store_true"); s.set_defaults(f=cmd_list)
s = sub.add_parser("users"); s.add_argument("session", nargs="+"); s.add_argument("--since", help="ISO time or 'ledger'"); s.add_argument("--width", type=int, default=300); s.set_defaults(f=cmd_users)
s = sub.add_parser("dump"); s.add_argument("session"); s.add_argument("--since"); s.add_argument("--until"); s.add_argument("--max", type=int, default=2500); s.set_defaults(f=cmd_dump)
s = sub.add_parser("mark"); s.add_argument("session", nargs="*"); s.add_argument("--all", action="store_true"); s.set_defaults(f=cmd_mark)
s = sub.add_parser("t3"); s.add_argument("--since"); s.set_defaults(f=cmd_t3)
a = p.parse_args()
a.f(a)
