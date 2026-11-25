---
name: apple-ship
description: Get iPhone, Apple Watch, Apple TV and Mac apps from code onto real devices and toward the App Store — free vs paid Apple Developer account, enrolment, Team ID, signing certificates, Developer Mode, pairing the Watch and TV with Xcode, bundle ID naming, XcodeGen projects, simulator and live-preview dev loops, TestFlight via App Store Connect, and the publishing checklist. Use this whenever the user mentions Xcode signing, provisioning, "install on my phone/watch/TV", Developer Mode, Team ID, bundle IDs, TestFlight, App Store Connect, the $99 developer account, simulators, or publishing an Apple app — even if they only paste an Xcode error.
---

# Apple Ship

Help the user get their Apple-platform apps running on their own devices, then distributed. They're a capable developer but new to Apple's tooling, so explain each Apple-specific step and why it exists.

## Free vs paid account

Explain this up front, since it decides the path:

| | Free (Personal Team) | Paid ($99/year) |
|---|---|---|
| Install | Xcode, by cable or pairing, every time | Xcode, **or TestFlight** (one tap per device) |
| App lifetime | 7 days | TestFlight builds last 90 days |
| Apps per device | 3 | No limit |
| Push, Sign in with Apple, HealthKit | Limited or unavailable | Work |

Enrol at https://developer.apple.com/programs/enroll/ (or in the Apple Developer app on iPhone): choose Individual, use the same Apple ID as Xcode, with two-factor on. Approval takes hours, up to 48. **Apple Developer** (developer.apple.com) is for building and signing; **App Store Connect** (appstoreconnect.apple.com) is for TestFlight, listings and review.

## First install on real devices (Xcode route)

1. **Team ID:** developer.apple.com/account → Membership details. Put it in the project definition (e.g. `DEVELOPMENT_TEAM` in XcodeGen's `project.yml`) so it survives regeneration, instead of picking it in the Xcode UI. The Team ID isn't secret, but **never** copy the membership page's address or phone number into the repo.
2. **Certificate:** Xcode → Settings → Accounts → the paid team (not "Personal Team") → Manage Certificates → + → Apple Development. If macOS says it's untrusted, the Apple WWDR intermediate certificate is usually missing from the keychain.
3. **iPhone:** connect by cable, unlock, tap Trust. **Developer Mode** (Settings → Privacy & Security) only appears after the phone has been connected to Xcode once. Turning it on restarts the phone; confirm "Turn On" afterwards. Keep it unlocked while installing.
4. **Watch:** goes through the paired iPhone (keep the phone connected and unlocked). Open Xcode → Window → Devices and Simulators, trust the Mac on the watch, then turn on Developer Mode on the watch. The first install is slow (5–10 min).
5. **TV:** same Wi-Fi as the Mac. On the TV, open Settings → Remotes and Devices → Remote App and Devices; in Xcode's Devices window, Pair and enter the code; then turn on Developer Mode on the TV.
6. If the app needs a local backend, the iPhone will ask for **local network** permission. Tell the user to allow it.

If you can run commands on the Mac, check device state yourself (`xcrun devicectl list devices`) before telling the user what to do next.

## Bundle IDs and names

- Three kinds of name: the **bundle ID** (hidden, permanent, unique across Apple), the **display name** (under the icon, needn't be unique), and the **App Store Connect name** (unique across the store, max 30 characters).
- Convention: reverse domain, `com.<prefix>.<app>`, with `.watchkitapp` for the Watch and a suffix like `.tv` for TV. Prefer a prefix matching a domain the user owns.
- **Settle the prefix before the first upload.** It can be changed freely until then; afterwards it's locked to that App Store Connect entry.

## Dev loop on the Mac

- Web dashboard: Vite hot reload. Backend: a file watcher that rebuilds on save (e.g. `cargo watch`). SwiftUI: Xcode **Previews** for instant UI, and ⌘R into a simulator for the full app.
- Offer small scripts: `dev.sh` (backend + web together, creates dev tokens on first run) and `sim.sh [iphone|watch|tv|all]` (build, boot simulators, install, launch already signed in).
- Debug builds can accept a dev token via launch arguments, so simulators start signed in.

## TestFlight (the "simple" path the user expects)

1. In App Store Connect → Apps → + → New App, create one record per bundle ID (iPhone, Watch-only app, TV), unless one record can cover several platforms.
2. Archive and upload (Xcode → Product → Archive → Distribute → TestFlight, or later from CI). Processing takes 10–30 min.
3. Add the user as an internal tester; install the TestFlight app on iPhone and TV and tap Install. The Watch app installs from TestFlight on the phone.

Point TestFlight builds at a reachable backend (e.g. the VPS), not the Mac, or they only work at home.

## Publishing checklist (when asked)

A backend that's always up with a reviewer demo account; real sign-in (Sign in with Apple) instead of pasted tokens; **in-app account deletion**; privacy policy URL and App Privacy answers; HealthKit rules (no ads, disclose any sharing with an AI provider, get consent); "not medical advice" where relevant; in-app purchase if charging; per-user cost limits and guardrails for AI features; icons, screenshots and a support URL. Expect at least one rejection the first time.
