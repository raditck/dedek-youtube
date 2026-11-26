#!/usr/bin/env python3
"""Daily sync: discover every channel upload with yt-dlp, merge into the Combined sheet.

Secrets/env:
  SPREADSHEET_ID                required
  GOOGLE_SERVICE_ACCOUNT_JSON   required (raw JSON string)
  MAX_PER_CHANNEL               optional, 0 = all uploads (default 0)
"""
import json, os, re, subprocess, sys, urllib.request
from datetime import datetime, timezone

from google.oauth2 import service_account
from googleapiclient.discovery import build

SID = os.environ["SPREADSHEET_ID"]
MAX = int(os.environ.get("MAX_PER_CHANNEL", "0"))
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d")
HEAD = ["video_id", "video_url", "title", "channel_id", "channel_name",
        "source", "published_at", "updated_at"]

creds = service_account.Credentials.from_service_account_info(
    json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]),
    scopes=["https://www.googleapis.com/auth/spreadsheets"],
)
svc = build("sheets", "v4", credentials=creds, cache_discovery=False)


def read(sheet):
    r = svc.spreadsheets().values().get(
        spreadsheetId=SID, range=f"'{sheet}'!A:Z").execute()
    return r.get("values", [])


def write(sheet, rows):
    svc.spreadsheets().values().clear(
        spreadsheetId=SID, range=f"'{sheet}'!A:H").execute()
    svc.spreadsheets().values().update(
        spreadsheetId=SID, range=f"'{sheet}'!A1", valueInputOption="RAW",
        body={"values": rows}).execute()


VID = re.compile(r"(?:v=|/shorts/|/live/|/embed/|youtu\.be/)([A-Za-z0-9_-]{11})")


def vid(s):
    s = (s or "").strip()
    m = VID.search(s)
    if m:
        return m.group(1)
    return s if re.fullmatch(r"[A-Za-z0-9_-]{11}", s) else None


def oembed(v):
    u = ("https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v="
         f"{v}&format=json")
    try:
        with urllib.request.urlopen(u, timeout=15) as r:
            d = json.load(r)
            return d.get("title", ""), d.get("author_name", "")
    except Exception:
        return "", ""


def uploads(url):
    url = url.strip()
    if url.endswith(("/videos", "/streams", "/shorts")):
        return url
    return url.rstrip("/") + "/videos"


def ytdlp(url):
    cmd = ["yt-dlp", "--flat-playlist", "--dump-single-json", "--no-warnings",
           "--ignore-errors", "--skip-download"]
    if MAX:
        cmd += ["--playlist-end", str(MAX)]
    cmd.append(url)
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    except subprocess.TimeoutExpired:
        print(f"[warn] timeout {url}", file=sys.stderr)
        return []
    if not out.stdout.strip():
        print(f"[warn] no output {url}: {out.stderr[-300:]}", file=sys.stderr)
        return []
    try:
        return json.loads(out.stdout).get("entries") or []
    except Exception as e:
        print(f"[warn] parse {url}: {e}", file=sys.stderr)
        return []


def main():
    pool = {r[0]: r for r in read("Combined")[1:] if r and r[0]}
    print(f"existing: {len(pool)}")

    exclude = set()
    for r in read("Exclude"):
        v = vid(r[0]) if r and r[0] else None
        if v:
            exclude.add(v)

    for r in read("Video"):
        v = vid(r[0]) if r and r[0] else None
        if not v:
            continue
        title, author = oembed(v)
        pool[v] = [v, f"https://www.youtube.com/watch?v={v}", title, "",
                   author, "manual", "", NOW]

    for r in read("Channel"):
        url = r[0].strip() if r and r[0] else ""
        if not url:
            continue
        entries = ytdlp(uploads(url))
        print(f"channel {url}: {len(entries)}")
        for e in entries:
            v = e.get("id")
            if not v:
                continue
            pool[v] = [v, f"https://www.youtube.com/watch?v={v}",
                       e.get("title", ""), e.get("channel_id", ""),
                       e.get("channel") or e.get("uploader", "") or "",
                       url, e.get("upload_date", "") or "", NOW]

    for v in exclude:
        pool.pop(v, None)

    write("Combined", [HEAD] + [pool[v] for v in sorted(pool)])
    print(f"written: {len(pool)} videos, excluded: {len(exclude)}")


if __name__ == "__main__":
    main()