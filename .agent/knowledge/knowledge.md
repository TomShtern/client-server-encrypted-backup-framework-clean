# 🧠 Project Knowledge Base: Client-Server Encrypted Backup Framework

> **Status:** ULTRATHINK Edition
> **Version:** 1.0.0
> **Last Updated:** December 2025

This document serves as the **single source of truth** for the architectural logic, hidden invariants, and critical constraints of the system. It is designed to prevent "chesterton's fence" violations—do not change these logic paths without understanding *why* they exist.

---

## 1. 🧬 System DNA & Core Identity

This is **not** a typical web app. It is a **Hybrid Multi-Runtime System** that orchestrates a native C++ crypto-engine, a Python management core, and modern reactive UIs.

*   **Core Philosophy**: "Native Speed, Python Agility, Beautiful UI."
*   **Primary Constraint**: Security and Data Integrity > User Convenience.
*   **The "Secret Sauce"**: The `ProperDynamicBufferManager` (C++) and `ServerBridge` (Python) are the unique differentiators.

---

## 2. ⚡ The Architectural "Laws of Physics" (Do NOT Break)

These are hard constraints. Violating them will cause immediate system failure.

### A. The "Zero-IV" Constraint (Security/Protocol)
*   **Law**: The AES-256-CBC encryption **MUST** use an Initialization Vector (IV) of all zeros (`b"\0" * 16`).
*   **Why?**: This was a Protocol v3 design decision to simplify the handshake.
*   **Consequence**: The first block of encryption is deterministic.
*   **Code Location**: `python_server/server/file_transfer.py:724`.
*   **Warning**: Changing this requires a breaking Protocol v4 update for both Client (C++) and Server (Python).

### B. The 3-Line `transfer.info` Format
*   **Law**: The `transfer.info` file passed to the C++ client must have **exactly 3 lines**:
    1.  `IP:PORT` (e.g., `127.0.0.1:1256`)
    2.  `USERNAME`
    3.  `ABSOLUTE_FILE_PATH`
*   **Constraint**: The C++ client uses `std::getline` and expects this exact structure.
*   **Process**: Managed by `RealBackupExecutor._generate_transfer_info`.

### C. The UTF-8 Subprocess Mandate
*   **Law**: **NEVER** use `subprocess.Popen` directly. **ALWAYS** use `Shared.filesystem.utf8_solution.Popen_utf8`.
*   **Reason**: Windows console encoding is chaotic. Standard Python subprocess calls will crash or mangle paths when handling non-ASCII filenames (e.g., Hebrew, Cyrillic) in the console output.
*   **Mechanism**: `Popen_utf8` forces the environment to UTF-8 and handles the codepage switching.

### D. The Flet ServerBridge Facade
*   **Law**: The Flet Desktop GUI (`FletV2/`) does **NOT** make network calls to the local API server.
*   **Design**: It uses `FletV2ServerAdapter` to import `DatabaseManager` and `RealBackupExecutor` **directly** into the Flet process memory space.
*   **Why?**: Zero-latency UI updates and easier single-user deployment.
*   **Risk**: The GUI thread can block if DB calls aren't wrapped in `asyncio.get_event_loop().run_in_executor`.

---

## 3. 🕸️ Deep Component Analysis

### A. C++ Client (`Client/cpp/`)
The "Muscle" of the operation.
*   **`ProperDynamicBufferManager`**:
    *   **What it does**: Dynamically resizes the read/send buffer between 1KB and 64KB.
    *   **Intelligence**: Monitors *network throughput* independent of encryption time. If throughput is rising, it increases buffer size (up to L1 cache limit). If jitter occurs, it throttles back to prevent packet loss.
    *   **Hysteresis**: Uses a 1.15x threshold to preventing "thrashing" (rapidly resizing buffers).
*   **`--batch` Mode**:
    *   **Crucial**: The client is interactive by default. You **MUST** pass `--batch` flag when spawning from Python or it will hang indefinitely waiting for `cin`.

### B. Python Server (`python_server/`)
The "Brain" and Orchestrator.
*   **`FileTransferManager`**:
    *   **Dual-Locking**: Uses a global `transfer_lock` AND a per-file `_file_locks` mutex. This allows Client A and Client B to upload *different* files simultaneously, but prevents Client A from uploading `report.pdf` while Client B is also uploading `report.pdf`.
*   **Network Layer**:
    *   **Threaded**: Spawns a new thread per client connection (`client_handler`).
    *   **Protocol Dispatch**: Maps OpCodes (1025-1031) to handler functions.

### C. Web UI (`api_server/web_ui/`)
The "Face" of the operation.
*   **`StateStore`**:
    *   **Type**: Custom vanilla JS state manager (Redux-lite).
    *   **Optimization**: Uses `requestAnimationFrame` to batch UI updates.
*   **`PerformanceOptimizer`**:
    *   **Role**: Manages the render loop. During high-speed transfers (1 Gbit+), it throttles DOM updates to keep the browser responsive (60fps) instead of trying to render every single packet event.

---

## 4. 🌊 Critical Data Flows

### A. The "Secure Handshake" (Trust Establishment)
1.  **REQ_REGISTER (1025)**: Client says "Hello, I'm [Name]". Server assigns UUID.
2.  **REQ_SEND_PUBLIC_KEY (1026)**: Client sends RSA-1024 Public Key.
3.  **Server Action**: Generates AES-256 Key -> Encrypts it with Client's Public Key -> Sends it back.
4.  **Lock Initiated**: Both sides now switch to AES-256-CBC (Zero-IV) for all future traffic.

### B. The Backup Pipeline
1.  **Python**: `RealBackupExecutor` creates `transfer.info` and spawns `EncryptedBackupClient.exe --batch`.
2.  **C++**: Reads `transfer.info` -> Connects to Port 1256 -> Handshakes -> Starts sending chunks.
3.  **Python Server**: Receives chunks -> Decrypts on the fly -> Calculates running CRC32.
4.  **Verification**: C++ sends "I'm done, here is my CRC". Server checks against calculated CRC.
    *   **Match**: Server saves file, updates DB `verified=1`.
    *   **Mismatch**: Server deletes partial file, updates DB `verified=0`.

---

## 5. 🛠️ Developer "Cheat Sheet"

| Concept | The Truth |
| :--- | :--- |
| **Default Port** | `1256` (Server), `9090` (API) |
| **Database** | SQLite3 (`data/database/defensive.db`) |
| **Config Source** | `Shared/config/unified_config.py` (Env > JSON > Default) |
| **Logs** | `logs/*.log` (Rotating, UTF-8) |
| **Subprocess** | **ONLY** use `Popen_utf8` |
| **Paths** | **ALWAYS** use `os.path.abspath()` before passing to C++ |

### Common Pitfalls
1.  **" The GUI is freezing!"**
    *   *Cause*: You called a DB method directly in the Flet main thread.
    *   *Fix*: Use `await asyncio.get_event_loop().run_in_executor(None, self.db.method)`.
2.  **" The Backup process hangs!"**
    *   *Cause*: You forgot `--batch` or the `transfer.info` file is missing/malformed.
3.  **" I see weird characters in the logs!"**
    *   *Cause*: You used `print()` instead of `safe_print()` or `enhanced_logger`.

---

> **Final Note**: This system is built for **resilience**. The `UnifiedFileMonitor` and `RealBackupExecutor` are designed to recover from crashes, timeouts, and network disconnects. Do not bypass these wrappers.
