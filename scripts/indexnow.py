#!/usr/bin/env python3
"""Submit URLs to IndexNow (shared by Bing, Yandex, Seznam, Naver). No account needed.

    python3 scripts/indexnow.py            # every URL in sitemap.xml
    python3 scripts/indexnow.py URL [URL]  # just these
"""
import json, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_BASE = "https://hernandez188515-del.github.io/florida-wind-mitigation-directory"
HOST = "hernandez188515-del.github.io"
key_files = [p for p in ROOT.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem)]
if not key_files:
    raise SystemExit("No IndexNow key file (32 hex chars .txt) in the site root")
KEY = key_files[0].stem
urls = sys.argv[1:] or re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text())
body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"{SITE_BASE}/{KEY}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(r.status, r.reason, f"({len(urls)} URLs)")
except urllib.error.HTTPError as e:
    print(e.code, e.reason, e.read().decode()[:300])
    sys.exit(1)
