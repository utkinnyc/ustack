# Deploy kit skeleton

Placeholders: `<app>`, `<host>`, `<port>`, `<owner>/<repo>`. Adapt names; keep the behaviour.

```
deploy/
  README.md                 the walkthrough, same steps as the skill
  setup.sh                  one-time, re-runnable server setup
  <app>-deploy.sh           pull-based deploy, installed to /usr/local/sbin
  <app>.caddy               site block, imported from /etc/caddy/Caddyfile
  <app>.env.template        app settings and secrets (blank)
  deploy.env.template       GITHUB_REPO, GITHUB_TOKEN (blank)
  litestream.yml            DB replication to object storage (if SQLite)
  systemd/
    <app>.service
    <app>-deploy.service    Type=oneshot, ExecStart=/usr/local/sbin/<app>-deploy
    <app>-deploy.timer      OnBootSec=1min, OnUnitActiveSec=5min
    litestream-override.conf  EnvironmentFile= the app env, for bucket credentials
```

Server layout:

```
/srv/<app>/
  current -> releases/<tag>   symlink switched atomically
  releases/<tag>/<app>        last N kept
  data/<app>.db               only dir the service can write (plus home/)
  backups/                    pre-deploy DB snapshots
  <app>.env                   0640 root:<app>
  deploy.env                  0600 root
  deploy-history.log, bad-releases
```

## `setup.sh` outline

```bash
#!/usr/bin/env bash
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "run with sudo"; exit 1; }
: "${API_HOST:?set API_HOST=<host>}"
step() { printf '\n==> %s\n' "$*"; }

step "Updating Ubuntu";               apt-get update && apt-get -y upgrade && apt-get -y install curl jq unattended-upgrades fail2ban
step "SSH: keys only, no root login"; # drop-in under /etc/ssh/sshd_config.d/, sshd -t, reload
step "Firewall";                      ufw allow OpenSSH; ufw allow 80/tcp; ufw allow 443; ufw --force enable
step "Swap (small boxes)";            # only if none exists
step "Caddy";                         # official apt repo, if not installed
step "App user and /srv/<app>";       # useradd --system, install -d -o/-g/-m for each dir
step "Backup tool";                   # pinned version, checksum
step "Env files (existing values are kept)"  # copy template only if missing; add new keys, never overwrite
step "systemd units";                 # install, daemon-reload, enable (timer --now)
step "Caddy site";                    # sed __API_HOST__, import line once, caddy validate,
                                      # chown caddy:caddy the log file (validate creates it as root), reload || restart
echo "Setup done. Next: fill in /srv/<app>/<app>.env and deploy.env, then start <app>-deploy."
```

## `<app>-deploy.sh` outline

```bash
set -euo pipefail
exec 9>/run/<app>-deploy/lock; flock -n 9 || exit 0
env_get KEY FILE        # read a value without sourcing the file
missing=(); ...; ((${#missing[@]})) && { echo "not deploying: fill in ${missing[*]}"; exit 0; }
tag=$(api .../releases/latest | jq -r .tag_name)
[[ $tag == "$(readlink current)" ]] && exit 0; grep -qx "$tag" bad-releases && [[ $FORCE == 0 ]] && exit 0
download asset + asset.sha256 (Accept: application/octet-stream); sha256sum -c
restore_if_missing      # stop backup service, restore -if-replica-exists, die on error
snapshot DB             # sqlite3 .backup into backups/
switch_to "$tag"; systemctl restart <app>
health_ok || { switch_to "$prev"; systemctl restart <app>; echo "$tag" >> bad-releases; exit 1; }
prune releases beyond KEEP; history "DEPLOYED $tag"
```

Secrets go through environment variables, never argv (argv is visible in `ps`).

## Release workflow (CI)

On push to main, after the test workflow passes: build the Linux binary (`x86_64-unknown-linux-gnu`, or musl for static), write `<asset>.sha256`, `gh release create build-$(date -u +%Y%m%d-%H%M%S)-<shortsha> <asset> <asset>.sha256`. Allow a manual `workflow_dispatch` with a `force` input.
