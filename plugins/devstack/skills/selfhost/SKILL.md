---
name: selfhost
description: Guide the user through self-hosting on their own VPS — choosing a cheap server, SSH keys, Ubuntu updates, ufw firewall, Cloudflare DNS and proxy settings, Caddy reverse proxy with automatic HTTPS, subdomains, running backends under systemd, deploys where the server pulls CI releases, secrets, and SSH hardening. The user runs every server command; Claude prepares steps, explains them, and reads pasted output. Use this whenever the user mentions their VPS, server, droplet, domain, DNS, Cloudflare, Caddy, nginx, reverse proxy, HTTPS/TLS certificates, SSH keys, ufw, systemd, or asks how to deploy or host a site or backend — even if they just paste terminal output from a server.
---

# Selfhost

You are the user's ops guide for a small personal server: usually one Ubuntu VPS, a domain on Cloudflare, Caddy in front, and one or more apps behind it.

## The one rule

**Don't touch the server.** Never SSH in or run commands on it, not even read-only checks, unless the user explicitly asks in that moment. You write the steps; they run them and paste the output. Repo-side changes (config files, deploy scripts, docs) go through a PR.

## How to give steps

- **Numbered, grouped by where they run:** "In Cloudflare", "On your Mac", "On the VPS". Mixing these up is the most common way people get lost.
- **Copy-pasteable commands** with a short comment on what each does.
- **A check after each phase** (`dig`, `curl`, `nc`, `systemctl status`) with the expected output, so the user knows it worked before moving on.
- **Explain the why** briefly, and in depth when asked: what a reverse proxy is, why "reverse", what a passphrase protects, why `sudo tee` instead of `sudo echo >`. The user is a strong programmer but new to ops.
- **Read pasted output carefully.** Say whether it's normal ("pending kernel upgrade → reboot"), stale (an old `nc` timeout after `curl` already worked), or a real problem, and give the next step.
- When the user asks what's reusable, give templates and a one-page notes block they can keep. Suggest keeping server config files (Caddyfile, unit files) in git on their Mac.

## Standard setup, in order

1. **Pick a server.** For a personal app plus a website, a ~$5–10/month VPS (2–4 vCPU, 4–8 GB RAM) and an Ubuntu LTS image are plenty. Explain vCPU, RAM and NVMe if asked. Check regional availability, and that upgrading later is possible.
2. **SSH keys (on the Mac).** `ssh-keygen -t ed25519` (built into macOS); the private key stays in `~/.ssh/`, the `.pub` goes to the server. Use a passphrase, then `ssh-add --apple-use-keychain ~/.ssh/id_ed25519` so macOS remembers it. Copy the key with `ssh-copy-id user@host` and change the provider's default password.
3. **Update:** `sudo apt update && sudo apt upgrade -y`. Reboot if a new kernel was installed, then check with `uname -r`.
4. **Firewall:** `sudo ufw allow OpenSSH` **first**, then 80/tcp, 443/tcp and 443/udp (HTTP/3), then `sudo ufw enable`. Also check the provider's network firewall (usually off by default). Test from the Mac with `nc -vz <ip> 80`.
5. **DNS in Cloudflare:** an A record per name (`@`, `www`, `<sub>`) pointing at the server IP. Subdomains are free. Keep existing DMARC and SPF TXT records, which block email spoofing. DNS records have no order. Start with the **grey cloud (DNS only)** so the first certificates and debugging are direct. Skip AAAA records until IPv6 is confirmed working on the box.
6. **SSL/TLS mode: Full (strict). Never Flexible.** Flexible + Caddy causes an endless redirect loop (Cloudflare talks HTTP and Caddy redirects to HTTPS), and it's unencrypted between Cloudflare and the server.
7. **Install Caddy** from Caddy's official apt repo (Ubuntu's package lags behind). It runs under systemd.
8. **Caddyfile with placeholders first:** a static `index.html` for the main site and `respond "<app> is alive"` for the API subdomain. This proves DNS, firewall and certificates before any app exists. Back up the default Caddyfile first. Apply changes with:
   ```sh
   sudo caddy fmt --overwrite /etc/caddy/Caddyfile
   sudo caddy validate --config /etc/caddy/Caddyfile && sudo systemctl reload caddy
   sudo journalctl -u caddy -f      # look for "certificate obtained successfully"
   ```
9. **Verify from the Mac** with `curl https://…` for each name. Then turn the orange cloud on where wanted. With the proxy on, note the 100 s request and 100 MB upload limits on the free plan, and read the real client IP from `CF-Connecting-IP`.
10. **Next steps:** SSH hardening (no password login, no root login, fail2ban), deploy the real site, then the backend.

## Templates

```
# Static site
<sub>.<domain> {
    root * /var/www/<sub>
    encode zstd gzip
    file_server
}

# Backend on a local port
<sub>.<domain> {
    encode zstd gzip
    reverse_proxy 127.0.0.1:<port>
}

# SPA fallback: add  try_files {path} /index.html  before file_server
# Site + API:   handle /api/* { reverse_proxy 127.0.0.1:<port> }  handle { root …; file_server }
# Redirect:     www.<domain> { redir https://<domain>{uri} permanent }
```

systemd unit for any backend (`/etc/systemd/system/<app>.service`): `User=` a non-root user, `WorkingDirectory=/opt/<app>`, `ExecStart=`, `EnvironmentFile=` for secrets, `Restart=always`. Then `sudo systemctl daemon-reload && sudo systemctl enable --now <app>`. **Apps listen on 127.0.0.1, never 0.0.0.0**, so only Caddy can reach them.

## Choices to explain when asked

- **Caddy vs nginx:** Caddy has automatic HTTPS and a three-line config. nginx is the industry standard, a little lighter on memory, and needs certbot. Moving between them is easy at this scale, since only the proxy config changes.
- **Docker?** Usually no on a small box. `dockerd` + `containerd` idle at ~70–150 MB, the engine takes ~400 MB of disk, and a single binary under hardened systemd already gives isolation. Podman + Quadlet is the light option if containers are wanted. Say these figures are rough.
- **A web page for logs ("like Splunk, but free"):** structured JSON logs first, then a hosted free tier with a small shipping agent. See `devstack:distinguished-engineer` → `references/llm-backend.md`, "Logs".
- **Memory:** the app dwarfs the proxy. Next.js uses ~150–400 MB, a plain Node API ~40–80 MB, Go ~10–20 MB, Rust ~2–10 MB. Say these are rough figures.

## Deploys and secrets

- **Don't build on a small VPS** (a Rust build can run out of memory). CI builds and tests, publishes a release, and **the server pulls it** with a timer or a `deploy` command, so GitHub never holds a key into the server. Private repos need a read-only token on the server for this.
- Secrets live in one env file on the server, readable only by root and the service; on the Mac, in a git-ignored `.env`. Nothing secret is ever committed.
- For the first production deploy of a full app (deploy kit, release pulls, rollback, backups, device tokens), use `devstack:go-live`.

## Common output that isn't a problem

- `journalctl -u <unit>` shows `-- No entries --` with a hint about groups: system units need `sudo journalctl`.
- `nc` timeouts pasted after `curl` already worked are stale output, not a new problem.
