# VS Code Settings & Diagnostics — Migration Summary (2025-09-24)

This short note summarises what was wrong, what I changed, why I changed it, and the current state.

1) What was wrong
- Workspace-level `python.analysis.*` keys and many large workspace settings were present in `.vscode/settings.json`. These conflicted with the project-level `FletV2/pyrightconfig.json` and caused Pylance to emit persistent settings conflicts and a huge diagnostics flood in the Problems pane (~100K+ in earlier runs).
- The Problems pane also showed many C/C++ build warnings from `Client/cpp` which are legitimate compiler warnings but not useful for day-to-day Python work.

2) What I changed
- Backed up the original workspace settings to `.vscode/settings.removed_backup.json` (safe JSON copy).
- Replaced root `.vscode/settings.json` with a minimal, safe configuration that:
  - Pins the project interpreter to the project's `flet_venv`.
  - Keeps terminal activation and a single PowerShell profile that activates the venv.
  - Adds minimal `files.exclude` to reduce file explorer noise.
  - Adds a `problems.exclude` entry for the known vcpkg build path warning file.
- Created `Client/cpp/.vscode/settings.json` to quiet the C/C++ extension (`errorSquiggles` disabled), and to hide compiled build artifacts from the explorer.
- Ensured per-folder `.vscode/settings.json` files exist under `FletV2/`, `Shared/`, `python_server/`, and `api_server/` so each folder uses the correct interpreter without needing large workspace-level analysis settings.
- Left `FletV2/pyrightconfig.json` as the authoritative place for `extraPaths` and analysis settings.

3) Why I did it
- Pylance/Pyright treats project-level config as authoritative; conflicting workspace-level `python.analysis` settings cause it to display a persistent warning and to re-run diagnostics in a way that floods the Problems pane.
- Minimising workspace-level settings removes the conflict and stabilises the language server while keeping essential conveniences (interpreter pin, terminal activation).
- Moving C/C++ noise into a per-subproject `.vscode` file prevents those compiler warnings from cluttering Python diagnostics.

4) Current state and outcome
- The workspace is now stable for Python/Pylance: the pyright warning about `python.analysis.exclude` conflicts should be gone if the editor is reloaded (Developer: Reload Window).
- The Problems pane should show far fewer irrelevant items (mostly real Python issues only). C/C++ compiler warnings are now scoped to `Client/cpp` and do not show as global squiggles.
- All original settings are preserved in `.vscode/settings.removed_backup.json` so nothing is lost.

5) Things you should know / next steps
- Reload VS Code now (Developer: Reload Window) to clear any cached extension state.
- If you want specific blocks restored (Copilot, SpecStory, custom terminal profiles, C/C++ global quieting), tell me which ones and I will reapply them in appropriate, non-conflicting places (per-folder `.vscode` or a separate `.code-workspace`).
- If you prefer the previous exact layout, I can restore it verbatim, but this will reintroduce the original Pylance conflict until we isolate which keys to keep.

If you'd like, I can now (automatically):
- Reintroduce specific Copilot/SpecStory entries into a separate backup-enabled file, or
- Move C/C++ quieting to a workspace-wide `.code-workspace` if you want those suppressed globally.

Tell me which of the above you'd like next and I'll proceed.
