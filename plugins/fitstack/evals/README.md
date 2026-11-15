# fitstack evals

Cases for `claude plugin eval`. All data here is synthetic; no real person's data.

## Run

From `plugins/fitstack/`:

```bash
# one case, one run: quick and cheap
claude plugin eval . --scaffold --ablation none --runs 1 --case user-new-workout --no-publish

# a group, by tag (gather, user, next, pending, injury, goals, messy, clean, ...)
claude plugin eval . --scaffold --ablation none --tag gather --no-publish

# everything: 13 cases x 3 runs
claude plugin eval . --scaffold --ablation none --no-publish
```

`--scaffold` is required: it runs each case's `setup.sh`, which builds the workspace.
`--ablation none` skips the run without fitstack, which tells little here. Results go to
`evals/results/` (git-ignored).

## Layout

```
_fixtures/
  load.sh        builds a workspace: copies a fixture, then the case's own changes
  clean/         tidy data, with planted traps for the data-gatherer
  messy/         a regular user, written the way real logs are written
<case>/
  case.yaml      the user's message + every check (graders)
  setup.sh       one line: which fixture to load
  state-append.jsonl   optional: extra state lines for this case (e.g. a pending plan)
  overlay/             optional: files that replace fixture files
```

### The two fixtures (today is Sat 2026-11-14 in both)

**clean**: four tidy log days, a month file and a stale daily file that must be
ignored, an AI Summary that must not be used, and a small Strava snapshot (two runs and
a ride in the window, one old run outside it).

**messy**: a lifter who plays pickleball 2-3 times a week and is building toward a half
marathon. Blank lines, `each side`, `45 each side x 6 so 90 x 6`, `35 seconds`, typos
(`Latt pull down`, `each sidr`), form, food and timing notes, a month file inside the
daily folder, an AI Summary, Strava with default titles, descriptions and weather, a
logged day with no Strava (Nov 4), a Strava session with no log (Oct 29), and a state
history of plans and outcomes. `--new-user` removes `AgentReferences/` for a first run.

## Cases

| Case | Fixture | The user says | Checks |
|---|---|---|---|
| `gather-nov12-sets` | clean | What did I do at the gym on Nov 12? | every set, odd formats expanded, the note kept |
| `gather-ignores-decoys` | clean | Show me all my workouts from the last 30 days. | traps never used; October from the monthly file |
| `gather-strava-snapshot` | clean | Pull up my training ... including my Strava activities. | snapshot, fixed today, 30-day window, merge |
| `gather-messy-logs` | messy | Show me all my workouts from the last 30 days. | messy lines handled, notes kept, gaps reported |
| `user-first-time` | messy, new user | I'm new ... What should I do today? | setup from the prompt's answers, then a workout |
| `user-pending-not-done` | messy + Nov 13 run plan | What should I do today? | "pending since Nov 13", the same run |
| `user-pending-expired` | messy + Nov 8 swim plan | What should I do today? | expired, fresh plan |
| `user-new-workout` | messy | What should I do today? | fitcheck first; no heavy legs after pickleball; last numbers |
| `user-asks-back-day` | messy + pending legs | Feeling like doing back day today. | the request wins; the leg plan stays pending |
| `user-lower-back-pain` | messy | My lower back is a bit sore ... | no spinal loading; support work; injury recorded |
| `user-updates-goals` | messy | Add a 10K under 55 min by March 2027. | old goals kept; priorities; milestones proposed |
| `user-wants-run` | messy | I want to run today. | a run sized from real runs |
| `user-no-legs` | messy | ... no leg exercises. | an upper-body session from history |
| `user-plan-done-today` | messy + today's back plan + today's log of it | What should I do today? | judged done; "Done today ✓"; the card is for tomorrow |
| `user-plan-done-other-exercises` | messy + back plan + pull-ups, cable row | What should I do today? | same muscles → modified, counts as done |
| `user-plan-substituted` | messy + back plan + a chest log | What should I do today? | substituted; the back day is tomorrow's card |

Every fixture has `dry_run: true`, so checks read the `WOULD WRITE` section of the reply
instead of files.

**Every workout case** (all `user-*` except `user-updates-goals`) also checks the reply
is only a card: `card-used` (the card skill ran), `no-fluff-markers` (no "why this
session", "data notes" or "(last"), and `reply-is-card` (an AI judge). The reasoning is
not on the card, so checks about it read the plan's `reason` in `WOULD WRITE`.

## Adding a case

Copy a case folder, then change `name`, `prompt` and `graders` in `case.yaml`. For a
different situation, add a `state-append.jsonl` or an `overlay/` rather than changing a
fixture, because fixture changes can break other cases' checks.
