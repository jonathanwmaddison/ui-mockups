#!/usr/bin/env -S uv run --quiet --with pillow python
"""Render a mocked Claude Code session GIF demoing the ui-mockups skill.

Output: <repo>/assets/demo.gif
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "assets" / "demo.gif"
RESULT_IMG = REPO / "mockups" / "demo-claude-code-flow" / "mockup-2.png"

W, H = 1024, 640
BG = (11, 13, 16)
SURFACE = (21, 24, 29)
BORDER = (31, 35, 42)
FG = (230, 232, 235)
MUTED = (138, 143, 152)
CLAY = (217, 119, 87)
GREEN = (166, 227, 161)

FONT_MONO = "/System/Library/Fonts/SFNSMono.ttf"

f_user = ImageFont.truetype(FONT_MONO, 18)
f_sys = ImageFont.truetype(FONT_MONO, 16)
f_label = ImageFont.truetype(FONT_MONO, 13)


def base_frame() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    pad = 32
    win = (pad, pad, W - pad, H - pad)
    d.rounded_rectangle(win, radius=12, fill=SURFACE, outline=BORDER, width=1)

    # title bar
    bar_h = 36
    bar = (win[0], win[1], win[2], win[1] + bar_h)
    d.rounded_rectangle(bar, radius=12, fill=SURFACE)
    d.line([(win[0], win[1] + bar_h), (win[2], win[1] + bar_h)], fill=BORDER, width=1)
    cy = win[1] + bar_h // 2
    for i, cx in enumerate([win[0] + 18, win[0] + 34, win[0] + 50]):
        d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(60, 64, 72))
    title = "Claude Code"
    tw = d.textlength(title, font=f_label)
    d.text(((W - tw) / 2, cy - 8), title, font=f_label, fill=MUTED)

    return img


def draw_user_input(img: Image.Image, text: str, cursor: bool) -> None:
    d = ImageDraw.Draw(img)
    pad = 32
    bar_h = 36
    x = pad + 24
    y = pad + bar_h + 24

    d.text((x, y), ">", font=f_user, fill=CLAY)
    d.text((x + 22, y), text, font=f_user, fill=FG)
    if cursor:
        tw = d.textlength(text, font=f_user)
        cx = x + 22 + tw + 2
        d.rectangle((cx, y + 2, cx + 9, y + 22), fill=FG)


def draw_user_bubble(img: Image.Image, text: str) -> int:
    d = ImageDraw.Draw(img)
    pad = 32
    bar_h = 36
    x = pad + 24
    y = pad + bar_h + 24
    tw = d.textlength(text, font=f_user)
    box = (x, y - 6, x + 22 + tw + 16, y + 28)
    d.rounded_rectangle(box, radius=8, fill=(28, 32, 38), outline=BORDER, width=1)
    d.text((x + 12, y), text, font=f_user, fill=FG)
    return box[3] + 18


def draw_assistant_lines(img: Image.Image, y0: int, lines: list[tuple[str, str]]) -> int:
    """lines: list of (kind, text). kind in {'launch','muted','mono','done'}"""
    d = ImageDraw.Draw(img)
    pad = 32
    x = pad + 24
    y = y0
    for kind, text in lines:
        if kind == "launch":
            d.ellipse((x + 2, y + 8, x + 10, y + 16), fill=CLAY)
            d.text((x + 22, y), text, font=f_sys, fill=FG)
        elif kind == "muted":
            d.text((x + 22, y), text, font=f_sys, fill=MUTED)
        elif kind == "mono":
            d.text((x + 22, y), text, font=f_sys, fill=FG)
        elif kind == "done":
            d.text((x + 2, y), "✓", font=f_sys, fill=GREEN)
            d.text((x + 22, y), text, font=f_sys, fill=FG)
        y += 26
    return y


def paste_result(img: Image.Image, y0: int, alpha: float) -> None:
    if alpha <= 0:
        return
    if not RESULT_IMG.is_file():
        return
    src = Image.open(RESULT_IMG).convert("RGB")
    # tight crop on just the settings card (skips the arrow + dark padding)
    sw, sh = src.size
    src = src.crop((int(sw * 0.50), int(sh * 0.18), int(sw * 0.97), int(sh * 0.82)))
    # fit into available space
    pad = 32
    avail_w = W - 2 * pad - 80
    avail_h = H - pad - y0 - 40
    ratio = min(avail_w / src.width, avail_h / src.height)
    nw, nh = max(1, int(src.width * ratio)), max(1, int(src.height * ratio))
    src = src.resize((nw, nh), Image.LANCZOS)

    # blend with bg using alpha
    bg = Image.new("RGB", (nw, nh), SURFACE)
    blended = Image.blend(bg, src, alpha)

    px = (W - nw) // 2
    py = y0 + 4
    img.paste(blended, (px, py))

    d = ImageDraw.Draw(img)
    border_alpha = int(alpha * 80)
    d.rectangle((px - 1, py - 1, px + nw, py + nh), outline=BORDER, width=1)


def build_frames() -> list[Image.Image]:
    frames: list[Image.Image] = []
    user_text = 'mock up a settings page in our style'

    # 1. empty input with blinking cursor — 8 frames
    for i in range(8):
        f = base_frame()
        draw_user_input(f, "", cursor=(i % 4 < 2))
        frames.append(f)

    # 2. typewriter (varied speed)
    for n in range(1, len(user_text) + 1):
        f = base_frame()
        draw_user_input(f, user_text[:n], cursor=True)
        # repeat some frames for "thinking" pauses on spaces
        repeat = 2 if user_text[n - 1] == " " else 1
        for _ in range(repeat):
            frames.append(f)

    # 3. brief hold after typing — 4 frames
    for i in range(4):
        f = base_frame()
        draw_user_input(f, user_text, cursor=(i % 4 < 2))
        frames.append(f)

    # 4. commit to bubble + assistant lines appear sequentially
    assistant = [
        ("launch", "Launching skill: ui-mockups"),
        ("muted", "Reading mockups/STYLEGUIDE.md..."),
        ("mono", "Generating 3 mockups..."),
    ]

    # bubble appears, no assistant lines yet — 3 frames
    for _ in range(3):
        f = base_frame()
        draw_user_bubble(f, user_text)
        frames.append(f)

    # add assistant lines one at a time
    for k in range(1, len(assistant) + 1):
        for _ in range(4):
            f = base_frame()
            y_after = draw_user_bubble(f, user_text)
            draw_assistant_lines(f, y_after, assistant[:k])
            frames.append(f)

    # 5. result fades in — 8 frames
    for i in range(1, 9):
        alpha = i / 8
        f = base_frame()
        y_after = draw_user_bubble(f, user_text)
        y_after = draw_assistant_lines(f, y_after, assistant)
        paste_result(f, y_after, alpha)
        frames.append(f)

    # 6. done line appears, hold longer so the result is readable — 40 frames (~3.4s)
    full = assistant + [("done", "Wrote mockups/settings-page/mockup-1.png")]
    for _ in range(40):
        f = base_frame()
        y_after = draw_user_bubble(f, user_text)
        y_after = draw_assistant_lines(f, y_after, full)
        paste_result(f, y_after, 1.0)
        frames.append(f)

    return frames


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames = build_frames()
    print(f"rendering {len(frames)} frames -> {OUT}")
    # ~12 fps
    palette_frames = [f.convert("P", palette=Image.ADAPTIVE, colors=128) for f in frames]
    palette_frames[0].save(
        OUT,
        save_all=True,
        append_images=palette_frames[1:],
        duration=85,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
