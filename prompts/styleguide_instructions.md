# Generating `mockups/STYLEGUIDE.md` for a repo

Follow these instructions to author a single markdown artifact at `<repo>/mockups/STYLEGUIDE.md` that captures the visual identity of the codebase tightly enough that an image-generation model can produce on-brand UI mockups from it.

The output is **prose plus tight reference tables** — not raw token dumps. Aim for ~600–1500 words. Optimize for *directability*: a designer reading it should be able to mock up a new screen and have it feel native.

## Scan order — what to read

Read in this priority. Stop early if you have enough; don't read every component file.

1. **Token sources** (must read all that exist):
   - `tailwind.config.{js,ts,cjs,mjs}` — `theme.extend.colors`, `fontFamily`, `borderRadius`, `boxShadow`, `spacing`
   - `app/globals.css`, `src/app/globals.css`, `src/index.css`, `styles/globals.css` — CSS custom properties on `:root`/`.dark`
   - `design-tokens.json` / `tokens.json` if present
   - `components.json` (shadcn) — note style and base color
   - `src/theme.ts`, `theme/*.ts`, `lib/theme.ts`
2. **Component vocabulary** (sample 5–8 representative files):
   - `components/ui/button.{tsx,jsx}` and 4–7 other primitives (input, card, dialog, badge)
   - One or two real screen-level components (e.g. a page route file) to see how primitives are composed
3. **Layout signals**:
   - The root layout (`app/layout.tsx` or equivalent) for typography defaults and container widths
   - One marketing or dashboard page to read density
4. **Voice signals** (skim, don't dwell):
   - Real product copy in nav items, button labels, empty states — capture casing convention and tone

If a category has no signal, say so explicitly in the styleguide rather than inventing one.

## Required sections

Use these section headers verbatim so the prompt assembler can rely on the structure:

```markdown
# {Product or repo name} — visual styleguide

## Identity in one sentence
{One sentence: the overall feel. e.g. "Quiet, neutral utility UI with a single saturated accent and ample whitespace — Linear-adjacent."}

## Color
- **Palette role table** (one row per role: background, foreground, primary, accent, muted, border, destructive, success, etc.) with the actual hex/HSL values and the variable name they're stored under.
- One paragraph on how color is used: where the accent appears, whether semantic colors are saturated or muted, dark mode strategy.

## Typography
- Families with fallback stacks.
- The type scale actually in use (read it from the components, not the config — what sizes show up in headings, body, micro-copy).
- Weight strategy (e.g. "headings 600, body 400, no italics in product UI").
- Line-height and tracking notes if non-default.

## Spacing & layout
- The base unit and the rhythm (e.g. "Tailwind defaults; primary spacing is 4 / 8 / 16 / 24, page gutters 24–32px").
- Container widths.
- Density: tight, medium, airy. Cite a component as evidence.

## Radii & elevation
- Radius scale and where each tier is used.
- Shadow language: are shadows soft and subtle, or layered and dramatic? Is elevation done via shadow, border, or background contrast?

## Component vocabulary
For 4–6 primitives, give a 1–2 sentence visual description: what they look like, not what they do. Examples:
- **Button (primary):** filled, single accent color, ~36px tall, sm radius, no shadow, white text.
- **Card:** subtle 1px border, no shadow, 12px radius, generous internal padding (24px).
- **Input:** ghost background, 1px border that darkens on focus, no inner shadow.

## Iconography & imagery
- Icon library in use (lucide, heroicons, custom) and stroke weight.
- Whether the product uses photography, illustration, or none.

## Voice & content
- Casing convention for labels (sentence vs Title).
- Are CTAs imperative or noun-style?
- Empty states: friendly and verbose, or terse and functional?

## Do / don't (only if you see clear signals)
- 2–4 bullets each. Skip if you're guessing.

## Sources scanned
- Bullet list of files you read, relative paths.
```

## Quality bar

- **Quote real values, not invented ones.** If `--primary` is `199 89% 48%`, say that.
- **Prefer evidence over confidence.** If you can't tell whether the product uses imagery, write "no signal — defer to prompt".
- **Be concrete about the *feel*.** "Linear-adjacent" or "Stripe-inflected" or "Vercel monochrome" tells the image model more than 200 words of hedging.
- **No code blocks longer than ~10 lines.** If you find yourself dumping a config, summarize instead.
- **Mark uncertainty inline** — `(inferred)` next to a claim is fine, and helps the human reviewer.

## After writing

1. Save to `<repo>/mockups/STYLEGUIDE.md` (create the directory if missing).
2. If `<repo>/.gitignore` doesn't already ignore `mockups/`, suggest adding `mockups/*.png` and `mockups/*/reference.png` so generated images aren't committed but the styleguide is.
3. Tell the user: "Styleguide written to `mockups/STYLEGUIDE.md` — review and edit before generating mockups; this is the source of truth for the image model."
