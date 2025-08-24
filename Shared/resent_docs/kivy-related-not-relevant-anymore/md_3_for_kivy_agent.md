# Material Design 3 (M3) Implementation Guide — Agent Instructions

> **Purpose:** A single-file spec your coding agent can consume to convert an existing Tkinter GUI into a *Material Design 3 (M3)* app implemented in **Kivy + KivyMD**. This document focuses *only* on M3 (no Expressive) and places Expressive as a **long-term extension** after full M3 compliance is achieved.

---

## Quick summary (read first)
- **Goal:** Produce a token-driven, testable, Kivy/KivyMD implementation that follows Google Material Design 3 guidelines (color system, design tokens, elevation, typography, motion, components, accessibility).
- **Constraints:** Use KivyMD where possible; implement adapters/custom widgets where KivyMD lacks direct support. Dynamic color (Material You) is optional but supported by KivyMD and achievable via runtime color extraction and token mapping.
- **Long-term plan:** Add Material Design 3 — **Expressive** only after the app is fully compliant with canonical M3.

---

## How your agent should work (top-level flow)
1. **Ingest baseline:** read the provided Tkinter GUI files and assets (images, icons). Produce a component map of screens + widgets.
2. **Create design tokens:** output a canonical JSON/YAML file with M3 tokens (colors, radii, typography, elevation, motion durations, spacing grid).
3. **Map tokens → KivyMD:** produce a mapping file that translates tokens to `theme_cls` properties, widget properties, and adapter behaviors.
4. **Generate adapter layer:** produce `components/` with small adapter classes (e.g. `MD3Button`, `MD3Card`, `MD3TextField`) that wrap KivyMD widgets and enforce tokens.
5. **Generate screens:** for each Tkinter screen, create a Kivy KV layout file plus a Python screen controller that uses adapter components and tokens.
6. **QA & tests:** generate automated accessibility checks (contrast ratios, touch targets), visual regression (screenshots + pixel diffs), and unit tests for adapter APIs.
7. **Iterate:** produce screenshots for designer review, accept feedback, then refine tokens and layouts.

---

## Must-follow M3 rules (high level — encode these into automated checks)
- **Color system & roles:** implement the M3 token roles (primary, on-primary, primary-container, etc.). Use tonal palettes generated from a seed color. Ensure UI semantics map to the proper color roles.
- **Design tokens:** centralize every visual decision (colors, type scale, corner radii, elevation) in tokens. Widgets read tokens rather than hard-coded values.
- **Type scale:** implement the M3 type tokens (display, headline, title, body, label) and map them to KivyMD typography/hints.
- **Elevation & surfaces:** create elevation tokens and make sure shadows/contrast indicate hierarchy. Elevation must be consistent across components.
- **Motion:** short, meaningful motion only. Use motion durations from tokens (e.g. micro 100–120ms, short 120–200ms, medium up to 300ms). No motion longer than ~300ms for micro-interactions.
- **Accessibility:** WCAG contrast >= AA for normal text; touch targets >= 48dp; readable sizes on default scale; keyboard focus and structure for non-touch use.
- **Spacing:** follow an 8dp baseline grid (multiples of 4dp acceptable for small tweaks).

> *Agent task:* Implement checkers that validate token adherence and flag components that violate rules.

---

## Token schema (JSON) — canonical example
```json
{
  "palette": {
    "seed_color": "#6750A4",
    "primary": "#6750A4",
    "on_primary": "#FFFFFF",
    "primary_container": "#EADDFF",
    "on_primary_container": "#21005D",
    "secondary": "#625B71",
    "on_secondary": "#FFFFFF",
    "background": "#FFFBFE",
    "surface": "#FFFBFE",
    "error": "#B3261E",
    "on_error": "#FFFFFF"
  },
  "shape": {
    "corner_small": 6,
    "corner_medium": 12,
    "corner_large": 16
  },
  "elevation": {
    "level0": 0,
    "level1": 1,
    "level2": 3,
    "level3": 6,
    "level4": 8,
    "level5": 12
  },
  "typography": {
    "display_large": "40sp",
    "headline_medium": "28sp",
    "title_large": "22sp",
    "body_medium": "14sp",
    "label_large": "14sp"
  },
  "motion": {
    "micro": 100,
    "short": 160,
    "standard": 250
  },
  "spacing": {
    "grid": 8,
    "gutter": 16
  }
}
```

- All sizes are in **dp/sp** equivalents. The agent must be able to output different units if target platform or environment requires.

---

## Mapping tokens → Kivy/KivyMD (guidelines & examples)
- `theme_cls.primary_palette` → choose the palette that most closely matches `palette.primary` and set `theme_cls.primary_hue` to the proper hue string.
- `theme_cls.theme_style` → `Light` or `Dark` according to user preference or token background luminance.
- Corner radius: KivyMD widgets accept `radius` in list form. Adapter should set `radius` from token values (e.g. `radius: [corner_large,]`).
- Elevation: KivyMD supports `elevation` on some widgets. Agent must add visual elevation (shadow or surface tint) where KivyMD lacks elevation by using canvas instructions (opacity layers + shadow bitmaps).
- Typography: map `typography` tokens to KivyMD `font_style` or set `font_size` directly when `font_style` is insufficient.

> Example mapping table (agent-readable):
>
> | Token | Kivy/KivyMD target |
> |---|---|
> | `palette.primary` | `theme_cls.primary_palette` / `primary_hue` or set `md_bg_color` directly |
> | `shape.corner_medium` | `MDCard.radius` or direct canvas rounding |
> | `elevation.level3` | `elevation` property or custom canvas shadow |
> | `typography.title_large` | `MDLabel.font_style` or `font_size` |

---

## Dynamic color (Material You) — optional but supported
- **Approach:** extract dominant/seed color from user image (wallpaper or brand asset). Generate tonal palettes (5 palettes as M3 does) and map to M3 roles.
- **Implementation notes:**
  - Use Python libraries like `colorthief` or a small K-means clustering on RGB or CIELAB colorspace to find a dominant color.
  - Convert dominant color to tonal palettes. KivyMD includes a `dynamic-color` module that can help with baselines; otherwise, agent generates palettes and then sets tokens at startup.
  - Always verify contrast of derived colors; if they fail accessibility, apply fallback adjustments (e.g. change tone or pick neutral container colors).

> Sample seed extraction (Python):
> ```py
> from colorthief import ColorThief
> ct = ColorThief('wallpaper.jpg')
> dominant = ct.get_color(quality=1)  # (r,g,b)
> ```

---

## Component adapter layer (required)
Create a small, strict API layer in `components/` that your agent will auto-generate. Each adapter does three things:
1. Consume tokens (read-only) at construction.
2. Enforce size, padding, radius, elevation, and typography according to tokens.
3. Map high-level semantic props (e.g. `variant='primary'`, `tone='container'`) to concrete color and style properties.

**Examples to generate:**
- `MD3Button` (variants: filled, tonal, outlined, text, elevated)
- `MD3Card` (surface, elevated surface)
- `MD3TextField` (with leading/trailing icons, helper text, error handling)
- `MD3TopAppBar`, `MD3BottomNav`, `MD3Drawer` (navigation)
- `MD3FAB` (regular, extended)

Agent must include unit tests for each adapter that assert attributes equal token-derived values.

---

## Converting your Tkinter UI (practical mapping rules)
1. **Navigation pane (left)** → `MDNavigationDrawer` or a `BoxLayout` + `MDList` inside a permanent drawer-like `MDNavigationLayout`.
2. **Header / Topbar** → `MDTopAppBar` with title and action icons. Use tokens for height, padding, and typography.
3. **Dashboard cards & panels** → `MDCard` with `radius` from `shape` tokens, internal padding from `spacing.gutter`, and elevation from `elevation.level2/3`.
4. **Action buttons (colored stacked buttons)** → use `MDRectangleFlatButton`/custom `MD3Button` variants; use semantic color roles (primary, error) for colors.
5. **Charts** → leave charts as separate canvas/plot widgets; skin their background/surface and legend via tokens. (Use Matplotlib or Kivy Garden Chart and set colors from tokens.)
6. **Activity log / scrollable lists** → `MDList` inside `ScrollView`, set `touch` target sizes, spacing, and contrast.

> Agent must create a one-to-one mapping file listing old Tkinter widget → new MD3 adapter/widget with any additional notes (e.g., "needs custom icon font" or "map to card with level3 elevation").

---

## Automated QA checklist (agent will run these after generation)
- Color & contrast
  - All text meets at least **WCAG AA** (normal text 4.5:1) — generate a report of failing elements.
- Touch target
  - All tappable controls >= 48dp in at least one axis.
- Spacing
  - Layout conforms to 8dp grid; flag misalignments >4dp.
- Motion
  - All enter/exit micro-interactions < 300ms; durations match tokens.
- Consistency
  - Widgets use adapter layer, not raw KivyMD widgets with custom inline styles.
- Visual regression
  - Capture baseline screenshots and produce pixel-diff with a threshold. Save diffs for designer review.

---

## Sample Kivy/KV + Python snippets (agent should use these templates)
### main.py (app + token load)
```py
from kivy.lang import Builder
from kivymd.app import MDApp
import json

class MD3AgentApp(MDApp):
    def build(self):
        with open('tokens.json') as f:
            self.tokens = json.load(f)
        # apply theme minima
        self.theme_cls.theme_style = 'Light'
        # mapping example: set palette via direct colors if needed
        # self.theme_cls.primary_palette = 'Blue'
        return Builder.load_file('screens.kv')

if __name__ == '__main__':
    MD3AgentApp().run()
```

### adapter/button.py (concept)
```py
from kivymd.uix.button import MDRaisedButton

class MD3Button(MDRaisedButton):
    def __init__(self, tokens, variant='filled', **kwargs):
        super().__init__(**kwargs)
        self.tokens = tokens
        # set radius
        self.radius = [tokens['shape']['corner_medium'],]
        # set padding according to tokens
        self.padding = [tokens['spacing']['gutter'], tokens['spacing']['grid']]
        # map variant -> color
        if variant == 'primary':
            self.md_bg_color = hex_to_rgba(tokens['palette']['primary'])
```

> Agent must generate `hex_to_rgba` helper and central `tokens` loader.

---

## Visual strategy & UX notes (professional design thinking)
- **Hierarchy:** use elevation and larger type for primary information (server status, big numbers). Secondary info gets smaller type and lower elevation.
- **Focus:** navigation group on left — for desktop, a permanent navigation with clear selected state. For mobile, collapse into a navigation drawer.
- **Affordance:** buttons must look tappable (contrast + shadow + padding). Use consistent iconography (Material Icons font).
- **Density:** desktop can use slightly denser spacing, but respect touch target minima if touch is supported.
- **Branding:** allow a `brand_seed_color` token; keep branding purely in tokens so skinning is trivial.

---

## Where KivyMD helps & where to implement custom work
- **Helps (use directly):** App scaffolding, many components (buttons, cards, top app bar, lists), theming via `theme_cls`, dynamic color support exists in KivyMD docs.
- **Custom work required:** pixel-perfect shadows/elevation, exact M3 motion curves, component anatomy not implemented in KivyMD, some M3 component variants (if missing), and complex dynamic color tonal generation (agent must implement tonal mapping).

---

## Deliverables for each agent run (explicit checklist to generate)
- `tokens.json` (canonical tokens)
- `mapping.yaml` (Tkinter widget → MD3 adapter mapping)
- `components/` adapter modules with unit tests
- `screens/` KV + Python controllers
- `assets/` icon fonts, images, and extracted palettes
- `qa/` accessibility_report.json, screenshot baselines, pixel diffs
- `README_AGENT.md` describing how to run tests and iterate

---

## Long-term plan: Material Design 3 — Expressive
> *Perform only after achieving full M3 compliance.*
- Expressive adds more playful palettes, larger shapes, stronger motion. Plan: once M3 baseline passes automated QA, add a feature flag (`expressive_mode`) that alters tokens (more saturated palettes, larger corner radii, increased motion amplitude) and a/b test user reactions.

---

## Practical constraints & assumptions
- The target runtime is desktop (Windows 11) but code should be cross-platform if possible.
- KivyMD v2.x+ is available and can be installed (agent should pin a version and include a `requirements.txt`).
- The agent must create small, reviewable commits and a runnable scaffold. Keep each generated module small and testable.

---

## Example project structure (agent should create)
```
project_root/
  tokens.json
  mapping.yaml
  requirements.txt
  main.py
  README_AGENT.md
  components/
    __init__.py
    button.py
    card.py
    textfield.py
  screens/
    dashboard.kv
    settings.kv
    controllers/
      dashboard.py
  assets/
    icons.ttf
    wallpaper.jpg
  qa/
    accessibility_report.json
    baselines/
      dashboard.png
    diffs/
```

---

## Starter `requirements.txt` suggestion
```
kivy==2.1.0
kivymd==2.0.0
colorthief==0.2.1
Pillow==9.5.0
pytest
```

---

## How to run the generator (agent contract)
1. Place Tkinter source files into `input/tk/`.
2. Run `python agent_generate.py --input input/tk --out project_root`.
3. The generator must produce the deliverables above and return a JSON summary with errors/warnings found by QA checks.

---

## Designer checklist (for review after generation)
- Verify semantic color usage (primary vs. container).
- Verify typography hierarchy across screens.
- Test keyboard navigation and focus order.
- Check micro-interaction feel and shorten motions that feel laggy.
- Validate baselines vs. designer-approved images.

---

## Notes for the human reviewer (you)
- This doc is intentionally prescriptive: tokens-first, adapter layer, automated QA. It’s possible to produce an M3-looking app quickly with KivyMD, but for *correctness* implement token enforcement and tests.
- Expect to implement a handful of custom canvas drawings for exact elevation and container visuals.

---

## Attachments & assets
- The agent should copy the provided Tkinter screenshot(s) and any icon assets into `assets/` and use them to propose a visual mapping.

---

## Next steps for you
1. Confirm you want the agent to **generate the full project scaffold** now.
2. If yes, agent will run: parse Tkinter sources, produce `tokens.json`, then generate adapters and screens.


---

*End of MD3 agent spec.*

