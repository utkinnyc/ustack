---
name: go-live
description: Take a working app to production for the first time — backend on a VPS, web dashboard on the same host, mobile apps on TestFlight — and set it up so later releases ship by merging to main. Covers the repo-side deploy kit (idempotent setup script, env templates, a pull-based deploy script with checksum, health check and automatic rollback, hardened systemd units, Caddy serving API and SPA on one host, continuous database backups), the guided walkthrough split by who does what and where, secrets, per-device tokens, and the failures seen on first deploys. Use this whenever the user says "deploy everything", "put it in production", "go live", "ship it to my server", "give me steps to deploy the backend/web/apps", or asks how releases reach the server.
---

# Go live

Get a working app reachable from anywhere, with the least change to the app itself, and leave a setup where **merge to main = deploy**.

## Ground rules

- **Deploy first, fix later.** If the user says "don't change code logic, I want to deploy it first", only touch deploy files, config and build settings. Log app bugs you notice for afterwards.
- **You don't touch the server.** Same rule and step format as `devstack:selfhost`: you prepare the kit in a PR and write the steps grouped by where they run; the user runs server commands and pastes output. Commands on the Mac, `gh`, and checks from outside (`curl https://<host>/health`) are fine.
- **Secrets never go in chat or git.** The user pastes them straight into env files on the server. Say "don't paste the values here" every time you ask for one.
- **Explain when asked.** Break commands down piece by piece (what `rsync -a --delete src/ host:dst/` does, why the trailing slash matters, what `sudo -u` does). Answer "what are all these?" with a short table of each file and its job.
- **One step at a time.** When they say "let's talk one by one", give the next step only, with what to paste back.

## The shape

| What | How it reaches production | How often |
|---|---|---|
| Backend binary | CI builds and tests on merge to main, publishes a GitHub Release with a `.sha256`; **the server pulls it** on a timer | Every merge |
| Deploy kit (`deploy/`: setup script, unit files, Caddy file, env templates) | Copied once from the Mac with `rsync`, then `setup.sh` | Once, and when `deploy/` changes |
| Web dashboard | **In the same release as the backend:** CI typechecks, tests and builds it, then attaches `<app>-web.tar.gz` and its `.sha256`. The deploy script unpacks it into the same release folder, so a rollback restores both. Caddy serves `/srv/<app>/current/web`; make `/srv/<app>` mode `0751` so Caddy can pass through while the secrets stay unreadable. A manual `rsync dist/` is only a stopgap. | Every merge that touches web or contract |
| Apple apps | Archive and upload to TestFlight (see `devstack:apple-ship`) | When the apps change |

Explain why the kit is copied rather than pulled: the server can't reach a private repo until a token exists, and the token goes in a file that `setup.sh` creates. Cloning on the server also works, but leaves the token in git config.

The goal is one path: a merge to main deploys everything except the Apple apps. When asked "how is each part built and deployed?", answer for *this* project with a table (part → built by → deployed by → tested in CI). Offer a `docs/deploy-pipeline.html` page that shows each part as check → build → ship → runs on, coloured automatic, manual or missing, plus a dependency diagram (see `devstack:explain` for docs pages).

**Containers:** not needed for one binary on a small VPS (see `devstack:selfhost`, "Docker?"). The hardened systemd unit already isolates it, and containers would lose this kit's rollback and DB snapshot.

**GitHub Actions costs to mention:**
- macOS minutes cost about 10× Linux; see `devstack:apple-ship` for keeping Apple checks local.
- Pin third-party actions to commit SHAs.
- The server's release-download token can expire, and then deploys silently stop.
- You only learn a workflow is broken after you push.

## The deploy kit (repo side, one PR)

Read `references/deploy-kit.md` for the file list and the skeleton of each. The skeletons are in shell. If the user reads Python more easily (ask), write `setup` and `deploy` as typed, standard-library-only Python instead (`sudo python3 setup.py`; see `devstack:distinguished-engineer`). Drop one-time cleanups once they've run. Typed Python comes out ~30% longer than the bash, so say so. Inline tiny templates into the script. Test the deploy script on the Mac against a fake GitHub server, with a temp folder standing in for `/srv/<app>` and stubbed `systemctl`/`journalctl`. Test each path: first deploy, up to date, bad checksum, failed health check → rollback, rollback also failing.

**Logging that says where it broke:**
- Every deploy log line starts with its step (`[download]`, `[switch]`, `[health check]`, `[rollback]`). A failed command shows its exit code and the last lines of its output, and the health check says what it last saw (`HTTP 500`, `service not running`).
- Errors during an install also go to the history file with the release tag and step. A GitHub outage goes only to the journal, so it doesn't add a line every 5 minutes.
- Setup tees everything to `/var/log/<app>-setup.log` and ends a failure with `ERROR in step '<step>': <command> exited with <code>`.
- Put a "where to look" table (history file, journal, setup log) in the deploy README.

In short:

- **`setup.sh`**, safe to re-run: OS updates and unattended security upgrades; SSH keys only with no root login; ufw (SSH, 80, 443); fail2ban; swap on small boxes; Caddy; an unprivileged app user and `/srv/<app>/`; backup tool (e.g. Litestream for SQLite); any CLI the app runs; env files written from templates **keeping existing values**; systemd units; Caddy site imported from the main Caddyfile, validated, then reloaded. Print `==> step` lines and end with "Setup done" plus the next steps.
- **`<app>-deploy.sh`** (timer, every ~5 min, as root): lock; refuse politely (exit 0) while required secrets are empty and list which ones; fetch the latest release; verify sha256; restore the DB from backup if none exists, and **stop rather than start empty** if the restore fails; snapshot the DB; atomically repoint `current` (`ln -sfn` + `mv -T`); restart; poll `/health`; on failure roll back and remember the bad tag; keep the last N releases; append to a history log.
- **systemd unit**: non-root user, `EnvironmentFile=`, `ReadWritePaths=` only the data dir, `ProtectSystem=strict` and the other hardening flags, `ConditionPathExists=` on the binary so a fresh box isn't "failed", memory cap. Leave out flags that break JIT runtimes (`MemoryDenyWriteExecute`).
- **Caddy**: one host for both: `/v1/*` and `/health` go to `127.0.0.1:<port>`, everything else is the SPA (`try_files {path} /index.html`). Security headers, a small `request_body` limit when uploads go straight to object storage with signed URLs, and a rolling log file.
- **Env templates** with every key blank and a comment saying where each value comes from.
- **README** with the same steps the user will follow.

## The walkthrough (user side)

Group every step by place: **Browser**, **Mac**, **Server**. Typical order:

1. **Merge** the deploy PR. Check a release exists (`gh release list`); if not, run the release workflow manually.
2. **Accounts and tokens (browser):** object storage buckets (e.g. Cloudflare R2: one for uploads, one for DB backups, both private, a token scoped to just those buckets with object read/write); a GitHub **fine-grained** token scoped to the one repo, Contents read-only, with an expiry and a reminder; the LLM credential (an API key, or for the Claude CLI `claude setup-token`, which uses the user's subscription instead of per-use billing; explain the difference).
3. **Copy the kit (Mac):** `git switch main && git pull`, then `rsync -a --delete deploy/ <user>@<host>:<app>-deploy/`. No output means success.
4. **Server:** open **two SSH sessions** and leave one alone, since setup switches SSH to keys only. Run `sudo API_HOST=<host> bash ~/<app>-deploy/setup.sh`. Paste the last ~20 lines.
5. **Secrets (server):** `sudo nano` each env file. No spaces around `=`, no quotes; Ctrl-O, Enter, Ctrl-X.
6. **First deploy:** start the backup service and the deploy unit, then `sudo journalctl -u <app>-deploy -n 30 --no-pager`.
7. **Check from outside (you can do this):** `/health` returns ok; an authenticated route returns 401 without a token; any existing site on the same Caddy still returns 200.
8. **Device tokens (server):** run the app's own CLI as the app user against the live DB, once per device (iPhone, Watch, TV, Web). Explain them as an API key per device, printed once, stored hashed, revocable one by one. The user saves them in a password manager.
9. **Web (Mac):** build, rsync `dist/` to the served folder, open the site, paste the Web token, Test connection.
10. **Apps:** TestFlight via `devstack:apple-ship`; release builds must point at the public host, not the Mac.
11. **Then** confirm a fresh SSH login works before closing the spare session, and say what the real LLM brain now costs per log (it's live).

## Reading pasted output

- See also `devstack:selfhost`, "Common output that isn't a problem".
- `not deploying: fill in …`: the timer ran before the secrets were filled in. Harmless; the next run deploys.
- `no matching backups found` on a fresh server is correct.
- `_apt … Permission denied` during a `.deb` install, and "`~/.local/bin` not in PATH" after a CLI install for a service user, are harmless.
- **Caddy "Valid configuration" then "Job for caddy.service failed"** with `open /var/log/caddy/<app>.log: permission denied`: `caddy validate` ran as root and created the log file root-owned. Fix: `sudo chown caddy:caddy /var/log/caddy/<app>.log && sudo systemctl restart caddy`, then fix `setup.sh` to chown after validating. Warn first that every site on that Caddy is down until it restarts, and give the backup Caddyfile path as a quick way back.

After it's live, summarise: what runs where, how a change reaches production, where logs are, and how to roll back (`sudo <app>-deploy --force` for a specific retry, or repoint `current`).
