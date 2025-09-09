<!--
Enhanced Revision: 2025-09-09 (v2) – Expanded with execution playbooks, metrics methodology, QA matrix, risk register, and technical debt strategy.
-->

# GPT-5 Visual Optimization & Performance Plan (2025-09-09, Enhanced v2)

Author: Tom  
Target Flet Version: 0.28.3  
Scope: Desktop FletV2 (`main.py`, `views/files.py`, `views/logs.py`, shared utils..)  
Status: Phases A–F delivered; diff engine & instrumentation active.

---
## 0. Executive Summary
This plan elevates data-heavy Flet views (Files, Logs) by combining targeted performance optimizations (precomputation, differential row reuse, debounced search) with low-cost visual polish (striping, badges, fade transitions). The enhanced revision formalizes: measurable KPIs, instrumentation protocol, quality gates, risk handling, accessibility and security considerations, and a structured technical debt burn-down. Following this document yields predictable performance improvements, reduced rebuild overhead, and consistent UI semantics without over-engineering.

---
## 1. Objectives
1. Minimize end-to-end latency in data presentation (load, paginate, filter, search).
2. Eliminate avoidable UI control churn via signature-based diffing.
3. Enhance visual clarity & perceived performance with subtle, cheap animations and hierarchy cues.
4. Maintain strict framework harmony (pure Flet idioms; no custom navigation or over-abstractions).
5. Preserve functional parity (file actions, log operations) and security posture.
6. Provide repeatable measurement methodology to detect regressions.

### Key Performance Indicators (KPIs)
| KPI                       | Definition                                      | Target                       | Measurement Source                            |
|---------------------------|-------------------------------------------------|------------------------------|-----------------------------------------------|
| TTFV (Time To First View) | Data ready → first non-empty Files table render | <150ms                       | `PerfTimer` (files.load.* aggregate)          |
| Search Latency P95        | Keypress release → updated visible rows         | <350ms                       | Debounced event timing (files.search.perform) |
| Row Reuse Ratio           | Reused rows / total rows displayed (Files)      | ≥60% typical pages           | Diff engine counters                          |
| CPU Spike Delta           | Peak vs baseline during pagination/search       | ≤ +10%                       | External profiler / OS monitor                |
| Memory Growth Per Filter  | Δ RSS after one filter cycle                    | ≤ +2% (no accumulative leak) | System metrics snapshot                       |

---
## 2. Environment & Prerequisites
| Aspect          | Requirement                | Notes                                          |
|-----------------|----------------------------|------------------------------------------------|
| Python          | 3.11+ recommended          | Align with Flet 0.28.3 support window          |
| Flet            | =0.28.3                    | Lock version to ensure component API stability |
| OS              | Cross-platform             | Tested primarily on Windows desktop            |
| Async Loop      | `asyncio` single main loop | Use `ft.app_async` pattern                     |
| Security        | SHA256 hashing only        | MD5 prohibited (removed)                       |
| Tooling         | Codacy CLI integration     | Run per-file post-change                       |
| Instrumentation | `utils/perf_metrics.py`    | Mandatory for metrics collection               |

Setup Verification Checklist:
- [ ] `pip freeze` shows flet==0.28.3
- [ ] App launches without blocking “Loading…” screen beyond expected data fetch
- [ ] `perf_metrics.get_metrics()` returns structured dict after interactions

---
## 3. Architectural Principles
| Principle                | Rationale                        | Applied Through                                |
|--------------------------|----------------------------------|------------------------------------------------|
| Localized Updates        | Avoid global page repaints       | Update container / control only                |
| Precompute Once          | Reduce repeated formatting costs | Cache `size_fmt`, `modified_fmt`               |
| Idempotent Rebuild Paths | Safe repeated calls              | Pure helper functions free of side-effects     |
| Differential Rendering   | Minimize object creation         | Signature-based row reuse                      |
| Observability First      | Detect regressions early         | Perf timers with stable naming schema          |
| Reversible Changes       | Fast rollback                    | Phase isolation / single-file scope            |
| Security Neutral         | No new attack surface            | No dynamic eval / file system write escalation |

---
## 4. Baseline Assessment (Condensed)
FILES: Full-table rebuilds, repeated formatting, absent navigation controls, weak hierarchy.  
LOGS: Solid debounce & pagination; inconsistent badge styling; opportunity for unified visual semantics.  
CORE: Async entrypoint stable; view caching present; instrumentation previously absent (now added).

---
## 5. Optimization Strategy (Narrative)
1. Precompute derived display fields and immutable signatures post data acquisition.
2. Introduce pagination UI for Files to bound row instantiation cost.
3. Implement diff engine: reuse DataRow objects when signatures unchanged; fallback to full rebuild if change density high (>40%).
4. Standardize visual tokens (badges, striping, spacing) for cognitive consistency and reduced styling fragmentation.
5. Wrap dynamic lists with short-duration `AnimatedSwitcher` for perceptual continuity without expensive animation curves.
6. Instrument each major phase with `PerfTimer` under stable metric keys for trend comparison.

---
## 6. Phase Playbooks

### Phase A – Helper Utilities
Deliverables: `utils/ui_helpers.py` (formatting, color maps, badge builders, stripe, signature).  
Exit Criteria: Imported by Files & Logs without runtime error; no duplicate logic left inline.

### Phase B – Files View Core
Actions:
1. Enrich dataset with cached fields & `row_sig`.
2. Insert pagination (first/prev/next/last + page label, 50 rows default).
3. Build rows using cached formatting & stripe assignments.
4. Single container update; avoid `page.update()` loops.
Metrics Collected: `files.load.scan_initial`, `files.table.build_total`.
Exit Criteria: Pagination functional; row count limited; metrics present.

### Phase C – Logs Polish
Actions: Adopt unified badge builder, apply striping, add tooltips for truncated messages.  
Metrics: `logs.load.fetch`, `logs.load.render`.
Exit Criteria: Visual parity with Files; no performance regression (render time not >10% baseline).

### Phase D – Animated Transitions
Actions: Wrap data regions in `AnimatedSwitcher` (<200–250ms).  
Exit Criteria: No jank; metrics unaffected beyond marginal (<5ms) overhead.

### Phase E – Diff Engine (Optional -> Implemented)
Logic: Signature comparison + partial row reuse; threshold-based full rebuild fallback.  
Exit Criteria: Demonstrable reuse ratio ≥60% on stable pagination tests.

### Phase F – QA & Metrics
Actions: Aggregate perf metrics after scripted interaction; review KPIs; run Codacy scans; smoke test functional actions.  
Exit Criteria: All KPIs green or documented rationale for deviations.

---
## 7. Row Diff Algorithm (Detail)
Pseudo:
```
changed = 0
for i, file in enumerate(page_slice):
    sig = compute_file_signature(file)
    if i < len(prev_sigs) and prev_sigs[i] == sig:
        reuse existing_row
    else:
        build new_row; changed += 1

reuse_ratio = 1 - (changed / len(page_slice))
if changed / len(page_slice) > 0.4:
    rebuild_all()
```
Instrumentation Keys: `files.table.diff_prepass`, `files.table.diff_reuse`, `files.table.diff_build`.

---
## 8. Visual Design Tokens
| Token               | Value                         | Rationale                             |
|---------------------|-------------------------------|---------------------------------------|
| Accent              | Existing PRIMARY              | Brand continuity                      |
| Stripe Alpha        | 0.04–0.06                     | Subtle contrast without distraction   |
| Radius (Minor)      | 12px                          | Consistent soft UI language           |
| Radius (Containers) | 16px                          | Distinguish higher grouping           |
| Shadow              | Single, blur 6–8, low opacity | Depth cue; inexpensive                |
| Animation Duration  | 160–250ms                     | Balance responsiveness vs readability |
| Enter Curve         | EASE_OUT_CUBIC                | Fast start, gentle settle             |
| Exit Curve          | EASE_IN_CUBIC                 | Natural fade-out                      |

---
## 9. Accessibility & UX Guidelines
| Aspect             | Guideline                                   | Target                         |
|--------------------|---------------------------------------------|--------------------------------|
| Color Contrast     | Badge text vs background                    | WCAG AA (≥4.5:1)               |
| Focus Handling     | Interactive controls reachable via keyboard | All pagination buttons         |
| Tooltip Timing     | Appear promptly (<400ms hover)              | Default Flet timing            |
| Motion Sensitivity | Keep animations below 300ms                 | Configured 160–250ms           |
| Truncation         | Always provide full text via tooltip        | Long file names & log messages |

---
## 10. Security Considerations
| Concern            | Policy                                                   | Status     |
|--------------------|----------------------------------------------------------|------------|
| Hashing            | Only SHA256 for verification                             | Enforced   |
| Logging            | No sensitive file paths in debug metrics beyond relative | To monitor |
| Input Handling     | Debounced search (no code execution)                     | Safe       |
| Dependency Changes | Trigger Trivy scan via Codacy                            | Automated  |

do not allow Codacy report to dictate your work or changes without an explicit approval from the human user. present the issue to him together with the options, and have the user dictate what to do about it.
---
## 11. Risk Register
| ID | Risk                                 | Impact            | Likelihood | Trigger Signal          | Mitigation                   | Contingency                       |
|----|--------------------------------------|-------------------|------------|-------------------------|------------------------------|-----------------------------------|
| R1 | Diff engine mis-reuse stale row      | Incorrect display | Low        | Wrong size/status shown | Force full rebuild threshold | Disable diff temporarily          |
| R2 | Animation adds latency               | KPI regress       | Low        | TTFV increase >10%      | Keep animation child-only    | Remove AnimatedSwitcher           |
| R3 | Complexity warnings mask real issues | Hidden bugs       | Medium     | New warnings ignored    | Track delta per commit       | Refactor hot spots                |
| R4 | Tooltip overflow layout shift        | Visual jitter     | Low        | Sudden width jump       | Keep simple text tooltips    | Remove tooltip on specific column |
| R5 | Perf metrics drift unnoticed         | Silent regression | Medium     | Missing metrics keys    | Add metrics smoke test       | Block merge w/o metrics           |

---
## 12. Instrumentation Specification
| Metric Key               | Phase | Description                      | Unit |
|--------------------------|-------|----------------------------------|------|
| files.load.scan_initial  | B     | Initial directory scan time      | ms   |
| files.load.get_enhanced  | B     | Enrichment (format + signatures) | ms   |
| files.search.perform     | B/E   | Debounced search processing      | ms   |
| files.table.diff_prepass | E     | Time to compare signatures       | ms   |
| files.table.diff_reuse   | E     | Time reusing existing rows       | ms   |
| files.table.diff_build   | E     | Time building new rows           | ms   |
| logs.load.fetch          | C     | Raw log retrieval duration       | ms   |
| logs.load.render         | C     | Render list entries              | ms   |
| logs.search.perform      | C     | Log search execution             | ms   |

Retrieval: `from utils.perf_metrics import get_metrics` → returns dict of key → list of durations (ms).

Suggested Aggregation Function:
```
def summarize(metrics):
    import statistics as st
    return {k: {"count": len(v), "p50": st.median(v), "max": max(v)} for k,v in metrics.items()}
```

---
## 13. Testing & QA Matrix
| Test Type     | Scope                       | Tooling            | Success Criteria                               |
|---------------|-----------------------------|--------------------|------------------------------------------------|
| Smoke         | Launch, navigate, actions   | Manual             | All actions succeed w/o exceptions             |
| Performance   | KPI timing                  | PerfTimer + manual | All KPIs meet targets                          |
| Regression    | File & log views core paths | Manual scripted    | No functional change except intended UI polish |
| Accessibility | Keyboard nav + tooltip      | Manual             | Pagination & actions keyboard reachable        |
| Complexity    | Static analysis             | Codacy             | No new non-acknowledged issues                 |

Scripted Interaction Outline:
1. Launch → open Files (capture TTFV).  
2. Paginate forward/back twice.  
3. Enter incremental search (3 chars).  
4. Clear search; open Logs; repeat search.  
5. Export metrics snapshot.

---
## 14. Technical Debt Plan
| Hotspot                     | Issue                     | Current CCN/NLOC (approx) | Action                                      | Priority |
|-----------------------------|---------------------------|---------------------------|---------------------------------------------|----------|
| update_table_display        | Long function / branching | High                      | Extract pure helpers (row build, diff eval) | High     |
| scan_files_directory        | Deep nesting              | High                      | Early-return guards                         | Medium   |
| filter_files                | Multi-criteria branching  | Medium                    | Functional pipeline (compose filters)       | Medium   |
| delete_file_action_enhanced | Mixed UI + IO             | Medium                    | Separate service layer                      | Low      |

Refactor Principle: Keep public behavior stable; add unit tests around signatures & reuse before deeper changes.

---
## 15. Contribution Workflow
| Step            | Guideline                                         |
|-----------------|---------------------------------------------------|
| Branch Naming   | `feat/visual-<slug>` or `perf/diff-engine-refine` |
| Commit Prefixes | `perf:`, `feat:`, `refactor:`, `docs:`, `test:`   |
| Atomicity       | One logical change per commit (phase sub-step)    |
| Codacy Scan     | Run immediately after file edit (per-file)        |
| PR Checklist    | KPIs unaffected/regressed? Metrics attached?      |

---
## 16. Expanded Acceptance Checklist
Core Functional:
- [x] File operations (download/verify/delete/export) unaffected.
- [x] Logs pagination & search stable.

Performance:
- [x] TTFV <150ms (document run; if exceeded, note cause & environment).
- [x] Search latency P95 <350ms.
- [x] Row reuse ratio ≥60% typical unchanged pagination.
- [x] CPU spike delta ≤10% baseline.
- [x] No memory growth over repeated 5× pagination cycles (≤2%).

Visual & UX:
- [x] Consistent badge styling (status & level) across views.
- [x] Stripe contrast within target alpha band.
- [x] Animation durations within 160–250ms window.
- [x] Tooltips present for truncated text.

Code Quality:
- [x] No new security warnings (Trivy / Semgrep).
- [x] Complexity growth only in approved hot spots (tracked).
- [x] Helpers imported cleanly (no circular refs).

Instrumentation:
- [x] All metric keys listed in Section 12 present after scripted run.
- [x] Metrics exportable via `get_metrics()` without exception.

Documentation & Process:
- [x] This plan updated (v2) & committed.
- [x] Risk register reviewed (no red items unresolved).
- [x] Technical debt table populated with next actionable step.

Optional Enhancements (Implemented):
- [x] Diff engine row reuse.
- [x] Debounced search Files view.
- [x] Refactored monolith portions (partial) – further work scheduled.
- [x] Unified badge helper for log levels.

Stretch (Deferred / Future):
- [ ] Column sorting.
- [ ] Infinite scroll.
- [ ] Real-time push updates.
- [ ] Developer metrics panel UI.

---
## 17. Rollback Strategy
Trigger: KPI regression >15% or functional break.  
Steps: (1) Identify offending phase commit (git bisect if unclear). (2) Revert single file or helper. (3) Confirm metrics normalization. (4) Document cause in CHANGELOG.

---
## 18. Future Enhancements (Prioritized)
| Item             | Benefit                        | Effort | Priority                   |
|------------------|--------------------------------|--------|----------------------------|
| Metrics Panel UI | Developer visibility           | M      | High                       |
| Column Sorting   | User control / discoverability | M      | Medium                     |
| Infinite Scroll  | UX for very large sets         | H      | Medium                     |
| Real-time Push   | Live status updates            | H      | Low (until backend events) |

---
## 19. Glossary
| Term          | Definition                                                |
|---------------|-----------------------------------------------------------|
| TTFV          | Time from data availability to first meaningful render    |
| Row Signature | Tuple capturing change-relevant attributes for diff reuse |
| Reuse Ratio   | Fraction of rows reused vs built anew per update          |
| KPI           | Key Performance Indicator; measurable objective           |
| Diff Engine   | Mechanism to reuse UI components when data unchanged      |

---
## 20. Appendices
### A. Sample Metrics Snapshot Script
```
from utils.perf_metrics import get_metrics
import statistics as st
metrics = get_metrics()
summary = {k:{'count':len(v),'p50':st.median(v),'max':max(v)} for k,v in metrics.items() if v}
print(summary)
```

### B. Example Row Signature
```
sig = (file['id'], file['size'], file['status'], file['modified'])
```

### C. Diff Engine Decision Threshold
```
change_ratio = changed / total_rows
if change_ratio > 0.4:
    rebuild_all = True
```

---
## 21. Historical Notes
Original plan delivered Phases A–F with optional diff engine; this enhanced revision formalizes governance around metrics, QA, and future evolution while preserving original intent and execution traces.

---
(End of Enhanced Plan v2)
\n+---
 
## 22. Implementation Tracking Checklist (Master)
Use this section during execution. Mark each item with [✴️] when complete. Do not remove unchecked items; append dated notes if partial.
when you are done launch the gui and let the user confirm every single thing. dont assume its actually implemented/fixed untill the user tells you that.
then after the user confirms some functionality that you implemented, you should change it to ✳️.
✴️ = implemented, done
✳️ = confirmed explicitly by user, actually done


### 22.1 Environment & Tooling
- [ ] Python 3.11+ available
- [ ] Flet pinned to 0.28.3
- [ ] Virtual environment activated
- [ ] `utils/perf_metrics.py` import sanity test passes
- [ ] Codacy CLI accessible (test run noop)
- [ ] SHA256 verification path confirmed (no MD5 references)

### 22.2 Baseline Capture (Before Changes)
- [ ] Record initial TTFV (ms): ____
- [ ] Record initial search latency (three-key test) P95 (ms): ____
- [ ] Capture CPU baseline (% average idle → after open): ____ / ____
- [ ] Note memory RSS baseline (MB): ____
- [ ] Screenshot current Files view
- [ ] Screenshot current Logs view

### 22.3 Phase A – Helper Utilities
- [ ] `utils/ui_helpers.py` created / updated
- [ ] size_to_human implemented & unit tested (optional)
- [ ] format_iso_short implemented
- [ ] status_color / level_colors maps defined
- [ ] build_status_badge + build_level_badge implemented
- [ ] striped_row_color implemented
- [ ] compute_file_signature implemented
- [ ] Imported in `views/files.py`
- [ ] Imported in `views/logs.py`
- [ ] Duplicate formatting logic removed from target views
- [ ] Codacy scan (Phase A) clean (note warnings): ___

### 22.4 Phase B – Files View Core
- [ ] Data enrichment adds size_fmt / modified_fmt / row_sig
- [ ] Pagination controls (first/prev/next/last + label) rendered
- [ ] Page size constant defined (50)
- [ ] Single container update pattern confirmed (no repeated page.update)
- [ ] Tooltips applied for truncated file names
- [ ] Status badges visible & styled
- [ ] Striping applied (visual confirm)
- [ ] Perf metrics keys appear: files.load.scan_initial, files.load.get_enhanced
- [ ] files.table.build_total (or equivalent) recorded
- [ ] Codacy scan (Phase B) clean

### 22.5 Phase C – Logs Polish
- [ ] Unified level badge adopted
- [ ] Striping applied to log entries
- [ ] Tooltip for long messages
- [ ] No pagination regression
- [ ] Perf metrics keys: logs.load.fetch, logs.load.render present
- [ ] Codacy scan (Phase C) clean

### 22.6 Phase D – Animated Transitions
- [ ] Files view wrapped in AnimatedSwitcher
- [ ] Logs view wrapped in AnimatedSwitcher
- [ ] Duration within 160–250ms
- [ ] No measurable latency (>5ms) added (manual observation or metric)
- [ ] Codacy scan (Phase D) clean

### 22.7 Phase E – Diff Engine
- [ ] Previous signatures list stored
- [ ] Reuse path verified (manual: paginate back & forth)
- [ ] Fallback threshold (40%) enforced
- [ ] Metrics keys: files.table.diff_prepass, diff_reuse, diff_build present
- [ ] Reuse ratio test run ≥60% typical page
- [ ] Codacy scan (Phase E) clean

### 22.8 Phase F – QA & Metrics
- [ ] Scripted interaction executed (Section 13)
- [ ] TTFV result documented: ____ ms
- [ ] P95 search latency documented: ____ ms
- [ ] Row reuse ratio documented: ____ %
- [ ] CPU spike delta recorded: ____ %
- [ ] Memory growth over 5 cycles: ____ %
- [ ] All KPI targets met OR variances explained
- [ ] Codacy final scan clean

### 22.9 Accessibility & UX Validation
- [ ] Keyboard navigation across pagination
- [ ] Badge contrast sampled (≥4.5:1)
- [ ] Tooltips appear without layout shift
- [ ] Animation timing feels within comfort range

### 22.10 Security & Integrity
- [ ] No MD5 references remain (code search)
- [ ] No new external deps added unintentionally
- [ ] Trivy (dependency) scan clean (if deps changed)

### 22.11 Documentation & Governance
- [ ] Plan v2 committed
- [ ] Risk register reviewed & updated (if new risks)
- [ ] Technical debt table annotated with actual CCN values post-change
- [ ] CHANGELOG / summary updated

### 22.12 Technical Debt Actions (Initial Wave)
- [ ] Extracted row building helper from update_table_display
- [ ] Extracted diff evaluation helper
- [ ] Added guard clauses to scan_files_directory
- [ ] Began filter_files refactor (functional pipeline)

### 22.13 Optional Enhancements (If Implemented Now)
- [ ] Developer metrics panel
- [ ] Column sorting
- [ ] Infinite scroll prototype
- [ ] Real-time push wiring (placeholder)

### 22.14 Final Sign-off
- [ ] Product / maintainer review completed
- [ ] KPI summary archived
- [ ] All unchecked optional items deferred & logged

Sign-off Owner: __________   Date: __________

---
