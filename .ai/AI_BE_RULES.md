# AI Data & Sync Rules

There is no server. The rules here define the data contract, the playback algorithm, browser
storage, and the external sync. Append-only.

## Spreadsheet

ID: `1OTAoHRg0ijCUS9YdZG2Vl8a4WsaadiwAnLHko3LWEJ8`

Sheet names are **case-sensitive** and must match the existing tabs exactly:

| Sheet      | Role                        | Columns |
| ---------- | --------------------------- | ------- |
| `Video`    | manual video URLs           | `url` (or full URL list) |
| `Channel`  | channel URLs                | `url` (any format: `@handle`, `/channel/UC..`, `/c/..`, `/user/..`) |
| `Exclude`  | ids/URLs never to be played | `video_id` |
| `Combined` | generated pool (read by app)| `video_id, video_url, title, channel_id, channel_name, source, published_at, updated_at` |

`index.html` reads `Combined` as CSV (CORS-enabled, no key):

```
https://docs.google.com/spreadsheets/d/1OTAoHRg0ijCUS9YdZG2Vl8a4WsaadiwAnLHko3LWEJ8/gviz/tq?tqx=out:csv&sheet=Combined
```

Never write to the sheet from the browser.

## Playback algorithm (authoritative)

- Active pool = all `Combined` rows (deduped by `video_id`).
- Pick: find the minimum play count; randomly choose among videos tied at that minimum;
  never pick the current video while another candidate exists. If only one video exists,
  it may repeat.
- Count `+1`: new selection, next (swipe up / `ArrowDown`), previous (swipe down / `ArrowUp`),
  click in History/All-Videos.
- Count `0`: replay current (`R`), initial restore of the last video on page load.
- Video ends → behave like next (`+1`).
- Unplayable video (private / embed-disabled / removed): skip immediately, do NOT increment
  again, keep it in the library, no blacklist.
- Update List: keep counts of surviving videos; a newly appearing video inherits the **average**
  of the existing counts (decimals kept); removed videos keep their count + history but leave
  the active pool.
- Refresh List: clears all local playback data and reloads the pool (counts start at 0).

## localStorage contract (key `dy.v1`)

```
version    1
videos     { [id]: { id, url, title, channel_id, channel_name, source, published_at, updated_at } }
counts     { [id]: number }   // kept even after a video leaves the pool
timeline   [id, ...]          // chronological play log, max 100
pos        number             // cursor into timeline (prev/next browsing)
current    { id } | null
position   number             // seconds into the current video
sound      boolean
interacted boolean
lastSync   ISO string | null
```

Bump the key (`dy.v2`) if the shape changes; write a migration or reset on mismatch.

## Sync (GitHub Actions + yt-dlp)

Decision: **option C** — exactly two extra repo files are allowed:

- `.github/workflows/sync.yml` — daily cron (03:17 UTC) + manual dispatch.
- `tools/sync.py` — yt-dlp discovery + Sheets write.

Flow (incremental, never destructive of counts):

1. Read existing `Combined` (kept as the base).
2. For each `Channel` URL, `yt-dlp --flat-playlist` on its `/videos` tab (all uploads;
   `MAX_PER_CHANNEL` caps a run). Metadata of known ids is refreshed.
3. For each `Video` URL, fetch title/author via YouTube oEmbed (no yt-dlp call).
4. Drop every id listed in `Exclude`.
5. Rewrite `Combined` (header + rows).

Required GitHub secrets: `SPREADSHEET_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON`. The sheet must be
shared with the service-account email as **Editor**. Optional repo variable
`MAX_PER_CHANNEL` (0 = all).

Never write play counts to the sheet; counts stay in `localStorage`.

## Deploy config

- Sheet ID: `1OTAoHRg0ijCUS9YdZG2Vl8a4WsaadiwAnLHko3LWEJ8`
- `Combined` must stay readable by anyone with the link (for the CSV fetch).

## Testing

No test framework (single file). Validate changes with the manual checklist in
`AI_TASK.md # Verification` and by playing the app locally.

## Future Rules

Append new rules below as sections; do not rewrite history.