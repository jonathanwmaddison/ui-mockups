You are generating a high-fidelity UI mockup image for an existing product. The mockup must visually feel like it belongs in the same product as the styleguide below — same color palette, type voice, spacing rhythm, corner radii, shadow language, and component vocabulary.

## Styleguide — the look you must match

The following styleguide was authored by reading the product's codebase. Treat it as the source of truth for the look:

---

# ui-mockups — visual styleguide

> Note: this repo has no UI code. The styleguide below is brand-identity oriented (for cover art, README headers, social cards) rather than derived from components. It is intended to direct generative image models when producing marketing-adjacent visuals for the skill itself.

## Identity in one sentence

A quiet, technical developer tool — terminal-adjacent dark surfaces, a single saturated accent, geometric mark, and the unmistakable feel of "Claude Code skill" (workmanlike, precise, not flashy).

## Color

| Role | Value | Notes |
| --- | --- | --- |
| Background (primary) | `#0B0D10` near-black | Deep neutral, slight cool cast — not pure black |
| Surface (raised) | `#15181D` | One step lighter than bg, used for cards/panels |
| Foreground (primary) | `#E6E8EB` | Off-white, never pure `#FFF` |
| Foreground (muted) | `#8A8F98` | For metadata, secondary labels |
| Border | `#1F232A` | Hairline, low contrast |
| Accent (single) | `#D97757` Anthropic clay/terracotta | The one saturated color in the frame; used sparingly — one mark, one underline, never as a fill across large areas |
| Accent (alt, optional) | `#C7956D` warm sand | Lower-saturation companion to the clay accent for gradients |
| Code/mono tint | `#A6E3A1` muted green | Reserved for terminal-style inline code, never UI chrome |

Color usage: 90% of the frame is neutral dark. The clay accent appears in *one place* — a logo glyph, a single underline, the cursor in a code block. Never two saturated elements competing. No rainbow gradients. No purple/blue tech-startup palette.

## Typography

- **Display:** a geometric sans with slight humanist warmth — Inter, Söhne, or General Sans at 600–700 weight. Tight tracking (`-0.02em`).
- **Body:** same family at 400.
- **Mono:** JetBrains Mono, Geist Mono, or Berkeley Mono. Used for code, CLI snippets, and occasional decorative labels (`v0.1`, file paths).
- Type scale: a single hero phrase ~64–96px on cover art, supporting line ~18–22px, mono caption ~14px.
- No script fonts, no italics, no all-caps tracking.

## Spacing & layout

- Generous negative space — the cover should feel under-filled, not packed.
- Strong asymmetry is fine: weight in the lower-left, breathing room in the upper-right.
- 12-column mental grid, but content rarely uses more than 6–8 columns of it.
- Edge gutters ~64–96px on a 1536×1024 frame.

## Radii & elevation

- Radii: 0, 6px, 12px. Cards/panels at 12px. Sharp corners are acceptable for the outermost frame.
- Shadows: avoid drop shadows on dark surfaces — use a 1px border (`#1F232A`) for separation, or a subtle background-color step.
- Glow: one tasteful hint of accent-color glow (low-opacity terracotta) is okay, but resist; the look is matte, not neon.

## Component vocabulary (for cover art)

- **Logo glyph:** a single geometric mark — square, hexagon, or stacked-rectangles motif suggesting "image + frame". Stroke-style, not filled. Clay accent.
- **Code block (decorative):** dark surface, hairline border, mono font, 3–6 lines max, with a single colored token (the accent) — e.g. `--prompt "settings page"`.
- **Window chrome (optional):** macOS-style traffic-light dots in muted greys, no bright red/yellow/green — just three same-color dots to suggest "terminal window" without screaming it.
- **Tag/pill:** rounded 6px, hairline border, mono caption inside (e.g. `gpt-image-1`, `v1`).

## Iconography & imagery

- Line-style geometric icons, 1.5–2px stroke. No 3D, no isometric illustrations, no stock photography of people at laptops, no AI-generated faces.
- If imagery is needed: abstract grids, technical diagrams, schematic frames-within-frames.
- The motif "frame within a frame" is on-brand (the skill generates images of UIs — picture-of-a-picture is meta-appropriate).

## Voice & content

- Sentence case for everything. No Title Case headers.
- Imperative, terse: "Generate UI mockups", not "AI-Powered UI Mockup Generation Platform".
- Mono-font micro-copy is fine and welcome (e.g. `--count 3`, `mockups/STYLEGUIDE.md` rendered as a path).
- No exclamation marks. No emoji.

## Do

- One accent color per frame, used in one place.
- Lots of negative space.
- Mono font for any technical detail.
- Hairline borders over shadows.
- Suggest the workflow visually (prompt → image) without being literal.

## Don't

- Don't use a blue/purple SaaS gradient.
- Don't draw a robot, brain, or sparkle.
- Don't fill the frame edge-to-edge with content.
- Don't use multiple saturated colors.
- Don't render lorem-ipsum-looking text — if there's copy, it should be plausible (`uv run scripts/generate_mockups.py`).

## Sources scanned

- `SKILL.md` — overall purpose, voice, technical surface
- `prompts/styleguide_instructions.md` — tone of the skill's own prose
- `prompts/mockup_system.md` — output expectations
- `scripts/generate_mockups.py` (filename only, for command surface)

(No tailwind/CSS/component files exist in this repo — see top note.)

---



## What to render

Wide horizontal hero illustration showing the Claude Code agent skill flow. Left half: a Claude Code chat interface on a near-black surface with hairline border — at the top a user message bubble in muted off-white containing the line 'mock up a settings page in our style'; below it a Claude response showing a small system line in mono reading 'Launching skill: ui-mockups' with a tiny clay-terracotta dot beside it, then an italic line 'Reading mockups/STYLEGUIDE.md...' in muted gray, then 'Generating 3 mockups...' in mono. Middle: a thin clay-accent arrow pointing right, very subtle. Right half: a single floating UI mockup card — a clean settings page with sidebar nav (general, appearance, integrations) and a few preference rows (theme, mode, auto-save toggle in clay accent). The mockup card sits on the same near-black background with a hairline border, slight offset shadow only via background-color step. Lots of negative space around everything. The whole composition reads at-a-glance as: 'I asked Claude Code, the ui-mockups skill ran, a UI image came out.' Workmanlike and matte — no glow, no gradient, no sparkles.

## Output requirements

- A single, polished UI screen — not a moodboard, not annotated, not a wireframe sketch.
- Realistic content (not lorem ipsum). Text should be plausible for the product described in the styleguide.
- Crisp UI: clear typography hierarchy, real component spacing, no blurry placeholders.
- Honor the radii, shadow language, and density signals from the styleguide.
- Match the casing and voice conventions from the styleguide for any visible labels and copy.
- No watermarks, no captions, no surrounding device frame unless the prompt asks for one.
- Frame the screen edge-to-edge in the image.
