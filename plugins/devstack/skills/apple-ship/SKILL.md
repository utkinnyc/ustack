---
name: apple-ship
description: Get iPhone, iPad, Apple Watch, Apple TV and Mac apps onto devices and out through TestFlight and the App Store: developer account, signing, Developer Mode, bundle IDs, a scripted TestFlight upload, App Store Connect, and upload or install failures. Use when the user wants to install on a device, release to TestFlight, asks about Xcode signing, bundle IDs or publishing, or pastes an Xcode archive or upload error.
---

# Apple Ship

Get the user's Apple apps onto their devices, then to testers and the App Store. Many developers are new to Apple's tooling, so on a first run explain each Apple-specific step and why it exists. On later runs, skip the explanations and ship.

## First, see what exists

Read before asking, and cite what you find:
- **Project:** `project.yml` (XcodeGen), `*.xcodeproj`, `*.xcworkspace` (CocoaPods or several projects), `Package.swift`. React Native, Flutter and Expo apps have their own build tools, but signing, App Store Connect and TestFlight below still apply.
- **Targets and platforms:** which of iPhone, iPad, Watch, TV and Mac exist, and whether the Watch app is embedded in the iPhone app.
- **Release script:** is there already a `scripts/testflight.sh` (or similar)?
- **Device state**, if you can run commands on the Mac: `xcrun devicectl list devices`.

## Release again (the usual case)

If the repo already has an upload script and has shipped before:

1. Check the tree is clean and on the branch the user wants to ship (usually `main`, after merging). Ask before shipping uncommitted changes.
2. Run the project's own checks first (tests, lint), if they're quick.
3. Run the upload script, e.g. `scripts/testflight.sh` or `scripts/testflight.sh <scheme>`, and filter the noise: `… 2>&1 | grep -E "==>|Upload (succeeded|failed)|error:"`.
4. Report which schemes uploaded and the build number. Builds show up in TestFlight after 10–30 min of processing; internal testers get them automatically.
5. If it fails, match the error against **When things fail** below before guessing.

Apple builds don't run on merge unless CI uploads were set up, so say so after a merge, and offer to run the script.

## First time: account and devices

### Free vs paid account

Explain this up front, since it decides the path:

| | Free (Personal Team) | Paid ($99/year) |
|---|---|---|
| Install | Xcode, by cable or pairing, every time | Xcode, **or TestFlight** (one tap per device) |
| App lifetime | 7 days | TestFlight builds last 90 days |
| Apps per device | 3 | No limit |
| Push, Sign in with Apple, HealthKit, iCloud | Limited or unavailable | Work |

Enrol at https://developer.apple.com/programs/enroll/ (or in the Apple Developer app on iPhone) with the same Apple ID as Xcode, with two-factor on. Approval takes hours, up to 48. **Apple Developer** (developer.apple.com) is for building and signing; **App Store Connect** (appstoreconnect.apple.com) is for TestFlight, listings and review.

### Install on real devices

1. **Team ID:** developer.apple.com/account → Membership details. Put it in the project definition (`DEVELOPMENT_TEAM`, in `project.yml` for XcodeGen) so it survives regeneration. It isn't secret, but never copy the membership page's address or phone number into the repo.
2. **Certificate:** Xcode → Settings → Accounts → the paid team (not "Personal Team") → Manage Certificates → + → Apple Development. If macOS says it's untrusted, the Apple WWDR intermediate certificate is usually missing from the keychain.
3. **iPhone / iPad:** connect by cable, unlock, tap Trust. **Developer Mode** (Settings → Privacy & Security) only appears after the device has been connected to Xcode once. Turning it on restarts the device; confirm "Turn On" afterwards.
4. **Watch:** goes through the paired iPhone (keep it connected and unlocked). Xcode → Window → Devices and Simulators, trust the Mac on the watch, then turn on Developer Mode on the watch. The first install is slow (5–10 min).
5. **TV:** same Wi-Fi as the Mac. On the TV: Settings → Remotes and Devices → Remote App and Devices; in Xcode's Devices window, Pair and enter the code; then turn on Developer Mode on the TV.
6. If the app talks to a server on the Mac, iOS asks for **local network** permission. Allow it.

### How signing works (when asked "why is this so complicated?")

| Thing | What it is | Where it lives |
|---|---|---|
| Certificate | Who you are (name + Team ID) | The Mac's Keychain |
| App ID | The registered bundle ID | The developer account |
| Provisioning profile | Permission slip: this certificate may sign this App ID, for these devices (**development**) or for the App Store (**distribution**) | Downloaded by Xcode |

Development profiles list each device, registered by connecting or pairing it. Distribution profiles (TestFlight, App Store) need no device list. `-allowProvisioningUpdates` lets Xcode register App IDs and fetch profiles itself.

## Bundle IDs and app records

- Three names: the **bundle ID** (hidden, permanent, unique across Apple), the **display name** (under the icon), and the **App Store Connect name** (unique across the store, max 30 characters).
- Bundle IDs are reverse-domain, `com.<prefix>.<app>`, ideally matching a domain the user owns. **Settle it before the first upload**; afterwards it's locked to that record.
- **One record for every platform** (Universal Purchase) is the default: the Watch app embedded in the iPhone app as `com.<prefix>.<app>.watchkitapp`; TV, iPad and Mac builds with the **same bundle ID**, added as platforms on the record (App Store Connect → the app → **+** next to the first platform). One TestFlight page, one tester group, one name. Records that have had builds can't be deleted, so avoid creating extras.
- **Ask before changing the app's shape** (separate records, a standalone Watch app, separate bundle IDs). Give the options and trade-offs; don't pick a workaround silently because a build failed.

## First upload to TestFlight

**Before it**, every target needs an app icon, and a TV app also needs Top Shelf images (use `designstack:app-icons` if installed, otherwise ask for a 1024×1024 PNG). Set `ITSAppUsesNonExemptEncryption = NO` on each target if the app only uses standard HTTPS, so every upload doesn't ask about encryption. Every privacy-sensitive entitlement needs its usage-description strings in `Info.plist` (HealthKit needs **both** `NSHealthShareUsageDescription` and `NSHealthUpdateUsageDescription`, even for read-only use).

1. **App record (the user, in App Store Connect → Apps → + → New App):** give them the platform, name, bundle ID and SKU as a table. If the bundle ID is missing from the dropdown, do one archive with `-allowProvisioningUpdates` to register it, then refresh. Add any extra platform (tvOS) **before** uploading that build, or it may never show up.
2. **Upload script:** copy `references/testflight.sh` to `scripts/testflight.sh` and fill in the block at the top from what you found: project or workspace, one `scheme:platform` line per app, `WATCH_IN` if the Watch app is embedded, and `PRECHECK` for tests. It regenerates XcodeGen projects, reads the Team ID from the project, uses a timestamp as the build number (Apple rejects repeats), checks each archive really contains the app (and the Watch app), then exports and uploads. Run it once and fix what fails.
3. **Testers (the user, once):** TestFlight tab → **+** next to Internal Testing → a group with automatic distribution on → add themselves. Internal testing needs no review.
4. **Install:** the TestFlight app on each device, signed in with the tester's Apple ID. An embedded Watch app comes with the iPhone app. Later uploads arrive automatically.

Release builds must point at a backend that's reachable from anywhere, not the Mac, or they only work at home (see `devstack:go-live` if installed).

## Reading App Store Connect

| Status | Meaning |
|---|---|
| "1.0 Prepare for Submission" | The public App Store page. Ignore it for TestFlight. |
| Processing | Apple is checking the upload (10–30 min); an email follows |
| Missing Compliance | The encryption question: answer **None of the algorithms mentioned above** if only standard HTTPS/Keychain, then set `ITSAppUsesNonExemptEncryption = NO` so it doesn't return |
| Ready to Submit / Ready to Test | Ready. "Submit" is for external testers only; internal testers can install now |
| Invalid | Rejected; the email says why |

## When things fail

- **"Redundant binary upload" / build number already used:** the build number must increase every upload. The script uses a timestamp; check nothing overrides `CURRENT_PROJECT_VERSION`.
- **Archive has no app:** `SKIP_INSTALL = YES` on the app target (it should be on frameworks only).
- **TV archive fails to sign with no Apple TV registered:** archive unsigned (`:unsigned` in the script) and let the export sign it for distribution. An unsigned archive carries no team, which is why the export options set `teamID`.
- **"Multiple commands produce …":** usually a shared Swift package with a code-generating build plugin (e.g. the OpenAPI generator) built twice in one build, for iPhone and Watch. Fix the cause (run the generator from a script before building, into a git-ignored folder) rather than splitting the apps apart.
- **Watch app not on the watch:** first confirm the iPhone archive contains it (the script checks). Then on the iPhone's Watch app → My Watch, scroll to the bottom: **Available Apps → Install**; or under **Installed on Apple Watch**, turn on **Show App on Apple Watch**. A spinner that never finishes: restart both, watch unlocked on its charger next to the phone on the same Wi-Fi, try again. Still stuck: install from TestFlight on the watch itself, or from Xcode by cable.
- **App not offered on a device:** TestFlight shows "requires iOS/watchOS X" when the device's OS is older than the deployment target. Check the device first; lower the target only if the code builds against the older SDK. After an OS update, force-quit TestFlight; it caches the device version.
- **Moved from separate records to one:** the Watch and TV apps count as new apps on devices. Delete the old ones and sign in again.

## Project setup (offer when relevant, with the reason)

- **Share logic, not UI.** If there are several Apple apps, a shared Swift package (`<App>Kit`) holds the API client, auth token storage (Keychain) and models; each app draws its own screens. Shared views fill up with `#if os(watchOS)`.
- **Generated code:** consider building it rather than committing it, so generated diffs don't drown real changes in PRs. Ask the user's preference.
- **CI:** macOS runners on GitHub Actions cost about 10× Linux minutes. A cheap alternative is running `swift test` from the upload script's `PRECHECK`, so a failure stops the upload. Mention the trade-off; don't remove an existing macOS job without asking. If one fails with "package is using Swift tools version X but the installed version is Y", the runner's Xcode is older: move to a runner image with the right Xcode rather than lowering `swift-tools-version`.
- **A web companion that looks native:** about 200 lines of hand-written CSS usually beat a UI library: `-apple-system, system-ui` fonts, Apple's system colours as CSS variables with a dark variant, inset grouped lists, large titles, a tab bar, and a few inline SVG icons (SF Symbols' licence doesn't cover the web). Konsta UI needs Tailwind, Ionic adds ~245 KB, and Framework7 brings its own router. Keep the Apple apps on system colours (they adapt to accessibility settings) rather than generating them from a shared token file. Before matching the web to the apps, list where the apps disagree with each other (icons, status colours, formats, error style) and let the user pick one of each.
- **Web size:** a React SPA is ~75 KB compressed, mostly React; `preact/compat` takes it to ~15 KB. Cache headers for hashed assets help more than code-splitting.
- **Offline data on Watch and iPhone** must persist to disk: the system kills apps often, and an in-memory queue loses data silently.

## Sign in with Apple (when adding login)

- Needs the paid account and the capability on **each** App ID, including the Watch's. The web needs a **Services ID** with a verified domain and return URL. These are portal steps the user does; list them.
- Native on iPhone, iPad, Mac, Watch and TV (`AuthenticationServices`). Google has no Watch SDK, and on TV needs the device-code flow.
- The token's `aud` differs per client: the Watch's can be its own bundle ID (`….watchkitapp`), the web's is the Services ID. The server must accept all of them.
- **Hide My Email** gives a relay address (`…@privaterelay.appleid.com`), and Apple sends the email only on the **first** sign-in. Don't key users on email; store the `sub`.
- **Apple refuses `localhost` return URLs.** For local web or CLI login, point a `dev.<domain>` return URL at `127.0.0.1` in `/etc/hosts` and serve it with a `mkcert` certificate, or use a tunnel. The iOS Simulator signs in fine against a local server.

## Publishing to the App Store (when asked)

A backend that's always up, with a demo account for the reviewer; real sign-in rather than pasted tokens; if the app offers third-party login (e.g. Google), it must also offer **Sign in with Apple**; if it creates accounts, **in-app account deletion**; a privacy policy URL and the App Privacy answers; any category rules that apply (health data, kids, payments through in-app purchase); screenshots for each device size, icons and a support URL. Expect at least one rejection the first time; the rejection message says what to fix.
