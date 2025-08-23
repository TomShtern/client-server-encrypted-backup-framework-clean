# Implementing Material Design 3 (M3) & Material 3 Expressive (M3E) in Flet — Practical Guide

**Purpose:** a compact, practical handbook for implementing best-practice Material Design 3 (M3) in Flet apps and for approximating *Material 3 Expressive (M3E)* features (dynamic color, expressive motion, shape morphing, typography). Focus is on measurable, implementable advice and concrete Flet code patterns — especially animations and high-quality UI/UX.

> **Scope & constraints**
> - Flet renders via Flutter under the hood but exposes a Python API. You get most M3 primitives (theming, seeded color schemes, components) but not every M3E nicety out-of-the-box. This doc shows what is directly supported, what must be approximated, and how to do it well.

---

## Quick TL;DR
- **Yes:** you can implement high-fidelity M3 in Flet: theming, seeded color schemes, typography, shape systems, elevation, responsive layout.
- **Partially:** M3 Expressive features (advanced motion physics, dynamic runtime material tokens, shape morphing) are not native — but **you can approximate them** with Flet's animation primitives, AnimatedSwitcher, Lottie/Rive, custom components and theme updates.
- **Practical rule:** keep the visual system tokenized: seed color → derived palette → component tokens. Use implicit animations for transitions and explicit animations or Rive/Lottie for complex expressive motion.

---

## 1. Design-first workflow (how to approach)
1. **Design tokens first** — pick a `seed color`, typography family, a small shape system (corner radii: 4/8/12/16), and 4 elevation levels. Put these in a single `theme.py` file as constants.
2. **Prototype with Flet theme** — use `page.theme = ft.Theme(...)` and `page.dark_theme` for the two modes.
3. **Keep UI stateless where possible** — make small stateful controls with isolated animations so transitions are predictable.
4. **Prefer implicit animations** for property changes (position, offset, opacity, scale). Only use heavy timeline animations (Lottie/Rive) for hero moments.
5. **Accessibility & performance:** avoid long-running animations, provide reduced-motion option, and test on device (desktop/mobile/web).

---

## 2. M3 in Flet — Core mappings

### Theming (seeded color, light/dark)
Flet supports seeded color schemes. Generate a base theme from a seed and expose 30 derived colors via `page.theme.color_scheme`.

```python
import flet as ft

def main(page: ft.Page):
    page.title = "M3 Flet Demo"

    page.theme = ft.Theme(
        use_material3=True,                # defaults to True but explicit is clearer
        color_scheme_seed=ft.Colors.INDIGO,
        font_family="Inter",
    )

    page.dark_theme = ft.Theme(
        color_scheme_seed=ft.Colors.INDIGO,
        brightness=ft.ThemeMode.DARK,
        font_family="Inter",
    )

    page.add(ft.Text("Material 3 in Flet"))

ft.app(target=main)
```

**Notes:**
- Keep theme tokens in a `theme.py` file and read them from there. You can override individual `Theme.color_scheme` entries if you need exact brand colors.
- To implement dynamic color (M3E-like), update `page.theme.color_scheme_seed` at runtime and call `page.update()`; animate the transition using fade or cross-fade to avoid abrupt repaints.


### Typography
- Import web fonts or ship local fonts and set `Theme.font_family`. Individual `Text` controls support `font_family`, `size`, `weight`.

```python
# fonts: define in page.fonts then
page.theme = ft.Theme(font_family="Inter")
# specific control
ft.Text("Big headline", size=28, weight=700, font_family="Inter")
```

**M3 tip:** implement a `text_styles` helper mapping M3 scale (display/heading/title/label/body) to Flet text sizes/weights.


### Shapes & Elevation
- Use `border_radius` on `Container`, `Card` for rounded shapes; use `Card` or `ElevatedButton` for elevation shadows.
- Define a small shape scale for consistent radius values and use semantic names (e.g., `shape_small`, `shape_medium`, `shape_large`).

```python
CARD_RADIUS = 12
card = ft.Card(content=ft.Text("Card content"), elevation=4)
container = ft.Container(border_radius=ft.border_radius.all(CARD_RADIUS))
```

**M3E shape morphing:** approximate by animating `border_radius` and swapping containers inside an `AnimatedSwitcher` so the shape change cross-fades.

---

## 3. Components: building M3-ish widgets in Flet
- **App bar / Navigation bar**: use `AppBar`, `NavigationBar`. Theme overrides exist (e.g., `navigation_bar_theme`).
- **Cards & Surfaces**: `Card`, `Container` + `elevation`/shadow props.
- **Buttons**: `FilledButton`, `OutlinedButton`, `ElevatedButton` — themeable via `Theme.filled_button_theme` / `Theme.elevated_button_theme`.
- **Dialogs / Sheets**: `AlertDialog` and `BottomSheet` exist; style via theme colors and `dialog_theme`.

**Pro tip:** emulate M3 "tonal" surfaces by using subtle color roles from `page.theme.color_scheme` (e.g., `primaryContainer`, `surfaceVariant`, etc.) and build small helper wrappers that map your tokens to Flet properties.

---

## 4. Motion & Animations — make it expressive (M3E-ish)
This is where Flet shines for M3 approximation. Two approaches:

- **Implicit animations** (recommended for most UI): use `animate_*` properties on controls (e.g., `animate_offset`, `animate_scale`, `animate_rotation`, `animate_position`, `animate_opacity` via `opacity`/`animate` patterns).
- **AnimatedSwitcher / explicit timeline**: good for content swaps, hero transitions, complex chained motion.
- **Rive / Lottie**: use for complex, bespoke, springy interactions that are authored by motion designers.

### Animation primitives & patterns (concrete)
- **Implicit translation (slide-in)**
```python
c = ft.Container(width=200, height=60, bgcolor="primaryContainer",
                 offset=ft.transform.Offset(-1, 0),
                 animate_offset=ft.animation.Animation(400, ft.AnimationCurve.FAST_OUT_SLOWIN))

# to trigger
c.offset = ft.transform.Offset(0, 0)
page.update()
```

- **Scale + spring feel (button pop)**
```python
btn = ft.Container(scale=ft.transform.Scale(1), animate_scale=ft.animation.Animation(180, ft.AnimationCurve.EASE_OUT_BACK))
# on press
btn.scale = ft.transform.Scale(0.95)
page.update()
# restore after short delay
```

- **Cross-fade / content morph**
Use `AnimatedSwitcher` to swap dense content with clean fading and shared layout.

```python
switcher = ft.AnimatedSwitcher(content=first_control, duration=300)
# swap content
switcher.content = second_control
page.update()
```

- **Chained animations / callbacks**
`AnimatedSwitcher` and other animation controls support `on_animation_end` which lets you chain a secondary animation when the first completes.

- **Rive / Lottie**
When you need full M3E expressive motion (spring, follow-through, staged easing), offload to Lottie/Rive animations authored in their editors and display via `ft.Lottie` / `ft.Rive`. Use them for hero transitions or brand moments — **not** for every micro-interaction.

### Motion system rules (M3E-inspired)
1. **Use hierarchy of motion:** macros (page transitions) 400–600ms, micro (button press) 100–200ms, content swap 200–350ms.
2. **Use easing curves deliberately:** `FAST_OUT_SLOWIN` or `EASE_OUT_CUBIC` for entry; `EASE_IN` for exits; `ELASTIC_OUT` for playful micro-interactions only.
3. **Avoid motion overload:** animate only what's necessary; use staggered entrances instead of simultaneous movement of everything.
4. **Reduced-motion toggle:** implement `user_prefers_reduced_motion` flag and set `animate_*` to `0` or `False` when active.

---

## 5. Implementing specific M3E features in Flet (how-to hacks)

### 5.1 Dynamic color (Material You-like)
**Goal:** user picks wallpaper/seed color → app theme updates.

**Approach:**
1. Let user pick a color or extract palette from an image outside Flet (Python `colorthief` or `palette` package) or via a small backend service.
2. Set `page.theme.color_scheme_seed` to the extracted color.
3. Cross-fade UI using `AnimatedSwitcher` or overlay a half-transparent container while the new theme applies, then fade out.

**Pattern:**
```python
page.theme.color_scheme_seed = picked_color
# snapshot the old UI -> overlay fade
overlay.opacity = 1
page.update()
# short delay, then fade out overlay
overlay.opacity = 0
page.update()
```

**Caveat:** theme reflow may be expensive on large trees—keep theme updates to a few roots or rebuild views lazily.


### 5.2 Expressive motion (spring physics)
**Goal:** reproduce M3E spring-based motion.

**Approach:**
- Use `ft.animation.Animation(duration, ft.AnimationCurve.ELASTIC_OUT)` as the `animate_*` parameter for scale/offset. For complex spring behavior, use **Rive** animations authored with spring curves.

```python
c.animate_scale = ft.animation.Animation(600, ft.AnimationCurve.ELASTIC_OUT)
c.scale = ft.transform.Scale(1.12)
page.update()
```

**Pro tip:** chain small overshoot scales for a believable spring: 1.12 → 0.98 → 1.0 with short durations (120 ms, 90 ms, 80 ms).


### 5.3 Shape morphing
**Goal:** change a pill to a square smoothly.

**Approach:** animate `border_radius` by cross-fading two containers inside an `AnimatedSwitcher` or animate a custom property inside a `UserControl` that interpolates `border_radius` values.

```python
# rough pattern
switcher = ft.AnimatedSwitcher(content=pill_container, duration=300)
# swap to square container
switcher.content = square_container
page.update()
```

True morphing (vertex interpolation) needs Rive or a custom canvas; otherwise use well-timed cross-fades and scale/offset to sell it.


### 5.4 Adaptive typography
**Goal:** responsive type scale that follows M3 recommendations.

**Approach:** central `text_styles` map keyed by device breakpoints. On `page.on_resize`, compute the best text scale and update the tree (or update `Theme.text_theme` if you want app-wide changes).

---

## 6. Fancy UI/UX snippets & patterns
### Animated Sidebar (position animation)
Use `Stack` and `animate_position` to slide a drawer in/out.

### List entrance staggering
Stagger list item entrance by applying `animate_offset` with increasing delays and using `on_animation_end` to trigger the next item.

### Micro-interaction: ripple + pop
Use `Ink` or clickable `Container` with short `animate_scale` and `animate_opacity` to create tactile feedback.

### Transition pattern for page navigation
Use `Page.views` with `PageTransitionsTheme` and custom `page_transitions` in `Theme` for consistent page transitions. For more complex hero animations, combine `AnimatedSwitcher` + overlayed Lottie.

---

## 7. Performance & testing checklist
- Profile CPU and memory on target platforms (desktop/mobile/web).
- Limit the number of simultaneous animated controls.
- Prefer transforms (offset/scale) over layout-triggered animations where possible.
- Provide a reduced-motion toggle and test with it enabled.
- Test dark/light theme tokens: ensure contrast meets accessibility (AA) thresholds.

---

## 8. Tooling & assets
- **Motion assets:** Lottie (JSON) and Rive (file) — use them for brand moments.
- **Palette extraction:** `colorthief`, `palette` in Python to generate seed colors from images.
- **Design tools:** Material Theme Builder (Figma) to generate token values, export color tokens and typography scales.

---

## 9. Example: small practical M3-ready component (flet)

```python
import flet as ft
from math import pi

CARD_RADIUS = 12

def main(page: ft.Page):
    page.title = "M3 Card + Motion"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.DEEP_PURPLE, font_family="Inter")

    c = ft.Container(
        width=300,
        height=120,
        border_radius=ft.border_radius.all(CARD_RADIUS),
        bgcolor=page.theme.color_scheme.surface_variant,
        offset=ft.transform.Offset(-0.4, 0),
        animate_offset=ft.animation.Animation(420, ft.AnimationCurve.FAST_OUT_SLOWIN),
    )

    def show(e):
        c.offset = ft.transform.Offset(0, 0)
        page.update()

    page.add(ft.Column([
        ft.ElevatedButton("Show card", on_click=show),
        c
    ]))

ft.app(target=main)
```

---

## 10. Do's & Don'ts (short)
**Do**
- Tokenize theme values.
- Use implicit animations for state changes.
- Use Lottie/Rive for signature expressive motion.
- Offer reduced-motion toggle.

**Don't**
- Animate layout-heavy properties unnecessarily.
- Re-theme the whole app on every small interaction.
- Use elastic/overshoot curves for everything — use them sparingly.

---

## 11. Next steps — a practical checklist for you
- [ ] Create `theme.py` tokens (seed color, radii, text scale)
- [ ] Build a `ThemeManager` helper that can swap themes (with cross-fade)
- [ ] Replace raw colors in UI with `page.theme.color_scheme.*` tokens
- [ ] Replace instant content swaps with `AnimatedSwitcher`
- [ ] Add a `reduced_motion` toggle and respect it in all `animate_*` props
- [ ] Author a small Rive animation for a hero moment and plug with `ft.Rive`

---

## Appendix: useful Flet API hints
- `page.theme = ft.Theme(use_material3=True, color_scheme_seed=..., font_family=...)`
- `ft.animation.Animation(duration_ms, ft.AnimationCurve.FAST_OUT_SLOWIN)` — used with `animate_offset`, `animate_scale`, `animate_rotation`, etc.
- `ft.AnimatedSwitcher(content=..., duration=...)` for cross-fades and content swapping.
- `ft.Lottie` / `ft.Rive` to play authored expressive animations.

---

If you want, I can:
- Produce a `theme.py` starter file using your brand colors.
- Convert one existing screen from your app into an M3-styled Flet version (code + assets).
- Generate a small Rive/Lottie plan for a hero animation and show how to integrate it.

Tell me which one and I’ll scaffold it next.

