# System Architecture

> Client-Server Encrypted Backup Framework - Technical Architecture Overview

## Technology Stack

```
+---------------------------+---------------------------+
|        CLIENT             |         SERVER            |
+---------------------------+---------------------------+
| Language: C++17           | Language: Python 3.11+    |
| Compiler: MSVC 19.44      | Framework: Threading      |
| Platform: Windows         | Platform: Cross-platform  |
+---------------------------+---------------------------+
| Networking: Boost.Asio    | Networking: socket        |
| Crypto: Crypto++ Library  | Crypto: PyCryptodome      |
| GUI: Win32 Console API    | GUI: Optional (Flet)      |
| Build: Batch Scripts      | Database: SQLite3         |
+---------------------------+---------------------------+
```

## Directory Structure

```
project-root/
|
+-- src/                          # Source implementations
|   +-- client/                   # C++ client (3,215 LOC)
|   |   +-- client.cpp            # Main logic, protocol handling
|   |   +-- protocol.cpp          # Binary packet construction
|   |   +-- ClientGUI.cpp         # Windows console interface
|   |   +-- cksum.cpp             # CRC-32 (Linux cksum compatible)
|   |
|   +-- wrappers/                 # Crypto abstractions (552 LOC)
|       +-- RSAWrapper.cpp        # RSA-1024 key exchange
|       +-- AESWrapper.cpp        # AES-256-CBC encryption
|       +-- Base64Wrapper.cpp     # Key encoding
|
+-- include/                      # Header files
|   +-- client/                   # Client headers
|   |   +-- client.h, protocol.h, cksum.h, ClientGUI.h
|   +-- wrappers/                 # Wrapper headers
|       +-- RSAWrapper.h, AESWrapper.h, Base64Wrapper.h
|
+-- server/                       # Python server (2,662 LOC)
|   +-- server.py                 # Multi-threaded TCP server
|   +-- ServerGUI.py              # Monitoring interface
|   +-- crypto_compat.py          # Encryption compatibility
|   +-- defensive.db              # SQLite client database
|
+-- third_party/                  # External dependencies
|   +-- crypto++/                 # Bundled Crypto++ library
|
+-- tests/                        # Test suite
|   +-- test_rsa_*.cpp            # RSA implementation tests
|   +-- test_connection.py        # Protocol tests
|
+-- scripts/                      # Build utilities
|   +-- build_*_test.bat          # Test compilation scripts
|
+-- docs/                         # Documentation
+-- build/                        # Generated artifacts
+-- client/                       # Client runtime files
```

## Component Architecture

```
+----------------+                              +----------------+
|    CLIENT      |                              |    SERVER      |
|   (C++17)      |                              |   (Python)     |
+----------------+                              +----------------+
|                |       TCP/IP Port 1256       |                |
| +------------+ |    Binary Protocol v3        | +------------+ |
| |  Client    | | <--------------------------> | |  Server    | |
| |  Core      | |      Little-Endian           | |  Core      | |
| +------------+ |                              | +------------+ |
|       |        |                              |       |        |
| +------------+ |                              | +------------+ |
| |  Protocol  | |                              | |  Protocol  | |
| |  Handler   | |                              | |  Handler   | |
| +------------+ |                              | +------------+ |
|       |        |                              |       |        |
| +------------+ |                              | +------------+ |
| |  Crypto    | |                              | |  Crypto    | |
| |  Wrappers  | |                              | |  Compat    | |
| +------------+ |                              | +------------+ |
|       |        |                              |       |        |
| +------------+ |                              | +------------+ |
| |  Crypto++  | |                              | |PyCryptodome| |
| +------------+ |                              | +------------+ |
|                |                              |       |        |
|                |                              | +------------+ |
|                |                              | |  SQLite    | |
|                |                              | |  Database  | |
|                |                              | +------------+ |
+----------------+                              +----------------+
```

## Client Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **Client Core** | `client.cpp` | Connection management, state machine, file operations |
| **Protocol Handler** | `protocol.cpp` | Packet creation/parsing, endianness conversion |
| **RSA Wrapper** | `RSAWrapper.cpp` | Key generation, RSA-OAEP encryption |
| **AES Wrapper** | `AESWrapper.cpp` | AES-256-CBC file encryption |
| **Base64 Wrapper** | `Base64Wrapper.cpp` | Key encoding for storage |
| **CRC Calculator** | `cksum.cpp` | Linux-compatible checksum |
| **GUI** | `ClientGUI.cpp` | Windows console interface |

## Server Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **Server Core** | `server.py` | TCP listener, thread pool, request routing |
| **Client Manager** | `server.py` | Client state, session management |
| **Database Layer** | `server.py` | SQLite client/file persistence |
| **Crypto Compat** | `crypto_compat.py` | RSA/AES operations |
| **GUI** | `ServerGUI.py` | Real-time monitoring |

## Security Architecture

```
                    ENCRYPTION LAYERS
+--------------------------------------------------------+
|                                                        |
|  +--------------------------------------------------+  |
|  |                TRANSPORT LAYER                   |  |
|  |                   (TCP/IP)                       |  |
|  +--------------------------------------------------+  |
|                          |                             |
|  +--------------------------------------------------+  |
|  |               KEY EXCHANGE LAYER                 |  |
|  |                                                  |  |
|  |   Client generates RSA-1024 keypair             |  |
|  |   Client sends public key to server             |  |
|  |   Server generates AES-256 session key          |  |
|  |   Server encrypts AES key with RSA-OAEP         |  |
|  |   Client decrypts AES key with private key      |  |
|  |                                                  |  |
|  +--------------------------------------------------+  |
|                          |                             |
|  +--------------------------------------------------+  |
|  |                DATA LAYER                        |  |
|  |                                                  |  |
|  |   Files encrypted with AES-256-CBC              |  |
|  |   CRC-32 integrity verification                 |  |
|  |                                                  |  |
|  +--------------------------------------------------+  |
|                                                        |
+--------------------------------------------------------+
```

## Database Schema

```sql
-- SQLite: defensive.db

CREATE TABLE clients (
    id          BLOB PRIMARY KEY,    -- 16-byte UUID
    name        TEXT NOT NULL,       -- Username (max 255)
    public_key  BLOB,                -- RSA public key (DER)
    aes_key     BLOB,                -- Current AES session key
    last_seen   TIMESTAMP            -- Last activity
);

CREATE TABLE files (
    id          INTEGER PRIMARY KEY,
    client_id   BLOB REFERENCES clients(id),
    filename    TEXT NOT NULL,
    filepath    TEXT NOT NULL,       -- Server storage path
    checksum    INTEGER,             -- CRC-32 value
    size        INTEGER,             -- Original file size
    verified    BOOLEAN DEFAULT 0,
    created_at  TIMESTAMP
);
```

## Key Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| Protocol Version | 3 | Binary, little-endian |
| Default Port | 1256 | Configurable via `port.info` |
| RSA Key Size | 1024-bit | 162 bytes DER format |
| AES Key Size | 256-bit | 32 bytes |
| AES Mode | CBC | Static IV (zero) |
| Max Filename | 255 bytes | Null-terminated |
| Client ID | 16 bytes | UUID format |
| Header Size | 23 bytes | Request header |

## Build System

```
BUILD PIPELINE (No CMake)
+--------+     +--------+     +--------+     +----------+
| Source | --> |  MSVC  | --> | Object | --> |   EXE    |
| Files  |     | 19.44  |     | Files  |     | (build/) |
+--------+     +--------+     +--------+     +----------+
                   |
                   v
           +-------------+
           | Crypto++    |
           | (selective) |
           +-------------+
                   |
                   v
           +-------------+
           | Win32 Libs  |
           | ws2_32.lib  |
           | advapi32    |
           | user32      |
           +-------------+
```

| Build Script | Purpose |
|--------------|---------|
| `build.bat` | Primary client compilation |
| `clean.bat` | Remove build artifacts |
| `start_server.bat` | Launch Python server |
| `start_client.bat` | Launch C++ client |

## Dependencies

### Client (C++)
- **Crypto++** - RSA, AES, Base64 (bundled in `third_party/`)
- **Boost.Asio** - Cross-platform networking (headers only)
- **Windows SDK** - Console APIs, Winsock2

### Server (Python)
- **PyCryptodome** - `Crypto.Cipher`, `Crypto.PublicKey`
- **Standard Library** - `socket`, `threading`, `sqlite3`
- **Optional** - Flet (GUI framework)

## Code Statistics

| Category | Files | Lines of Code |
|----------|-------|---------------|
| C++ Client | 8 | ~3,400 |
| Python Server | 6 | ~2,700 |
| Tests | 15 | ~1,500 |
| **Total** | **29** | **~7,600** |
