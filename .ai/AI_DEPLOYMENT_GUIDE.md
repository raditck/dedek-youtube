# AI Deployment Guide — GitHub Pages + GitHub Actions

No cPanel, no Laravel, no servers. Two moving parts:

1. **GitHub Pages** serves `index.html` at `https://dedek.tantua.com`.
2. **GitHub Actions** (`tools/sync.py`) runs the daily yt-dlp sync into the sheet.

## 1. GitHub Pages

Repo contains only `index.html` (plus `.ai/` and `.pi/` which Pages ignores).

1. Repo → Settings → Pages.
2. Source: *Deploy from a branch*.
3. Branch: `main`, folder: `/ (root)`.
4. Custom domain: `dedek.tantua.com` → Save (GitHub creates the CNAME entry; no CNAME file
   is committed, keeping the repo single-file).
5. Wait for the DNS check, then enable **Enforce HTTPS**.

DNS at the domain provider:

```
Type   Name   Value
A      @      185.199.108.153
A      @      185.199.109.153
A      @      185.199.110.153
A      @      185.199.111.153
CNAME  www    <user>.github.io
```

For the subdomain only, a single `CNAME dedek <user>.github.io` is enough.

Cache note: Pages caches aggressively. Hard-reload after deploys; `index.html` is a single
document so there is no asset-hash problem.

PWA/service worker is intentionally absent: a service worker cannot be inlined into
`index.html`. If offline support is later required, the user must allow exactly one extra
file, `sw.js`.

## 2. GitHub Actions sync (yt-dlp)

Two files: `.github/workflows/sync.yml` + `tools/sync.py`. Nothing else.

1. Google Cloud → create a service account → JSON key.
2. Share the spreadsheet with the service account email as **Editor**.
3. Repo → Settings → Secrets and variables → Actions:
   - `SPREADSHEET_ID` = `1OTAoHRg0ijCUS9YdZG2Vl8a4WsaadiwAnLHko3LWEJ8`
   - `GOOGLE_SERVICE_ACCOUNT_JSON` = the whole JSON key (one line)
4. (optional) repo variable `MAX_PER_CHANNEL` — 0 or unset = every upload.
5. Run the workflow manually once (Actions → sync → Run workflow), confirm `Combined` fills.

Notes: GitHub runners are often throttled by YouTube; if a channel comes back empty, re-run
or lower `MAX_PER_CHANNEL`. The job timeout is 350 min (actions cap is 6 h).

Sync contract (see `AI_BE_RULES.md`): incremental merge, metadata refresh, `exclude`
filtering, dedup by `video_id`, counts never written back.

## 3. First-run checklist

1. script.google.com → New project → paste `tools/init_sheets.gs` → run `initDedekSheets`
   once (standalone script; opens the sheet via the `SHEET_ID` constant). It creates
   `Video`, `Channel`, `Exclude`, `Combined` with headers and sets link sharing.
2. Add a few URLs to `Video` (and/or channels to `Channel`).
3. Run the sync workflow once; confirm `Combined` fills.
4. Open the Pages URL; the app should fetch the CSV and play.

(`Combined` header must stay: `video_id, video_url, title, channel_id, channel_name, source, published_at, updated_at`.)

## 4. Definition of done for a deploy

1. `https://dedek.tantua.com/` returns 200 and loads the app.
2. Video plays; next/prev/replay work.
3. `Combined` changes are visible after Update List (no page cache).
4. No console errors (YouTube iframe warnings excepted).

## Future Rules

Append new rules below as sections; do not rewrite history.