---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

---
description: Essential AI development guidance for the encrypted backup framework
applyTo: '**'
---

# Copilot Instructions - Encrypted Backup Framework

AI coding agents should follow these guidelines when working on this multi-component encrypted backup system.

## 🧠 AI Persona

- **Role**: Professional Software Engineer, Expert Flet UI/UX Designer, Frontend Specialist.
- **Flet Version**: Always use Flet version 0.28.3 components.
- **Reasoning**: Use ultrathink and sequential thinking to enhance reasoning capabilities.
- **Effort**: Apply the highest degree of reasoning effort.
- **Code Quality**: Write working code and avoid breaking existing functionality.
- **Tool Usage**: Leverage available tools (context7, MCP, web search, fetch) as needed.
- **Implementation**: Implement plans to the highest degree.

## 🏗️ System Architecture

This is a **5-component encrypted backup framework**:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   C++ Client    │───▶│  Python Server   │───▶│    Database     │
│                 │    │                  │    │   (SQLite3)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Web GUI (JS)    │    │ Desktop GUI      │    │ Server Bridge   │
│ Tailwind CSS    │    │ (FletV2)         │    │ Communication   │
└─────────────────┘    └──────────────────┘    └─────────────────┘

```

### When going through massive logs:
🔹 On-Disk + Grep/Awk Tools
If you don’t want the overhead:
ripgrep (rg) or ag (silversearcher) – insanely fast search in files.
ast-grep – structured searching if logs have consistent format (JSON logs).
fzf – fuzzy finder, useful when you know part of the error.
Pipe logs through grep | tail -n 50 style workflows.

🔹 Using ripgrep (rg)
Fastest way to pull out the “couple of bad lines.”
Find all ERROR lines:
rg "ERROR" app.log
Show 5 lines of context around each match:
rg -C 5 "Exception" app.log
Search across multiple logs at once:
rg "timeout" /var/logs/
Stream logs + highlight in real time:
tail -f app.log | rg "ERROR"

🔹 Using ast-grep
Best if your logs are structured (e.g., JSON). Lets you query fields instead of regex spaghetti.
Example log (JSON):
{"level": "ERROR", "msg": "Database connection failed", "code": 500}
Find all ERROR-level logs:
sg -p ' { "level": "ERROR", ... } ' logs.json
Find logs with specific error codes:
sg -p ' { "code": 500, ... } ' logs.json
Match only the message field:
sg -p ' { "msg": $MSG } ' logs.json

🚀 Pro tip
Use ripgrep when you’re just scanning for keywords.
Use ast-grep when your logs are JSON or structured, so you can surgically extract only what matters.
Combine them with fzf (if you install it) for interactive filtering.



**Encryption**: RSA-1024 key exchange + AES-256-CBC file encryption
**Database**: SQLite3 with clients, files, logs tables
**Communication**: Socket-based with JSON protocol

## 🚨 CRITICAL STARTUP ISSUE ALERT

**⚠️ STARTUP PROBLEM NOT FIXED**: The FletV2 application currently hangs on a "Loading..." screen at startup. The dashboard only appears after manual navigation. This is the PRIMARY issue that needs to be resolved.

**Previous Attempts**: 
- ✅ Made main function async (Flet 0.21.0+ requirement)
- ✅ Simplified `_create_enhanced_view` method
- ❌ **ISSUE PERSISTS** - Loading screen still appears

**Root Cause**: Complex async detection in `_create_enhanced_view` method incorrectly treats synchronous view functions as async, causing placeholder display.

**Reference**: See `important_docs/new_agent_onboarding.md` for comprehensive context and mission objectives.

---

## 🎯 Primary Development Directory

**CRITICAL**: Work exclusively with `FletV2/` directory for desktop GUI development.
- `flet_server_gui/` is obsolete and over-engineered
- Reference `CLAUDE.md` for detailed Flet patterns and best practices

## 🚀 Launch Commands

```bash
# FletV2 Development (Hot Reload)
cd FletV2 && flet run -r main.py

# FletV2 Production (ASYNC REQUIRED - Flet 0.21.0+)
cd FletV2 && python main.py

# System Integration Testing
python scripts/one_click_build_and_run.py
```

**CRITICAL**: Main function must be `async def main(page: ft.Page)` and use `asyncio.run(ft.app_async(target=main, view=ft.AppView.FLET_APP))`

## 📁 Key Directories & Files

```
FletV2/                           # Desktop GUI (PRIMARY)
├── main.py                       # Application entry point
├── theme.py                      # Material Design 3 theming
├── views/                        # UI views (function-based)
│   ├── dashboard.py              # Server overview
│   ├── clients.py                # Client management
│   ├── files.py                  # File browser
│   ├── database.py               # Database viewer
│   └── database.py               # Database viewer
│   ├── analytics.py          # Analytics charts
│   ├── logs.py               # Log viewer
│   └── settings.py           # Configuration
└── utils/                        # Helper utilities
    ├── server_bridge.py          # Server communication
    ├── debug_setup.py          # Enhanced terminal debugging
    └── utf8_solution.py          # UTF-8 handling

python_server/                    # Backend server
Client/                           # C++ client application
api_server/                       # Flask web API bridge
scripts/                          # Automation tools
```

## 🔧 Critical Development Patterns

### **Framework Harmony (Flet)**
- Use `ft.NavigationRail` for navigation (not custom routers)
- Use `expand=True` + `ResponsiveRow` for layouts
- Use `control.update()` not `page.update()` for performance
- Prefer Flet built-ins over custom components

### **UTF-8 Handling**
```python
# ALWAYS import in files with subprocess/console I/O
import Shared.utils.utf8_solution
```

### **Enhanced Debugging Setup**
```python
# ALWAYS use at the top of main.py and other entry points
from utils.debug_setup import setup_terminal_debugging, get_logger
logger = setup_terminal_debugging(logger_name="YourModuleName")
```

### **Server Bridge Pattern**
```python
# Enhanced bridge with fallback
from utils.server_bridge import ServerBridge, create_server_bridge
BRIDGE_TYPE = "Unified Server Bridge (with built-in mock fallback)"
```

### **State Management System**
```python
# Reactive UI updates with real-time subscriptions
from utils.state_manager import StateManager, create_state_manager
state_manager = create_state_manager(page)

# Subscribe to real-time updates
state_manager.subscribe("server_status", callback_function)
```

### **File Size Guidelines**
- View files: ~200-500 lines maximum
- Component files: ~100-400 lines maximum
- If >600 lines: mandatory decomposition required

## 🚨 Anti-Patterns (Never Do These)

- Custom navigation managers (use `ft.NavigationRail`)
- Custom responsive systems (use `expand=True`)
- Complex theme managers (use `page.theme`)
- `page.update()` abuse (use `control.update()`)
- Hardcoded dimensions (use responsive patterns)

## 🔍 Integration Points

### **Database Schema**
- `clients` table: id, name, status, last_seen
- `files` table: id, client_id, filename, path, size, checksum
- `logs` table: id, timestamp, level, component, message

### **Communication Protocol**
- JSON-based socket communication
- Server bridge handles connection management
- Automatic fallback to mock data for development

### **Development Workflow**
1. Develop in `FletV2/` using hot reload
2. Test with mock data (automatic fallback)
3. Integration test with full system
4. Reference `CLAUDE.md` for detailed Flet guidance
5. **CRITICAL**: Read `important_docs/new_agent_onboarding.md` for comprehensive project context and startup problem analysis

### **Documentation Resources**
- `important_docs/new_agent_onboarding.md` - **CRITICAL**: Complete context for new agents, startup problem analysis
- `important_docs/emoji_inventory.md` - Comprehensive emoji inventory
- `important_docs/FletV2_Architecture_Blueprint.md` - System design and architecture
- `important_docs/FletV2_Infrastructure_Enhancement_Summary.md` - Recent improvements
- `important_docs/FletV2_Issues.md` - Known problems and solutions
- `important_docs/Consolidated_Context7_Flet_Desktop_Framework.md` - Framework guide
- `PERFORMANCE_OPTIMIZATION_SUMMARY.md` - Documenting timers & usage
- `important_docs/emoji_inventory.md` - Comprehensive emoji inventory

## 💡 Quick Reference

- **Theme**: Material Design 3 with system detection
- **Colors**: Semantic color tokens (`ft.Colors.PRIMARY`)
- **Layout**: Responsive with `ft.ResponsiveRow`
- **Navigation**: `ft.NavigationRail` with 7 destinations
- **Data**: Server bridge with automatic mock fallback
- **Encryption**: RSA + AES for secure file transfer
- **Documentation**: See `important_docs/new_agent_onboarding.md` for comprehensive context
- **Startup Issue**: App hangs on loading screen - PRIMARY issue to resolve

Follow these patterns for consistent, maintainable code that works with the framework rather than against it.

│   ├── dashboard.py          # Server dashboard
│   ├── clients.py            # Client management
│   ├── files.py              # File browser
│   ├── database.py           # Database viewer
│   ├── analytics.py          # Analytics charts
│   ├── logs.py               # Log viewer
│   └── settings.py           # Configuration
└── utils/                     # Helper utilities
    ├── debug_setup.py        # Terminal debugging
    ├── server_bridge.py      # Full server integration
    └── simple_server_bridge.py # Fallback bridge
```

### **Launch Commands**
```bash
# FletV2 Desktop (Production/Testing)
cd FletV2 && python main.py

# FletV2 Development with Hot Reload (RECOMMENDED for development)
# Uses desktop for instant hot reload - identical runtime behavior to native desktop while enabling instant hot reload. The workflow is: develop in browser → test in native desktop → deploy as desktop app.
cd FletV2
flet run -r main.py

# Alternative: Command-line hot reload
cd FletV2 && flet run --web main.py

# System integration testing (only after FletV2 is complete, and the user approved)
python scripts/one_click_build_and_run.py
```

### **Development Workflow (Desktop Apps)**
  ★ Insight ─────────────────────────────────────
  Hot Reload Validation: The WEB_BROWSER view for desktop development is a Flet best practice - it provides identical runtime behavior to native desktop while enabling instant hot reload. The workflow is: develop in browser → test in native desktop → deploy as desktop app.
  ─────────────────────────────────────────────────
**Recommended Pattern**: Develop in browser → Test in native desktop → Deploy as desktop app
- **Browser development**: Instant hot reload, identical Flet runtime, browser dev tools available
- **Native testing**: Final validation of desktop-specific features, window management, OS integration
- **Both modes**: Run the exact same Flet application code - no differences in functionality

---

## 🔧 SEARCH & DEVELOPMENT TOOLS

You have access to ast-grep for syntax-aware searching:
- **Structural matching**: `ast-grep --lang python -p 'class $NAME($BASE)'`
- **Fallback to ripgrep**: Only when ast-grep isn't applicable
- **Never use basic grep**: ripgrep is always better for codebase searches (basic grep when other tools fail)

### **Sequential Thinking Tool**
For complex problem analysis and systematic debugging:
```python
# Use sequential thinking for:
# - Startup problem diagnosis
# - Complex refactoring analysis
# - Multi-step problem solving
# - Architectural decision making
```

---

## 💡 KEY INSIGHTS

**★ Framework Enlightenment**: Desktop resizable apps with navigation are trivial in Flet. The entire application can be ~700 lines instead of 10,000+ lines of framework-fighting code(not really, but to illustrate the point).

**★ The Semi-Nuclear Protocol**: When refactoring complex code, analyze first to understand TRUE intentions, then rebuild with simple Flet patterns while preserving valuable business logic, achieving feature parity.

**★ Performance Secret**: Replacing `page.update()` with `control.update()` can improve performance by 10x+ and eliminate UI flicker.

**★ Flet Version Requirements**: Flet 0.21.0+ is required for async-first architecture. Main function must be async and use `asyncio.run(ft.app_async())`.

**The FletV2 directory is the CANONICAL REFERENCE** for proper Flet desktop development. When in doubt, follow its examples exactly.

---

## 📝 .gitignore Management
When modifying the `.gitignore` file, adhere to the following guidelines:
- **Avoid Duplication**: Ensure each ignore rule is unique and doesn't overlap with existing rules.
- **Consolidation**: Group related rules together (e.g., all `.vscode` related ignores should be under the `.vscode/*` section).
- **Clarity**: Use comments to explain complex or project-specific ignore rules.

---

## 💻 VS Code Configuration

### **Python Interpreter Path**
To ensure VS Code uses the correct Python interpreter for the FletV2 project, set the `python.defaultInterpreterPath` in `.vscode/settings.json` to the Flet virtual environment:

```jsonc
{
    // ...existing code...
    "python.defaultInterpreterPath": "./flet_venv/Scripts/python.exe",
    // ...existing code...
}
```

---

## 🐛 Debugging

### **Consolidated Debugging Report Guidelines:**
- **Severity Ranking**: Prioritize issues by severity (High, Medium, Low).
- **Symptom Description**: Clearly describe the observed behavior.
- **Root Cause Analysis**: Explain the underlying cause of the issue.
- **Status Tracking**: Track issues from discovery to resolution, including regressions.
- **Asynchronous Task Management**: Pay close attention to the correct usage of async/await patterns in Flet.
- **Dependency Management**: Ensure all required packages are correctly installed and listed in the project's environment.

### **Known Issues:**
- **Systemic Asynchronous Task Crash**:
    - **Symptom**: Application crashes on startup or during specific actions due to `RuntimeError: no running event loop`.
    - **Root Cause**: Incorrect use of `asyncio.create_task()` from synchronous functions.
    - **Status**: Critical. Requires immediate attention and architectural review.
- **Data Sourcing Failure**:
    - **Symptom**: Application consistently displays mock data instead of live information.
    - **Root Cause**: `ServerBridge` component starts in `FALLBACK` mode.
    - **Status**: Persistent and Critical. Investigate backend connection issues.
- **UI Race Condition in Clients View**:
    - **Symptom**: Initial list of clients fails to appear in the "Clients" view.
    - **Root Cause**: Data population logic runs before the UI `DataTable` control is rendered.
    - **Status**: Persistent. Ensure UI elements are fully initialized before populating data.
- **Incorrect API Usage**:
    - **Symptom**: `AttributeError: 'Page' object has no attribute 'after'` when interacting with UI elements.
    - **Root Cause**: Attempt to call non-existent methods on Flet objects.
    - **Status**: Unresolved. Review API usage and consult Flet documentation.

---

**Last Updated**: September 9, 2025
**Project Status**: FletV2 GUI launched successfully. Startup loading screen issue appears to be resolved. Requires further testing and visual optimization based on `Gpt5_Visual_Optimization_Plan_09092025.md`.
**Priority**: Visual optimization and ensure stability.

### **Visual Optimization Plan Progress:**
- **Phase A (Helper Utilities):** ✅
- **Phase B (Files View Pagination & Formatting):** ✅
  - Replaced legacy MD5 with SHA256 in files verify path. ✅
- **Phase C (Logs View Enhancements):** ✅
  - Removed unused build_status_badge import in logs view (warning cleared). ✅
- **Phase E (Diff Engine):** ✅
- **Phase F (Performance Metrics):** ✅
  - Added `perf_metrics.py` (PerfTimer, record_metric, get_metrics, reset_metrics).
  - Instrumented Files view: initial scan, enhanced load, search, table total, slice, prepass, rebuild/partial paths.
  - Instrumented Logs view: search, load fetch, load render.
  - Created `PERFORMANCE_OPTIMIZATION_SUMMARY.md` documenting timers & usage.

### **Ongoing Tasks:**
- ✅ Add debounced search (Files view)
- ✅ Refactor update_table_display (reduced from 157→86 lines; CCN still high but improved)
- ✅ Unify logs level badge helper
- Cleanup unused imports/files view

### **Complexity Warnings:**
- NLOC (Number of Lines of Code): Function body length. Exceeds maintainability thresholds (e.g., 50). Harder to scan/test.
- Cyclomatic Complexity (CCN): Count of independent paths (branches, loops, exceptions). Higher CCN (e.g., 17–30) raises risk of hidden bugs and insufficient test coverage.
- File NLOC: Total non-empty logical lines in file. Over 500 indicates monolith; refactor into modules.
- Affected hotspots:
  - update_table_display (now 86 lines, down from 157; CCN still high but improved) – added diff logic + pagination/status + dual build paths.
  - filter_files (branches across multiple filters).
  - scan_files_directory / get_files_data: nested conditionals and path logic.
  - Async operations (load_files_data_async, delete_file_action_enhanced.confirm_delete_async) combine UI + IO + branching.
  - create_files_view wrapper function itself (too many nested helpers in closure scope).

### **Mitigation Strategy:**
- Extract pure helpers (signatures, row build, pagination status formatting).
- Isolate IO vs UI code (e.g., file scanning vs control creation).
- Reduce nested if/else by early returns / guard clauses.

#### Detailed Removal/Change Audit (From Enhanced Plan)
1. Success Criteria bullet list
Replaced by: KPI table (Section 1)
Justification: Converted qualitative bullets into quantifiable metrics (traceable & automatable).
Risk: Possible loss of plain-language intent.
Mitigation: KPI definitions + glossary.

2. Constraints & Compatibility table
Replaced by: Environment & Prerequisites (Section 2) + Architectural Principles (Section 3)
Justification: Split operational setup (version, hashing, tooling) from enduring design principles; reduced mixed concerns.
Risk: Harder to see all constraints at once.
Mitigation: Two focused tables

3. Verbose Baseline bullet lists (per-view)
Replaced by: Condensed Baseline Assessment paragraph (Section 4)
Justification: Removed repetition already implied by later phase playbooks.
Risk: Slightly less narrative context.
Mitigation: Phase playbooks retain actionable specifics.

4. Original Optimization Strategy numbered list + Visual Polish sub‑bullets
Replaced by: Narrative Strategy (Section 5) + Design Tokens (Section 8)
Justification: Separated mechanics vs styling tokens; improved semantic grouping.
Risk: Readers may miss a single “all-in-one” checklist.
Mitigation: Phase Playbooks encode execution steps.

5. Implementation Phases summary table
Replaced by: Phase Playbooks (Section 6) with exit criteria & metrics keys
Justification: Table lacked room for metrics/exit criteria; playbook format adds operational clarity.
Risk: Less compact overview.
Mitigation: Section headings scannable; glossary added.

6. Detailed Task Breakdown (Phases A–D) section
Merged into: Phase Playbooks (removed duplication)
Justification: Eliminated two sources of truth.
Risk: None (content preserved).

7. Standalone Row Diff (Phase E) brief pseudo
Replaced by: Expanded Row Diff Algorithm (Section 7) with reuse ratio logic & instrumentation keys
Justification: Added observability + decision thresholds.
Risk: Slightly longer to read.
Mitigation: Pseudo kept concise.

8. Visual Design Tokens bullet list
Replaced by: Token table with rationale (Section 8)
Justification: Adds reasoning column → design defensibility.
Risk: None.

9. Risks & Mitigations simple table
Replaced by: Risk Register (Section 11) with IDs, triggers, contingency
Justification: Moves from static awareness to operational risk management.
Risk: Moves from static awareness to operational risk management.
Risk: Slight complexity increase.
Mitigation: Limited to 5 high-signal risks.

10. Validation & Metrics “Manual quick checks” list
Replaced by: KPI table + Instrumentation Spec (Section 12) + QA Matrix (Section 13)
Justification: Moves to measurable, repeatable framework; explicit metric keys.
Risk: Loss of informal guidance tone.
Mitigation: Scripted interaction outline reintroduced.

11. Rollback Plan early placement
Moved to: Section 17
Justification: Grouped near Acceptance & Future for lifecycle continuity.
Risk: Slightly later discovery.
Mitigation: TOC-like sectional organization.

12. Future Enhancements (unsorted list)
Replaced by: Prioritized matrix (Section 18) + Stretch list inside Acceptance
Justification: Adds effort/prioritization dimension → planning clarity.
Risk: Subjective effort labels.
Mitigation: Clearly marked “Prioritized”.

13. Execution Order enumerated list
Replaced by: Implied flow via Phase Playbooks + Contribution Workflow (Section 15)
Justification: Avoided divergence between “order” list and actual working practice; workflow now enforces gating (metrics, scans).
Risk: New contributors may want explicit sequence.
Mitigation: Phase numbers still indicate natural order.

14. Original Acceptance Checklist
Replaced by: Expanded Acceptance (Section 16) segmented (Functional / Performance / UX / Code / Instrumentation / Process)
Justification: Improves traceability to KPIs & risk register.
Risk: Larger list might discourage completion.
Mitigation: Logical grouping reduces cognitive load.

15. Notes section (patch size, Codacy reminder, contingency for DataRow color)
Integrated into: Architectural Principles (reversibility), Contribution Workflow (per-file scans), Visual Tokens (fallback rationale implied), Rollback Strategy.
Justification: Removed orphan advice; embedded where actionable.
Risk: Specific fallback (DataRow color unsupported) less prominent.
Mitigation: Can re-add as an inline footnote if still needed.

16. Explicit “Keep changes incremental, reversible, and Codacy‑clean” wording in Objectives
Reframed as: Architectural Principle “Reversible Changes” + Contribution Workflow + Code Quality segment
Justification: De-duplicated phrasing; encoded as enforceable principle.
Risk: Tone less direct.
Mitigation: Principle table concise.

Net Effect:
- Removed redundancy (dual phase descriptions, overlapping strategy vs tasks).
- Elevated measurability (KPIs, instrumentation keys).
- Increased operational resilience (risk register, rollback, debt plan).
- Added governance (contribution workflow, prioritized enhancements).

If you want any removed micro-detail reinstated (e.g., explicit DataRow color fallback), specify and it can be reinserted minimally.

### **Implementation Tracking Checklist**

This checklist is intended for tracking progress during the implementation of the visual optimization plan. Mark items as you complete them.

**General Setup**
- [ ] Read and understand `important_docs/new_agent_onboarding.md`
- [ ] Activate the `flet_venv` virtual environment
- [ ] Verify Flet version 0.28.3 is being used

**Phase A: Helper Utilities**
- [ ] Implement helper utilities as defined in the plan

**Phase B: Files View Pagination & Formatting**
- [ ] Implement pagination in Files view
- [ ] Implement formatting optimizations in Files view
- [ ] Replace legacy MD5 with SHA256 in files verify path

**Phase C: Logs View Enhancements**
- [ ] Enhance Logs view according to the plan
- [ ] Remove unused `build_status_badge` import in logs view

**Phase E: Diff Engine**
- [ ] Implement diff engine with signature-based reuse
- [ ] Integrate caching arrays: `previous_page_signatures`, `previous_page_rows`

**Phase F: Performance Metrics**
- [ ] Add `perf_metrics.py` (PerfTimer, record_metric, get_metrics, reset_metrics)
- [ ] Instrument Files view (initial scan, enhanced load, search, table total, slice, prepass, rebuild/partial paths)
- [ ] Instrument Logs view (search, load fetch, load render)
- [ ] Create `PERFORMANCE_OPTIMIZATION_SUMMARY.md` documenting timers & usage

**Refactoring**
- [ ] Add debounced search (Files view)
- [ ] Refactor `update_table_display`
- [ ] Unify logs level badge helper
- [ ] Cleanup unused imports/files view

**Documentation**
- [ ] Update relevant documentation with changes

**Testing & QA**
- [ ] Perform functional testing of all modified features
- [ ] Conduct performance testing and record metrics
- [ ] Verify accessibility and responsiveness

**Code Quality**
- [ ] Run Codacy analysis and address any new issues
- [ ] Address any complexity warnings identified

**Final Steps**
- [ ] Review all changes and ensure they meet requirements
- [ ] Commit changes with appropriate commit messages

### **Debugging**
#### **Final Combined Debugging Report**
Based on the analysis of all provided logs, here is a consolidated summary of the issues found in the Flet application, ranked by severity. This report tracks issues from their initial discovery, through fixes, to regressions.
##### **High-Severity Issues (Application-Breaking)**
- **Systemic Asynchronous Task Crash: RuntimeError: no running event loop (CRITICAL REGRESSION)**
    - **Symptom**: The application crashes on startup when trying to load the initial dashboard view. Previously, this same error occurred when clicking the "Refresh" button.
    - **Root Cause**: There is a recurring architectural flaw in how asynchronous tasks are being called. The code incorrectly uses asyncio.create_task() from synchronous functions (first in an on_click handler, and now in the create_dashboard_view function). This pattern is fundamentally incompatible with Flet's event model.
    - **Status**: Critical Regression. Although one instance of this bug was fixed, its reappearance at startup indicates a core misunderstanding of how to manage async operations in Flet. This is the highest priority bug to fix.
- **Missing Dependency: ModuleNotFoundError: No module named 'aiofiles' (FIXED)**
    - **Symptom**: The application crashed instantly when started directly with python main.py.
    - **Root Cause**: A required package, aiofiles, was not listed or installed in the project's environment.
    - **Status**: Resolved. The logs show a successful pip install aiofiles.
- **Incorrect API Usage: AttributeError: 'Page' object has no attribute 'after' (Unresolved)**
    - **Symptom**: Clicking the theme-toggle button in the Settings view causes an AttributeError.
    - **Root Cause**: The event handler _on_theme_toggle in main.py attempts to call self.page.after(...), a method that does not exist on the Flet Page object.
    - **Status**: Unresolved.
##### **Medium-Severity Issues (Functionality-Impairing)**
- **Data Sourcing Failure (Persistent and Critical)**
    - **Symptom**: The application consistently displays mock data instead of live information across all views.
    - **Root Cause**: The ServerBridge component is confirmed to be starting in FALLBACK mode in every log. This indicates a fundamental inability to connect to its intended backend data source.
    - **Status**: Persistent and Critical. While the app doesn't crash because of this, its primary purpose is defeated. This is the most significant unresolved functional issue after the startup crash.
- **UI Race Condition in Clients View (Persistent)**
    - **Symptom**: When navigating to the "Clients" view, the initial list of clients fails to appear.
    - **Root Cause**: A recurring WARNING (Table reference update failed: DataTable Control must be added to the page first) shows that the data population logic runs before the UI DataTable control has been rendered.
    - **Status**: Persistent and Unresolved.
##### **Low-Severity Issues (Inefficiencies & Environment)**
- **Redundant UI Label Updates (Minor)**
    - **Symptom**: Labels showing item counts are updated twice in rapid succession.
    - **Root Cause**: The view-updating logic contains a redundancy.
    - **Status**: Minor. A non-critical inefficiency.
- **Development Environment Tooling (Minor)**
    - **Symptom**: Attempts to run the pyflakes linter failed.
    - **Root Cause**: pyflakes was not installed, and a shell command (|| true) incompatible with PowerShell was used.
    - **Status**: Minor. Indicates a small issue in the development workflow setup.

### **AI Agent Prompt**
```text
Claude Sonnet 4 Agent Prompt — Implement the GPT-5 Visual Optimization Plan

You are an expert software engineer agent. Your mission: implement the "GPT-5 Visual Optimization & Performance Plan (Enhanced v2)" located at `Gpt5_Visual_Optimization_Plan_09092025.md` in this repository, and complete Phases A–F end-to-end until all Acceptance Checklist items are satisfied or explained. Work in the FletV2 desktop GUI area; focus on `views/files.py`, `views/logs.py`, and `utils/` helpers.

Behavioral contract (must-follow)
- Work sequentially, phase-by-phase (A → B → C → D → E → F). Do not skip phases.
- Before editing any file, create a git branch named `perf/<your-short-slug>` and only edit that branch.
- After editing each file, run Codacy per-repo policy (codacy_cli_analyze) for that file and, if dependencies changed, run Trivy analysis and fix security issues before continuing.
- Use Flet 0.28.3 idioms and avoid experimental APIs.
- Keep commits small and atomic; each commit message must start with `perf:`, `feat:`, `refactor:` or `docs:` as appropriate.
- Write minimal unit tests for any new pure logic (e.g., signature calculation, diff engine). Run tests locally.
- If a phase introduces risky complexity (large functions), add unit tests that exercise the surface behavior before heavy refactors.

Technical requirements (explicit)
- Implement helper utilities in `utils/ui_helpers.py`:
  - size_to_human, format_iso_short, status_color, level_colors, build_status_badge, build_level_badge, striped_row_color, compute_file_signature.
  - Include a small unit test file `tests/test_ui_helpers.py` for signature and formatting functions.
- Files view (`views/files.py`):
  - Add precomputation of `size_fmt`, `modified_fmt`, `row_sig`.
  - Add pagination controls (page size default 50) and a single container.update() pattern.
  - Add debounced search (300ms).
  - Wrap table body in AnimatedSwitcher and integrate diff engine comparing `prev_sigs`.
  - Instrument timing with `utils/perf_metrics.py` keys: files.load.scan_initial, files.load.get_enhanced, files.search.perform, files.table.diff_prepass, files.table.diff_reuse, files.table.diff_build, files.table.build_total.
  - Provide a fallback to full rebuild if change ratio > 0.4.
- Logs view (`views/logs.py`):
  - Adopt unified `build_level_badge`, apply striping, tooltips for long messages, AnimatedSwitcher for list updates.
  - Instrument keys: logs.load.fetch, logs.load.render, logs.search.perform.
- Instrumentation:
  - Use `utils/perf_metrics.py` to record timings.
  - Provide `get_metrics()` and small `scripts/metrics_summary.py` that prints aggregated p50/p95/max for keys.
  - Testing and verification:
  - Before Phase A edits, capture baseline measures: TTFV, P95 search latency, CPU, memory. Record them in the repository at `important_docs/metrics_baseline.json`.
  - After Phases complete, run the scripted interaction (Section 13) and record results to `important_docs/metrics_results.json`.
  - Ensure reusable tests: Add `tests/test_diff_engine.py` to verify reuse/fallback behavior (happy path + >40% changes).
- Codacy & Security:
  - After each file edit, run codacy_cli_analyze with rootPath set to the repo and file path set to the modified file.
  - If any package or dependency is added, immediately run codacy_cli_analyze with tool=trivy and fix issues before proceeding.
- Accessibility:
  - Ensure keyboard focusable pagination and tooltips for truncated text.
- Documentation:
  - Update `Gpt5_Visual_Optimization_Plan_09092025.md` progress: mark subitems you complete, append `important_docs/IMPLEMENTATION_NOTES.md` summarizing decisions, tradeoffs, and any deferred tasks.

Reporting cadence & deliverables
- After each phase (A–F) commit, produce a short PR description with:
  - Files changed list.
  - Metrics pre/post for impacted keys.
  - Codacy/Trivy findings and how you resolved them.
  - Unit tests added/updated and test outputs.
- When all phases complete, attach `important_docs/metrics_results.json`, `important_docs/metrics_baseline.json`, and `important_docs/IMPLEMENTATION_NOTES.md`, and request formal sign-off.

Failure modes & fallback
- If Codacy/Trivy finds an unfixable security issue in a third-party package: revert the package change and propose an alternative implementation.
- If the diff engine reduces reuse below 30% and increases CPU: disable diff engine by default and open a follow-up task to optimize the signature logic.
- If an edit breaks existing file actions (download/verify/delete), immediately revert the change and create a safe fix branch.

Execution constraints
- Do not run network calls except to fetch official dependencies via pip if strictly necessary.
- Preserve existing public APIs and UI flows unless the change is explicitly small and justified in `IMPLEMENTATION_NOTES.md`.

Prompt wrap-up
Start now: create branch `perf/implement-visual-plan`, capture baseline metrics, and begin Phase A. After each phase, push commits and report a concise phase summary (files changed, key metrics, Codacy/Trivy status, tests added, next steps). Work until the Acceptance Checklist in `Gpt5_Visual_Optimization_Plan_09092025.md` is green or each deviation is documented with rationale.

End of prompt.
```