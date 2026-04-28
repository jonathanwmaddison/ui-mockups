#!/usr/bin/env -S uv run --quiet --with openai --with pillow python
"""Generate N UI mockup images using OpenAI gpt-image-2, anchored on a repo's styleguide.

Usage:
    generate_mockups.py \\
        --prompt "settings page with profile, billing, notifications" \\
        --repo /path/to/ui-repo \\
        --styleguide /path/to/STYLEGUIDE.md \\
        [--screenshot /tmp/screenshot.png] \\
        [--count 3] \\
        [--size 1536x1024] \\
        [--slug settings-page]

Reads the API token from ~/.claude/skills/ui-mockups/.token (chmod 600).
Saves images to <repo>/mockups/<slug>/.

The styleguide is a Claude-authored markdown file — see
prompts/styleguide_instructions.md for the format. It is treated as the
source of truth for the visual identity; this script just embeds it into
the image prompt.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path


_DEFAULT_TOKEN_FILE = Path.home() / ".claude" / "skills" / "ui-mockups" / ".token"
TOKEN_FILE = Path(os.environ.get("UI_MOCKUPS_TOKEN_FILE", str(_DEFAULT_TOKEN_FILE)))

# gpt-image-2 size constraints
_MIN_PIXELS = 655_360
_MAX_PIXELS = 8_294_400
_MAX_EDGE = 3840
_MULTIPLE = 16
_MAX_RATIO = 3.0

_EXT_BY_FORMAT = {"png": "png", "jpeg": "jpg", "webp": "webp"}


def parse_size(value: str) -> str:
    if value == "auto":
        return value
    m = re.fullmatch(r"(\d+)x(\d+)", value)
    if not m:
        raise argparse.ArgumentTypeError(
            f"invalid --size {value!r}: expected 'WxH' (e.g. 1536x1024) or 'auto'"
        )
    w, h = int(m.group(1)), int(m.group(2))
    if w % _MULTIPLE or h % _MULTIPLE:
        raise argparse.ArgumentTypeError(
            f"--size {value}: both edges must be multiples of {_MULTIPLE}"
        )
    if max(w, h) > _MAX_EDGE:
        raise argparse.ArgumentTypeError(f"--size {value}: max edge is {_MAX_EDGE}px")
    pixels = w * h
    if pixels < _MIN_PIXELS or pixels > _MAX_PIXELS:
        raise argparse.ArgumentTypeError(
            f"--size {value}: total pixels must be between {_MIN_PIXELS:,} and {_MAX_PIXELS:,}"
        )
    ratio = max(w, h) / min(w, h)
    if ratio > _MAX_RATIO:
        raise argparse.ArgumentTypeError(
            f"--size {value}: aspect ratio must be ≤ {_MAX_RATIO}:1"
        )
    return value


def read_token() -> str | None:
    try:
        t = TOKEN_FILE.read_text(encoding="utf-8").strip()
        return t or None
    except FileNotFoundError:
        return None
    except OSError:
        return None


def slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return (s[:48] or "mockup")


def build_prompt(template_path: Path, styleguide: str, user_prompt: str, has_reference: bool) -> str:
    tpl = template_path.read_text(encoding="utf-8")
    reference_block = (
        "## Style reference\n\nA reference screenshot of the existing app is attached. "
        "Match its visual rhythm, density, and component vocabulary, but render the new screen described below."
        if has_reference else ""
    )
    return (
        tpl.replace("{styleguide}", styleguide.strip())
           .replace("{reference_block}", reference_block)
           .replace("{user_prompt}", user_prompt.strip())
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--styleguide", required=True, help="path to STYLEGUIDE.md")
    ap.add_argument("--screenshot", default=None, help="optional reference image path")
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument(
        "--size",
        default="1536x1024",
        type=parse_size,
        help="WxH (multiples of 16, max edge 3840, ratio ≤ 3:1) or 'auto'",
    )
    ap.add_argument("--slug", default=None)
    ap.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    ap.add_argument(
        "--background",
        default="auto",
        choices=["opaque", "auto"],
        help="gpt-image-2 does not support transparent",
    )
    ap.add_argument(
        "--output-format", default="png", choices=["png", "jpeg", "webp"], dest="output_format"
    )
    ap.add_argument(
        "--output-compression",
        type=int,
        default=None,
        dest="output_compression",
        help="0-100; only applies to jpeg/webp",
    )
    ap.add_argument("--moderation", default="auto", choices=["auto", "low"])
    args = ap.parse_args()

    if args.output_compression is not None:
        if args.output_format == "png":
            print("error: --output-compression only applies to jpeg/webp", file=sys.stderr)
            return 2
        if not 0 <= args.output_compression <= 100:
            print("error: --output-compression must be 0-100", file=sys.stderr)
            return 2

    token = read_token()
    if not token:
        setup = Path(__file__).resolve().parent / "set_token.py"
        print(
            f"error: no token at {TOKEN_FILE}\n"
            f"  fix: in your own terminal (not in Claude Code chat), run:\n"
            f"    python3 {setup}",
            file=sys.stderr,
        )
        return 2

    count = max(1, min(10, args.count))
    repo = Path(args.repo).resolve()
    styleguide_path = Path(args.styleguide).resolve()
    if not styleguide_path.is_file():
        print(f"error: styleguide not found: {styleguide_path}", file=sys.stderr)
        print("hint: have the coding agent author one first using prompts/styleguide_instructions.md", file=sys.stderr)
        return 2
    styleguide = styleguide_path.read_text(encoding="utf-8")

    slug = args.slug or slugify(args.prompt)
    out_dir = repo / "mockups" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    template = Path(__file__).resolve().parent.parent / "prompts" / "mockup_system.md"
    has_ref = bool(args.screenshot and Path(args.screenshot).is_file())
    prompt = build_prompt(template, styleguide, args.prompt, has_ref)

    (out_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    if has_ref:
        ref_dest = out_dir / "reference.png"
        ref_dest.write_bytes(Path(args.screenshot).read_bytes())

    from openai import OpenAI

    client = OpenAI(api_key=token)

    print(f"generating {count} mockup(s) at {args.size} into {out_dir}...", file=sys.stderr)

    common_kwargs: dict = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "n": count,
        "size": args.size,
        "quality": args.quality,
        "background": args.background,
        "output_format": args.output_format,
        "moderation": args.moderation,
    }
    if args.output_compression is not None:
        common_kwargs["output_compression"] = args.output_compression

    if has_ref:
        edit_kwargs = {k: v for k, v in common_kwargs.items() if k != "moderation"}
        with open(args.screenshot, "rb") as f:
            resp = client.images.edit(image=f, **edit_kwargs)
    else:
        resp = client.images.generate(**common_kwargs)

    ext = _EXT_BY_FORMAT[args.output_format]
    written: list[str] = []
    for i, item in enumerate(resp.data, start=1):
        b64 = getattr(item, "b64_json", None)
        if not b64:
            print(f"warning: item {i} has no b64_json; skipping", file=sys.stderr)
            continue
        path = out_dir / f"mockup-{i}.{ext}"
        path.write_bytes(base64.b64decode(b64))
        written.append(str(path))

    if not written:
        print("error: no images returned", file=sys.stderr)
        return 1

    summary = {
        "out_dir": str(out_dir),
        "count": len(written),
        "size": args.size,
        "files": written,
        "reference": str(args.screenshot) if has_ref else None,
        "styleguide": str(styleguide_path),
        "slug": slug,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
