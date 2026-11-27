---
name: logo
description: Design a logo or brand mark with the user — pin down the idea, explore two or three concepts, then draw it as a hand-written SVG master checked into the repo, render it, look at it, and iterate. Produces the mark, an optional wordmark and lockup, and mono variants that the other designstack skills export from. Use when the user asks for a logo, brand mark, wordmark, "make something like X", a symbol for their app or site, or wants to change an existing logo.
---

# Logo

Design the mark once, as SVG code in the repo. Every other asset (app icons, favicons, banners) is exported from it, so a tweak like "make the f bolder" is a one-line edit and a re-run, not a redraw.

## 1. Pin down the idea

- If the repo already has a logo (`design/`, `assets/`, `public/`, `*.svg`, an `AppIcon.appiconset`), start from it and ask what should change.
- Otherwise ask, in one message: what the product is, who it's for, two or three words for the feel (e.g. "calm, precise"), colours to use or avoid, and any logo they like.
- Restate the idea in one line before drawing: "an *f* made of a bent barbell; the wide red plate is the crossbar".

## 2. Explore, then pick one

Propose **two or three concepts** as one line each, ideally of different kinds: a letterform, a symbol of what the product does, an abstract shape. Draw rough versions of each and show them side by side (render them to one PNG). The user picks one, or mixes them. Don't polish anything before they choose.

## 3. Draw the master

Write `design/logo.svg` by hand, and keep it readable: someone should be able to change a colour or stroke from the source.

- `viewBox="0 0 1024 1024"`, square, with the mark centred and about 10% padding. No fixed `width`/`height`.
- Colours as CSS variables or a `<style>` block at the top, so variants just swap them.
- Simple geometry: `rect`, `circle`, `path` with few points. Group with `<g id="mark">` so exports can reuse it.
- **No text elements** in the mark: fonts aren't embedded and render differently everywhere. Convert letters to paths, or draw them.
- No filters, blurs or gradients that won't survive at 16 px. A gradient is fine if the mark still reads in one flat colour.

Variants, each its own file in `design/`:

| File | What it is |
|---|---|
| `logo.svg` | The mark in colour (the master) |
| `logo-mono.svg` | One colour on transparent, for small sizes and tinted contexts |
| `logo-inverse.svg` | For dark backgrounds, if the colour version doesn't work there |
| `wordmark.svg`, `lockup.svg` | Only if asked: the name, and mark + name side by side. For the name, use a font with a licence that allows it, note it in `design/README.md`, and outline the text to paths if a tool is available (`inkscape --export-text-to-path`) |

## 4. Render and look

Render with `rsvg-convert` (`brew install librsvg`), or Python `cairosvg`, or `inkscape`. Use whichever is installed and say which. Open the PNGs yourself before showing the user. Check:

- the mark at **1024, 128, 32 and 16 px**: does it still read at 16?
- on light and dark backgrounds, and inside a rounded square and a circle (that's how app icons crop it);
- off-centre shapes, strokes poking past joins, uneven gaps, thin lines that vanish when small.

Fix obvious defects yourself two or three times, then show the user one sheet with all sizes and backgrounds, and describe it in a sentence.

## 5. Hand off

- Commit `design/*.svg`, `design/README.md` (colours as hex, font and its licence, which file is for what) and any render script on a branch. Don't commit the throwaway concept renders.
- For app icons and favicons, continue with `designstack:app-icons`, which exports from `design/logo.svg`.

## Rules

- Original work only. If the user wants something "like" an existing brand, take the feel, not the shapes. Don't copy trademarks.
- The user decides. Give your view of which concept is strongest and why, but don't push past a clear choice.
