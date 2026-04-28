#!/usr/bin/env -S uv run --quiet --with playwright python
"""Capture a full-page screenshot of a running app for use as a style reference.

Usage:
    capture_screenshot.py <url> [--out path.png] [--width 1440] [--height 900] [--wait 1000]

Requires `playwright install chromium` to have been run once.
If <url> is actually a file path that exists, just copies it to --out.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="URL to screenshot, or path to existing PNG")
    ap.add_argument("--out", default=None)
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--wait", type=int, default=1000, help="ms to wait after load")
    args = ap.parse_args()

    if args.out:
        out = Path(args.out)
    else:
        fd, name = tempfile.mkstemp(prefix="screenshot-", suffix=".png")
        out = Path(name)

    src = Path(args.url)
    if src.is_file():
        shutil.copyfile(src, out)
        print(out)
        return 0

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "error: playwright not installed. run once: "
            "uv tool install playwright && playwright install chromium",
            file=sys.stderr,
        )
        return 2

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": args.width, "height": args.height})
        page = ctx.new_page()
        page.goto(args.url, wait_until="networkidle")
        page.wait_for_timeout(args.wait)
        page.screenshot(path=str(out), full_page=True)
        browser.close()

    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
