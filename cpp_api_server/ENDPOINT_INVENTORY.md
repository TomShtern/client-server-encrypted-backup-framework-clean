# CyberBackup API Server - Complete Endpoint Inventory
## Phase 0 Discovery Documentation

Generated from: `api_server/cyberbackup_api_server.py` (~1,389 lines)

---

## Static File Endpoints (4)

| Route | Method | Handler | Purpose | Implementation Notes |
|-------|--------|---------|---------|---------------------|
| `/` | GET | `serve_client()` | Serve NewGUIforClient.html | Drogon: StaticFileHandler with root_path |
| `/<path:filename>` | GET | `serve_client_assets()` | Serve CSS, JS, images, favicons | Drogon: StaticFileHandler with MIME type detection |
| `/progress_config.json` | GET | `serve_progress_config()` | Phase timing configuration | Drogon: Read JSON file from disk |
| `/favicon.ico` | GET | `serve_favicon()` | Favicon serving | Drogon: StaticFileHandler, return 204 if missing |

---

## REST API Endpoints (24)

### Connection Management (3)

| Route | Method | Handler | Purpose | Request/Response |
|-------|--------|---------|---------|------------------|
| `/api/connect` | POST | `api_connect()` | Connect to backup server, test TCP reachability | **Request:** JSON `{host, port, username}` or form data<br>**Response:** `{success, connected, message, server_config}` |
| `/api/disconnect` | POST | `api_disconnect()` | Disconnect from backup server | **Response:** `{success, connected, message}` |
| `/api/test` | POST | `api_test()` | Debug POST endpoint | **Response:** `{success, message}` |

### Backup Operations (7)

| Route | Method | Handler | Purpose | Request/Response |
|-------|--------|---------|---------|------------------|
| `/api/start_backup` | POST | `api_start_backup_working()` | Start backup with file upload | **Request:** Multipart form `{file, username, host, port}`<br>**Response:** `{success, message, filename, username, job_id}` |
| `/api/status` | GET | `api_status()` | Get current backup/server status | **Query:** `?job_id={job_id}` optional<br>**Response:** `{phase, message, progress: {percentage, bytes_transferred}, backing_up, connected}` |
| `/api/stop` | POST | `api_stop_backup()` | Stop backup (legacy compatibility) | **Response:** `{success, message}` |
| `/api/pause` | POST | `api_pause_backup()` | Pause backup (compatibility only) | **Response:** `{success, message}` |
| `/api/resume` | POST | `api_resume_backup()` | Resume backup (compatibility only) | **Response:** `{success, message}` |
| `/api/cancel/<job_id>` | POST | `api_cancel_job()` | Cancel specific backup job | **Request:** Optional JSON `{reason}`<br>**Response:** `{success, job_id, phase}` |
| `/api/cancel_all` | POST | `api_cancel_all_jobs()` | Cancel all running jobs | **Response:** `{success, results: {job_id: bool}}` |

### Monitoring & Status (7)

| Route | Method | Handler | Purpose | Request/Response |
|-------|--------|---------|---------|------------------|
| `/health` | GET | `health_check()` | System health check | **Response:** `{status, backup_server_status, api_server, system_metrics: {cpu_usage_percent, memory_usage_percent, active_websocket_connections, active_backup_jobs}, timestamp, uptime_info}` |
| `/api/health` | GET | `api_health_check()` | Alias for /health | Same as /health |
| `/api/server_info` | GET | `api_server_info()` | Server metadata | **Response:** `{success, server: {version, name, port, backup_server_port, uptime, status}}` |
| `/api/monitor_status` | GET | `api_monitor_status()` | File monitoring status | **Response:** `{monitoring_active, watched_directory, pending_jobs, recent_receipts}` |
| `/api/server/connection_health` | GET | `api_server_connection_health()` | Connection health metrics | **Response:** `{success, connections: {active_count, failed_count, health_percentage}}` |
| `/api/cancelable_jobs` | GET | `api_cancelable_jobs()` | List running jobs | **Response:** `{success, jobs: [{job_id, phase, file, progress, message}]}` |
| `/api/received_files` | GET | `api_list_received_files()` | List received files | **Response:** `{success, files: [{filename, size, timestamp, verified}]}` |

### File Receipt & Verification (1)

| Route | Method | Handler | Purpose | Request/Response |
|-------|--------|---------|---------|------------------|
| `/api/check_receipt/<filename>` | GET | `api_check_file_receipt()` | Check file receipt status | **Response:** `{success, filename, received, verified, size, hash, timestamp}` |

### Performance Metrics (2)

| Route | Method | Handler | Purpose | Request/Response |
|-------|--------|---------|---------|------------------|
| `/api/perf` | GET | `api_perf_all()` | All job performance stats | **Response:** `{success, jobs: [{job_id, duration_ms, bytes_total, throughput_mbps}]}` |
| `/api/perf/<job_id>` | GET | `api_perf_job()` | Job-specific performance | **Response:** `{success, job: {job_id, duration_ms, bytes_total, throughput_mbps, phases: {...}}}` |

---

## WebSocket Events

### Client → Server Events (4)

| Event | Handler | Payload | Purpose |
|-------|---------|---------|---------|
| `connect` | `handle_connect()` | - | Client connection, enforces MAX_CONNECTIONS limit, generates client_id UUID |
| `disconnect` | `handle_disconnect()` | - | Client disconnection cleanup, removes from connected_clients set |
| `request_status` | `handle_status_request()` | `{job_id?: string}` | Request status update for specific job or general server status |
| `ping` | `handle_ping()` | - | Keepalive test |

### Server → Client Broadcasts (6)

| Event | Trigger | Payload | Purpose |
|-------|---------|---------|---------|
| `status` | On connect | `{connected: bool, server_running: bool, timestamp: number, message: string}` | Initial connection status |
| `status_response` | On request_status | `{status: {...}, job_id?: string, timestamp: number}` | Reply to status request |
| `pong` | On ping | `{timestamp: number}` | Keepalive response |
| `progress_update` | Job status change | `{job_id: string, phase: string, data: any, timestamp: number}` | Real-time progress updates |
| `file_receipt` | File verified | `{event_type: string, data: {...}, timestamp: number}` | File verification events |
| `job_cancelled` | Job cancelled | `{job_id: string, success: bool, phase: string, reason?: string, timestamp: number}` | Single job cancellation notification |
| `jobs_cancelled` | Bulk cancel | `{results: {[job_id]: bool}, timestamp: number}` | Bulk cancellation results |

---

## Flask Implementation Details

### Connection Management
- **MAX_CONNECTIONS**: 10 concurrent WebSocket connections
- **MAX_CONNECTIONS_PER_IP**: 12 HTTP connections per IP
- **Connection tracking**: In-memory sets (`connected_clients`, `ip_connection_counts`)
- **Cleanup thread**: Runs every 15 seconds, removes stale connections

### Job Management
- **Job tracking**: `active_backup_jobs` dictionary with thread lock
- **Job state**: `{phase, message, progress, status, events, connected, backing_up, last_updated, executor}`
- **Status handler**: Per-job callback registered with `CallbackMultiplexer`
- **Executor**: `RealBackupExecutor` instance per job, launches C++ client subprocess

### File Monitoring
- **Monitor**: `UnifiedFileMonitor` singleton watches `received_files/`
- **Verification**: Compares expected size/hash from job registration
- **Callbacks**: `on_completion()` and `on_failure()` per registered job

### State Management
- **Server status**: Global `server_status` dict with lock, tracks connection state
- **Connection check**: `check_backup_server_status()` uses TCP socket probe to port 1256
- **Session state**: `connection_established` flag, `connection_timestamp`

### Background Tasks
- **WebSocket cleanup**: Daemon thread, 15s interval, managed via `thread_manager`
- **File monitor**: Separate thread watching filesystem events
- **Performance monitor**: Singleton tracking job metrics

### Configuration
- **Port**: 9090 (configurable via `get_config('api.port', 9090)`)
- **Server config**: `{host: '127.0.0.1', port: 1256, username: 'default_user'}`
- **Paths**: `CLIENT_GUI_PATH`, `PYTHON_SERVER_PATH` from project root

### Logging & Observability
- **Dual logging**: Console + file via `setup_dual_logging()`
- **Structured logging**: `create_enhanced_logger()` with context
- **Sentry**: Error tracking with `capture_error()` on 500/exceptions
- **Metrics**: `get_performance_monitor()` singleton for timing
- **Health tracking**: `get_connection_health_monitor()` for connection stats

---

## SQL Queries Used

From `UnifiedFileMonitor` and related code:

```sql
-- Check file receipt (DatabaseService will need this)
SELECT * FROM files WHERE original_name = ? ORDER BY stored_at DESC LIMIT 1

-- List received files
SELECT id, original_name, size_bytes, checksum_crc32, stored_at, verified
FROM files
ORDER BY stored_at DESC
LIMIT ? OFFSET ?

-- Get client info
SELECT * FROM clients WHERE client_id = ?

-- Get file transfer status
SELECT * FROM transfers WHERE file_id = ? ORDER BY started_at DESC LIMIT 1

-- Connection health aggregate
SELECT COUNT(*) as total, SUM(CASE WHEN last_seen > ? THEN 1 ELSE 0 END) as active
FROM clients
```

---

## C++ Implementation Priorities

### Phase 1 (HTTP & WebSocket Skeleton) - Week 1
1. CMakeLists.txt with vcpkg dependencies
2. AppServer boots Drogon on port 9090
3. Static file serving for Client-gui/
4. Health endpoint with system metrics
5. WebSocket controller with ping/pong

### Phase 2 (Job Runner) - Week 2
1. JobService wraps EncryptedBackupClient.exe
2. Stdout/stderr parsing for progress
3. Cancellation support
4. Job state snapshots

### Phase 3 (Database Facade) - Week 3
1. DatabaseService with SQLiteCpp
2. Prepared statements for queries above
3. Connection pooling
4. Read-only optimizations

### Phase 4 (REST API) - Week 4-5
1. Controllers for all 24 endpoints
2. Multipart upload handling
3. JSON serialization with nlohmann::json
4. Error responses matching Flask

### Phase 5 (Testing) - Week 6-7
1. Parity test harness
2. Upload/integrity tests
3. WebSocket regression tests
4. Performance benchmarks
5. 12-hour soak test

---

## Simplified WebSocket Protocol (Target)

Replace Socket.IO with plain WebSocket JSON:

```json
{
  "type": "progress",
  "jobId": "backup_123",
  "phase": "TRANSFER",
  "percent": 42.5,
  "bytesTransferred": 1048576,
  "totalBytes": 2500000,
  "etaMs": 183000
}
```

Message types:
- `status` - connection/server status
- `progress` - backup progress update
- `fileReceipt` - file verification result
- `jobCancelled` - cancellation notification
- `error` - error message

Client compatibility shim (`ws_adapter.js`) will translate between Socket.IO API and plain WebSocket.

---

## Dependencies Required

### vcpkg Packages
- `drogon` - HTTP framework
- `sqlitecpp` - SQLite wrapper
- `nlohmann-json` - JSON serialization
- `spdlog` - Structured logging
- `boost-process` - Process spawning

### System Libraries (Windows)
- `ws2_32.lib` - Winsock for TCP probes
- `pdh.lib` - Performance counters (CPU/memory)

---

## Configuration Schema

`cpp_api_server/config/default_config.json`:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 9090,
    "threads": 4,
    "document_root": "../Client/Client-gui"
  },
  "backup_server": {
    "host": "127.0.0.1",
    "port": 1256
  },
  "database": {
    "path": "../python_server/server/defensive.db",
    "readonly": true
  },
  "job_runner": {
    "client_exe": "../build/Release/EncryptedBackupClient.exe",
    "max_concurrent_jobs": 5,
    "timeout_seconds": 3600
  },
  "websocket": {
    "max_connections": 10,
    "ping_interval_seconds": 10,
    "ping_timeout_seconds": 20
  },
  "observability": {
    "log_level": "info",
    "log_file": "logs/cpp_api_server.log",
    "sentry_dsn": "",
    "metrics_enabled": true
  }
}
```

---

## Next Steps

1. ✅ Endpoint inventory complete
2. ⏳ Update CMakeLists.txt with dependencies (Phase 1.1)
3. ⏳ Implement AppServer with Drogon (Phase 1.2)
4. ⏳ Create health controller (Phase 1.3)
5. ⏳ Implement WebSocket controller (Phase 1.4)

**Entry Criteria Met:** Plan approved, Flask server documented, baseline metrics recorded.

**Phase 1 Exit Criteria:** Static assets served, /health working, WebSocket ping/pong verified, CI build succeeds.
