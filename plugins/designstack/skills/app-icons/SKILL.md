---
name: app-icons
description: Turn a logo into every app icon and favicon a project needs — iPhone/iPad, Apple Watch, Apple TV layered icons and Top Shelf images, macOS, Liquid Glass `.icon` files, and the web favicon set and manifest — with a checked-in export script, then build and check them. Use when the user asks for app icons or a favicon, placeholder icons before TestFlight or the App Store, or Xcode/App Store Connect complains about a missing icon or Top Shelf image.
---

# App icons

Export every icon from one source with a script checked into the repo, so all sizes and platforms stay consistent and a change to the logo is a re-run.

## 1. Find the source

In order of preference:
1. `design/logo.svg` from `designstack:logo` (or another SVG mark in the repo).
2. A 1024×1024 PNG the user provides. Fine for Apple, but favicons and the tvOS layers will be blurrier and can't be separated.
3. Nothing: run `designstack:logo` first. For a quick placeholder before a TestFlight upload, a letter on a flat colour is acceptable; say it's a placeholder.

An app icon is two layers: an **opaque, full-bleed background** (flat colour or gradient, no rounded corners, no transparency; the system applies the mask) and the **mark** centred on it. Keep the background in `design/icon-bg.svg` (or as a colour in the script) so the layers stay separable; tvOS and Liquid Glass need them apart.

## 2. Write the export script

`scripts/export-icons.py`, standard library only, shelling out to `rsvg-convert` (`brew install librsvg`) for SVG → PNG. If it isn't installed, say so and give the command; on a Mac without it, `swift` with CoreGraphics can draw the PNGs instead.

- `compose(bg, mark, size, scale)` builds an SVG string: background full-bleed, mark centred at `scale` of the side.
- One writer per target below, each writing its PNGs and `Contents.json` (`json.dump`, not hand-typed).
- Only write the targets the project has: look for `*.xcodeproj`, `project.yml` (XcodeGen), `Assets.xcassets`, `public/` or `app/` for web.

## 3. What each platform needs

| Platform | Asset | Notes |
|---|---|---|
| iPhone / iPad | `AppIcon.appiconset`: one 1024×1024 PNG, `idiom: universal, platform: ios` | Logo box (which already has ~10% padding) at ~0.9 of the side; Xcode derives other sizes |
| Apple Watch | Same, `platform: watchos` | Cropped to a **circle**: logo box at ~0.8 so corners don't clip |
| Apple TV | `App Icon & Top Shelf Image.brandassets` containing `App Icon.imagestack` (400×240 @1x/@2x) and `App Icon - App Store.imagestack` (1280×768), each with **Front** (mark, transparent) and **Back** (background) layers for the parallax tilt; plus `Top Shelf Image` (1920×720) and `Top Shelf Image Wide` (2320×720), @1x/@2x | App Store Connect rejects tvOS uploads without the Top Shelf images |
| macOS | `AppIcon.appiconset` with 16–512 @1x/@2x | macOS doesn't mask: draw the rounded square and its margin yourself |
| Web | `favicon.svg` (the mono or colour mark), `favicon.ico` or `favicon-32.png`, `apple-touch-icon.png` (180, opaque background), `icon-192.png` and `icon-512.png`, and a `manifest.webmanifest` listing them | Below 32 px, use `logo-mono.svg` or a simplified mark. Add the `<link>` tags to the site's head (Next.js: `app/icon.svg` and `app/apple-icon.png` are picked up automatically) |

### Liquid Glass (iOS 26 and later)

Apple's newer icons are a layered `.icon` file made in **Icon Composer** (Apple's free app). It takes the layers as SVG or PNG and renders the light, dark, tinted and clear looks itself.

- Export the layers separately (`design/export/icon-bg.svg`, `icon-mark.svg`) so they can go into Icon Composer, or into a command-line tool that builds `.icon` files. Community tools exist, such as `glassmith` and `icon-composer-mcp`. Check one is installed and read its README before using it, and tell the user it's third-party.
- **Keep the `AppIcon.appiconset` PNGs as well.** Older OS versions use them, and developers report App Store uploads need them alongside the `.icon` file.
- If none of this is set up, the classic asset catalog still works. Say that Liquid Glass is optional and offer it.

## 4. Look, wire in, build

1. **Look at the output** before showing the user: open the 1024 iPhone icon, the Watch icon in a circle, the tvOS front layer over the back, and the 16 and 32 px favicons. Check for banding, an off-centre mark, clipping in the circle, and contrast on light and dark wallpapers. Fix and re-run on your own for obvious defects.
2. **Wire it in.** XcodeGen: add `Assets.xcassets` to each target's sources; set `ASSETCATALOG_COMPILER_APPICON_NAME` if not the default (and the tvOS brand-assets name for TV). Web: the head tags or framework files above.
3. **Build every target** for the simulator and confirm the built `Info.plist` names the icon. For web, load the page and check the favicon request returns 200.
4. Commit the script and the generated assets in one PR. Say what was checked (simulator, browser) and what wasn't (a real device).

## Related upload settings

While touching the project before a first upload, also set `ITSAppUsesNonExemptEncryption = NO` (if the app only uses standard HTTPS) so TestFlight doesn't ask the export-compliance question on every build. See `devstack:apple-ship` if installed.
