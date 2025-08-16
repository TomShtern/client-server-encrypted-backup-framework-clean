# CyberBackup Framework - AI Coding Agent Instructions

## Architecture Overview
This is a **4-layer encrypted backup system** with hybrid web-to-native architecture:

```
Web UI → Flask API Bridge → C++ Client (subprocess) → Python Server
  ↓           ↓                    ↓                     ↓
HTTP      RealBackupExecutor    --batch mode       Custom Binary
requests  process management   + transfer.info     TCP Protocol
```

**Critical Understanding**: Flask API Bridge (`cyberbackup_api_server.py` + `real_backup_executor.py`) is the coordination hub. Web UI communicates ONLY with Flask API, never directly with C++ client or Python server.

**Key Client Components**:
- **Web Client**: Single 8000+ line HTML file with modular JavaScript classes (ApiClient, FileManager, App, ThemeManager, ParticleSystem, etc.)
- **C++ Client**: Production-ready executable with RSA/AES encryption, CRC verification, and --batch mode for subprocess integration
- **Both clients** connect to the same Python server but through different pathways (web→Flask→C++→server vs direct C++→server)

## CyberBackup — concise AI agent instructions

Purpose: help an AI coding agent be productive quickly. Read linked files before changing behavior.

High-level agent contract:
- Inputs: code, tests, and repository files; environment is Windows with vcpkg/CMake and Python 3.13+ available when running build scripts.
- Outputs: minimal, runnable changes (small patches or docs), tests or smoke-checks demonstrating the change, and a short verification note showing build/tests status.
- Error modes: missing C++ build artifacts, port conflicts (9090/1256), transfer.info race conditions. Always surface these explicitly when proposing changes.

- Big picture (read these first): `api_server/cyberbackup_api_server.py`, `api_server/real_backup_executor.py`, `python_server/server/server.py`, `scripts/one_click_build_and_run.py`, `Shared/utils/unified_config.py`, `Shared/utils/file_lifecycle.py`, `client/transfer.info`.

- Additional reference docs: read `CLAUDE.md` and `GEMINI.md` in the repo for agent-specific notes and past assistant interactions before making behavioral changes.

- Architecture (short): Web UI ↔ Flask API bridge (9090) → spawns C++ client (build/Release) in --batch mode → Python backup server listens on 1256. The Flask bridge is the coordination hub.

- Critical patterns to preserve:
    - transfer.info is a legacy 3-line file (server:port, username, absolute filepath). Many modules search common locations (see `Shared/utils/unified_config.py`).
    - Subprocess invocation: C++ client must run with `--batch` and cwd set to directory containing `transfer.info` (see `RealBackupExecutor` in `api_server/real_backup_executor.py`).
    - Use the file lifecycle helpers (`Shared/utils/file_lifecycle.py` / SynchronizedFileManager) to avoid race conditions when creating or copying `transfer.info`.

- Quick developer workflows (examples found in repo):
    - Fast start (recommended & canonical launcher): `#file:one_click_build_and_run.py` (located at `scripts/one_click_build_and_run.py`) — this script is the canonical launcher for building and starting the full system, running checks, and creating `transfer.info` when missing.
    - Manual: start server first `python python_server/server/server.py` (port 1256), then API `python api_server/cyberbackup_api_server.py` (port 9090).
    - C++ build: use vcpkg toolchain: `cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg\scripts\buildsystems\vcpkg.cmake"` then `cmake --build build --config Release` (output: `build/Release/EncryptedBackupClient.exe`).

- Tests and verification to run (repo examples): `tests/integration/test_complete_flow.py`, `tests/test_direct_executor.py`, `tests/test_web_gui_fix.py`. Always verify actual files show up in `server/received_files/` and compare SHA256 hashes.

- Project-specific gotchas (mention before edits):
    - Missing `--batch` or wrong cwd causes client to hang. Don't rely on subprocess exit code alone—verify file receipt.
    - Multiple legacy `transfer.info` locations exist; prefer using `unified_config` helpers.
    - Port conflicts: check ports 9090 and 1256 before starting services.

- When changing integration code, run the minimal smoke test: start server, start API, generate a small test file and run the executor path (or use `one_click_build_and_run.py`). Update tests under `tests/` accordingly.

If anything here is unclear or you'd like more detail on a specific file (example: exact RealBackupExecutor flow or transfer.info lifecycle), tell me which file and I'll expand the section.
# 3. Build C++ client (after any C++ changes)
