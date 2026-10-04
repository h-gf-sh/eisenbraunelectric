# eisenbraunelectric.co

Static rebuild of the Wix site at www.eisenbraunelectric.co, for hosting on Vercel.

## Layout

```
site/                 deployable root (set Vercel "Root Directory" to site)
  index.html          home: header nav + eight sections with their players
  about/index.html    contact page
  assets/style.css    all styling; desktop mirrors the Wix 980px grid, <=640px reflows
  assets/fonts/       Newsreader variable (wght + opsz), roman and italic (OFL)
  assets/sky.jpg      original-resolution background (2208x1242) pulled from Wix media
  vercel.json         cleanUrls, long cache on /assets
_reference/           what the live Wix site looked like on 2026-10-03
  screenshots/        live desktop/mobile captures, rebuild on mobile
  capture/            rendered Wix HTML, rich-text blocks, measured line positions
  wix-embeds/         the six Wix "HTML embed" wrappers that held the Bandcamp players
  type-comparison-kepler-crimson-newsreader.png
tools/                Playwright capture + build scripts (python3, playwright)
```

`python3 tools/build.py` (from this folder; needs `beautifulsoup4`) regenerates both HTML pages from `_reference/capture/`; the text is carried over from the live markup, not retyped.

Links and asset paths are root-relative clean URLs (`/`, `/about`, `/#radio-ghost`, `/assets/…`), matching what Vercel serves with `cleanUrls`, so no click goes through a redirect. That means the pages don't preview from disk; run `vercel dev` (or `python3 -m http.server`) inside `site/`.

## Deploy

Pushes that touch `site/` are deployed by GitHub Actions (`.github/workflows/deploy.yml`) to the Vercel project `eisenbraunelectric` in the `eisenbraun-electric-co` scope: `main` goes to production, any other branch to a preview. Vercel's built-in Git integration isn't used because the Vercel account's GitHub login is a different account from the one that owns this repo. Repo settings needed: secret `VERCEL_TOKEN`, variables `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID`. To deploy by hand instead: `vercel --prod` from `site/`.

## Parity

At 1440px wide, every section heading, text block and player lands on the same pixel row as the live page (headings, first and last text lines, player tops, page height 6981px), with identical line breaks in every paragraph, Page text and outbound links diff clean against the live site, apart from the contact address (below).

## Type

Newsreader replaces Wix's Kepler W03 Light SemiCond Caption (Wix-licensed, not included; DIN Next Light was declared but unused). Weight 300 throughout, kept a shade lighter than Kepler on purpose; optical size pinned at 18 for display and 20 for text, which are its narrowest cuts and reproduce every Wix line break. Its vertical metrics are overridden to Kepler's (`ascent-override: 75%` / `descent-override: 25%`) so baselines sit where Kepler's did. Crimson Pro was the other candidate (see `_reference/type-comparison-kepler-crimson-newsreader.png`).

## Contact

The About page address is `tom@eisenbraunelectric.co` (was `tom@eisenbraunmusic.com` on Wix; that domain is being wound down). The swap lives in `tools/build.py` (`OLD_CONTACT` / `CONTACT`), since the page text is otherwise regenerated from the Wix capture.

## Embeds (were hidden behind Wix widgets)

| Section | Player |
|---|---|
| light is sound made visible | YouTube `zcBaPQwS2ZA` |
| the imagined psaltery | SoundCloud playlist 696557559 ("from the imagined psaltery") |
| Still Life | Bandcamp album 1607365099 |
| Guided Meditation for the Solar Eclipse | Bandcamp album 3446417610 |
| Memory of the Sound of Home | Bandcamp album 1065130046 |
| Radio Ghost | Bandcamp album 1572416429 (white player variant, as on Wix) |
| Slow Joy | Bandcamp album 1723711786 |
| The October Country | Bandcamp album 3081737407 |

The Bandcamp embed fallbacks on Wix linked to `tunes.eisenbraunmusic.com`, which no longer resolves (NXDOMAIN). The rebuild points them at `tomeisenbraun.bandcamp.com` instead.

## Background

The sky is a fixed layer the size of the viewport (`100lvh`, so mobile toolbars collapsing never expose a strip) with `background-size: cover; no-repeat`: it scales to whichever dimension needs it, never tiles, and holds still while the page scrolls. The white text washing out over the pale lower half is intentional.

## Deliberate departures from Wix

- Narrow screens get a fluid version of the same layout instead of Wix's scaled-down 980px grid. Under 640px the column goes full width (16px gutters), the title scales to fit one line, players go full width, and the nav keeps its tight right-aligned stack, dropped into flow under the tagline.
- Section headings are `h2` with anchor ids (`#still-life`, `#radio-ghost`, …) instead of Wix's `#comp-…` ids.
- Wix's Google Analytics tag (`G-MN4RN3JYWL`) is not carried over.
- The Wix favicon was Wix's generic one; none is set yet.

## Domain

Live on Vercel since 2026-10-04. DNS stays at Wix: apex A records `216.198.79.1` and `64.29.17.1`, `www` CNAME to `ffccbb534deca3bb.vercel-dns-017.com` (redirects 308 to the apex, which is canonical). Google Workspace MX, SPF, site-verification, DKIM (`google._domainkey`, 2048-bit) and DMARC (`_dmarc`) records are in the same Wix zone.

## To do

- Favicon (none set yet).
- DMARC is `p=none` (monitoring, reports to tom@). After a few weeks of clean reports, move `_dmarc` to `p=quarantine`.
