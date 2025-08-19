# Technical Architecture Diagrams

This file contains detailed ASCII diagrams for the 5-layer Client-Server Encrypted Backup Framework architecture.

## Complete 5-Layer System Architecture
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LAYER 1: WEB UI                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  NewGUIforClient.html (8000+ lines SPA)                            │    │
│  │  • ApiClient, FileManager, ThemeManager, ParticleSystem            │    │
│  │  • WebSocket client for real-time progress                         │    │
│  │  • Professional UI with tooltips, form memory, error boundaries    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │ HTTP Requests
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 2: FLASK API BRIDGE                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  cyberbackup_api_server.py (PORT 9090)                             │    │
│  │  • /api/start_backup, /api/backup_status endpoints                 │    │
│  │  • WebSocket broadcasting via SocketIO                             │    │
│  │  • CallbackMultiplexer (solves race conditions)                    │    │
│  │  • Sentry integration for error tracking                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  RealBackupExecutor (src/api/real_backup_executor.py)              │    │
│  │  • Subprocess management with --batch mode                         │    │
│  │  • Multi-layer progress monitoring system                          │    │
│  │  • FileReceiptProgressTracker (ground truth verification)          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │ subprocess.Popen()
                              │ + transfer.info generation
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LAYER 3: C++ CLIENT                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  EncryptedBackupClient.exe (build/Release/)                        │    │
│  │  • RSA-1024 + AES-256-CBC encryption                               │    │
│  │  • Custom binary protocol (23-byte headers)                        │    │
│  │  • CRC32 verification                                               │    │
│  │  • --batch mode for subprocess compatibility                       │    │
│  │  • Requires transfer.info (3-line config)                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │ TCP Connection
                              │ Binary Protocol
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LAYER 4: PYTHON SERVER                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  server.py (PORT 1256)                                              │    │
│  │  • Multi-threaded TCP server                                        │    │
│  │  • Protocol codes: REQ_REGISTER(1025), REQ_SEND_FILE(1028)         │    │
│  │  • RSA key exchange, AES file decryption                            │    │
│  │  • File storage in received_files/                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 5: SERVER MANAGEMENT GUI                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ServerGUI.py (python_server/server_gui/)                          │    │
│  │  • Professional Tkinter-based administration interface             │    │
│  │  • Dashboard, client monitoring, file management                   │    │
│  │  • Analytics and database management                               │    │
│  │  • Independent of main backup flow                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Critical Integration Points & Data Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SUBPROCESS MANAGEMENT PATTERN                        │
└─────────────────────────────────────────────────────────────────────────────┘

Flask API Request
     │
     ▼
┌─────────────────────────────────────────┐
│  RealBackupExecutor                     │
│  1. Generate transfer.info              │ ◄──── Critical: 3-line format
│     server:port                         │       Must be in CWD
│     username                            │
│     /absolute/file/path                 │
│  2. Set working directory               │
│  3. Launch: subprocess.Popen()          │
├─────────────────────────────────────────┤
│  [client_exe, "--batch"]                │ ◄──── Critical: --batch prevents hang
│  cwd=directory_containing_transfer_info │
│  stdin/stdout/stderr=subprocess.PIPE    │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  C++ Client Process                     │
│  1. Read transfer.info                  │
│  2. Connect to server (port 1256)       │
│  3. RSA key exchange                    │
│  4. AES encrypt file                    │
│  5. Send via binary protocol            │
│  6. Output progress to stdout           │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  Python Server (port 1256)             │
│  1. Accept TCP connection               │
│  2. Protocol handshake                  │
│  3. Receive encrypted file              │
│  4. Decrypt and save to received_files/ │
│  5. Send CRC confirmation               │
└─────────────────────────────────────────┘

Progress Updates Flow:
C++ stdout → RealBackupExecutor → CallbackMultiplexer → WebSocket → Web UI
```

## Multi-Layer Progress Monitoring System
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PROGRESS MONITORING ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────────────┘

RealBackupExecutor
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  RobustProgressMonitor (Multi-layer tracking)                              │
│                                                                             │
│  Layer 0: FileReceiptProgressTracker (HIGHEST PRIORITY)                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Watches received_files/ directory                               │   │
│  │  • File appears → IMMEDIATE 100% completion                        │   │
│  │  • Ground truth verification (overrides all other trackers)        │   │
│  │  • Uses watchdog library + polling fallback                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Layer 1: StatisticalProgressTracker                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Parses C++ client stdout for progress indicators                 │   │
│  │  • Statistical analysis of transfer patterns                        │   │
│  │  • Calibrated against progress_config.json                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Layer 2: TimeBasedEstimator                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • File size based time estimation                                  │   │
│  │  • Historical transfer rate data                                    │   │
│  │  • Phase-aware progress (connect, encrypt, transfer)                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Layer 3: BasicProcessingIndicator                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Fallback spinner/processing indicator                            │   │
│  │  • Used when other trackers fail                                    │   │
│  │  • Ensures UI always shows activity                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  CallbackMultiplexer (Solves Race Conditions)                              │
│  • Routes progress to correct job handlers                                 │
│  • Thread-safe per-job callback management                                 │
│  • Eliminates callback overwriting in global singleton                     │
└─────────────────────────────────────────────────────────────────────────────┘
     │
     ▼
WebSocket Broadcasting → Web UI Real-time Updates
```

## File Transfer Verification Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       VERIFICATION & ERROR DETECTION                        │
└─────────────────────────────────────────────────────────────────────────────┘

File Upload Request
     │
     ▼
┌─────────────────────────────────────────┐
│  Pre-Transfer Validation                │
│  • Check file exists and readable       │
│  • Calculate SHA256 hash                │
│  • Verify server connectivity (1256)    │
│  • Check transfer.info format           │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  Transfer Execution                     │
│  • Launch C++ client subprocess         │
│  • Monitor stdout/stderr streams        │
│  • Track process exit code              │
│  • Monitor network activity             │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  Multi-Point Verification              │
│  ✓ File appears in received_files/     │ ◄──── PRIMARY verification
│  ✓ File size matches original          │
│  ✓ SHA256 hash matches                 │
│  ✓ Network activity on port 1256       │
│  ✓ CRC32 verification from server      │
│  ⚠ Process exit code (UNRELIABLE)      │ ◄──── Do NOT rely on this alone
└─────────────────────────────────────────┘

Critical Truth: File presence in received_files/ is the ONLY reliable success indicator
Exit codes can be zero even when transfer fails - always verify actual file receipt
```

## System Startup & Deployment Process Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          COMPLETE SYSTEM STARTUP                            │
└─────────────────────────────────────────────────────────────────────────────┘

scripts/one_click_build_and_run.py (RECOMMENDED ENTRY POINT)
     │
     ▼
┌─────────────────────────────────────────┐
│  Environment Validation                 │
│  ✓ Python 3.13+ available              │
│  ✓ CMake and vcpkg toolchain present    │
│  ✓ Ports 9090 and 1256 free             │
│  ✓ Check dependencies (requirements.txt)│
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  C++ Client Build (if needed)           │
│  1. cmake -B build -DCMAKE_TOOLCHAIN... │
│  2. cmake --build build --config Release│
│  ✓ Output: build/Release/Encrypted...   │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  Configuration Setup                    │
│  • Create/validate transfer.info        │
│  • Load progress_config.json            │
│  • Initialize server_gui_settings.json  │
│  • Setup UTF-8 environment              │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  Service Startup Sequence (CRITICAL)    │
│  1. Start Python Server (port 1256)     │ ◄──── MUST start FIRST
│  2. Wait for server ready signal        │
│  3. Start Flask API Bridge (port 9090)  │
│  4. Launch web browser → localhost:9090 │
│  5. [Optional] Launch Server GUI        │
└─────────────────────────────────────────┘

Manual Startup Alternative:
python python_server/server/server.py        # Terminal 1
python api_server/cyberbackup_api_server.py  # Terminal 2
python -m python_server.server_gui           # Terminal 3 (optional)
```

## Build System & Dependency Management
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BUILD SYSTEM ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────────┘

Developer Change → Build Process
     │
     ▼
┌─────────────────────────────────────────┐
│  CMake Configuration                    │
│  REQUIRED: vcpkg toolchain              │
│  cmake -B build -DCMAKE_TOOLCHAIN_FILE │
│  ="vcpkg/scripts/buildsystems/vcpkg.cmake│
│                                         │
│  Dependencies from vcpkg.json:          │
│  • boost-asio, boost-beast, boost-iostreams
│  • cryptopp (RSA/AES encryption)        │
│  • zlib (compression)                   │
│  • sentry-native (error reporting)      │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  Compilation Process                    │
│  cmake --build build --config Release   │
│                                         │
│  Source Files:                          │
│  • Client/cpp/main.cpp                  │
│  • Client/cpp/client.cpp (1.6K lines)   │
│  • Client/deps/*.cpp (crypto wrappers)  │
│                                         │
│  Critical Flags:                        │
│  • WIN32_LEAN_AND_MEAN                  │
│  • NOMINMAX (prevent min/max conflicts) │
│  • C++17 standard required              │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  Python Dependencies                    │
│  pip install -r requirements.txt        │
│                                         │
│  Critical Packages:                     │
│  • flask-cors (CORS handling)           │
│  • flask-socketio (WebSocket support)   │
│  • watchdog (file monitoring)           │
│  • sentry-sdk (error tracking)          │
│  • psutil (process management)          │
│  • pycryptodome (crypto fallback)       │
└─────────────────────────────────────────┘

Output Artifacts:
• build/Release/EncryptedBackupClient.exe (C++ client)
• Python services ready for deployment
• Configuration files validated
```

## Error Handling & Recovery Flows
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ERROR DETECTION & RECOVERY                            │
└─────────────────────────────────────────────────────────────────────────────┘

System Error Detected
     │
     ▼
┌─────────────────────────────────────────┐
│  Error Classification                   │
│  • Port conflicts (9090/1256)           │
│  • Subprocess hang (missing --batch)    │
│  • Transfer failure (file not received) │
│  • Build failures (missing vcpkg)       │
│  • Configuration errors (transfer.info) │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  Automatic Recovery Attempts           │
│                                         │
│  Port Conflicts:                        │
│  • Kill existing processes              │
│  • Wait for TIME_WAIT (30-60 seconds)   │
│  • Retry service startup                │
│                                         │
│  Subprocess Issues:                     │
│  • Force kill hung processes            │
│  • Regenerate transfer.info             │
│  • Restart with correct --batch mode    │
│                                         │
│  Transfer Failures:                     │
│  • Verify file receipt in received_files│
│  • Compare SHA256 hashes                │
│  • Check network connectivity           │
│  • Retry with new job ID                │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  Emergency Recovery Protocol           │
│  taskkill /f /im python.exe             │
│  taskkill /f /im EncryptedBackupClient  │
│  del transfer.info                      │
│  python scripts/one_click_build_and_run │
│                                         │
│  Diagnostic Commands:                   │
│  netstat -an | findstr ":9090\|:1256"  │
│  tasklist | findstr "python"           │
│  dir received_files                     │
└─────────────────────────────────────────┘

Error Reporting Flow:
Local Error → Sentry SDK → Error Dashboard
          ↘ Log Files → observability.py → Structured Logs
```