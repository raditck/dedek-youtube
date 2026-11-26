---
name: chatgpt-share-fetch
description: Fetch and extract the full message text of a ChatGPT shared conversation (chatgpt.com/share/<id>). Share pages are JS-rendered and defeat plain web fetchers; this skill extracts the embedded conversation data directly. Use whenever the user gives a ChatGPT share link or asks to read, re-read, or analyze a shared ChatGPT conversation.
---

# ChatGPT Share Fetch

Extract all user/assistant messages from a `chatgpt.com/share/<id>` URL into markdown.

## Why not a normal web fetch

The share page renders via JavaScript. Generic fetchers (and most readability extractors) return nothing. The conversation actually ships inside the HTML as an escape-encoded **turbo-stream flat array** inside `streamController.enqueue("...")` script chunks. `scripts/extract.py` decodes that directly. Stdlib only, no dependencies.

## Usage

```bash
python scripts/extract.py <share-url-or-saved-html-file> [output.md]
```

Examples:

```bash
# straight from URL
python scripts/extract.py "https://chatgpt.com/share/6a918c54-7b54-83ec-96de-c6f52893bd74" convo.md

# two-step (use when urllib is blocked by Cloudflare / returns a challenge page)
curl -sL "<url>" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36" -o share.html
python scripts/extract.py share.html convo.md
```

Output: `ROLE: user|assistant|tool` sections in conversation order. Tool/plugin messages read `The output of this plugin was redacted` — that is upstream redaction by ChatGPT, not an extraction failure.

## Health check

A good run prints `messages: N` (N > 0) and writes non-trivial bytes. Run with the known test URL above if extraction ever looks empty.

## Troubleshooting

- `no chunk with linear_conversation`: page HTML changed, or fetch was a challenge/redirect page. Save HTML to a file, `grep -c linear_conversation` it; 0 hits means bad HTML — re-curl with the UA header.
- Mojibake (`Ã—`): never use `unicode_escape` to unescape; the script decodes via `json.loads('"' + chunk + '"')` which preserves UTF-8.
- 403/Cloudflare page: use the curl two-step, or re-save from a real browser (Save As → HTML) and pass the file.
- 0 messages but data parsed: message shape changed; inspect `page['linear_conversation'][0]` keys and adjust the extractor.
