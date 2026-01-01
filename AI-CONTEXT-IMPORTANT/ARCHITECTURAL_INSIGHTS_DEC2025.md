# Project Knowledge Base (ULTRATHINK Edition)

> [!IMPORTANT]
> This document serves as the "Second Brain" for the Deepmind Antigravity Agent. It captures deep architectural insights, hidden dependencies, and critical system invariants that are not immediately obvious from code comments.

## 1. System DNA & Invariants

### 🔒 Security Invariants (Immutable)
*   **Zero-IV AES-CBC**: The protocol strictly enforces `AES.MODE_CBC` with `iv=b"\0" * 16`. This is a hard protocol constraint (Client v3 / Server v3).
    *   *Code Reference*: `python_server/server/file_transfer.py:724`.
*   **RSA-1024 Exchange**: Public key exchange is bounded to 1024 bits.
*   **CRC32 Verification**: Deterministic usage of polynomial `0x04C11DB7`.

### ⚡ Performance Invariants
*   **ProperDynamicBufferManager**: A sophisticated C++ adaptive buffer system exists in `Client/cpp/client.h`.
    *   It isolates **Network Throughput** (Mbps) from **Encryption Latency** (ms).
    *   It adheres to L1 cache sizes (Max 32KB) for the buffer pool.
*   **Memory-Efficient Streaming**: The Python server uses a specific `MemoryUsageTracker` and `get_transfer_manager` to prevent varying RAM spikes during multi-GB transfers.

## 2. Critical Paths & Nervous System

### A. The C++ "Heartbeat"
The client is NOT just a dumb script; it has a `ProperDynamicBufferManager` that actively fights network jitter.
- **Reference**: `Client/cpp/client.h` (Lines 132-203).

### B. The Python "Brain"
- **FileTransferManager** (`python_server/server/file_transfer.py`) uses a dual-locking mechanism:
    1.  `transfer_lock` (Global)
    2.  `_file_locks` (Per-file, per-client mutex)
    *   *Verification*: Confirmed (`Line 103`) to avoid race conditions during parallel uploads.
- **RealBackupExecutor** (`api_server/real_backup_executor.py`):
    *   **Subprocess Lifecycle**: Uses `Popen_utf8` with `--batch` to prevent interactive hangs.
    *   **Synchronization**: Uses `SynchronizedFileManager` to manage `transfer.info` creation/deletion, preventing race conditions where the C++ client reads a half-written config or the server deletes it too early.
    *   **Adaptive Timeout**: Implements `base + (size_mb * 2)` logic to prevent timeouts on large files.

### C. The Flet Bridge
- **Direct Object Integration**: `FletV2/server_adapter.py` does NOT use HTTP to talk to the local server. It imports `RealBackupExecutor` and `DatabaseManager` directly.
    *   *Inference*: This removes network latency for admin tasks but tightly couples the GUI to the Server implementation.

## 3. The "Dark Matter" (Hidden Complexity)

### ProperDynamicBufferManager
Located in `Client/cpp/client.h` (Line 132).
- **Purpose**: Dynamically adjusts buffer sizes (1KB - 64KB) based on *network throughput* independent of encryption time.
- **Logic**: Uses a hysteresis model (`THROUGHPUT_IMPROVEMENT_THRESHOLD = 1.15`) to prevent buffer size thrashing.

### Memory Efficient Streaming
`Shared/filesystem/memory_efficient_file_transfer.py` prevents the Python server from loading entire files into RAM. It uses bounded buffers for reassembly.

## 4. Architectural Risks & Debt

> [!WARNING]
> **Zero-IV AES-CBC**
> The protocol hardcodes `iv=b"\0"*16` (`file_transfer.py:724`). This renders the encryption deterministic for identical first blocks (ECB-like weakness for headers).
> *Remediation*: Requires a v4 Protocol change to transmit random IVs.

> [!CAUTION]
> **Fallback Database Manager**
> `FletV2/server_adapter.py` silently swaps in a `_FallbackDatabaseManager` if imports fail. This is great for UI dev but could mask deployment failures where the admin console says "Running" (fallback) but the actual server is dead.

## 5. Shared Library Topology
Verified structure matches `GEMINI.md`:
- `Shared/filesystem`: UTF-8, File Lifecycle, Streaming.
- `Shared/monitoring`: Unified Monitor, Process Monitor.
- `Shared/config`: Unified Config.
