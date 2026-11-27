---
name: app-icons
description: Design and generate app icons from code — a small script (Swift + CoreGraphics on a Mac, or Python/SVG) that draws the icon and writes every asset catalog Xcode needs (iPhone, Apple Watch, Apple TV layered icons and Top Shelf images, plus web favicons if wanted), then renders, looks at the result, and iterates. Use this whenever the user asks for an app icon, logo, favicon, "make an icon like X", placeholder icons before a TestFlight or App Store upload, or Xcode/App Store Connect complains about a missing icon or Top Shelf image.
---

# App icons

Draw icons with a script checked into the repo, so they're reproducible and easy to tweak ("make the f bolder") instead of being a one-off image.

## Why a script

- Every size and platform comes from one drawing, so they stay consistent.
- Changing a colour is a one-line edit and a re-run.
- No design tool or external service, and no licensing questions.

## Steps

1. **Pin down the idea in one line** and restate it: e.g. "an *f* made of a bent barbell with bumper plates stacked on it; the wide red plate is the crossbar". If the user gave only a vibe, propose two or three concepts briefly and pick one with them.
2. **Check the tools:** on a Mac, `swift` with AppKit/CoreGraphics is always there. Otherwise use Python with Pillow or cairosvg, or `rsvg-convert`.
3. **Write `scripts/make-icons.<ext>`** (on a branch). Structure:
   - `background(ctx, w, h)`: full-bleed fill or gradient. **Opaque, no transparency, no rounded corners**: the system applies the mask.
   - `glyph(ctx)`: the mark, drawn in a fixed 1024×1024 box so every output just scales it.
   - `render(path, w, h, bg, fg, scale)`: draws background and/or glyph, centred, with the glyph at `scale` of the shorter side.
   - Writers for each asset catalog and its `Contents.json`.
4. **Render and look at it.** Open the PNG (read the image) before showing the user. Check for: gradient seams or banding, the glyph off-centre, stroke ends poking out (use `.butt` caps where lines meet shapes), too thin to read at small sizes, and contrast against both light and dark wallpapers.
5. **Iterate** two or three times on your own for obvious defects, then show the user the 1024 px image and describe it in a sentence.
6. **Wire it into the project** (e.g. XcodeGen: add `Assets.xcassets` to each target's sources; set `ASSETCATALOG_COMPILER_APPICON_NAME` if not the default), then build every target for the simulator and confirm the built `Info.plist` names the icon.
7. Commit the script and the generated assets in one PR; say it's been checked in the simulator, not on a device.

## What each platform needs

| Platform | Asset | Notes |
|---|---|---|
| iPhone / iPad | `AppIcon.appiconset`: one 1024×1024 PNG, `idiom: universal, platform: ios` | Glyph ~0.9 of the side; Xcode derives other sizes |
| Apple Watch | Same, `platform: watchos` | Cropped to a **circle**: keep the glyph ~0.8 so corners don't clip |
| Apple TV | `App Icon & Top Shelf Image.brandassets` containing: `App Icon.imagestack` (400×240 @1x/@2x) and `App Icon - App Store.imagestack` (1280×768), each with **Front** (glyph, transparent) and **Back** (background) layers for the parallax tilt; `Top Shelf Image` (1920×720) and `Top Shelf Image Wide` (2320×720), @1x/@2x | App Store Connect rejects tvOS uploads without the Top Shelf image |
| macOS | `AppIcon.appiconset` with 16–512 @1x/@2x | macOS doesn't mask: draw the rounded shape yourself |
| Web | `favicon.svg` or 32/180/192/512 PNGs + manifest | Simplify the glyph for 16–32 px |

## Related upload settings

While touching the project for icons before a first upload, also set `ITSAppUsesNonExemptEncryption = NO` (if the app only uses standard HTTPS) so TestFlight doesn't ask the export-compliance question on every build. See `devstack:apple-ship`.
