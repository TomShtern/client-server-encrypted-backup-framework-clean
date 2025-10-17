# Dashboard Material 3 Audit (2025-10-17)

## Findings

1. **Progress indicator thickness is controlled with `height` instead of `bar_height`**  \
   Location: `FletV2/views/dashboard.py`, CPU panel setup around the `cpu_bar = ft.ProgressBar(value=0.0, height=8)` declaration.  \
   Evidence: The [ProgressBar reference](https://flet.dev/docs/controls/progressbar/#bar_height) specifies `bar_height` as the Material 3 property for configuring the indicator line thickness. Setting the generic control `height` does not change the rendered bar, so the CPU gauge remains the default 4 px regardless of the intended design.  \
   Impact: The dashboard shows a thinner bar than designed, reducing readability, especially on high-resolution displays. Using `bar_height=8` keeps the control compliant with the documented Material 3 API and delivers the expected visual weight.

2. **Severity palette relies on static Material 2 accent colors instead of theme-driven Material 3 tones**  \
   Location: `_activity_palette()` in `FletV2/views/dashboard.py`.  \
   Evidence: The palette uses constants like `ft.Colors.GREEN_ACCENT_100` and `ft.Colors.AMBER_ACCENT_100`. The [Colors documentation](https://flet.dev/docs/reference/colors/#theme-colors) notes that Material 3 expects components to source hues from `Theme.color_scheme` (e.g., `PRIMARY`, `ERROR`, `SECONDARY_CONTAINER`) so they react to the `color_scheme_seed`, dynamic theme changes, and dark mode. Hard-coded accent shades bypass the scheme entirely.  \
   Impact: Activity badges no longer harmonize with custom themes or dark mode, breaking Material 3 contrast guarantees and producing inconsistent visuals compared to the rest of the page. Switching to scheme-driven colors (for example `page.theme.color_scheme.error` / `tertiary_container`) restores adaptive styling.

## Notes

- Context7 documentation access was rate-limited during the review; the linked references come from the public Flet docs, which reflect the same Material 3 API surface.
