# MASTER DOCUMENTATION: Encrypted Backup Framework - Complete System Guide

**Version**: 3.0 Multi-Layer Architecture
**Status**: Core components operational | Enhanced layers in planning phase
**Last Updated**: 2025-11-11
**Total Project Files**: 147 files
**Codebase**: ~15,000+ lines

---

## Table of Contents

1. [Quick Start & Overview](#quick-start--overview)
2. [System Architecture (Current + Proposed)](#system-architecture-current--proposed)
3. [Project Structure & Files](#project-structure--files)
4. [Core Components Deep Dive](#core-components-deep-dive)
5. [Protocol Specification](#protocol-specification)
6. [Cryptographic Implementation](#cryptographic-implementation)
7. [Data Flows & Sequences](#data-flows--sequences)
8. [Configuration & Deployment](#configuration--deployment)
9. [Integration Guide](#integration-guide)
10. [Testing & Quality Assurance](#testing--quality-assurance)
11. [Security Analysis](#security-analysis)
12. [Troubleshooting](#troubleshooting)

---

## Quick Start & Overview

### What This System Does

The **Encrypted Backup Framework** is a secure file transfer system that enables clients to upload files to a server with **zero-knowledge encryption** - the server never has access to plaintext files. Files are encrypted on the client side before transmission, transferred securely, and verified upon receipt.

### Current System Components

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  C++ CLIENT     │◄─────►│ PYTHON SERVER   │◄─────►│  SQLITE DB      │
│ + Windows GUI   │ TCP   │ + Tkinter GUI   │       │ (defensive.db)  │
│                 │ Port  │                 │       │                 │
│ - RSA-1024      │ 1256  │ - Multi-thread  │       │ - Clients       │
│ - AES-256-CBC   │       │ - Session mgmt  │       │ - Files         │
│ - CRC-32        │       │ - Key exchange  │       │ - Metadata      │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                 │
                                 ▼
                          /received_files/
                         (Encrypted Files)
```

### Operational Status

| Component | Status | Details |
|-----------|--------|---------|
| C++ Client | ✅ Operational | 1,702 lines, GUI included |
| Python Server | ✅ Operational | 1,581 lines, multi-threaded |
| SQLite Database | ✅ Operational | Persistent storage |
| Crypto (RSA) | ✅ Operational | 1024-bit OAEP-SHA256 |
| Crypto (AES) | ✅ Operational | 256-bit CBC |
| CRC Verification | ✅ Operational | Linux cksum compatible |
| Tkinter GUI | ✅ Operational | Server monitoring |
| Windows GUI | ✅ Operational | Client interface |

### Proposed Enhanced Layers (Planning Phase)

```
Layer 1: Flask API Server (NEW) → Bridges C++ client and web access
Layer 2: Web-Based GUI (NEW)     → HTML/JS/React client interface
Layer 3: Flet 0.28.3 GUI (NEW)   → Replaces Tkinter for better desktop UX
```

---

## System Architecture (Current + Proposed)

### Current Architecture (OPERATIONAL)

```
TIER 1: CLIENT SIDE
═══════════════════════════════════════════════════════════════════════════
│                                                                           │
│  C++ Client Application (EncryptedBackupClient.exe)                     │
│  ├─ Windows Console GUI (status window, system tray)                   │
│  ├─ RSA Key Management                                                  │
│  │  ├─ Generates/Loads 1024-bit RSA key pair                          │
│  │  ├─ Stores private key in me.info (Base64-encoded)                │
│  │  └─ Sends public key (DER format, 162 bytes)                       │
│  ├─ File Processing                                                     │
│  │  ├─ Reads file from path specified in transfer.info                │
│  │  ├─ Calculates CRC using Linux cksum algorithm                     │
│  │  └─ Encrypts with AES-256-CBC (zero IV)                           │
│  ├─ Network Communication                                              │
│  │  ├─ Connects to server on port 1256 (3 retries)                   │
│  │  ├─ Implements custom binary protocol v3                           │
│  │  ├─ 23-byte little-endian headers                                  │
│  │  └─ Supports multi-packet transfers                                │
│  └─ Error Handling                                                      │
│     ├─ Connection retry logic (5s delays)                             │
│     ├─ CRC verification with auto-retry (3 attempts)                 │
│     └─ Comprehensive error messages                                   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘

         │
         │ Custom Binary Protocol v3 (TCP Port 1256)
         │ ├─ Request codes: 1025-1031
         │ ├─ Response codes: 1600-1607
         │ └─ Little-endian encoding

         ▼

TIER 2: SERVER SIDE
═══════════════════════════════════════════════════════════════════════════
│                                                                           │
│  Python Server Application (server.py)                                  │
│  ├─ Multi-Threaded TCP Server                                          │
│  │  ├─ Listens on 0.0.0.0:1256                                        │
│  │  ├─ Accepts concurrent client connections                          │
│  │  ├─ Daemon threads for each client                                 │
│  │  └─ 30-second socket timeout                                       │
│  ├─ Client Management                                                   │
│  │  ├─ Registration (generates 16-byte UUID)                          │
│  │  ├─ Session tracking with 10-min timeout                           │
│  │  ├─ Public key storage and validation                              │
│  │  └─ Automatic inactive client cleanup                              │
│  ├─ Key Exchange                                                        │
│  │  ├─ Generates 32-byte AES-256 session key                         │
│  │  ├─ Encrypts with client's RSA public key (OAEP-SHA256)           │
│  │  └─ Distributes encrypted key to client                            │
│  ├─ File Transfer                                                       │
│  │  ├─ Multi-packet reassembly with state tracking                   │
│  │  ├─ AES-256-CBC decryption (zero IV)                              │
│  │  ├─ PKCS7 padding removal                                          │
│  │  └─ Atomic file write to received_files/                          │
│  ├─ Verification & Storage                                             │
│  │  ├─ CRC-32 calculation (Linux cksum)                              │
│  │  ├─ Atomic file operations                                         │
│  │  └─ Database persistence                                           │
│  ├─ Monitoring GUI (Tkinter)                                           │
│  │  ├─ Real-time server status                                        │
│  │  ├─ Connected clients count                                        │
│  │  ├─ Transfer statistics                                            │
│  │  └─ System tray integration                                        │
│  └─ Maintenance                                                         │
│     ├─ 60-second cleanup cycle                                        │
│     ├─ Session timeout enforcement                                    │
│     └─ Resource cleanup                                               │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘

         │
         │ SQLite3 (ACID transactions)
         │ ├─ clients table (ID, Name, PublicKey, AESKey, LastSeen)
         │ ├─ files table (ID, FileName, PathName, Verified)
         │ └─ Automatic foreign key constraints

         ▼

TIER 3: PERSISTENCE
═══════════════════════════════════════════════════════════════════════════
│                                                                           │
│  SQLite Database (defensive.db)                                         │
│  ├─ Schema Version: 1.0                                                │
│  ├─ Transaction Log: WAL mode for concurrent access                   │
│  └─ Location: Same directory as server.py                             │
│                                                                           │
│  File Storage (received_files/)                                         │
│  ├─ Encrypted files from clients                                       │
│  ├─ Atomic write-then-rename operations                                │
│  └─ Zero-knowledge (server cannot decrypt)                             │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Proposed Enhanced Architecture (PLANNING)

```
ADDED LAYER 1: FLASK API SERVER (HTTP/REST GATEWAY)
═══════════════════════════════════════════════════════════════════════════
│                                                                           │
│  Flask Application (app.py)                                             │
│  ├─ HTTP/REST Endpoints (Port 5000)                                    │
│  │  ├─ POST /api/v1/auth/register - Register new client              │
│  │  ├─ POST /api/v1/auth/login - Authenticate client                │
│  │  ├─ POST /api/v1/keys/public - Public key exchange                │
│  │  ├─ POST /api/v1/files/upload - Upload encrypted file            │
│  │  ├─ POST /api/v1/files/verify - Verify CRC                       │
│  │  └─ GET /api/v1/status - Server status                           │
│  ├─ Protocol Translation (ServerProxy)                                 │
│  │  ├─ HTTP ↔ Binary protocol conversion                             │
│  │  ├─ JSON ↔ Binary payload encoding                                │
│  │  └─ Maintains backward compatibility with TCP clients             │
│  ├─ JWT Authentication                                                 │
│  │  ├─ Session token management                                       │
│  │  ├─ Token validation on each request                              │
│  │  └─ Configurable expiration times                                 │
│  ├─ Error Handling                                                      │
│  │  ├─ Standardized JSON error responses                             │
│  │  ├─ HTTP status codes (400, 401, 500)                            │
│  │  └─ Comprehensive logging                                          │
│  └─ CORS Support                                                        │
│     ├─ Cross-origin requests from web GUI                            │
│     └─ Configurable allowed origins                                   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘

         │ HTTP/REST + Optional WebSocket
         │

ADDED LAYER 2: WEB-BASED CLIENT GUI (REACT/VUE)
═══════════════════════════════════════════════════════════════════════════
│                                                                           │
│  Single Page Application (HTML/CSS/JavaScript)                          │
│  ├─ Dashboard Component                                                 │
│  │  ├─ Server connection status                                        │
│  │  ├─ File upload button                                             │
│  │  └─ Transfer history                                               │
│  ├─ File Uploader Component                                            │
│  │  ├─ File selection dialog                                          │
│  │  ├─ Progress bar with percentage                                   │
│  │  └─ Speed and ETA display                                         │
│  ├─ Authentication                                                      │
│  │  ├─ Login page                                                     │
│  │  ├─ Session token management                                       │
│  │  └─ Logout functionality                                           │
│  ├─ Client-Side Encryption                                             │
│  │  ├─ AES-256-CBC (JavaScript Web Crypto API)                       │
│  │  ├─ CRC-32 calculation (matching Linux cksum)                     │
│  │  └─ Zero-knowledge (encryption before upload)                      │
│  ├─ API Communication                                                   │
│  │  ├─ Axios/Fetch for REST calls                                    │
│  │  ├─ Error handling and retry logic                                │
│  │  └─ Automatic token refresh                                       │
│  └─ Responsive Design                                                   │
│     ├─ Desktop and mobile layouts                                     │
│     ├─ Dark/light theme support                                      │
│     └─ Accessibility features                                        │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘

         │ HTTP/REST (to Flask API Server)
         │

CORE SERVER (UNCHANGED)
═══════════════════════════════════════════════════════════════════════════
│  Python Server, SQLite DB, File Storage (as described in current)       │
└─────────────────────────────────────────────────────────────────────────┘

         │

ADDED LAYER 3: FLET 0.28.3 DESKTOP GUI (REPLACES TKINTER)
═══════════════════════════════════════════════════════════════════════════
│                                                                           │
│  Flet Desktop Application (main.py)                                     │
│  ├─ Navigation Rail                                                     │
│  │  ├─ Dashboard (server status)                                       │
│  │  ├─ Clients (client management)                                     │
│  │  ├─ Transfers (file transfer history)                              │
│  │  └─ Settings (configuration options)                                │
│  ├─ Dashboard Page                                                      │
│  │  ├─ Server status card (online/offline)                            │
│  │  ├─ Statistics cards (clients, transfers, bytes)                   │
│  │  ├─ Real-time activity feed                                        │
│  │  └─ Charts and graphs                                              │
│  ├─ Clients Page                                                        │
│  │  ├─ Connected clients list                                         │
│  │  ├─ Client details (ID, username, public key)                     │
│  │  ├─ Session management                                             │
│  │  └─ Manual client removal                                          │
│  ├─ Transfers Page                                                      │
│  │  ├─ Current transfers in progress                                  │
│  │  ├─ Transfer history                                               │
│  │  ├─ CRC verification status                                        │
│  │  └─ Performance metrics                                            │
│  ├─ Settings Page                                                       │
│  │  ├─ Server configuration                                           │
│  │  ├─ Database settings                                              │
│  │  ├─ Log level configuration                                        │
│  │  └─ Backup/restore options                                         │
│  ├─ Threading Model                                                     │
│  │  ├─ Flet UI in main thread                                         │
│  │  ├─ Server logic in background thread                              │
│  │  ├─ Queue-based updates to UI                                      │
│  │  └─ Non-blocking operations                                        │
│  └─ Real-Time Monitoring                                               │
│     ├─ 1-second update intervals                                      │
│     ├─ Automatic refresh on data changes                              │
│     └─ Activity notifications                                          │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure & Files

### Complete File Organization (147 files)

```
/client-server-encrypted-backup-framework-clean/
│
├─ SOURCE CODE (48 files)
│  ├─ /src/
│  │  ├─ /client/
│  │  │  ├─ client.cpp (1,702 lines) - Main client logic
│  │  │  ├─ protocol.cpp (350 lines) - Binary protocol handler
│  │  │  ├─ ClientGUI.cpp (658 lines) - Windows GUI
│  │  │  └─ cksum.cpp (94 lines) - CRC-32 implementation
│  │  │
│  │  ├─ /wrappers/
│  │  │  ├─ RSAWrapper.cpp (309 lines) - RSA-1024 encryption
│  │  │  ├─ AESWrapper.cpp (109 lines) - AES-256-CBC encryption
│  │  │  ├─ Base64Wrapper.cpp (25 lines) - Base64 encoding
│  │  │  └─ RSAWrapper_stub.cpp (168 lines) - Fallback RSA
│  │  │
│  │  └─ HELPERS
│  │     ├─ cfb_stubs.cpp - CFB cipher stubs
│  │     ├─ cryptopp_helpers.cpp - Crypto++ helpers
│  │     ├─ cryptopp_helpers_clean.cpp - Clean helpers
│  │     └─ randpool_stub.cpp - Random pool implementation
│  │
│  ├─ /include/
│  │  ├─ /client/
│  │  │  ├─ client.h - Client namespace
│  │  │  ├─ protocol.h - Protocol constants
│  │  │  ├─ ClientGUI.h - GUI class definition
│  │  │  └─ cksum.h - CRC function declarations
│  │  │
│  │  └─ /wrappers/
│  │     ├─ RSAWrapper.h - RSA public API
│  │     ├─ AESWrapper.h - AES public API
│  │     └─ Base64Wrapper.h - Base64 API
│  │
│  └─ /server/
│     ├─ server.py (1,581 lines) - Main server
│     ├─ ServerGUI.py (656 lines) - Tkinter GUI
│     ├─ crypto_compat.py (141 lines) - Crypto layer
│     ├─ test_server.py (159 lines) - Server tests
│     ├─ test_gui.py (125 lines) - GUI tests
│     └─ port.info - Port configuration
│
├─ TEST & UTILITY FILES (15+ files)
│  ├─ /tests/
│  │  ├─ test_rsa_final.cpp - RSA test suite
│  │  ├─ test_rsa_wrapper_final.cpp - RSA wrapper tests
│  │  ├─ test_rsa_crypto_plus_plus.cpp (177 lines) - Crypto++ tests
│  │  ├─ test_connection.py (206 lines) - Integration test
│  │  ├─ [8+ additional RSA/crypto tests]
│  │  └─ test.txt, test_file.txt - Test data
│  │
│  ├─ ROOT LEVEL TESTS
│  │  ├─ test_client.py (9.6 KB) - Client tests
│  │  ├─ test_system.py (12 KB) - System tests
│  │  ├─ simple_test.py - Basic connection test
│  │  ├─ minimal_test.py - Minimal test
│  │  └─ binary_test_client.py - Binary protocol test
│  │
│  └─ /scripts/
│     ├─ generate_valid_rsa_key.py (125 lines) - Key generation
│     └─ fix_emojis.py - Documentation cleanup
│
├─ BUILD & STARTUP (12 batch files)
│  ├─ build.bat - Main MSVC build
│  ├─ build.bat.backup - Build backup
│  ├─ build_safe.bat - Safe build
│  ├─ build_fixed.bat - Fixed build
│  ├─ clean.bat - Build cleanup
│  ├─ start_server.bat - Start server
│  ├─ start_client.bat - Start client
│  ├─ start_test_client.bat - Start test client
│  ├─ debug_client.bat - Debug mode
│  ├─ run_client_debug.bat - Debug runner
│  ├─ check_client_process.bat - Process checker
│  └─ run_simple_test.bat - Simple test runner
│
├─ DOCUMENTATION (26 files)
│  ├─ COMPREHENSIVE_SYSTEM_DOCUMENTATION.md - Full docs
│  ├─ COMPLETE_MULTI_LAYER_ARCHITECTURE.md - Multi-layer guide
│  ├─ MASTER_SYSTEM_DOCUMENTATION.md - THIS FILE
│  ├─ specification.md (31 KB) - Technical specification
│  ├─ RSA_FIX_IMPLEMENTATION_REPORT.md - RSA status
│  ├─ PROJECT_STATUS_CHECKPOINT.md - Status report
│  ├─ GUI_BASIC_CAPABILITIES.md - GUI features
│  ├─ GUI_INTEGRATION_STATUS.md - GUI status
│  ├─ [15+ additional documentation files]
│  └─ docs/ - All documentation
│
├─ CONFIGURATION
│  ├─ .gitignore - Git ignore rules
│  ├─ port.info - Server port (root)
│  ├─ /server/port.info - Server port
│  ├─ /config/.clang-format - Code formatting
│  ├─ /config/.clang-tidy - Static analysis
│  ├─ /.claude/settings.local.json - Claude settings
│  ├─ /.github/workflows/backup-branch.yml - CI/CD
│  └─ CLAUDE.md - Project instructions
│
├─ GIT & VCS
│  ├─ .git/ - Git repository
│  ├─ .gitignore - Ignore patterns
│  └─ /.github/workflows/ - GitHub workflows
│
├─ RUNTIME DIRECTORIES
│  ├─ /build/ - Compiled binaries (generated)
│  │  ├─ EncryptedBackupClient.exe - Client executable
│  │  ├─ test_rsa_final.exe - RSA test
│  │  └─ [test executables]
│  │
│  ├─ /client/ - Client test data
│  │  └─ test_file.txt
│  │
│  └─ /received_files/ - Server file storage (generated)
│
├─ THIRD-PARTY
│  └─ /third_party/crypto++/ - Bundled Crypto++ library
│
└─ MISC
   ├─ temp_complete_server.py - Backup server
   ├─ simple_test.cpp - C++ test
   ├─ simple_console_test.cpp - Console test
   ├─ test_minimal.cpp - Minimal test
   ├─ test_simple.cpp - Simple test
   ├─ test_simple_debug.bat - Debug test runner
   └─ diff_output.txt - Test output
```

---

## Core Components Deep Dive

### Component 1: C++ Client (`src/client/client.cpp`)

**Size**: 1,702 lines | **Language**: C++17 | **Platform**: Windows

**Main Responsibilities**:
1. **Initialization**: Load configuration, generate/load RSA keys
2. **Connection**: Connect to server with retry logic
3. **Registration**: Register if new, reconnect if existing
4. **Key Exchange**: Send public key, receive encrypted AES key
5. **File Transfer**: Encrypt file, transfer in packets
6. **Verification**: Verify CRC, retry on mismatch

**Key Functions**:
- `main()` - Entry point, initializes application
- `initialize()` - Load configuration and RSA keys
- `performRegistration()` - Register with server (REQ_REGISTER 1025)
- `sendPublicKey()` - Exchange public key (REQ_SEND_PUBLIC_KEY 1026)
- `transferFile()` - Upload encrypted file (REQ_SEND_FILE 1028)
- `verifyCRC()` - Verify file integrity with retry logic

**Dependencies**:
- Crypto++ (RSA, AES, Base64)
- Windows API (networking, GUI)
- Standard C++ library

### Component 2: Python Server (`server/server.py`)

**Size**: 1,581 lines | **Language**: Python 3.11+ | **Port**: 1256

**Main Responsibilities**:
1. **Socket Server**: Accept TCP connections
2. **Client Management**: Register clients, track sessions
3. **Key Exchange**: Distribute RSA-encrypted AES keys
4. **File Transfer**: Reassemble multi-packet files
5. **Verification**: Calculate CRC, persist files
6. **Database**: SQLite persistence of clients and files
7. **Maintenance**: Clean inactive sessions

**Key Classes**:
- `EncryptedBackupServer` - Main server
- `Client` - Client state representation
- Request handlers: `_handle_registration()`, `_handle_send_public_key()`, etc.

**Dependencies**:
- Python 3.11+
- PyCryptodome
- SQLite3
- Threading
- Socket

### Component 3: Binary Protocol

**Version**: 3 | **Transport**: TCP | **Encoding**: Little-endian

**Request Header (23 bytes)**:
- Bytes 0-15: client_id (16 bytes)
- Byte 16: version (1 byte)
- Bytes 17-18: code (uint16, little-endian)
- Bytes 19-22: payload_size (uint32, little-endian)

**Response Header (7 bytes)**:
- Byte 0: version
- Bytes 1-2: code (uint16, little-endian)
- Bytes 3-6: payload_size (uint32, little-endian)

**Request Codes**: 1025-1031 (registration, auth, file, CRC)
**Response Codes**: 1600-1607 (OK, fail, CRC, ACK, error)

### Component 4: Cryptography

**RSA (1024-bit OAEP-SHA256)**:
- Key generation: New 1024-bit pair per client
- Public key format: DER encoding (162 bytes)
- Encryption: PKCS1_OAEP with SHA-256
- Use: AES session key protection

**AES (256-bit CBC)**:
- Key size: 32 bytes
- Mode: CBC with PKCS7 padding
- IV: Static 16 bytes of zeros (protocol requirement)
- Use: File encryption on client, decryption on server

**CRC-32 (Linux cksum)**:
- Polynomial: 0x04C11DB7
- Table: 256 precomputed entries
- Compatibility: Exact match with Linux `cksum` command
- Use: File integrity verification

---

## Configuration & Deployment

### Configuration Files

**transfer.info** (Client):
```
localhost:1256
john_doe
/path/to/file.zip
```

**me.info** (Client Credentials):
```
john_doe
0a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
```

**port.info** (Server):
```
1256
```

### Deployment

**Client**:
1. Copy EncryptedBackupClient.exe
2. Create transfer.info with server details
3. Run executable

**Server**:
1. Install Python 3.11+
2. `pip install pycryptodome`
3. Run: `python server/server.py`
4. Optional GUI: `python server/ServerGUI.py`

---

## Security Properties

### Cryptographic Security

✅ **RSA-1024 OAEP-SHA256**: Secure key exchange
✅ **AES-256-CBC**: Strong file encryption
✅ **CRC-32**: File integrity (not cryptographic)
✅ **Zero-Knowledge**: Server never has plaintext
✅ **Session Isolation**: New AES key per connection

### Known Limitations

⚠️ **Static IV**: All files encrypted with same IV
⚠️ **No Message Auth**: No HMAC or signature verification
⚠️ **No Replay Protection**: Packets not sequence-numbered
⚠️ **Plaintext Headers**: Protocol codes visible on network
⚠️ **RSA-1024**: Below modern standards (recommend 2048-bit)

---

## Next Steps & Integration Guide

### For Flask API Integration:
See: `docs/COMPLETE_MULTI_LAYER_ARCHITECTURE.md` - **Section: Layer 1**

### For Web GUI Implementation:
See: `docs/COMPLETE_MULTI_LAYER_ARCHITECTURE.md` - **Section: Layer 2**

### For Flet GUI Integration:
See: `docs/COMPLETE_MULTI_LAYER_ARCHITECTURE.md` - **Section: Layer 3**

---

## Summary

**Current System** (OPERATIONAL):
- ✅ C++ Client with Windows GUI
- ✅ Python Server with Tkinter GUI
- ✅ SQLite3 Database
- ✅ RSA-1024 encryption
- ✅ AES-256-CBC encryption
- ✅ Custom binary protocol v3
- ✅ CRC-32 verification
- ✅ Multi-threaded handling
- ✅ Session management
- ✅ File persistence

**Proposed Enhancements** (PLANNING):
- ⏳ Flask API Server (HTTP/REST gateway)
- ⏳ Web-Based Client GUI (React/Vue)
- ⏳ Flet 0.28.3 Desktop GUI (replaces Tkinter)
- ⏳ WebSocket for real-time updates
- ⏳ JWT token authentication

**This Master Documentation** covers ALL components, current and proposed, with complete implementation details, code examples, and integration guides.

---

For detailed documentation, see:
- **Current Architecture**: `docs/COMPREHENSIVE_SYSTEM_DOCUMENTATION.md`
- **Multi-Layer Architecture**: `docs/COMPLETE_MULTI_LAYER_ARCHITECTURE.md`
- **Protocol Specification**: `docs/specification.md`
- **API Endpoints**: `docs/COMPLETE_MULTI_LAYER_ARCHITECTURE.md` (Layer 1)

