# AI Agent Rules

## Project

dedek-youtube — a single-file (`index.html`) reels-style YouTube player. Video metadata comes
from a public Google Spreadsheet; playback stats live in browser `localStorage`. No backend,
no build step, no npm, no framework.

## Source of Truth

`.ai/AI_TASK.md` is the only task file. Always reconstruct state from it, never from
conversation history. The user's Original Request inside it is immutable and authoritative.

## Deliverable — one file

The shipped artifact is **`index.html`** only. CSS and JS are inline. No `assets/`, no
bundler, no `package.json`, no external requests except YouTube + the Google Sheet CSV.

Anything that cannot physically live in `index.html` must be justified in `AI_TASK.md`:

- Google Sheet (data) — owned by the user, not a repo file.
- `.github/workflows/sync.yml` + `tools/sync.py` — daily yt-dlp sync (user chose this over a
  sheet-bound Apps Script). `tools/init_sheets.gs` is a paste-once helper, never deployed.
- GitHub Pages config (domain, HTTPS) — repo settings, not a file.

Known hard limit: a PWA service worker **cannot** be inlined, so offline app-shell caching
is intentionally out of scope unless the user explicitly allows `sw.js` back.

## Rules Files

- Editing `index.html` (markup, CSS, JS): read and follow `.ai/AI_FE_RULES.md`.
- Data contract, playback algorithm, storage keys, sync: read and follow `.ai/AI_BE_RULES.md`.
- Hosting, domain, sync: read and follow `.ai/AI_DEPLOYMENT_GUIDE.md`.
Those files are append-only; new rules go below existing ones.

## Preserve User Input

Everything the user writes inside the Original Request section is immutable. Never summarize,
rewrite, shorten, or reformat it — including code, payloads, file trees, and configuration.

## Task File Layout (fixed — from `.ai/AI_TASK.example.md`)

- `# Original Request` — verbatim user input; never modified after creation.
- `# Execution Plan` — checklist filled during Planning.
- `# Progress` — append findings as work happens (any file write resets the stall counter).
- `# Verification` — commands + results.
- `# Task State` — Current Phase + step recovery info.

Never rename, reorder, or remove sections. Phases: `Planning`, `Waiting Approval`,
`Implementing`, `Verifying`, `Complete`, `Blocked`.

## New Task Detection

New task = user says "make goal"/"start" pointing at `.ai/AI_TASK.md`. When the file has a
filled Original Request and an empty plan (`Current Phase: - Planning`):

1. Preserve the request verbatim.
2. Analyze the repository.
3. Fill the Execution Plan (implementation-oriented, grouped, concise).
4. Append findings to `# Progress` as you go.
5. Set `Current Phase: - Waiting Approval` and stop. No code changes during planning.

## Execution

After approval ("Approved"/"Proceed"/"Start"/"Continue"):

1. Execute all unchecked tasks without stopping between them.
2. Verify per plan; fix and repeat until green.
3. Update `.ai/AI_TASK.md` before/after milestones.
4. Set `Current Phase: - Complete` (or `Blocked` with blocker + required user action).

## Clarification Gate

If objective, requirements, expected behavior, or environment facts are unclear: STOP, ask
concise questions, do not guess, do not write code. Conflicts between request and repository
state → stop, explain, ask which wins.

## Anti-Guessing / Evidence

Do not make technical claims without evidence. Prefer repository code, official docs,
retrieved docs. State uncertainty when evidence is missing.

## Infinite Loop Prevention

If the same failure repeats 3 cycles without progress: STOP, summarize, ask. If blocked:
`Current Phase: Blocked` with blocker + required user action.

## Definition of Done

All plan items done · `index.html` loads and plays · selection rules hold · data contract
matches the sheet · no console errors · verification recorded in `AI_TASK.md`.