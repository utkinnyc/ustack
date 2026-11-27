---
name: apple-ship
description: Get iPhone, Apple Watch, Apple TV and Mac apps from code onto real devices and toward the App Store — free vs paid Apple Developer account, enrolment, Team ID, signing certificates, Developer Mode, pairing the Watch and TV with Xcode, bundle ID naming, XcodeGen projects, how signing and provisioning profiles work, simulator and live-preview dev loops, scripted TestFlight uploads (including unsigned tvOS archives and watch-only apps), upload rejections, Swift version mismatches in CI, and the publishing checklist. Use this whenever the user mentions Xcode signing, provisioning, "install on my phone/watch/TV", Developer Mode, Team ID, bundle IDs, TestFlight, App Store Connect, archive/export/upload errors, the $99 developer account, simulators, or publishing an Apple app — even if they only paste an Xcode error.
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
- Convention: reverse domain, `com.<prefix>.<app>`. Prefer a prefix matching a domain the user owns. **Settle it before the first upload**; afterwards it's locked to that App Store Connect record.

## One app on every device (the default)

Ship **one App Store record** for all platforms (Apple calls it Universal Purchase), and keep adding platforms (iPad, Mac) to it later:

| Device | How it fits |
|---|---|
| iPhone | The main app, `com.<prefix>.<app>` |
| Watch | **Embedded in the iPhone app**, `com.<prefix>.<app>.watchkitapp`. It can still run and talk to the server on its own. Installing on the phone offers it on the watch. |
| TV | A separate build with the **same bundle ID** as the iPhone app; the record gets a tvOS platform (App Store Connect → the app → **+** next to "iOS App" → tvOS) |
| Mac / iPad | Same bundle ID, added as platforms |

This means one TestFlight page, one tester group and one name. Separate records (a standalone watch-only app in an empty iPhone wrapper, or a TV app under `.tv`) multiply the setup, and records that have had builds can't be deleted.

**Ask before deviating.** Any choice that changes the app's shape (separate records, standalone Watch app, separate bundle IDs) goes to the user as options with trade-offs *before* you do it. Don't pick a workaround silently because something failed to build.

**The usual reason a Watch app gets split out:** a shared Swift package that generates code at build time (e.g. the OpenAPI generator plugin) is built twice, for iPhone and Watch, in one build, and Xcode fails with *"Multiple commands produce …/Types.swift"*. Fix the cause: run the generator as a script when the contract changes, commit its output, and add a CI check that fails if the committed code is stale. That also removes Xcode's "Trust & Enable" plugin prompt.

## Dev loop on the Mac

- Web dashboard: Vite hot reload. Backend: a file watcher that rebuilds on save (e.g. `cargo watch`). SwiftUI: Xcode **Previews** for instant UI, and ⌘R into a simulator for the full app.
- Offer small scripts: `dev.sh` (backend + web together, creates dev tokens on first run) and `sim.sh [iphone|watch|tv|all]` (build, boot simulators, install, launch already signed in).
- Debug builds can accept a dev token via launch arguments, so simulators start signed in.

## How signing works (explain when asked "why is Apple so complicated?")

| Thing | What it is | Where it lives |
|---|---|---|
| Certificate | Who you are (name + Team ID) | The Mac's Keychain |
| App ID | The registered bundle ID | The developer account |
| Provisioning profile | Permission slip: this certificate may sign this App ID, for these devices (**development**) or for the App Store (**distribution**) | Downloaded by Xcode |

Development profiles list each device, registered by connecting or pairing it with Xcode. Distribution profiles (TestFlight, App Store) need no device list, so **a device only needs to be on for TestFlight when installing**. `-allowProvisioningUpdates` lets Xcode register App IDs and fetch profiles itself; that's why bundle IDs appear in App Store Connect's dropdown after a first archive.

## TestFlight (the "simple" path the user expects)

**Before the first upload:** every target needs an app icon, and the TV also needs a Top Shelf image (see `devstack:app-icons`). Set `ITSAppUsesNonExemptEncryption = NO` if the app only uses standard HTTPS, so uploads don't ask about encryption. If the HealthKit entitlement is present, the upload needs **both** `NSHealthShareUsageDescription` and `NSHealthUpdateUsageDescription`, even for a read-only app.

1. **App record (user, App Store Connect → Apps → + → New App):** one record (platform, name, bundle ID, SKU, given as a table), then add tvOS to it if there's a TV app. Names must be unique across the store; if one is taken, add a suffix. If the bundle ID is missing from the dropdown, do one archive with `-allowProvisioningUpdates` to register it, then refresh.
2. **Upload (you, from a script):** offer `scripts/testflight.sh [schemes…]` (see `references/testflight.sh`). It regenerates the project, archives each scheme in Release with a **timestamp build number** (Apple rejects repeats), and exports with `method app-store-connect`, `destination upload`. Traps:
   - **TV with no registered Apple TV:** archive with `CODE_SIGNING_ALLOWED=NO`, and let the export sign it for distribution. An unsigned archive carries no team, so put `teamID` in the export options, read from the project rather than hard-coded.
   - **Check the archive:** the iPhone `.xcarchive` must contain `Products/Applications/*.app` with the Watch app under `Watch/` inside it. Run the export locally before uploading.
   - Filter `xcodebuild` noise in the output (`grep -E "==>|Upload (succeeded|failed)|error:"`).
   Processing takes 10–30 min.
3. **Testers (user, once per record):** TestFlight tab → **+** next to Internal Testing → a group (e.g. "Me") with automatic distribution on → add themselves and the build. No review needed.
4. **Install:** the TestFlight app on iPhone and TV (same Apple ID). The Watch app comes with the iPhone app (or from the iPhone's Watch app → Available Apps, or TestFlight on the watch). Later uploads arrive automatically.

**Reading App Store Connect:**

| What they see | Meaning |
|---|---|
| "1.0 Prepare for Submission" | The public App Store page. Ignore it for TestFlight. |
| Processing | Apple is checking the upload (10–30 min); an email follows |
| Missing Compliance | The encryption question: answer **None of the algorithms mentioned above** (standard HTTPS/Keychain only), then add `ITSAppUsesNonExemptEncryption = NO` to that target so it doesn't come back |
| Ready to Submit / Ready to Test | Ready. "Submit" refers to external testers only; internal testers can install now |
| Invalid | Rejected; the email says why |

**App not offered on a device:** TestFlight shows "uses watchOS X" (or similar) when the device's OS is older than the target's minimum. Check the device's version first, and ask whether to lower the deployment target only if the code builds against the older SDK. After an OS update, force-quit TestFlight; it caches the device version.

**Order matters for the TV:** add the tvOS platform to the record *before* uploading the TV build, or it may never show up (re-upload if it doesn't appear within ~30 min). When moving from separate records to one, the Watch and TV apps count as new apps on the devices: delete the old ones and sign in again.

Apple builds don't happen automatically on merge (only the backend does, through CI). Say so, and run the upload script after merges unless CI uploads have been set up.

Release builds must point at a reachable backend (e.g. the VPS), not the Mac, or they only work at home. Then each app needs its device token in Settings (see `devstack:go-live`).

## CI for Apple code

If `swift build` fails in CI with "package is using Swift tools version X but the installed version is Y", the runner image has an older Xcode. Move that job to a runner image with the matching Xcode (check the GitHub runner-images changelog) instead of lowering `swift-tools-version`.

## Publishing checklist (when asked)

A backend that's always up with a reviewer demo account; real sign-in (Sign in with Apple) instead of pasted tokens; **in-app account deletion**; privacy policy URL and App Privacy answers; HealthKit rules (no ads, disclose any sharing with an AI provider, get consent); "not medical advice" where relevant; in-app purchase if charging; per-user cost limits and guardrails for AI features; icons, screenshots and a support URL. Expect at least one rejection the first time.
