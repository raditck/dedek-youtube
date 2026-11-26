# Original Request

<!-- Paste your request verbatim below. Do not summarize, do not reformat.
     Preserve code blocks, payloads, error messages, URLs, etc. exactly.
     A top-level "NEW TASK" line is deprecated — this section is the source material. -->

i want to make index.html
containing of youtube videos
the playlist is from google spreadsheet
the google spreadsheet will be shared to public
spreadsheet will consist of 2 sheet
video and channel
video sheet is link of youtube video embed or youtube video page url
channel sheet is link of youtube channel url
while the index.html will only see video, and some buttons : next, prev, repeat this video
only 1 page, and will always play new video (randomly) from the logic when previous video ended
prev button should show previous video being shown, so we might need to save the video link array as history
maybe show history section too
channel inside channel sheet is a channel of which we will get a random video out of them
should not show the same video, always show different video, until all video is played, then the same video legit to be played again

nocodeyet tellme askme

Spreadsheet: https://docs.google.com/spreadsheets/d/1OTAoHRg0ijCUS9YdZG2Vl8a4WsaadiwAnLHko3LWEJ8/edit#gid=1521122054

# Execution Plan

<!-- Fill during Planning. Group related work; no micro-tasks. -->

- [x] 1. Re-analyze repo + shared spec; scope locked to a single `index.html`.
- [x] 2. Rebuild as ONE file: inline CSS + JS in `index.html`; delete all extra app files.
- [x] 3. Data layer: fetch `Combined` CSV, parse + normalize, dedup by `video_id`.
- [x] 4. `localStorage` `dy.v1` state model (pool, counts, timeline, cursor, current, position).
- [x] 5. Playback engine: strict lowest-count, no consecutive duplicate, all +1 / 0 rules, average count for new videos.
- [x] 6. Player UI: YouTube IFrame API, swipe + keyboard, resume position, autoplay/start gate.
- [x] 7. Drawers: history/all-videos/search, settings, empty state, confirmations.
- [x] 8. Spreadsheet prep: `tools/init_sheets.gs` (paste into Apps Script, run once) creates/headers `Video`, `Channel`, `Exclude`, `Combined` and sets link sharing.
- [x] 9. Daily sync: GitHub Actions + yt-dlp — `tools/sync.py` + `.github/workflows/sync.yml` (user chose C).
- [ ] 10. Deploy: GitHub Pages + `dedek.tantua.com`, HTTPS.
- [ ] 11. Verify manually (play/next/prev/repeat/search/settings, reload persistence) and record results.

# Progress

<!-- Append analysis findings here AS YOU GO — any byte change resets the
     goal-loop stall counter, so planning never silently stalls. -->

- Read full ChatGPT share spec (153 msgs) via chatgpt-share-fetch skill: `.pi/skills/chatgpt-share-fetch`.
- Design already debated and locked in that share; consolidated decisions below.
- RESOLVED: `.ai/` was is a stale copy of the "odrive" (Laravel/cPanel) project. Rewritten for dedek-youtube: AGENT/FE/BE/DEPLOYMENT/PROMPTS docs now describe a static single-file app. `.pi/` needed no change (generic goal-loop + share-fetch skill).
- Live repo state: `dedek-youtube/` empty; root has only `.ai/` and `.pi/`. No package/build tooling. Target = static files.
- Spreadsheet (live check via anonymous gviz/htmlview): title "dedek-youtube", tabs `Video` (gid 0), `Channel` (gid 1011004849), `Combined` (gid 1521122054). ALL EMPTY (no header row). No `exclude` tab. Readable anonymously; not yet published-to-web.

Confirmed decisions (from share):
- Channels: retrieve ALL uploads; no YouTube Data API key -> yt-dlp.
- Pool = `video` sheet + all channel uploads, dedup by YouTube video_id (one record, `source` lists origins).
- Selection: strict lowest play-count, random among ties, never same video twice in a row unless it is the only one.
- Count rules: new selection +1, swipe-next +1, swipe-prev via history +1, replay 0, search-click +1. New video on Update List inherits AVERAGE play count (decimals kept).
- Removed/excluded video: drop from active pool, KEEP play count + history; if playing now, let it finish.
- Nav: reels-style vertical swipe + keyboard Up/Down(prev/next), Space, R(repeat), H(history), F(fullscreen).
- History drawer: side panel, newest-first, thumbnail+title+channel+count, cap 100 events; plus "All Videos" view + search over title/channel; click plays now +1.
- Unplayable video: auto-skip, no blacklist, no count bump, stays in library.
- Empty state: message + Retry + Update List.
- Settings drawer: Refresh List (reset local stats), Update List (sync pool, preserve stats), Reset counts, Reset history, total videos, last sync; destructive actions need confirm.
- Startup: restore last video+position immediately (from localStorage), fetch CSV in background. Devices independent (A).
- Data access: published `Combined` CSV (no Apps Script endpoint).
- Combined columns: video_id, video_url, title, channel_id, channel_name, source, published_at, updated_at.
- Sync: GitHub Actions + yt-dlp (`tools/sync.py`, `.github/workflows/sync.yml`); all uploads, no YouTube API key.
- Host: GitHub Pages + custom domain `dedek.tantua.com` (unused), HTTPS. PWA DROPPED: a service worker cannot be inlined into a single file.
- Visual: responsive Shorts-style mobile / centered desktop; adaptive aspect ratio, no crop.
- No channel filter.

Open items / corrections (2026-11-26):
- SCOPE CORRECTION from user: "only need index.html as project files". Consolidated everything into `index.html`; deleted `assets/`, `icons/`, `manifest.webmanifest`, `sw.js`, `tools/`, `tests/`, `.github/`, `package.json`, `requirements.txt`, `CNAME`.
- DECISION: user chose **C** — allow exactly two extra files: `tools/sync.py` + `.github/workflows/sync.yml` (yt-dlp, all uploads, no API key). Deps installed inline in the workflow, so no `requirements.txt`.
- Remaining deleted: `assets/`, `icons/`, `manifest.webmanifest`, `sw.js`, `tests/`, `package.json`, `requirements.txt`, `CNAME`.
- Spreadsheet: run `tools/init_sheets.gs` in Apps Script once (creates `Video`, `Channel`, `Exclude`, `Combined` + headers + link sharing).
- Done: single-file app implements CSV load, localStorage `dy.v1`, selection/count rules, history drawer + search, settings, empty state, keyboard + swipe.

# Verification

(pending manual run — see AI_TASK # Verification)

- `node --check` on the inlined script: OK.
- `index.html` is one file; no extra app files remain.

# Task State

Current Phase:

- Waiting Approval

Current Step:

- Single-file `index.html` implemented. Awaiting the daily-sync decision (A/B/C) and approval to finish sheet prep + deploy.

Last Completed Step:

- Consolidated the whole app into `index.html`; rewrote `.ai/` docs for dedek-youtube; verified inlined JS with `node --check`.

Next Step:

- Remaining plan items 10, 11: Pages/domain + manual verify. Sheet prep now handled by `tools/init_sheets.gs`; set repo secrets for the sync.

---

Planning contract (agent):

1. Fill `# Execution Plan` with an implementation-oriented checklist.
2. Append analysis findings to `# Progress` as you go — never leave long silent stretches.
3. Set `Current Phase: - Waiting Approval` and stop. Never modify code before approval.
4. On approval: execute all unchecked tasks without stopping between them, then verify and set `Current Phase: - Complete` (or `Blocked`).
5. Never restructure this file's sections; only edit content inside them.
