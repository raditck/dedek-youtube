# AI FE Rules

Frontend rules for `index.html` — the whole app. Read before editing. Append-only.

## Non-Negotiables

- **One file.** All markup, CSS, JS inline in `index.html`. Never create `assets/`, `styles.css`,
  `app.js`, or any sibling file.
- **No build, no npm, no framework.** Vanilla ES6+. No React/Vue/Svelte/Alpine/jQuery.
- **One `<style>` in `<head>`, one classic `<script>` at end of `<body>`.** No ES modules
  (`import`/`export`), no CDN CSS, no external fonts, no icon packages.
- **No third-party JS.** Only external script allowed is YouTube's IFrame API
  (`https://www.youtube.com/iframe_api`) — it is required to embed video.
- Wrap app JS in one IIFE with `'use strict'`. Keep helpers and state inside it; no globals.
- Keep a clearly marked `/* ---- pure ---- */` section (CSV parse, id extraction, selection,
  timeline push) separate from DOM code so logic can be reasoned about and hand-tested.

## Design DNA

Dark, full-screen, reels/Shorts-like. Minimal chrome: title + channel, a right control rail,
a top bar with history/settings. Boring, fast, no marketing aesthetics.

- Tokens via CSS custom properties on `:root`; no duplicated color literals.
- Responsive: mobile = full-bleed vertical; desktop = centered player on dark background.
- No cropping video: size the player container, let YouTube letterbox.
- Animations <= 200ms; respect `prefers-reduced-motion`.

## Behaviour (must preserve)

- Swipe up / `ArrowDown` = next; swipe down / `ArrowUp` = previous; wheel = same.
- `Space` play/pause, `R` repeat, `H` history, `F` fullscreen, `Esc` close drawer.
- Arrow keys must not scroll the page.
- Buttons need `aria-label`; visible `:focus-visible` outline; `<button>` not clickable divs.
- Empty state offers Retry + Update List. Failed video is skipped silently.

## CSS / DOM Conventions

- Cache elements once (`const $ = (id) => document.getElementById(id)`).
- `dataset` for data attributes; `classList` for state.
- Use `textContent` for user/sheet strings; build only trusted markup with `innerHTML`
  (video ids are regex-validated `[A-Za-z0-9_-]{11}`).
- `loading="lazy"` on thumbnails.
- Never hardcode video data — always come from the sheet.

## Data / State

- Fetch the sheet CSV on load and on Update List only. Never poll.
- Persist playback state to `localStorage` under key `dy.v1` (schema in `AI_BE_RULES.md`).
- Never write play counts back to Google Sheets.
- Keep play counts keyed by YouTube video id, not array index.

## Avoid

- Frameworks, bundlers, transpilers, polyfills for modern browsers
- Toast/modal libraries, chart libs, icon fonts
- localStorage caches of the sheet contents as the source of truth (cache only for offline fallback)
- Reimplementing the selection algorithm outside the marked pure section
- Large media assets / base64 blobs in the HTML

## Future Rules

Append new rules below as sections; do not rewrite history.