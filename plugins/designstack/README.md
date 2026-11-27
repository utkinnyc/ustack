# designstack

designstack does the design work an app or site needs, as code in your repo. You design
the mark once as an SVG, and every other asset is exported from it, so a change like
"make the f bolder" is a one-line edit and a re-run.

```
/designstack:logo        # concept → SVG master, mono and inverse variants
/designstack:app-icons   # export to iPhone, Watch, TV, Mac, Liquid Glass and web favicons
```

- **Designs with you.** Two or three concepts side by side, you pick, then it refines.
- **Looks at its own work.** Renders every output and checks it at 16 px, in a circle, and
  on light and dark backgrounds before showing you.
- **Covers the awkward platforms.** Apple TV layered icons and Top Shelf images, the
  Watch's circular crop, macOS's unmasked icons, and Liquid Glass `.icon` layers.

More skills (banners, social and Open Graph images, store screenshots) will build on the
same SVG master.

## Install

```
/plugin marketplace add utkinnyc/ustack
/plugin install designstack@ustack
```

**Requirements:** [Claude Code](https://claude.com/claude-code), Python 3, and
`rsvg-convert` (`brew install librsvg`) to render SVG. Xcode for Apple targets.
[Icon Composer](https://developer.apple.com/icon-composer/) is optional, for Liquid Glass
icons.

## Skills

| Skill | What it does |
|---|---|
| `logo` | Pins down the idea, explores 2–3 concepts, draws a hand-written SVG master with mono and inverse variants, and checks it at every size. |
| `app-icons` | Exports the logo to every Apple asset catalog, Liquid Glass layers and the web favicon set with a checked-in script, then builds and checks them. |
