#!/usr/bin/env python3
"""Add LinkedIn posts to the News page.

Each post is saved to data/news.json and its photo is downloaded to
static/images/news/, so the News page keeps working even after LinkedIn's
image links expire.

Usage:
    # Add one or more posts (copy the link from the post's "..." menu -> "Copy link to post")
    python scripts/add_news.py https://www.linkedin.com/feed/update/urn:li:activity:7439976849226616832

    # Re-import every post a SociableKit widget knows about
    python scripts/add_news.py --sociablekit 25665425

Only uses the Python standard library.
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "news.json"
IMAGE_DIR = ROOT / "static" / "images" / "news"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def post_id(url):
    m = re.search(r"urn:li:(?:activity|ugcPost|share):(\d+)", url) or re.search(r"(\d{19})", url)
    if not m:
        raise ValueError(f"Could not find a post id in {url}")
    return m.group(1)


def resolve(url):
    """Expand lnkd.in short links and drop tracking query strings."""
    if "lnkd.in/" in url:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            url = resp.geturl()
    return url.split("?")[0]


def parse_post(url):
    """Return dict(id, date, text, image_url, link) for a public LinkedIn post."""
    url = resolve(url)
    page = fetch(url).decode("utf-8", "replace")
    data = None
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        try:
            candidate = json.loads(block)
        except json.JSONDecodeError:
            continue
        if candidate.get("@type") in ("SocialMediaPosting", "VideoObject"):
            data = candidate
            break
    if data is None:
        raise RuntimeError(f"No public post data found at {url} (is the post public?)")

    image_url = None
    og = re.search(r'<meta property="og:image" content="([^"]+)"', page)
    if og:
        image_url = html.unescape(og.group(1))
    # Posts without a photo get LinkedIn's generic placeholder or an avatar; skip those.
    if image_url and ("static.licdn.com" in image_url or "profile-displayphoto" in image_url
                      or "company-logo" in image_url):
        image_url = None

    return {
        "id": post_id(url),
        "date": (data.get("datePublished") or data.get("uploadDate") or "")[:10],
        "text": (data.get("articleBody") or data.get("description") or data.get("headline") or "").strip(),
        "image_url": image_url,
        "link": url,
    }


def download_image(item_id, image_url):
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = IMAGE_DIR / f"{item_id}.jpg"
    path.write_bytes(fetch(image_url))
    return f"images/news/{path.name}"


def load():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []


def save(items):
    items.sort(key=lambda x: x.get("date", ""), reverse=True)
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n")


def text_key(text):
    """Same post can appear under different ids (activity/share/ugcPost); match on text."""
    return re.sub(r"\W+", "", text).lower()[:120]


def add(urls):
    items = load()
    by_id = {i["id"]: i for i in items}
    by_text = {text_key(i["text"]): i for i in items if i.get("text")}
    for n, url in enumerate(urls):
        if n:
            time.sleep(1.5)  # be polite to LinkedIn
        try:
            post = parse_post(url)
        except Exception as e:  # keep going so one bad link doesn't stop the rest
            print(f"  ! skipped {url}: {e}", file=sys.stderr)
            continue
        existing = by_id.get(post["id"]) or by_text.get(text_key(post["text"]))
        entry = existing or {"id": post["id"]}
        entry.update(date=post["date"], text=post["text"], link=post["link"])
        if post["image_url"]:
            try:
                entry["image"] = download_image(entry["id"], post["image_url"])
            except Exception as e:
                print(f"  ! could not download image for {url}: {e}", file=sys.stderr)
        if existing is None:
            items.append(entry)
        by_id[entry["id"]] = entry
        by_text[text_key(entry["text"])] = entry
        print(f"  ✓ {post['date']}  {'[photo] ' if entry.get('image') else '[no photo]'} {post['text'][:60]!r}")
    save(items)
    print(f"Saved {len(items)} news items to {DATA_FILE.relative_to(ROOT)}")


def sociablekit_urls(embed_id):
    feed = json.loads(fetch(f"https://data.accentapi.com/feed/{embed_id}.json"))
    return [p["post_url"] for p in feed.get("posts", []) if p.get("post_url")]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("urls", nargs="*", help="LinkedIn post links")
    parser.add_argument("--sociablekit", metavar="EMBED_ID", help="import all posts from a SociableKit feed")
    args = parser.parse_args()

    urls = list(args.urls)
    if args.sociablekit:
        urls += sociablekit_urls(args.sociablekit)
    if not urls:
        parser.error("give at least one LinkedIn post link")
    add(urls)


if __name__ == "__main__":
    main()
