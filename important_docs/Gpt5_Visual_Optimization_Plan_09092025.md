# GPT-5 Visual Optimization & Performance Plan (2025-09-09)

Author: Automated Engineering Agent
Target Flet Version: 0.28.3
Scope: Desktop FletV2 (main app, `views/files.py`, `views/logs.py`)

---
## 1. Objectives
1. Reduce perceived and actual loading time of data-heavy views (Files, Logs).
2. Minimize unnecessary control rebuilds & diff only what changes.
3. Add tasteful, low-cost visual polish (striping, hover, badges, micro-animations) without FPS or memory penalties.
4. Maintain framework harmony (pure Flet patterns) and avoid gratuitous abstractions.
5. Keep changes incremental, reversible, and Codacy‑clean.

Success Criteria:
- No increase in CPU spikes during pagination / filtering (>10% baseline).
- Initial Files view visible (non-empty state) within < 150ms after data retrieval.
- Filter/search latency (keystroke → updated list) under 350ms including debounce.
- Zero functional regressions (download/verify/delete still function).

---
## 2. Constraints & Compatibility
| Area        | Constraint                                           | Strategy                                                                            |
|-------------|------------------------------------------------------|-------------------------------------------------------------------------------------|
| Flet 0.28.3 | Only use exposed properties; avoid experimental APIs | Verify features present (AnimatedSwitcher, DataTable, ListView, BoxShadow, Tooltip) |
| Large Data  | Potential hundreds of files/logs                     | Pagination + virtualization maintained; no rendering more than page size (50)       |
| Memory      | Avoid duplicating full datasets                      | Only cache derived display fields (size_fmt, modified_fmt, signature tuple)         |
| Performance | Minimize page.update() calls                         | Use control-level updates & batch modifications                                     |

---
## 3. Baseline Assessment (Key Findings)
### Files View
- Rebuilds entire DataTable each filter/pagination change.
- Recomputes size/time formatting on every rebuild.
- No pagination bar (difficult to navigate future larger sets).
- Lacks visual hierarchy (striping, subtle separators, truncation tooltip).

### Logs View
- Solid architecture (debounced search + pagination).
- Opportunities: row striping, hover emphasis, shared badge styling alignment with Files.

### main.py
- AnimatedSwitcher already efficient.
- Potential micro-optimization: lazy loading heavy views only when first accessed (cache). (Already partially present through `_loaded_views`).

---
## 4. Optimization Strategy
1. Data Preparation Layer: Precompute `size_fmt`, `modified_fmt`, and a `row_sig` signature once after load.
2. Row Diff Engine: Skip DataRow rebuild if signature unchanged (future extension; initial step builds all once).
3. Pagination Controls: Reuse a small helper builder to avoid redundant instantiation logic.
4. Debounced Filter/Search: Already present for Logs; unify 300ms debouncer for Files.
5. Batched Update: Build list of DataRows → assign → single container.update().
6. Visual Polish (low-cost):
   - Subtle row striping via alternating `DataRow(color=…)` or cell container backgrounds.
   - Tooltip on truncated file names & log messages.
   - Consistent status / level badges using helper factory with color map.
   - Soft gradient header (simple overlay Container; no heavy images).
   - Hover effect (Container `ink=True` where applicable) for select rows.
   - Animated fade when dataset changes (AnimatedSwitcher around table body).

---
## 5. Implementation Phases
| Phase | Title                  | Files                             | Description                                                                           |
|-------|------------------------|-----------------------------------|---------------------------------------------------------------------------------------|
| A     | Helper Utilities       | `utils/ui_helpers.py`             | Shared color maps, badge builder, formatting, signature calc, striping helper.        |
| B     | Files View Perf Core   | `views/files.py`                  | Integrate helpers, precompute display fields, add striping, pagination bar, tooltips. |
| C     | Logs View Polish       | `views/logs.py`                   | Apply badge helper, striping, tooltips; preserve logic.                               |
| D     | Animated Transitions   | `views/files.py`, `views/logs.py` | Wrap data region in AnimatedSwitcher (fast fade).                                     |
| E     | Diff Engine (Optional) | `ui_helpers`, `files.py`          | Replace full rebuild with conditional row rebuild using signatures.                   |
| F     | QA & Metrics           | N/A                               | Benchmark (manual), Codacy scans, smoke test.                                         |

Initial delivery target: Complete Phases A–D in first pass. Phase E optional if time / complexity acceptable.

---
## 6. Detailed Task Breakdown (Phases A–D)
### Phase A: Helper Utilities (`utils/ui_helpers.py`)
Functions:
- `size_to_human(bytes:int) -> str`
- `format_iso_short(ts:str) -> str` (ISO → `YYYY-MM-DD HH:MM`)
- `status_color(status:str) -> ft.Color`
- `level_colors(level:str) -> tuple[fg,bg]`
- `build_status_badge(text,status)` returns Container/Text.
- `striped_row_color(index:int)` returns optional color.
- `compute_file_signature(file_dict)` returns tuple `(id,size,status,modified)`.

### Phase B: Files View
1. Import helpers.
2. After loading `enhanced_data`, enrich each entry with:
   - `size_fmt`, `modified_fmt`, `row_sig`.
3. Add pagination bar mirroring logs (first/prev/info/next/last) – zero-based.
4. Build DataRows using preformatted values + `striped_row_color(idx)`.
5. Tooltip for long names (wrap Text in `ft.Tooltip`).
6. Status badge via helper.
7. Replace per-row size/time formatting with cached values.
8. Single update call.

### Phase C: Logs View
1. Introduce striped ListView tile backgrounds.
2. Use unified level badge style (consistent rounded pill + color mapping).
3. Tooltip for message overflow.
4. Minimal change: maintain pagination + search logic untouched.

### Phase D: Animated Switchers
- Wrap Files table container and Logs list container with `AnimatedSwitcher` for transitions on filter/page changes (duration ~120ms EASE_OUT).
- Swap only inner content to avoid large rebuild cost.

---
## 7. Row Diff (Phase E - Optional)
Concept: Maintain previous `row_sigs` list. On rebuild, compare new signatures; rebuild only changed rows. If >40% rows changed or page changed → rebuild all (cheaper than partial).
Pseudo:
```
new_rows = []
for i, f in enumerate(page_slice):
    sig = compute_file_signature(f)
    if i < len(old_sigs) and old_sigs[i] == sig:
        new_rows.append(existing_rows[i])
    else:
        new_rows.append(build_row(f,i))
```
Store `old_sigs = [sig...]`.

---
## 8. Visual Design Tokens
- Primary Accent: Existing `PRIMARY` color; low-alpha backgrounds (0.03 – 0.06) for stripe.
- Corner Radius: 12 (badges, table cells), 16 (major containers).
- Shadows: Single BoxShadow blur 6–8, low opacity (≤0.1) – no stacking.
- Animation Curves: EASE_OUT_CUBIC (entrance), EASE_IN_CUBIC (exit).

---
## 9. Risks & Mitigations
| Risk                                                     | Mitigation                                                           |
|----------------------------------------------------------|----------------------------------------------------------------------|
| Flet property mismatch (e.g., DataRow color unsupported) | Fallback: wrap first cell in colored Container stripe                |
| Added overhead from AnimatedSwitcher                     | Keep duration ≤160ms; only switch child content, not outer container |
| Tooltip overflow layout shift                            | Use simple text-only tooltips, no complex controls                   |
| Over-optimization complexity                             | Phase E optional; ship A–D first                                     |

---
## 10. Validation & Metrics
Manual quick checks:
- Time to first file table (log timestamps).
- Typing search: ensure debounce active (no jitter).
- Memory snapshot (optional) before/after applying filters.
- Confirm tooltip content accurate.

Codacy: Run after each file edit (mandatory) – fix style / unused imports.

---
## 11. Rollback Plan
- Each phase self-contained; revert by restoring single file version (Git diff).
- Helpers additive; safe to remove if unused.

---
## 12. Future Enhancements (Not in Current Scope)
- Infinite scrolling (replace pagination) with dynamic prefetch.
- Column sorting (size, modified) – add small icon buttons in header.
- Real-time websocket push for new logs / files (append & re-diff).

---
## 13. Execution Order
1. Phase A commit.
2. Phase B (Files) – integrate helpers.
3. Codacy scan & fix.
4. Phase C (Logs polish).
5. Codacy scan & fix.
6. Phase D (AnimatedSwitchers) + scan.
7. Optional Phase E.
8. Final smoke test & documentation update.

---
## 14. Acceptance Checklist
- [ ] Helpers file created & imported without errors.
- [ ] Files view uses cached formatting & shows striping.
- [ ] Pagination bar present in Files view.
- [ ] Logs view visually aligned (badges/striping) post Phase C.
- [ ] Animated transitions smooth (<200ms) post Phase D.
- [ ] No regressions in actions (download/verify/delete/clear/export).
- [ ] Codacy clean after each phase.

---
## 15. Notes
Keep patches small & logical. After each file edit: run Codacy for that file only (per project rules). If DataRow background unsupported, pivot quickly.

---
(End of Plan)
