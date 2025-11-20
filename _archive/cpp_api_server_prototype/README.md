# C++ API Server - Simplified Flask Replacement

## Overview

A lean C++ service replacing the Flask API server with direct SQLite access, plain WebSockets, and minimal dependencies. Built following the simplification principles outlined in `CPP_API_SERVER_MIGRATION_PLAN.md`.

## Architecture

Five focused modules, each under ~300 lines:

1. **AppServer** - Boots Drogon, wires routes/WebSocket hub, loads config
2. **JobService** - Wraps `EncryptedBackupClient.exe` launch/cancel with stdout parsing
3. **DatabaseService** - Direct SQLite queries via prepared statements
4. **Notifier** - WebSocket connection manager and JSON broadcast hub
5. **Config** - Strongly-typed configuration loader

## Directory Structure

```
cpp_api_server/
├── include/cpp_api_server/    # Public headers
│   ├── AppServer.h
│   ├── JobService.h
│   ├── DatabaseService.h
│   ├── Notifier.h
│   └── Config.h
├── src/                        # Implementation files
│   ├── AppServer.cpp
│   ├── JobService.cpp
│   ├── DatabaseService.cpp
│   ├── Notifier.cpp
│   ├── Config.cpp
│   └── main.cpp
├── controllers/                # Drogon HTTP controllers
│   ├── ApiController.h/.cpp
│   └── StatusWebSocketController.h/.cpp
├── config/
│   └── drogon.config.json     # Drogon server configuration
├── tests/                      # Unit tests (Catch2)
└── CMakeLists.txt
```

## Build Requirements

- CMake ≥ 3.26
- MSVC 17.x or GCC 11+
- vcpkg with packages:
  - drogon
  - sqlitecpp
  - nlohmann-json
  - spdlog
  - boost-process

## Quick Start

```bash
# Configure with vcpkg toolchain
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake"

# Build
cmake --build build --config Release

# Run
./build/Release/cpp_api_server
```

## Migration Status

Current Phase: **Phase 0 - Discovery & Blueprint**

- [ ] Endpoint inventory complete
- [ ] WebSocket protocol defined
- [ ] SQLite query catalog documented
- [ ] Baseline metrics captured

See `docs/CPP_API_SERVER_MIGRATION_PLAN.md` for full roadmap.

## Key Differences from Flask

- **Single language** - No Python embedding or subprocess orchestration
- **Direct data access** - SQLite queries without helper modules
- **Plain WebSockets** - No Socket.IO dependency
- **Explicit concurrency** - Thread pool and async I/O via Drogon
- **Predictable control flow** - Clear request → handler → response path

## Development

Hot-reload during development:
```bash
drogon_ctl run --sync
```

Run tests:
```bash
cd build && ctest --output-on-failure
```

## Documentation

- Architecture: See module READMEs in `include/cpp_api_server/`
- Migration plan: `docs/CPP_API_SERVER_MIGRATION_PLAN.md`
- Endpoint parity: `docs/ENDPOINT_PARITY_MATRIX.md` (TBD)
- WebSocket protocol: `docs/WEBSOCKET_PROTOCOL.md` (TBD)
