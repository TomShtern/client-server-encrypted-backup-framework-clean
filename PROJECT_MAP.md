# 🗺️ Project Architecture Map (The "ULTRATHINK" Edition)

> **Generated via Deep AST Analysis & Flow Tracing**
> *Date: December 26, 2025*
> *Status: Verified via `ast-grep` Structural Scan*

## 1. 🏛️ Architectural Overview

A **Hybrid Multi-Runtime Backup System** designed for high security and resilience. It orchestrates a native C++ crypto-engine, a Python management core, and modern reactive UIs.

### System Diagram

```mermaid
graph TD
    subgraph "Native Core (C++)"
        Client[EncryptedBackupClient.exe]
        Crypto[Crypto++ RSA/AES]
        Buffer[ProperDynamicBufferManager]
        Embedded[Embedded HTTP Server]
    end

    subgraph "Orchestration Layer (Python)"
        Net[NetworkServer (TCP)]
        Router[RequestHandlers]
        FTM[FileTransferManager]
        DB_Mgr[DatabaseManager]
    end

    subgraph "Interface Layer"
        API[Flask API Server]
        Pool[DatabaseConnectionPool]
        Bridge[FletV2ServerAdapter]
    end

    subgraph "User Experience"
        Web[Web UI (JS/StateStore)]
        Desktop[FletV2 Admin GUI]
    end

    Client -->|Binary Protocol 3.0| Net
    Net --> Router
    Router --> FTM
    FTM -->|Atomic Save| Disk[(File Storage)]
    FTM -->|Log/Status| DB_Mgr
    DB_Mgr --> Pool --> DB[(SQLite)]

    Desktop -->|Direct Calls| Bridge
    Bridge --> DB_Mgr & FTM

    Web -->|HTTP/Socket.IO| API
    API -->|Subprocess Control| Client
```

---

## 2. 🌊 Critical Data Flows (Deep Trace)

### A. The "Secure Handshake" (Security Architecture)
*The flow of trust establishment between Client and Server.*

1.  **Registration (`REQ_REGISTER`)**: Client sends name. Server generates UUID.
2.  **Key Exchange (`REQ_SEND_PUBLIC_KEY`)**:
    *   Client sends RSA-1024 Public Key.
    *   Server generates `AES-256` Session Key.
    *   Server encrypts AES Key with Client's Public Key (`PKCS1_OAEP`).
    *   Server sends encrypted AES Key back (`RESP_PUBKEY_AES_SENT`).
3.  **Session Locking**: All subsequent transfers use this AES key with Zero-IV CBC mode (Protocol Constraint).

### B. The "Pipeline" (File Transfer Data Flow)
*How a file actually moves from disk to disk.*

1.  **Read & Encrypt (C++)**:
    *   Client reads file chunk (size derived from `ProperDynamicBufferManager`).
    *   Chunk is AES-256-CBC encrypted.
2.  **Packetize (Binary Protocol)**:
    *   Header: `[EncSize | OrigSize | PktNum | TotalPkts | Filename]`
    *   Payload: `[Encrypted Content]`
3.  **Network Transport**: Sent over TCP to Port 1256.
4.  **Reassembly (Python `FileTransferManager`)**:
    *   `_handle_packet_reassembly` buffers chunks in memory (bounded).
    *   Checks for duplicate/missing packets.
5.  **Decryption & Validation**:
    *   Once all packets arrive: `_reassemble_encrypted_data`.
    *   `_decrypt_file_data` (AES-CBC).
    *   `calculate_crc32` verified against Client's sentinel.
6.  **Atomic Storage**:
    *   Write to `filename.uuid.tmp_EncryptedBackup`.
    *   `os.remove(final_path)` -> `os.rename(temp, final)`.
    *   DB Update: `Verified=True`.

---

## 3. 🧠 Component "Under the Hood"

### A. Python Server Core (`python_server/`)
*   **`RequestHandler`**: The dispatcher. Maps opcodes (1025-1031) to methods.
*   **`FileTransferManager`**: The heavy lifter. Contains `_file_locks` (mutex per file) to allow concurrent transfers from same client.
*   **`DatabaseConnectionPool`**: Features "Emergency Connection" logic—if pool is exhausted, it spawns a temporary connection to prevent deadlock.

### B. FletV2 Bridge (`server_adapter.py`)
*   **Pattern**: **Facade Adapter**.
*   **Logic**: Instead of Flet making HTTP calls to the Flask API (latency/complexity), it imports `DatabaseManager` directly.
*   **Async Wrapper**: Wraps blocking DB calls in `asyncio.get_event_loop().run_in_executor` to keep the GUI buttery smooth.
*   **Fallback**: If server modules are missing, it hot-swaps in `_FallbackDatabaseManager` (Mock Object) to allow UI development without a backend.

### C. Web UI (`api_server/web_ui/`)
*   **State Management**: `StateStore` (in `core-utils.js`). A lightweight Redux clone with `requestAnimationFrame` batching for high-performance updates.
*   **Optimization**: `PerformanceOptimizer` class manually manages the render loop to prevent layout thrashing during high-speed transfer updates.

---

## 4. 🎨 Frontend Assets (HTML/CSS)

### A. DOM Structure (`index.html`)
*   **Root**: `<html class="theme-dark">` (Default).
*   **Key Containers**:
    *   `#dragOverlay`: Full-screen drop zone.
    *   `#toastStack`: Notification center (aria-live region).
    *   `header.role="banner"`: Sticky stats bar (Latency, Server Status).
    *   `main#mainContent`: Grid layout for Logs & Transfers.

### B. CSS Architecture (`styles.css`)
*   **Design Tokens**: Strict variable system (`:root`).
    *   **Colors**: Semantic (`--surface`, `--surface-elevated`) vs. Raw (`#0a0e12`).
    *   **Motion**: `--duration-swift` (180ms), `--ease-overshoot`.
    *   **Shadows**: Deep Neomorphic stack (`--shadow-1` through `--shadow-5`).
*   **Theming**:
    *   **Dark Mode**: Default, uses `--bg-gradient` (Linear #0f1419 -> #0a0e12).
    *   **Light Mode**: `html.theme-light` override block重新defines *all* semantic colors (e.g., `--bg` becomes `#f8fafc`).
    *   **Solid Mode**: `html.solid-mode` class disables `backdrop-filter` blur effects for low-end GPU performance.

---

## 5. 🛠️ DevOps & Configuration

### A. Unified Config System (`Shared/config/unified_config.py`)
The system avoids "Config Hell" via a Strict Precedence Ladder:
1.  **Environment Variables**: `BACKUP_SERVER_PORT` (Highest Priority).
2.  **JSON Files**: `config/config.json`, `config/development.json`.
3.  **Legacy Adapters**: `transfer.info` (3-line format), `port.info` (auto-migrated).
4.  **Defaults**: Hardcoded fallbacks in `UnifiedConfigurationManager`.

### B. Critical Automation (`scripts/`)
*   **`one_click_build_and_run.py`**: The "God Script". Orchestrates CMake build (vcpkg), Python environment check, Database init, and subprocess spawning.
*   **`validate_database.py`**: Integrity checker for SQLite schemas.
*   **`setup_zai_key.ps1`**: PowerShell automation for secure key generation.

---

## 6. 📚 Reference Data (The "Cheat Sheet")

### A. Protocol Opcodes (v3)
| Code | Constant | Purpose |
| :--- | :--- | :--- |
| `1025` | `REQ_REGISTER` | Initial handshake |
| `1026` | `REQ_SEND_PUBLIC_KEY` | Key Exchange Step 1 |
| `1027` | `REQ_RECONNECT` | Session Resumption |
| `1028` | `REQ_SEND_FILE` | Payload Transfer |
| `1029` | `REQ_CRC_OK` | Verification Success |
| `1030` | `REQ_CRC_INVALID_RETRY` | Verification Fail (Client Retry) |
| `1031` | `REQ_CRC_FAILED_ABORT` | Verification Fail (Fatal) |

### B. Database Schema (SQLite)
*   **`clients`**: `ID` (BLOB 16), `Name` (Unique), `PublicKey` (RSA), `LastSeen` (ISO8601), `AESKey`.
*   **`files`**: `ID`, `FileName`, `PathName`, `Verified` (Bool), `CRC`, `ClientID` (FK -> clients.ID Cascade).
*   **`metrics_history`**: `timestamp`, `metric_name`, `value`.

### C. Runtime File Layout
*   `data/database/defensive.db` : SQLite DB.
*   `data/storage/` : Received encrypted files.
*   `data/security/` : RSA Keys (`priv.key`) & AES persistence.

---

## 7. ⚠️ Error Propagation Model

How does the user know something broke?

1.  **Origin**: **C++ Client** detects CRC mismatch.
2.  **Transport**: Sends `REQ_CRC_FAILED_ABORT` (1031) packet.
3.  **Server Action**: `RequestHandler` catches 1031.
    *   Logs via `logger.error("CRC Failed...")`.
    *   Deletes the partial/corrupted file.
    *   Updates DB: `Files(Verified=0)`.
4.  **UI Reflection**:
    *   **Flet**: Polls DB `logs` table -> Displays red error row.
    *   **Web**: Socket.IO `request_status` -> API reads DB -> Returns status -> JS `toastManager.show()`.

---

## 8. ✅ AST-Verified Structural Guarantees

*   **C++ PIMPL Idiom**: Confirmed `WebServerBackend` uses `class Impl` and `std::unique_ptr<Impl>` to hide Boost.Beast dependencies.
*   **Compliance Wrappers**: `ComplianceAESWrapper` and `RSAPrivateWrapper` enforce security standards at the type level.
*   **Inheritance**: `Client` explicitly inherits from `std::enable_shared_from_this<Client>` for safe async callbacks.
*   **JS Class Structure**: The Web UI is NOT functional spagetti; it uses strict ES6 classes (`App`, `StateStore`, `PerformanceOptimizer`) for logic encapsulation.

---
*Deeply mapped by Antigravity using `ast-grep` structural analysis*
