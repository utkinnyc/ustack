# Driving each platform

Wrap these in control commands; don't make agents retype them. Check each tool exists in `doctor` and print the install command if not. Commands marked † were checked against the installed tool when this was written; re-check `--help` if one fails.

## Backend and CLI

- **Up:** however the repo starts it (`npm run dev`, `cargo run`, `docker compose up`). Run it in the background, write its PID and log path to a git-ignored state file, poll the health endpoint until ready.
- **Act:** the app's own CLI first; HTTP (`curl -sS`, or the language's client) for what the CLI doesn't cover.
- **Inspect:** `state` reads the dev database or the API and prints JSON. `logs` tails the log file.
- **Reset:** recreate the dev database and seed a test user; never touch a database whose path or host isn't the dev one.

## Web

- **Driver:** Chrome via the DevTools Protocol. Reuse Playwright or Puppeteer if the repo has one; otherwise ask before adding Playwright (dev dependency).
- **Commands:** `open <path>`, `click <role> <name>` (by accessible role and name, not CSS), `type`, `press <key>`, `snapshot` (accessibility tree as JSON), `screenshot <file>`, `console` (errors since the last command), `network` (failed requests), `trace <file>` for performance.
- One-off checks without a script: Claude's browser tools, if available in the session. Scripted commands are better for anything repeated.

## iOS, iPadOS, watchOS, tvOS (Simulator)

| Step | Command |
|---|---|
| list devices | `xcrun simctl list devices available -j` † |
| boot | `xcrun simctl boot <udid>` †, then poll `xcrun simctl list devices booted -j` until it appears |
| build | `xcodebuild -scheme <scheme> -destination 'platform=iOS Simulator,id=<udid>' -derivedDataPath build/dd build` (watchOS / tvOS: change the platform) |
| install, launch | `xcrun simctl install <udid> <path>.app` †, `xcrun simctl launch <udid> <bundle id> [args]` † (args can carry a dev token or a test flag) |
| deep link | `xcrun simctl openurl <udid> <scheme>://…` † |
| screenshot, video | `xcrun simctl io <udid> screenshot <file>.png` †, `xcrun simctl io <udid> recordVideo <file>.mov` † (stop with Ctrl-C / SIGINT) |
| logs | `xcrun simctl spawn <udid> log stream --predicate 'subsystem == "<bundle id>"'` |
| state | `xcrun simctl ui <udid> appearance dark` †, `status_bar … override`, `privacy … grant`, `location`, `push` † |
| stop | `xcrun simctl terminate <udid> <bundle id>` †, `xcrun simctl shutdown <udid>` † |

**Limit:** `simctl` can't tap or read the screen's elements. For interaction, use XCUITest (`xcodebuild test -only-testing:<UITests>/<test>`) with one small UI test per flow, or `idb` if the user has it installed (`idb ui tap`, `idb ui describe-all`). Prefer deep links and launch arguments to reach a screen directly. TV focus moves need XCUITest's remote (`XCUIRemote`).

## Android (Emulator)

| Step | Command |
|---|---|
| list, boot | `emulator -list-avds`, `emulator -avd <name> -no-window -no-audio &`, `adb wait-for-device` |
| build, install | `./gradlew assembleDebug`, `adb install -r app/build/outputs/apk/debug/app-debug.apk` |
| launch, deep link | `adb shell am start -n <package>/<activity>`, `adb shell am start -a android.intent.action.VIEW -d '<url>'` |
| interact | `adb shell input tap <x> <y>`, `adb shell input text '<text>'`, `adb shell input keyevent KEYCODE_BACK` |
| inspect | `adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml` (element tree with bounds; tap the centre of an element's bounds) |
| screenshot, video | `adb exec-out screencap -p > <file>.png`, `adb shell screenrecord /sdcard/v.mp4` then `adb pull` |
| logs | `adb logcat -d --pid=$(adb shell pidof <package>)` |
| stop | `adb shell am force-stop <package>`, `adb emu kill` |

These Android commands were not checked on this machine (no Android SDK installed); `doctor` should confirm them.
