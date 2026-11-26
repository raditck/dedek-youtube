#!/usr/bin/env python3
"""Extract full message text from a ChatGPT shared conversation.

Usage: python extract.py <share-url-or-html-file> [output.md]

ChatGPT share pages embed conversation data as an escape-encoded
turbo-stream flat array inside streamController.enqueue("...") chunks.
Stdlib only.
"""
import json
import sys
import urllib.request

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}
DEFAULT_OUT = "conversation_extracted.md"


def load_source(src):
    if src.startswith("http"):
        req = urllib.request.Request(src, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "ignore")
    return open(src, encoding="utf-8", errors="ignore").read()


def enqueue_chunks(html):
    """Yield string payloads of streamController.enqueue("...") calls."""
    needle = '.enqueue("'
    i = 0
    while True:
        j = html.find(needle, i)
        if j < 0:
            return
        k = j + len(needle)
        buf = []
        esc = False
        while True:
            ch = html[k]
            if esc:
                buf.append("\\")
                buf.append(ch)
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                break
            else:
                buf.append(ch)
            k += 1
        yield "".join(buf)
        i = k


def decode_chunk(s):
    """Unescape the JS-string payload back into JSON text (UTF-8 safe)."""
    for candidate in (s, json.loads('"' + s.replace("\n", "\\n") + '"')):
        try:
            return json.loads(candidate)
        except Exception:
            continue
    raise ValueError("chunk is not valid JSON after unescaping")


def make_resolver(flat):
    memo = {}

    def resolve(idx):
        if not isinstance(idx, int) or idx < 0:
            return None if isinstance(idx, int) else idx
        if idx in memo:
            return memo[idx]
        v = flat[idx]
        if isinstance(v, dict):
            out = {}
            memo[idx] = out
            for k, val in v.items():
                rk = flat[int(k[1:])] if k.startswith("_") and k[1:].isdigit() else k
                out[rk] = resolve(val) if isinstance(val, int) and val >= 0 else val
            return out
        if isinstance(v, list):
            out = []
            memo[idx] = out
            for e in v:
                out.append(resolve(e) if isinstance(e, int) and e >= 0 else e)
            return out
        return v

    return resolve


def find_conversation(obj, seen=None):
    if seen is None:
        seen = set()
    if id(obj) in seen:
        return None
    seen.add(id(obj))
    if isinstance(obj, dict):
        if isinstance(obj.get("linear_conversation"), list):
            return obj["linear_conversation"]
        for v in obj.values():
            hit = find_conversation(v, seen)
            if hit is not None:
                return hit
    elif isinstance(obj, list):
        for v in obj:
            hit = find_conversation(v, seen)
            if hit is not None:
                return hit
    return None


def extract(src, out_path):
    html = load_source(src)
    flat = None
    for chunk in enqueue_chunks(html):
        if "linear_conversation" in chunk:
            flat = decode_chunk(chunk)
            break
    if flat is None:
        sys.exit("error: no chunk with linear_conversation (bad HTML or challenge page)")

    resolve = make_resolver(flat)
    root = resolve(0)
    convo = find_conversation(root)
    if not convo:
        sys.exit("error: linear_conversation not found in resolved data")

    lines = []
    for node in convo:
        msg = node.get("message") if isinstance(node, dict) else None
        if not msg:
            continue
        role = msg.get("author", {}).get("role", "?")
        content = msg.get("content", {})
        text = "\n".join(p for p in content.get("parts", []) if isinstance(p, str))
        if not text.strip():
            continue
        lines.append("=" * 70)
        lines.append(f"ROLE: {role} ({content.get('content_type', '?')})")
        lines.append("=" * 70)
        lines.append(text)
        lines.append("")

    body = "\n".join(lines)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"messages: {len(convo)}")
    print(f"wrote {len(body)} chars -> {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    extract(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT)
