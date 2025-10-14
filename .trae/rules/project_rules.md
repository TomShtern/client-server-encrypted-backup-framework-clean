
Trae Project Conversation Rules (LLM-optimized)
=============================================

Purpose
-------

Short, directive rules Trae must follow when interacting with this repository. Designed for reliable, repeatable LLM execution.

Top-line checklist (do this first)
---------------------------------

1. Read project context files and attachments: `AGENTS.md`, `.github/*`, `Shared/`, `FletV2/`, and any files the user attached.
2. If the task touches Flet UI, plan to fetch Flet 0.28.3 docs via Context7 MCP before generating code (see templates below).
3. Create a tiny todo list for the change, mark one item `in-progress`, then proceed.

Core rules (numbered for LLMs)
-----------------------------

1. Honor repository conventions and constraints.
	- Flet 0.28.3 patterns and limitations (use Flet 0.28.3-compatible APIs).
	- UTF-8 bootstrap on Windows (`Shared.utils.utf8_solution`).
	- TCP port 1256 is the default server port; guard `server_bridge` usage and mock fallbacks.
	- Use `db_manager.get_connection()` for SQLite access.

2. Make minimal safe edits.
	- Prefer the smallest change that completes the goal.
	- When editing code, add/update tests and run quick lint/tests locally (`ruff`/`pylint`/`pytest`) before reporting success.

3. Safety first.
	- Avoid network calls, secrets exfiltration, or external state changes unless the user explicitly authorizes them.

4. Plan-and-validate workflow.
	- Plan a short todo list, mark one item `in-progress`, perform the change, run validation (build/lint/tests), then mark completed and report results.

5. Flet async/UI rules (must-follow).
	- Never use `time.sleep()` in async contexts.
	- Always pass coroutine functions (not results) to `page.run_task` (e.g., `page.run_task(my_async_fn)` not `page.run_task(my_async_fn())`).
	- Guard UI updates until controls are attached (avoid `ListView` update-before-attach errors).

6. Risk handling.
	- For risky domains (schema, protocol, crypto), ask a focused clarifying question before proceeding.

7. Communication style.
	- Keep replies concise, reference files and symbols using backticks, and provide copy-pasteable commands or exact edits.

Context7 / MCP usage for Flet 0.28.3 (templates)
------------------------------------------------

- When touching Flet UI code, always resolve and fetch Flet 0.28.3 docs via Context7 MCP. Use the library ID (e.g., `/flet/flet`) and confirm the version is 0.28.3.

Context7 query template (single-shot)
> Resolve Flet 0.28.3 docs and return constructor signatures and supported props for: `ft.Text`, `ft.TextField`, `ft.Dropdown`, `ft.ListView`, `ft.Container`, `ft.Icons`.

Context7 multi-query strategy (high-risk changes)
1. Query: "Flet 0.28.3: constructor signatures and supported kwargs for X" (narrow per-component).
2. Query: "Examples and edge-cases for using X in Flet 0.28.3".
3. Query: "Which icons are available in Flet 0.28.3 and replacements for missing ones?".
4. Supplement with 2–3 targeted web searches (official docs, release notes, GitHub issues) and reconcile differences. Favor official docs.

Best-practice guidance
----------------------

- If Context7 or the project's MCP server is unavailable, explicitly state that and only proceed using conservative, backward-compatible code patterns that align with the repo's documented behavior.
- For UI generation, prefer small, testable factories (return control + dispose + setup) and avoid full-page redraws. Follow the project's `page.run_task` guidance.

Quality gates (must-check before reporting success)
-------------------------------------------------

- Build / Lint / Tests: run `ruff check` / `pylint` / `pytest -q` where appropriate. Report PASS/FAIL.
- If edits were made, and Codacy MCP is configured, run `codacy_cli_analyze` on each edited file per project policy; if unavailable, notify the user and provide exact next steps to run it.

Examples (minimal outputs)
--------------------------

When asked to implement a Flet view, output:

- A 2–4 line plan (todo list style).
- The Context7 queries used (or note Context7 unavailable).
- The exact file edits (or a short patch) and tests added.
- Validation results (build/lint/tests) and any follow-ups.

These rules are intentionally LLM-friendly: terse, numbered, and with templates to make following them deterministic.



