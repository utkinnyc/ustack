---
name: app-login
description: Design or add real login to an app that currently uses hand-made tokens — Sign in with Apple across iPhone, Watch, TV and web, Google sign-in, verifying identity tokens on the server, mapping provider IDs to one user, linking accounts so Apple and Google logins reach the same person, sessions per device, logging in from a CLI, Apple's localhost restriction for local development, keeping all auth code in one module, and the App Store rules that come with accounts. Use this whenever the user asks about login, sign-in, "log in with Apple/Google/Gmail", OAuth, replacing device or API tokens with accounts, "how do we know it's the same person", account linking, bearer tokens, `cli login`, or account deletion — even when they only ask whether it's feasible.
---

# App login

Add login as a nicer way to **get a session**, not a rewrite. If the backend already separates *users* from *devices/sessions*, login only replaces the step that issues the device token; everything after it stays.

## First, read what exists

Find how auth works now (token table, hashing, how requests are checked) and cite `path:line`. If the user says "don't make changes, tell me if it's feasible", answer feasibility only.

## The decision that matters more than the provider

Ask which goal it is before designing:

- **Just me, more convenient:** Sign in with Apple replaces pasting tokens (a big win on Watch and TV). Small change. Google is probably unnecessary.
- **Other people too:** the bigger work is multi-user, not login: every query and every agent run scoped to a user, per-user limits and cost caps, in-app account deletion, a privacy policy.

Recommend starting with Apple only, issuing the same per-device sessions the app already uses, and adding Google plus linking when a second user needs it.

## How each provider works

| | Sign in with Apple | Google |
|---|---|---|
| Needs | Paid developer account; capability on the App ID | OAuth client IDs in Google Cloud (free) |
| iPhone / iPad / Mac | Native (`AuthenticationServices`) | Google Sign-In SDK |
| Watch | Native | No SDK: rely on the phone or on Apple |
| TV | Native | Device-code flow ("enter a code on your phone") |
| Web | A **Services ID**, the verified domain and a return URL | Standard OAuth redirect |

**App Store rule:** offering Google (or any third-party login) means also offering Sign in with Apple. Apps that create accounts must let people **delete the account in the app**.

## Server side

1. The app sends the provider's **identity token** (a signed JWT). The server never trusts claims from the app itself.
2. Verify the signature against the provider's published keys (JWKS), and check `iss`, `aud` (your client IDs), `exp`, and the nonce.
3. Take **`sub`**: the provider's permanent, unique user ID. Look up `(provider, sub)` in an `identities` table → `user_id`. Create the user on first sign-in.
4. Issue your own session per device (hashed, revocable), exactly like the old device tokens. Refresh or expire as before.

5. **Library:** for Apple only, `jsonwebtoken` plus Apple's JWKS is the least code. `openidconnect` gets Google almost for free later, but needs more fiddling (Apple has sent `email_verified` as the string `"true"`).
6. **`aud` per app:** the Watch's token may carry the Watch bundle ID (`….watchkitapp`), and the web's carries the Services ID. Accept every client ID you ship.

**Owner-only gate (single user):** the server accepts only the Apple ID whose email matches an owner email in the server config. After that first sign-in, it remembers the `sub`. Tell the user to choose **Share My Email** on that first sign-in, or the email won't match and they'll get a 403.

## Keep it in one place

Put all login code in one module or crate: provider token checks, the `identities` table and its repo, issuing tokens, and config. The rest of the backend only sees `AuthDevice { device_id, user_id }`, and route handlers stay thin wrappers. On the clients, build one shared sign-in button in the shared package, so each app adds about one line, and one `<RequireSignIn>` wrapper on the web. A feature that touches every client otherwise turns into an 80-file PR (see `devstack:orchestrate` on PR size).

## CLI and local development

- **Sign in with Apple replaces pasting tokens, not tokens themselves.** Every request still sends `Authorization: Bearer <token>`: whoever holds the token gets in, so it lives in the Keychain and must be revocable.
- **CLI:** `cli login` opens the browser, the user signs in on a web page ("Allow the CLI?"), and the token is posted back to a listener on `127.0.0.1`, the way `gh auth login` works. That page must only ever send tokens to `127.0.0.1`. `logout` clears the token locally; revoke it on the server too. An admin command run over SSH is the simplest fallback.
- **Apple refuses `localhost` return URLs.** It only redirects to HTTPS domains you've proven you own, so nothing else on someone's machine can catch the token. Google allows localhost. Two workarounds:
  - Register a `dev.<domain>` return URL, point it at `127.0.0.1` in `/etc/hosts`, and serve it with a `mkcert` certificate.
  - Run a tunnel (e.g. Cloudflare Tunnel).

  The iOS Simulator signs in fine against a local server.
- **Portal steps the user does:** enable Sign in with Apple on each App ID, including the Watch's, and create a web Services ID with the domain and return URL. List these in the PR description.

## Same person across Apple and Google

**Don't match on email.** With Hide My Email, Apple gives a relay address (`…@privaterelay.appleid.com`), and Apple only sends the email on the first sign-in.

Use **explicit linking**: while signed in, the user taps "Link Google account" in Settings, completes Google sign-in, and the server attaches that `(google, sub)` to the current user. Optionally auto-link when both providers report the same *verified, non-relay* email. Without linking, a second login silently creates a second, empty account: the classic bug. Also handle unlinking, and refuse to unlink the last identity.

## Rollout

If the user is the only user and says to remove the old way, remove it in the same change. Otherwise keep the old token path working (dev and CLI) until every client has moved: add the new path first, then remove the old one in a last, tiny PR. Ship Apple first, then the web Services ID, then Google with linking. Add account deletion before anyone else gets access.
