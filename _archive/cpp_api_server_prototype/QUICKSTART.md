# C++ API Server - Quick Start Guide

## Prerequisites Installed ✅
- vcpkg 2025-09-03 (local installation)
- Drogon 1.9.11 + dependencies
- MSVC 19.44 Build Tools
- CMake 3.20+

## Build the Server

```powershell
# Configure CMake (first time only)
cmake -B cpp_api_server/build -S cpp_api_server `
  -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake" `
  -DCMAKE_BUILD_TYPE=Release `
  -DVCPKG_INSTALLED_DIR="$PWD/vcpkg_installed"

# Build
cmake --build cpp_api_server/build --config Release
```

## Run the Server

```powershell
# Option 1: Direct launch
.\cpp_api_server\build\Release\cpp_api_server.exe cpp_api_server\config\default_config.json

# Option 2: PowerShell script (recommended)
.\cpp_api_server\start_cpp_api_server.ps1
```

## Test the Server

```powershell
# Health check
Invoke-WebRequest http://127.0.0.1:9090/health

# Expected output:
# {
#   "status": "healthy",
#   "backup_server_status": "running",
#   "backup_server": "running",
#   "api_server": "running",
#   "system_metrics": {
#     "cpu_usage_percent": 0.0,
#     "memory_usage_percent": 0.0,
#     "active_websocket_connections": 0,
#     "active_backup_jobs": 0
#   },
#   "timestamp": "2025-11-07T18:33:54",
#   "uptime_info": "API server responsive"
# }
```

## Architecture

```
Client Browser/GUI
      ↓
C++ API Server (Drogon) :9090
      ↓
├─ HTTP Endpoints
│  ├─ /health - Health check
│  ├─ /api/health - Health check (alias)
│  └─ / - Static files (Client-gui)
│
├─ WebSocket
│  └─ /ws/status - Real-time updates
│
└─ Services
   ├─ JobService - Backup job management (Phase 2)
   ├─ DatabaseService - SQLite operations (Phase 2)
   └─ Notifier - WebSocket broadcasts
```

## Phase 1 Status

### ✅ Complete
- [x] Build system (CMake + vcpkg)
- [x] Drogon HTTP server
- [x] Health endpoint with backup server probe
- [x] WebSocket endpoint skeleton
- [x] Configuration management
- [x] Logging integration
- [x] Static file serving

### 🚧 Phase 2 TODO
- [ ] JobService with boost::process
- [ ] DatabaseService with SQLiteCpp
- [ ] Notifier with WebSocket broadcasts
- [ ] 10 remaining REST endpoints
- [ ] Full Flask API parity

## Configuration

Edit `cpp_api_server/config/default_config.json`:

```json
{
  "listeners": [
    {
      "address": "127.0.0.1",
      "port": 9090,
      "https": false
    }
  ],
  "threads": 4,
  "document_root": "../Client/Client-gui",
  "app": {
    "backup_server_host": "127.0.0.1",
    "backup_server_port": 1256,
    "database_path": "../python_server/server/defensive.db",
    "client_executable": "../build/Release/EncryptedBackupClient.exe"
  }
}
```

## Troubleshooting

### Build Errors

**Error**: `Could not find a package configuration file provided by "Drogon"`

**Solution**: Install vcpkg dependencies:
```powershell
.\vcpkg\vcpkg.exe install --triplet x64-windows
```

**Error**: `WinSock.h has already been included`

**Solution**: This is why boost::process is commented out in Phase 1. Will be fixed in Phase 2.

### Runtime Errors

**Error**: Server exits immediately

**Solution**: Provide config file path as first argument:
```powershell
.\cpp_api_server.exe path\to\config.json
```

**Error**: Cannot bind to port 9090

**Solution**: Check if Flask API server is already running:
```powershell
Get-NetTCPConnection -LocalPort 9090 -ErrorAction SilentlyContinue
# Kill conflicting process if found
```

## Development

### Adding a New Endpoint

1. Create controller in `include/cpp_api_server/`:
```cpp
#pragma once
#include <drogon/HttpSimpleController.h>

class MyController : public drogon::HttpSimpleController<MyController> {
public:
    PATH_LIST_BEGIN
    PATH_ADD("/api/my_endpoint", Get);
    PATH_LIST_END

    void asyncHandleHttpRequest(
        const drogon::HttpRequestPtr& req,
        std::function<void(const drogon::HttpResponsePtr&)>&& callback);
};
```

2. Implement in `src/`:
```cpp
#include "MyController.h"

void MyController::asyncHandleHttpRequest(
    const HttpRequestPtr& req,
    std::function<void(const HttpResponsePtr&)>&& callback) {

    Json::Value response;
    response["message"] = "Hello World";

    auto resp = HttpResponse::newHttpJsonResponse(response);
    callback(resp);
}
```

3. Add to CMakeLists.txt:
```cmake
set(CPP_API_SERVER_SOURCES
    # ... existing files ...
    src/MyController.cpp
)
```

4. Rebuild:
```powershell
cmake --build cpp_api_server/build --config Release
```

## Performance

### Expected Metrics (Phase 1)
- Startup time: < 1 second
- Memory usage: ~20-30 MB
- Health endpoint: < 1ms response
- Concurrent connections: 100 (configurable)
- Thread pool: 4 threads (configurable)

### Optimization Tips
- Increase threads for higher concurrency
- Use connection pooling for database
- Enable HTTP/2 in Drogon config
- Use release build (`-DCMAKE_BUILD_TYPE=Release`)

## Next Steps

1. **Test Phase 1**:
   - Verify health endpoint
   - Test WebSocket connection
   - Load test with multiple clients

2. **Start Phase 2**:
   - Implement JobService subprocess launching
   - Add DatabaseService CRUD operations
   - Implement remaining REST endpoints

3. **Integration**:
   - Replace Flask API server in `one_click_build_and_run.py`
   - Update web GUI to use C++ server
   - Performance benchmarking

## Resources

- [Drogon Documentation](https://drogon.org)
- [vcpkg Documentation](https://vcpkg.io)
- [Project Architecture](../AGENTS.md)
- [Endpoint Inventory](ENDPOINT_INVENTORY.md)
- [Build Instructions](BUILD_INSTRUCTIONS.md)
