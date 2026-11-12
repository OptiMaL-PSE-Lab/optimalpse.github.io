#!/usr/bin/env python3
"""Validate author profiles in content/authors/ so broken PRs fail CI.

Checks each content/authors/<name>/_index.md for:
  - parseable YAML front matter
  - required fields (title, first_name, last_name)
  - `authors` containing the folder name
  - `user_groups` values that exist on the People page
  - avatar images that are really JPG/PNG (e.g. not WebP/HEIC renamed to .jpg)
"""
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
AUTHORS_DIR = ROOT / "content" / "authors"
PEOPLE_PAGE = ROOT / "content" / "people" / "index.md"

REQUIRED = ["title", "first_name", "last_name"]
MAX_AVATAR_MB = 10

# Magic-byte signatures for formats Hugo can resize.
SIGNATURES = {
    "jpeg": [b"\xff\xd8\xff"],
    "png": [b"\x89PNG\r\n\x1a\n"],
}
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*(\n|$)", text, re.S)
    if not m:
        raise ValueError("file must start with a '---' front matter block closed by '---'")
    return yaml.safe_load(m.group(1)) or {}


def allowed_groups():
    fm = front_matter(PEOPLE_PAGE)
    for section in fm.get("sections", []):
        if section.get("block") == "people":
            return set(section["content"]["user_groups"])
    raise RuntimeError("could not find the people block in content/people/index.md")


def detect_format(path):
    head = path.read_bytes()[:16]
    for fmt, sigs in SIGNATURES.items():
        if any(head.startswith(s) for s in sigs):
            return fmt
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    if head[4:12] in (b"ftypheic", b"ftypheix", b"ftypmif1"):
        return "heic"
    return "unknown"


def check_profile(folder, groups):
    errors = []
    name = folder.name
    index = folder / "_index.md"

    if not re.fullmatch(r"[a-z0-9-]+", name):
        errors.append(f"folder name '{name}' must be lowercase letters, digits or '-' only")

    if not index.exists():
        return errors + ["missing _index.md"]

    try:
        fm = front_matter(index)
    except (ValueError, yaml.YAMLError) as e:
        return errors + [f"_index.md front matter is invalid: {e}"]

    for field in REQUIRED:
        if not str(fm.get(field) or "").strip():
            errors.append(f"missing required field '{field}'")

    # The site's own example profile ('admin') has no `authors` field.
    if name != "admin":
        authors = fm.get("authors") or []
        if name not in authors:
            errors.append(f"'authors' must contain '{name}' (the folder name), found {authors}")

    user_groups = fm.get("user_groups") or []
    if not user_groups:
        errors.append("'user_groups' is empty, so you won't appear on the People page")
    for g in user_groups:
        if g not in groups:
            errors.append(
                f"unknown user_group '{g}'. Use one of: " + ", ".join(sorted(groups))
            )

    for img in folder.iterdir():
        if not img.name.lower().startswith("avatar"):
            continue
        if img.suffix.lower() not in IMAGE_EXTS:
            errors.append(f"{img.name}: avatar must be a .jpg or .png file")
            continue
        # Hugo sniffs JPG vs PNG itself, but can't read WebP/HEIC renamed to .jpg.
        actual = detect_format(img)
        if actual not in SIGNATURES:
            errors.append(
                f"{img.name}: file is actually {actual.upper()}, not JPG/PNG. "
                "Re-save/export it as a real JPG or PNG"
            )
        size_mb = img.stat().st_size / 1e6
        if size_mb > MAX_AVATAR_MB:
            print(f"::warning file=content/authors/{name}/{img.name}::"
                  f"{img.name} is {size_mb:.1f} MB; please shrink it below {MAX_AVATAR_MB} MB")

    return errors


def main():
    groups = allowed_groups()
    failed = False
    for folder in sorted(p for p in AUTHORS_DIR.iterdir() if p.is_dir()):
        errors = check_profile(folder, groups)
        for e in errors:
            # GitHub Actions annotation, shown inline on the PR
            print(f"::error file=content/authors/{folder.name}/_index.md::{folder.name}: {e}")
        failed = failed or bool(errors)
    if failed:
        sys.exit(1)
    print("All profiles look good.")


if __name__ == "__main__":
    main()
