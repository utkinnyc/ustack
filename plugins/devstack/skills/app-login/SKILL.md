---
name: app-login
description: Design or add real login to an app that currently uses hand-made tokens — Sign in with Apple across iPhone, Watch, TV and web, Google sign-in, verifying identity tokens on the server, mapping provider IDs to one user, linking accounts so Apple and Google logins reach the same person, sessions per device, and the App Store rules that come with accounts. Use this whenever the user asks about login, sign-in, "log in with Apple/Google/Gmail", OAuth, replacing device or API tokens with accounts, "how do we know it's the same person", account linking, or account deletion — even when they only ask whether it's feasible.
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

## Same person across Apple and Google

**Don't match on email.** With Hide My Email, Apple gives a relay address (`…@privaterelay.appleid.com`), and Apple only sends the email on the first sign-in.

Use **explicit linking**: while signed in, the user taps "Link Google account" in Settings, completes Google sign-in, and the server attaches that `(google, sub)` to the current user. Optionally auto-link when both providers report the same *verified, non-relay* email. Without linking, a second login silently creates a second, empty account: the classic bug. Also handle unlinking, and refuse to unlink the last identity.

## Rollout

Keep the old token path working (dev and CLI) until every client has moved. Ship Apple first, then the web Services ID, then Google with linking. Add account deletion before anyone else gets access.
