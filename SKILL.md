---
name: ui-mockups
description: Generate AI image mockups of UI screens that match an existing repo's design language. On first run, scans the repo and authors a `mockups/STYLEGUIDE.md` artifact (color, typography, spacing, components, voice) that lives alongside the code. On subsequent runs, reuses that styleguide to generate N on-brand mockup PNGs via OpenAI gpt-image-2. Use when the user asks for "mockups", "design exploration", "visual variations", or "UI ideas in our style".
---

# ui-mockups

Generate on-brand UI mockup images for a target repo by combining a Claude-authored styleguide with a prompt, optionally anchored by a screenshot of the live app.

## When to invoke

Trigger when the user wants **visual exploration** of a UI before (or instead of) writing code:

- "mock up a settings page in our style"
- "give me 4 visual options for the empty state"
- "what could the new dashboard look like"
- "design exploration for X"

Do **not** invoke for tasks that are really code requests ("build the settings page") — those go to `frontend-design` or `figma-implement-design`. This skill outputs **images**, not code.

## Architecture: two phases

**Phase 1 — Styleguide (one-time per repo, you author it).**
The styleguide is a markdown artifact at `<repo>/mockups/STYLEGUIDE.md` that you write by reading the codebase. It captures color, typography, spacing, radii, shadow language, component vocabulary, and voice in ~600–1500 words of directable prose. It lives in the repo so the user can edit it and it improves with every iteration.

**Phase 2 — Mockup generation (cheap, repeatable).**
A Python script reads the styleguide, optionally a screenshot, and the user's prompt, then calls OpenAI `gpt-image-2` to produce N images saved under `<repo>/mockups/<slug>/`.

## Prerequisites

- `uv` available (Python scripts run via `uv run --with openai --with pillow ...`).
- An OpenAI API token at `~/.claude/skills/ui-mockups/.token` (see Token below).
- Optional, only for `--screenshot <url>`: Playwright (`playwright install chromium` once).

## Token

Stored at `~/.claude/skills/ui-mockups/.token` (chmod 600). Do not echo it back to the user or write it into any other file. If the token stops working (401), ask the user to regenerate it at https://platform.openai.com/api-keys and replace the contents of the `.token` file.

### First-time setup (user runs this in their own terminal)

Get a key at https://platform.openai.com/api-keys, then in a regular terminal (not inside Claude Code) run:

```bash
python3 ~/.claude/skills/ui-mockups/scripts/set_token.py
```

The script prompts with hidden input (`getpass`), writes to `~/.claude/skills/ui-mockups/.token` with mode 0600 atomically (via `O_CREAT`), and prints a redacted confirmation. Stdlib only — no `pip install`, no `--token` flag, no env-var path.

If the script is run with no TTY and no piped input — for example if Claude tries to invoke it via the Bash tool — it refuses and exits non-zero, so the key cannot be accidentally collected into a Claude Code session.

`generate_mockups.py` reads only from the `.token` file — no env var, no CLI flag — so the token never enters `ps`, environ, transcripts, or shell history.

### Agent guidance for new users

If `generate_mockups.py` aborts with "no token at ...", do **not** ask the user to paste the key into chat, and do **not** invoke `set_token.py` yourself via Bash — anything in chat ends up in the conversation transcript. Instead, tell the user to open their own terminal and run `python3 ~/.claude/skills/ui-mockups/scripts/set_token.py`. Once they confirm it's saved, re-run the skill.

## Workflow

### Step 1 — Resolve target repo

Default `--repo` to cwd. Confirm with the user if cwd doesn't look like a UI repo (no `package.json`, no `tailwind.config.*`, no `app/`/`src/`).

### Step 2 — Ensure `mockups/STYLEGUIDE.md` exists

Check if `<repo>/mockups/STYLEGUIDE.md` exists.

- **If it does:** read the first ~30 lines to confirm it's a real styleguide, then skip to Step 3. Optionally tell the user "using existing styleguide at `mockups/STYLEGUIDE.md` — let me know if you want it regenerated".
- **If it doesn't:** load and follow `prompts/styleguide_instructions.md` to scan the repo and author the file. Use Read/Glob/Grep — do **not** call any external tool for this. Save the result to `<repo>/mockups/STYLEGUIDE.md` and tell the user it's ready for review before generating mockups.

If the user asks to **regenerate** an existing styleguide, overwrite it. If the existing one is clearly stale (the user mentions a recent visual rebrand, new component library), suggest regenerating.

### Step 3 — (Optional) Capture screenshot

If the user mentioned the live app or passed `--screenshot`, run `scripts/capture_screenshot.py <url-or-path>` to get a PNG to use as visual anchor. If the arg is already a file path, the script just copies it.

### Step 4 — Generate mockups

Run `scripts/generate_mockups.py` with the user's prompt, the styleguide path, optional screenshot path, and `--count N` (default 3).

```bash
uv run scripts/generate_mockups.py \
  --prompt "settings page with profile, billing, notifications tabs" \
  --repo "$REPO" \
  --styleguide "$REPO/mockups/STYLEGUIDE.md" \
  --count 3
```

### Step 5 — Report

- Output directory and file count.
- Note that `prompt.md` is saved alongside for reproducibility.
- Offer: "Want me to vary one of these? I can re-run with that image as the reference via `--screenshot`."

## Argument shape (Phase 2)

| Arg | Default | Notes |
| --- | --- | --- |
| `--prompt` | required | what to mock up, plain language |
| `--styleguide` | required | path to `mockups/STYLEGUIDE.md` |
| `--repo` | cwd | output goes to `<repo>/mockups/<slug>/` |
| `--count` | 3 | clamp [1, 10] |
| `--screenshot` | none | URL or PNG path for visual anchor |
| `--slug` | derived from prompt | output subdir name |
| `--size` | `1536x1024` | `WxH` (edges multiples of 16, max edge 3840, ratio ≤ 3:1) or `auto` |
| `--quality` | `high` | `low`, `medium`, `high`, or `auto` |
| `--background` | `auto` | `opaque` or `auto` (transparent not supported) |
| `--output-format` | `png` | `png`, `jpeg`, or `webp` |
| `--output-compression` | none | 0–100; only applies to jpeg/webp |
| `--moderation` | `auto` | `auto` (standard) or `low` (less restrictive) |

## Output layout

```
<repo>/mockups/
├── STYLEGUIDE.md            # phase-1 artifact, edited by the user, reused across runs
└── <slug>/
    ├── prompt.md            # full prompt sent to gpt-image-2
    ├── reference.png        # screenshot used as anchor (if any)
    ├── mockup-1.<ext>       # ext matches --output-format (png/jpg/webp)
    ├── mockup-2.<ext>
    └── mockup-3.<ext>
```

## What to tell the user

- After Phase 1: "Wrote `mockups/STYLEGUIDE.md` — review and edit before generating mockups; it's the source of truth for the image model."
- After Phase 2: output dir, count, size, and the variation offer above.
- Suggest adding `mockups/*/*.png` to `.gitignore` if not already (commit the styleguide and prompts; don't commit images).

## What NOT to do

- Don't try to deterministically extract tokens with regex — your code-reading is better than that. Read the actual files.
- Don't describe the generated images in detail — the user will look.
- Don't claim the mockups match the design system perfectly. They're generative and approximate; treat them as exploration, not specs.
- Don't commit the `mockups/<slug>/*.png` files automatically.
- Don't regenerate the styleguide on every run — it's a stable artifact unless the user asks.
