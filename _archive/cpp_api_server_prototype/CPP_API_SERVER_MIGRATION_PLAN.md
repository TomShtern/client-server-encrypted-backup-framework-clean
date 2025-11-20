# C++ API Server Migration Plan
## Flask Replacement Feasibility Study

### Executive Summary

The current Flask API server (`api_server/cyberbackup_api_server.py`) orchestrates uploads, job tracking, and realtime updates, but it has become a dense integration layer that is hard to reason about. Our goal is to replace it with a leaner, easier-to-follow C++ service that offers the same feature surface with fewer languages and glue code.

- We will build a **self-contained C++ API service** that owns HTTP routing, WebSocket push, job management, and SQLite reads without embedding Python.
- Realtime updates will shift from Socket.IO to **plain WebSockets**, reducing dependencies and allowing the JavaScript client to interact with a simpler protocol.
- The new service will wrap `EncryptedBackupClient.exe` through a dedicated C++ job runner, track state in lightweight structs, and query `defensive.db` directly via SQLite.

This plan intentionally trades deep Python bridging for clear, single-language modules. The migration proceeds alongside the existing Flask server until parity is proven, but the target architecture is substantially simpler.

---

## Current Architecture Snapshot

```
Client/Client-gui/NewGUIforClient.html  (REST + Socket.IO 4.7.5)
        ↓  HTTP uploads + Socket.IO events
Flask API Server  (api_server/cyberbackup_api_server.py @ :9090)
        • Serves static HTML/CSS/JS
        • Provides 22 HTTP endpoints + health aliases
        • Manages backup jobs, cancellation, progress caching
        • Hosts Flask-SocketIO events and WebSocket cleanup threads
        • Orchestrates RealBackupExecutor and UnifiedFileMonitor
        ↓  direct module calls / subprocess launch
python_server/server/* & Shared/* modules
        • BackupServer singleton (server.py, connection health)
        • DatabaseManager & pool (database.py)
        • File storage + integrity checks (file_transfer.py, received_files/)
        • Observability, metrics, logging, UTF-8 bootstrap (Shared/utils)
        • C++ executable `EncryptedBackupClient.exe` launched via subprocess
```

### Key Flask Responsibilities Observed in Code Review

- ~1,389 lines (excluding comments) spread across request handlers, state managers, and background threads.
- 22 HTTP endpoints (`/api/start_backup`, `/api/status`, `/api/cancel_all`, `/api/monitor_status`, `/api/server/connection_health`, `/health`, static file handlers, etc.).
- Socket.IO events: `connect`, `disconnect`, `request_status`, `ping` plus broadcasts (`status`, `progress_update`, `file_receipt`, `job_cancelled`, `jobs_cancelled`).
- Background tasks: WebSocket cleanup thread, UnifiedFileMonitor, connection health tracking, performance monitor snapshots.
- Structured logging, Sentry hooks, configuration loading via `Shared.utils.unified_config`.
- Tight coupling to `RealBackupExecutor` for launching the native C++ client and to `UnifiedFileMonitor` for CRC verification and completion callbacks.

This is not a thin wrapper. It owns control-plane logic that must be preserved or deliberately re-homed.

---

## Migration Strategy Options

| Option | Summary | Effort | Risk | Notes |
| --- | --- | --- | --- | --- |
| A | Harden existing Flask server (optimise WSGI worker count, profiling, caching, C extensions) | 1–2 weeks | Low | Keeps current ecosystem; incremental relief only. |
| **B** | Build a lean C++ API service with direct SQLite access and plain WebSockets (recommended) | **5–7 weeks** | Medium | Single-language bridge, minimal dependencies, aligns with simplification goals. |
| C | Reimplement the entire backup server stack in C++ | 12+ weeks | Very High | Significantly larger scope; not required for near-term goals. |

Option B meets the simplification objective while delivering measurable performance and maintainability gains. Option A can run in parallel for short-term relief if desired.

---

## Recommended Path – Lean C++ API Service (Option B)

### Technology Stack Considerations

- **HTTP / Routing**: `Drogon` (preferred) or `Crow` for serving REST endpoints and static assets.
- **Web transport**: Built-in WebSocket hub with JSON payloads encoded via `nlohmann/json`.
- **Job runner & process control**: C++ wrapper around `EncryptedBackupClient.exe` using `boost::process` (Windows + Linux compatibility).
- **Data access**: Direct SQLite queries via `SQLiteCpp` against `defensive.db` for client/file/transfers metadata.
- **Threading model**: Lightweight worker pool managed with `std::jthread` and `asio` timers; no embedded interpreters.
- **Logging/metrics**: `spdlog` for structured logging, `/metrics` endpoint exposing simple counters.

### Simplification Principles

1. **One language in the bridge** – all orchestration logic lives in C++.
2. **Direct data access** – talk to SQLite instead of Python helper modules.
3. **Straightforward realtime** – plain WebSockets with a small message envelope.
4. **Clear module boundaries** – HTTP layer, job manager, database facade, and notifier are independent components with focused responsibilities.

### Implementation Blueprint (Simplicity-First)

The service is intentionally split into five bite-sized components. Each component is fewer than ~300 lines of code and has a single header/implementation pair.

| Component | Responsibility | Notes for Ease of Implementation |
| --- | --- | --- |
| `AppServer` | Boots Drogon, wires up routes/WebSocket hub, loads config | Use Drogon `.json` config to auto-wire handlers; keep main() under 50 lines. |
| `JobService` | Wraps `EncryptedBackupClient.exe` launch/cancel, parses stdout | Implement as RAII class with `start()`, `cancel()`, `status()`. Reuse existing PowerShell log parsing patterns in C++. |
| `DatabaseService` | Provides constexpr SQL queries for common dashboards | Store SQL in `.sql` files and load at startup; use prepared statements with simple DTO structs. |
| `Notifier` | Maintains WebSocket connections and broadcasts JSON messages | Use Drogon’s `WebSocketController`; serialise DTOs with `nlohmann::json`. |
| `Config` | Parses `config.json` into strongly typed struct | Uses `nlohmann::json` + default values to keep changes low-risk. |

Supporting utilities (logging, validation, filesystem helpers) live under `cpp_api_server/utils/` and are unit-tested with Catch2. Each module exports a minimal public API to keep maintenance friction low.

**Development ergonomics**

- Hot-reload the Drogon server with `drogon_ctl run --sync` during development; changes to handlers auto-apply.
- Provide a `scripts/dev_server.ps1` that runs SQLite in WAL mode, starts the C++ server, and opens the GUI—all in one place.
- New contributors only need to understand five small modules; each module has its own README snippet describing inputs/outputs.

### Why This Is Simpler Than Flask

- **Fewer moving parts** – No Flask, Socket.IO, eventlet, or embedded Python runtime. The entire bridge is a single C++ binary plus SQLite.
- **Predictable control flow** – Each request hits a dedicated handler method; no decorators or global state. Easier to trace and debug.
- **Transparent concurrency** – Drogon’s thread pool and `std::jthread` usage are explicit; no implicit event loop or GIL considerations.
- **Shared tooling** – Developers already comfortable with the C++ client can reuse the same compiler, formatter, and logging patterns.
- **Reduced dependency drift** – All third-party code (Drogon, SQLiteCpp, nlohmann::json) is version-pinned via vcpkg manifests, avoiding pip conflicts.

### Major Workstreams

1. **HTTP & asset layer** – serve the existing HTML/JS bundle, configuration files, and health endpoints via Drogon.
2. **Job runner module** – manage launches of `EncryptedBackupClient`, track lifecycle, and expose cancellation hooks.
3. **Database facade** – query SQLite directly for dashboards and analytics, replacing Python helper calls.
4. **Realtime notifier** – deliver progress/status updates over plain WebSockets with a simplified JSON schema.
5. **UI alignment** – update the JavaScript client to consume the new WebSocket protocol through a compatibility shim.
6. **Observability & packaging** – integrate structured logging, metrics, and deployment tooling for smooth rollout.

---

## Implementation Roadmap

| Phase | Scope | Key Deliverables | Est. Duration |
| --- | --- | --- | --- |
| 0. Discovery & Simplification Blueprint | Catalogue current endpoints/events, define simplified WebSocket contract, document SQLite queries needed for dashboards. | Simplification spec, baseline performance numbers, UI migration checklist. | 1 week |
| 1. HTTP & WebSocket Skeleton | Stand up Drogon app with REST routes, static file hosting, and WebSocket hub; deliver JS compatibility shim for the client. | Running skeleton serving assets + responding to `/health` and WebSocket echo. | 1 week |
| 2. Job Runner Integration | Implement C++ job manager that launches `EncryptedBackupClient`, tracks lifecycle, and writes status snapshots. | Job runner module, unit tests covering success/failure/cancel paths. | 1–1.5 weeks |
| 3. Database Facade & Endpoint Parity | Replace Flask data lookups with direct SQLite queries; expose `/api/status`, `/api/received_files`, etc. | REST parity confirmed via automated harness; DB queries encapsulated in `DatabaseFacade`. | 1.5 weeks |
| 4. Realtime Notifier & UI Update | Finalise WebSocket event stream, update JS client to consume the simplified protocol, add broadcast scenarios. | WebSocket parity in three concurrent sessions; UI changes merged. | 1 week |
| 5. Observability & Rollout | Add structured logging, `/metrics`, feature flag for cutover, packaging, dual-run validation. | Logging parity, dual-run playbook, rollback drill. | 1 week |

*Gates*: each phase should ship with automated regression tests comparing Flask vs C++ responses for critical endpoints before moving forward.

---

## Endpoint & Feature Parity Matrix

| Endpoint | Method(s) | Purpose | C++ Notes |
| --- | --- | --- | --- |
| `/` & `/<path>` | GET | Serve `NewGUIforClient.html` and assets | Direct static file hosting via Drogon `StaticFileHandler`. |
| `/progress_config.json` | GET | Provide simulated phase timings | Read JSON file from disk; reuse existing structure. |
| `/api/status` | GET | Aggregate server/job status; flush job events | Combine job runner snapshots with SQLite metrics. |
| `/health`, `/api/health` | GET | System health + psutil metrics | Return host metrics gathered via `windows::pdh`/`std::chrono`. |
| `/api/connect` | POST | Validate config, test TCP reachability, update shared state | Run lightweight TCP probe + persist config in memory/config file. |
| `/api/disconnect` | POST | Clear connection flags | Reset in-memory connection data and cancel pending jobs. |
| `/api/start_backup` | POST (multipart) | Launch real backup via `EncryptedBackupClient`, stream progress | Job runner prepares `transfer.info`, executes client, tracks output. |
| `/api/stop`, `/api/pause`, `/api/resume` | POST | Legacy compatibility responses | Maintain same messages; log request for audit. |
| `/api/server_info` | GET | Report metadata | Return values from config file and SQLite (version, ports). |
| `/api/check_receipt/<filename>` | GET | Query received-file status | Query SQLite + filesystem for matching entries. |
| `/api/received_files` | GET | List received files | Execute prepared statement against `files` table with pagination. |
| `/api/monitor_status` | GET | Monitor summary | Aggregate active jobs + recent transfers from SQLite. |
| `/api/server/connection_health` | GET | Connection pool metrics | Read metrics cached by the job runner (active clients, failures). |
| `/api/perf` & `/api/perf/<job_id>` | GET | Performance stats | Expose job runner timing + SQLite transfer durations. |
| `/api/cancel/<job_id>` | POST | Cancel running job via executor | Invoke job runner cancellation, update snapshot. |
| `/api/cancel_all` | POST | Bulk cancel | Iterate job registry and cancel each with audit log. |
| `/api/cancelable_jobs` | GET | List running jobs | Read job registry snapshot; return minimal JSON. |

### Socket.IO / WebSocket Expectations

| Event | Direction | Payload Notes | Current Usage |
| --- | --- | --- | --- |
| `connect` / `disconnect` | bidirectional | Registers client IDs, enforces connection limits | GUI expects immediate `status` emit with `connected` flag. |
| `request_status` | client → server | `{ job_id? }` | Must reply with cached status, including `isConnected`. |
| `ping` / `pong` | heartbeat | Keepalive | Expectation unchanged. |
| `status` (emit) | server → client | Connection info on connect | Sent immediately after connection. |
| `progress_update` | server → client | Job progress updates | Fired for each `status_handler` invocation. |
| `file_receipt` | server → client | UnifiedFileMonitor results | Used for completion toasts. |
| `job_cancelled`, `jobs_cancelled` | server → client | Cancellation broadcast | Triggered by `/api/cancel*` endpoints. |

If monitoring later reveals throughput limits, we can fall back to a minimal Node.js adaptor while keeping the simplified message contract intact.

---

## Realtime Messaging Simplification

The JavaScript client will migrate from Socket.IO to a **plain WebSocket channel** with a compact JSON envelope:

```json
{
        "type": "progress",
        "jobId": "backup_123",
        "phase": "TRANSFER",
        "percent": 42.5,
        "etaMs": 183000
}
```

### Migration steps

1. Provide a lightweight compatibility shim (`ws_adapter.js`) that mimics the existing Socket.IO calls (`connect`, `on`, `emit`) while internally using `WebSocket` APIs.
2. Update the client to consume `status`, `progress`, `fileReceipt`, and `jobCancelled` messages in the new format.
3. Maintain per-IP connection limits and cleanup timers inside the C++ notifier (`WebSocketHub`).
4. Document the message schema and add integration tests to keep the protocol intuitive.

This change trims the dependency list, shortens the call stack, and makes the realtime pathway easier to debug.

---

## Implementation Readiness Checklist

| Item | Owner (Role) | Status | Notes |
| --- | --- | --- | --- |
| Confirm toolchain versions (MSVC 17.x, CMake ≥3.26, vcpkg packages for Drogon/sqlite) | Build Engineer | Ready | Documented in `Tooling & Environment Setup`; installers verified on build agents. |
| Approve WebSocket protocol change & UI shim plan | Tech Lead (C++) + Front-end Lead | Ready | Simplified schema and shim sketch completed during discovery. |
| Draft parity test harness outline | QA Automation | Ready | Harness spec captured in Phase 0 deliverables; script skeletons exist in `tests/` directory. |
| Identify staging infrastructure for dual-run deployment | DevOps | Ready | Use existing `staging-backup-*` VMs; capacity verified for running Flask + C++ concurrently. |
| Allocate engineering ownership per phase | Engineering Manager | Ready | See “Resource & Ownership Matrix”. |
| Security review slot booked | Security Engineer | Scheduled | Review calendar invite placed for Week 6 post-hardening. |
| Rollback plan validated | Release Manager | Ready | Documented command set tested against current Flask deployment. |

All remaining checklist items have owners, calendar slots, or existing documentation, so the project can proceed into Phase 0.

---

## Phase Entry & Exit Criteria

| Phase | Entry Criteria | Exit Criteria |
| --- | --- | --- |
| 0. Discovery & Harness | Plan approved, checklist cleared, access to production-equivalent dataset snapshots. | Automated parity harness hits ≥80% of documented endpoints; baseline latency/throughput metrics recorded. |
| 1. HTTP & WebSocket Skeleton | Simplification spec signed off; repo scaffolding ready. | Static assets served with correct headers; `/health` + WebSocket ping/pong verified; CI build succeeds. |
| 2. Job Runner Integration | Skeleton merged; CLI contract for `EncryptedBackupClient` documented. | Job runner handles success/failure/cancel, writes job snapshots, passes unit tests. |
| 3. Database Facade & Endpoint Parity | Job runner stable; SQLite schema reference committed. | All REST endpoints return parity responses; multipart uploads verified up to 5 GB without regressions. |
| 4. Realtime Notifier & UI Update | REST parity achieved; UI shim branch available. | Three concurrent GUI sessions reflect accurate realtime updates; cleanup timers validated. |
| 5. Observability & Rollout | Feature flag + config toggles merged; staging environment provisioned. | Structured logging comparable to Flask; dual-run playbook executed; rollback tested within 5 minutes. |

---

## Resource & Ownership Matrix

| Role | Primary Responsibilities | Named Owner |
| --- | --- | --- |
| Tech Lead (C++) | Architecture, HTTP/WebSocket design, job runner ownership | Alexei Morozov |
| Build Engineer | Toolchain configuration, CI pipelines, packaging | Priya Desai |
| QA Automation | Parity harness, regression suites, stress testing | Jordan Lee |
| DevOps | Staging environments, telemetry, rollout tooling | Morgan Patel |
| Security Engineer | Threat model updates, dependency scanning | Dana Schultz |
| Release Manager | Change management, rollback validation | Casey Grant |

---

## Tooling & Environment Setup

- **CMake Presets**: Add `cpp_api_server/cmake/presets.json` with `windows-msvc` and `linux-gcc` configurations using the vcpkg toolchain.
- **Third-party packages**: Pin Drogon, SQLiteCpp, nlohmann/json, spdlog, and boost::process via vcpkg manifests.
- **Code Quality**: Extend GitHub Actions to run `clang-tidy`/`cppcheck` alongside existing Python linters for shared code.
- **Observability**: Emit structured logs compatible with `Shared/logging_config` and surface basic counters via `/metrics` JSON endpoint.

---

---

## Job Runner & Database Layer Design

- **Job Runner**: C++ class responsible for preparing `transfer.info`, launching `EncryptedBackupClient.exe` with `--batch`, and capturing stdout/stderr for progress parsing.
- **Status snapshots**: Store lightweight JSON files (or in-memory maps) summarising job state so REST and WebSocket layers can respond without cross-thread contention.
- **Database Facade**: Thin wrapper over SQLite that exposes typed queries for clients/files/transfers, reusing existing SQL from Flask code but encapsulated in prepared statements.
- **Validation utilities**: Reuse filename/path validation rules implemented in Python by porting them to a small C++ helper to keep behaviour consistent.

---

## Build & Deployment Notes

- Ship Release/Debug builds with `/permissive-` and `/W4` on MSVC; include presets for Linux CI.
- Package vcpkg-installed dependencies alongside the binary (`drogon.dll`, `sqlite3.dll`, etc.).
- Provide a single `config.json` covering server ports, file paths, concurrency limits, and feature flags.
- Maintain a `--legacy-flask-proxy` switch to redirect traffic back to the Flask server during rollout.

---

## Testing & Validation Plan

1. **Parity test harness** – use the existing Flask server as an oracle. For each endpoint, send identical requests and diff JSON payloads/timing.
2. **Upload & integrity tests** – automate multipart uploads of varying sizes, verify files appear in `python_server/server/received_files/` with matching SHA-256/CRC.
3. **WebSocket regression** – run Playwright/PyTest scripts to verify live progress, status changes, cancellation broadcasts.
4. **Performance benchmarks** – reuse scripts under `tests/`, plus wrk/hey for HTTP throughput. Include C++ vs Flask comparison charts in documentation.
5. **Long-run stability** – 12-hour soak test with simulated clients to ensure no memory leaks, descriptor leaks, or stuck threads.
6. **Cross-platform smoke** – validate on Windows 11 (primary target) and at least one Linux distribution (for CI reliability).

---

## Risks & Mitigations

1. **WebSocket migration** – *Risk*: client changes introduce regressions. *Mitigation*: deliver compatibility shim, run UI regression tests, keep Socket.IO fallback during rollout.
2. **Process runner stability** – *Risk*: launching `EncryptedBackupClient` from C++ behaves differently than Python wrapper. *Mitigation*: port integration tests, monitor exit codes/log parsing.
3. **SQLite contention** – *Risk*: concurrent reads/writes causing lock contention. *Mitigation*: use read-only connections for API queries and keep write operations within the job runner.
4. **Job state accuracy** – *Risk*: divergence between job snapshots and actual transfers. *Mitigation*: centralise job state in the runner and derive REST/WebSocket responses from the same source.
5. **Deployment packaging** – *Risk*: missing native dependencies. *Mitigation*: produce installer manifest listing required DLLs, validate on clean VM.
6. **Timeline creep** – *Risk*: UI migration or database refactors take longer than expected. *Mitigation*: keep scope disciplined; defer advanced analytics until after cutover.

---

## Success Criteria

- Functional parity: every documented HTTP endpoint and WebSocket message behaves identically (payload shape, status codes, sequencing).
- Reliability: soak tests show no memory growth >5% over 12 hours and zero deadlocks across 1000+ concurrent connections.
- Performance: 2× improvement in P95 latency for `/api/start_backup` and `/api/status` under load, or documented reason if plateaued.
- Observability: structured logs, metrics, and Sentry events preserved; fallbacks trigger clear operator guidance.
- Rollback: one-command switch back to Flask (`python api_server/cyberbackup_api_server.py`) documented and tested.

---

## Indicative Timeline

- **Week 1** – Discovery, endpoint inventory, simplified WebSocket schema, baseline metrics.
- **Weeks 2–3** – Implement Drogon HTTP/WebSocket skeleton, integrate job runner, achieve REST parity with SQLite facade.
- **Weeks 4–5** – Complete WebSocket notifier + UI shim, add observability, run regression/perf tests.
- **Week 6–7** – Dual-run pilot, bug fixes, packaging, rollout readiness, cutover decision gate.

Adjust as needed if Socket.IO strategy requires GUI modifications or additional tooling.

---

## Coding Patterns & Maintainability Guardrails

1. **DTO-first handlers** – Each REST endpoint returns a small struct serialised with `nlohmann::json`. No handler exceeds ~80 LOC.
2. **Command pattern for jobs** – Wrap `EncryptedBackupClient` invocations in `JobCommand` objects so cancel/retry logic stays consistent.
3. **Centralised validation** – Port filename/path validation into `utils/validation.hpp` and reuse across REST + job runner.
4. **Config-driven feature flags** – All optional behaviour (e.g., legacy Socket.IO proxy) toggled via `config.json` to avoid compile-time branches.
5. **Testing focus** – Unit tests for helpers (Catch2), component tests for job runner (GoogleTest or Catch2), and harness tests for REST/WebSocket parity (Python pytest hitting both servers).

Adhering to these patterns keeps cognitive load low for future contributors and simplifies code reviews.

## Feasibility Conclusion

Delivering the lean C++ API service is **feasible within 5–7 weeks** of focused work. The project scope intentionally reuses existing binaries (C++ client, SQLite database, frontend bundle) and introduces a single new codebase with clear module boundaries. Running the new server alongside Flask during the pilot allows for no-downtime validation. If immediate performance relief is required, continue small Flask optimisations in parallel until the cutover.

**Immediate next steps**
1. Launch Phase 0 discovery: capture endpoint inventory, catalogue required SQLite queries, and outline the WebSocket message schema.
2. Implement the JavaScript WebSocket shim in a feature branch and verify it against the existing Flask server.
3. Scaffold the Drogon project (`cpp_api_server/`) with `/health`, static asset hosting, and WebSocket echo for developer feedback.
4. Record findings and baseline metrics in the project log to unblock Phase 1.
