# Coding Patterns for Client-Server Encrypted Backup Framework

This document outlines the coding patterns, conventions, and architectural decisions used throughout this project. These patterns should be followed when extending or modifying the codebase to maintain consistency and quality.

---

## Table of Contents

1. [Project Architecture Patterns](#project-architecture-patterns)
2. [C++ Coding Patterns](#c-coding-patterns)
3. [Python Coding Patterns](#python-coding-patterns)
4. [Protocol and Network Patterns](#protocol-and-network-patterns)
5. [Cryptography Patterns](#cryptography-patterns)
6. [Error Handling Patterns](#error-handling-patterns)
7. [Build System Patterns](#build-system-patterns)
8. [Testing Patterns](#testing-patterns)
9. [Documentation Patterns](#documentation-patterns)
10. [GUI Patterns](#gui-patterns)

---

## Project Architecture Patterns

### 1. **Language Separation by Component**
- **Client**: C++17 for performance and Windows integration
- **Server**: Python 3.11+ for rapid development and cross-platform support
- **Rationale**: Each language chosen for its strengths in the specific domain

### 2. **Wrapper Pattern for Third-Party Libraries**
```cpp
// Pattern: Always wrap third-party crypto libraries
class RSAWrapper {
    // Internal Crypto++ objects hidden from users
private:
    CryptoPP::RSA::PrivateKey privateKey;
    std::vector<char> keyData;
public:
    // Simple public interface
    std::string encrypt(const std::string& plain);
    std::string decrypt(const std::string& cipher);
};
```
**Why**: Isolation from library changes, consistent API, easier testing

### 3. **Configuration File Hierarchy**
```
transfer.info    → Client runtime config (server, username, file)
me.info          → Client persistent state (UUID, keys)
port.info        → Server port configuration
priv.key         → Cached private key (binary DER)
```
**Pattern**: Simple text files with specific formats, one value per line

### 4. **Binary Protocol with Explicit Endianness**
```cpp
// ALWAYS use little-endian for network protocol
uint16_t code = ...;
headerBytes[17] = code & 0xFF;        // Low byte
headerBytes[18] = (code >> 8) & 0xFF; // High byte
```
**Critical**: Never rely on struct packing - manually construct protocol bytes

---

## C++ Coding Patterns

### 1. **Header Organization**
```cpp
#pragma once  // Always use pragma once, not include guards

// System headers first
#include <iostream>
#include <string>

// Third-party headers second
#include "../../third_party/crypto++/rsa.h"

// Project headers last
#include "../../include/wrappers/Base64Wrapper.h"
```

### 2. **Class Structure Pattern**
```cpp
class Client {
public:
    // Public interface methods first
    bool initialize();
    bool run();

private:
    // Configuration methods
    bool readTransferInfo();
    bool validateConfiguration();

    // Network operations
    bool connectToServer();
    bool sendRequest(uint16_t code, const std::vector<uint8_t>& payload);

    // Crypto operations
    bool generateRSAKeys();

    // Utility functions
    std::string bytesToHex(const uint8_t* data, size_t size);

    // Visual feedback
    void displayStatus(const std::string& operation, bool success);

    // Member variables at the end
    std::array<uint8_t, CLIENT_ID_SIZE> clientID;
    std::string username;
    RSAPrivateWrapper* rsaPrivate;
};
```
**Pattern**: Group methods by functionality, public before private

### 3. **Constants as constexpr**
```cpp
// Pattern: Use constexpr for compile-time constants
constexpr uint8_t CLIENT_VERSION = 3;
constexpr uint16_t REQ_REGISTER = 1025;
constexpr size_t CLIENT_ID_SIZE = 16;
constexpr size_t RSA_KEY_SIZE = 162;  // DER format for 1024-bit
```

### 4. **Packed Structures for Protocol**
```cpp
#pragma pack(push, 1)
struct RequestHeader {
    uint8_t client_id[16];
    uint8_t version;
    uint16_t code;
    uint32_t payload_size;
};
#pragma pack(pop)
```
**Critical**: Always use `#pragma pack(push, 1)` for protocol structures

### 5. **Manual Byte Packing (Preferred over structs)**
```cpp
// PREFERRED: Manual byte construction for protocol compliance
std::vector<uint8_t> headerBytes(23);
std::copy(clientID.begin(), clientID.end(), headerBytes.begin());
headerBytes[16] = CLIENT_VERSION;
headerBytes[17] = code & 0xFF;
headerBytes[18] = (code >> 8) & 0xFF;
headerBytes[19] = payload_size & 0xFF;
headerBytes[20] = (payload_size >> 8) & 0xFF;
headerBytes[21] = (payload_size >> 16) & 0xFF;
headerBytes[22] = (payload_size >> 24) & 0xFF;
```
**Why**: Guarantees exact byte layout regardless of compiler/platform

### 6. **Resource Management Pattern**
```cpp
// Pattern: RAII with explicit cleanup
class Client {
public:
    Client() : rsaPrivate(nullptr), connected(false) {
        std::fill(clientID.begin(), clientID.end(), 0);
    }

    ~Client() {
        closeConnection();
        if (rsaPrivate) {
            delete rsaPrivate;
            rsaPrivate = nullptr;
        }
    }

    // Delete copy operations for safety
    Client(const Client&) = delete;
    Client& operator=(const Client&) = delete;
};
```

### 7. **Error Reporting with Visual Feedback**
```cpp
void Client::displayStatus(const std::string& operation, bool success,
                          const std::string& details) {
#ifdef _WIN32
    SetConsoleTextAttribute(hConsole,
        success ? FOREGROUND_GREEN : FOREGROUND_RED | FOREGROUND_INTENSITY);
    std::cout << (success ? "[OK] " : "[FAIL] ");
    SetConsoleTextAttribute(hConsole, savedAttributes);
#endif
    std::cout << operation;
    if (!details.empty()) {
        std::cout << " - " << details;
    }
    std::cout << std::endl;
}
```
**Pattern**: Color-coded console output on Windows, plain text fallback

### 8. **Platform-Specific Code Isolation**
```cpp
#ifdef _WIN32
    #include <windows.h>
    // Windows-specific implementation
#else
    // Cross-platform fallback
#endif
```
**Pattern**: Always provide fallbacks for non-Windows platforms

### 9. **Debug Logging Pattern**
```cpp
// Pattern: Conditional debug output with context
displayStatus("Debug: Request header", true,
             "Version=" + std::to_string(CLIENT_VERSION) +
             ", Code=" + std::to_string(code) +
             ", PayloadSize=" + std::to_string(payload_size));
```

### 10. **String Field Padding (Protocol Compliance)**
```cpp
// Pattern: Fixed-size string fields with null termination and zero padding
std::vector<uint8_t> createPaddedString(const std::string& str, size_t targetSize) {
    std::vector<uint8_t> result(targetSize, 0);  // Zero-filled
    size_t copySize = std::min(str.size(), targetSize - 1);  // Room for null
    std::memcpy(result.data(), str.c_str(), copySize);
    return result;
}
```

---

## Python Coding Patterns

### 1. **Module Organization**
```python
# Standard library imports first
import socket
import threading
import struct
import logging

# Third-party imports second
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA

# Local imports last
from ServerGUI import ServerGUI
```

### 2. **Configuration Constants at Module Level**
```python
# Pattern: ALL_CAPS for configuration constants
SERVER_VERSION = 3
DEFAULT_PORT = 1256
DATABASE_NAME = "defensive.db"
CLIENT_SOCKET_TIMEOUT = 60.0
MAX_PAYLOAD_READ_LIMIT = (16 * 1024 * 1024) + 1024
```

### 3. **Custom Exception Hierarchy**
```python
class ServerError(Exception):
    """Base class for server-specific exceptions."""
    pass

class ProtocolError(ServerError):
    """Indicates an error in protocol adherence by the client."""
    pass

class ClientError(ServerError):
    """Indicates an error related to client state or validity."""
    pass
```
**Pattern**: Specific exceptions for different error categories

### 4. **Thread-Safe Client State Management**
```python
class Client:
    def __init__(self, client_id: bytes, name: str,
                 public_key_bytes: Optional[bytes] = None):
        self.id: bytes = client_id
        self.name: str = name
        self.lock: threading.Lock = threading.Lock()  # Per-client lock
        self.last_seen: float = time.monotonic()

    def update_last_seen(self):
        with self.lock:
            self.last_seen = time.monotonic()
```
**Pattern**: Per-object locks for fine-grained concurrency control

### 5. **Logging Pattern**
```python
# Pattern: Structured logging with context
logger.info(f"Client '{client_name}' successfully registered with ID: {client_id.hex()}")
logger.warning(f"Invalid request code {code} from client '{client_name}'")
logger.error(f"Database error: {e}", exc_info=True)
logger.critical(f"CRITICAL FAILURE: {message}")
```
**Convention**: Use appropriate log levels, include context in messages

### 6. **Database Interaction Pattern**
```python
def _db_execute(self, query: str, params: tuple = (),
                commit: bool = False, fetchone: bool = False,
                fetchall: bool = False) -> Any:
    """Centralized database access with error handling."""
    try:
        with sqlite3.connect(DATABASE_NAME, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()
            return cursor
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        if not commit and (fetchone or fetchall):
            raise ServerError(f"Critical database error: {e}") from e
        return None
```
**Pattern**: Single database access function with consistent error handling

### 7. **Binary Protocol Parsing**
```python
# Pattern: struct.unpack with explicit little-endian format
def _parse_request_header(self, header_data: bytes) -> Tuple[bytes, int, int, int]:
    client_id = header_data[:16]
    version = int(header_data[16])
    code = struct.unpack("<H", header_data[17:19])[0]  # Little-endian uint16
    payload_size = struct.unpack("<I", header_data[19:23])[0]  # Little-endian uint32
    return client_id, version, code, payload_size
```

### 8. **Type Hints Pattern**
```python
# Pattern: Comprehensive type hints for clarity
def _read_exact(self, sock: socket.socket, num_bytes: int) -> bytes:
    """Reads exactly num_bytes from socket."""
    pass

def _handle_registration(self, sock: socket.socket, payload: bytes) -> None:
    """Handles client registration."""
    pass

# Use typing module for complex types
from typing import Dict, Optional, Any, Tuple, List
```

### 9. **Server Main Loop Pattern**
```python
def start(self):
    self.running = True
    self.shutdown_event.clear()

    # Setup
    self._load_clients_from_db()
    self.server_socket.bind(('0.0.0.0', self.port))
    self.server_socket.listen(10)
    self.server_socket.settimeout(1.0)  # Allow periodic shutdown checks

    # Main accept loop
    try:
        while not self.shutdown_event.is_set():
            try:
                client_conn, client_addr = self.server_socket.accept()
                handler = threading.Thread(
                    target=self._handle_client_connection,
                    args=(client_conn, client_addr),
                    daemon=True
                )
                handler.start()
            except socket.timeout:
                continue  # Normal - check shutdown event
    finally:
        self.running = False
```
**Pattern**: Timeout-based accept loop for graceful shutdown

### 10. **CRC Calculation Pattern (POSIX cksum compatible)**
```python
# Pattern: Lookup table for performance
_CRC32_TABLE = (0x00000000, 0x04c11db7, ...)  # 256 entries

def _calculate_crc(self, data: bytes) -> int:
    crc = 0x00000000
    for byte in data:
        crc = (crc << 8) ^ self._CRC32_TABLE[(crc >> 24) ^ byte]
    # Append length
    length = len(data)
    while length > 0:
        crc = (crc << 8) ^ self._CRC32_TABLE[(crc >> 24) ^ (length & 0xFF)]
        length >>= 8
    return ~crc & 0xFFFFFFFF
```

---

## Protocol and Network Patterns

### 1. **Binary Protocol Structure**
```
Request:  [ClientID(16)] [Version(1)] [Code(2)] [PayloadSize(4)] [Payload(N)]
Response: [Version(1)] [Code(2)] [PayloadSize(4)] [Payload(N)]
```
**Pattern**: Fixed header + variable payload, all multi-byte values little-endian

### 2. **Request-Response Flow**
```cpp
// Pattern: Every request gets exactly one response
bool sendRequest(uint16_t code, const std::vector<uint8_t>& payload) {
    // Send request
    send_header_and_payload();
    return true;
}

bool receiveResponse(ResponseHeader& header, std::vector<uint8_t>& payload) {
    // Receive response
    read_header();
    validate_header();
    read_payload();
    return true;
}
```

### 3. **Socket Timeout Management**
```cpp
// Client pattern
socket->set_option(boost::asio::socket_base::keep_alive(true));

// Python server pattern
client_conn.settimeout(CLIENT_SOCKET_TIMEOUT)  # Per-operation timeout
```

### 4. **Exact Byte Reading Pattern**
```python
def _read_exact(self, sock: socket.socket, num_bytes: int) -> bytes:
    """Read exactly num_bytes, no more, no less."""
    data_chunks = []
    bytes_received = 0
    while bytes_received < num_bytes:
        chunk = sock.recv(min(num_bytes - bytes_received, 4096))
        if not chunk:
            raise ConnectionError("Socket closed")
        data_chunks.append(chunk)
        bytes_received += len(chunk)
    return b''.join(data_chunks)
```
**Critical**: Never assume recv() returns requested amount

### 5. **Protocol Version Checking**
```cpp
// Pattern: Check version first, reject mismatches immediately
if (header.version != SERVER_VERSION) {
    displayError("Invalid server version", ErrorType::PROTOCOL);
    return false;
}
```

### 6. **Payload Size Validation**
```python
# Pattern: Validate before allocation to prevent DoS
if num_bytes > MAX_PAYLOAD_READ_LIMIT:
    raise ProtocolError(f"Payload size {num_bytes} exceeds limit")
if num_bytes < 0:
    raise ValueError("Negative payload size")
```

---

## Cryptography Patterns

### 1. **RSA Key Management**
```cpp
// Pattern: Fallback strategy for robustness
RSAPrivateWrapper::RSAPrivateWrapper() {
    try {
        // Primary: Real Crypto++ RSA generation
        AutoSeededRandomPool rng;
        privateKey.GenerateRandomWithKeySize(rng, 1024);
    } catch (const Exception& e) {
        // Fallback: Use deterministic compatible key
        std::vector<uint8_t> knownGoodPublicKey = { /* ... */ };
        publicKeyData.assign(knownGoodPublicKey.begin(), knownGoodPublicKey.end());
    }
}
```
**Pattern**: Always have a fallback for crypto operations

### 2. **Key Storage Format**
```cpp
// Pattern: DER format for interoperability
std::string derPublicKey;
StringSink ss(derPublicKey);
publicKey.DEREncode(ss);

// For text storage: Base64 encode
std::string encoded = Base64Wrapper::encode(privateKey);
```

### 3. **AES Encryption Pattern**
```cpp
// Pattern: Static zero IV for protocol compliance (documented limitation)
AESWrapper::AESWrapper(const unsigned char* key, size_t keyLength,
                       bool useStaticZeroIV) {
    keyData.assign(key, key + keyLength);
    iv.resize(AES::BLOCKSIZE);
    if (useStaticZeroIV) {
        std::fill(iv.begin(), iv.end(), 0);  // Static IV
    } else {
        // Random IV for general use
        generate_random_iv();
    }
}
```

### 4. **Crypto++ Integration Pattern**
```cpp
// Pattern: Pipeline-style API usage
std::string result;
StringSource(plain, true,
    new PK_EncryptorFilter(rng, encryptor,
        new StringSink(result)
    )
);
return result;
```

### 5. **Key Size Constants**
```cpp
// Pattern: Explicit sizes as class constants
class RSAPublicWrapper {
public:
    static const unsigned int KEYSIZE = 162;  // DER format, 1024-bit
    static const unsigned int BITS = 1024;
};

class AESWrapper {
public:
    static const unsigned int DEFAULT_KEYLENGTH = 32;  // AES-256
};
```

---

## Error Handling Patterns

### 1. **Typed Error Categories**
```cpp
enum class ErrorType {
    NONE,
    NETWORK,
    FILE_IO,
    PROTOCOL,
    CRYPTO,
    CONFIG,
    AUTHENTICATION,
    SERVER_ERROR
};

void displayError(const std::string& message, ErrorType type = ErrorType::NONE);
```

### 2. **Try-Catch Hierarchy**
```cpp
// Pattern: Specific to general exception handling
try {
    // Operation
} catch (const CryptoPP::Exception& e) {
    // Crypto-specific handling
} catch (const std::runtime_error& e) {
    // Runtime errors
} catch (const std::exception& e) {
    // General exceptions
} catch (...) {
    // Unknown exceptions
}
```

### 3. **Python Exception Propagation**
```python
# Pattern: Convert library exceptions to custom types
try:
    cursor.execute(query, params)
except sqlite3.OperationalError as e:
    logger.error(f"Database locked: {e}")
    raise ServerError(f"Database error: {e}") from e
```

### 4. **Graceful Degradation Pattern**
```cpp
// Pattern: Optional GUI with fallback
try {
    ClientGUIHelpers::updateProgress(current, total, speed, eta);
} catch (...) {
    // GUI update failed - continue without GUI
}
```

### 5. **Validation Before Operation**
```cpp
// Pattern: Validate all inputs before processing
if (!key || keylen != EXPECTED_SIZE) {
    throw std::invalid_argument("Invalid key data");
}
if (filepath.empty()) {
    displayError("File path cannot be empty", ErrorType::CONFIG);
    return false;
}
```

---

## Build System Patterns

### 1. **Direct MSVC Compilation (No CMake)**
```batch
REM Pattern: Explicit compiler paths and settings
set "CL_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\..."
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT /c ^
    /I"include\client" /I"include\wrappers" /I"third_party\crypto++" ^
    /Fo:"build\client\\" src\client\*.cpp
```

### 2. **Selective Crypto++ Compilation**
```batch
REM Pattern: Only compile needed Crypto++ modules
"%CL_PATH%" /c /I"third_party\crypto++" /Fo:"build\third_party\crypto++\\" ^
    third_party\crypto++\base64.cpp ^
    third_party\crypto++\rsa.cpp ^
    third_party\crypto++\aes.cpp
REM Exclude problematic files:
REM third_party\crypto++\algebra_instantiations.cpp - template issues
```

### 3. **Linking Pattern**
```batch
REM Pattern: Link all objects with required Windows libraries
"%CL_PATH%" /Fe:"client\EncryptedBackupClient.exe" ^
    build\client\*.obj ^
    build\third_party\crypto++\*.obj ^
    ws2_32.lib advapi32.lib user32.lib /link /SUBSYSTEM:CONSOLE
```

### 4. **Clean Build Pattern**
```batch
REM Pattern: Remove all artifacts systematically
if exist "client\EncryptedBackupClient.exe" del /q "client\EncryptedBackupClient.exe"
if exist "build\client\*.obj" del /q "build\client\*.obj"
if exist "build\third_party\crypto++\*.obj" del /q "build\third_party\crypto++\*.obj"
```

### 5. **Dependency Management**
```batch
REM Pattern: Third-party libraries bundled in project
/I"third_party\crypto++"                    REM Crypto++
/I"C:\...\boost_1_88_0\boost_1_88_0"       REM Boost (external)
```

---

## Testing Patterns

### 1. **Test Organization**
```
tests/
├── test_rsa_final.cpp           → Integration test
├── test_rsa_wrapper_final.cpp   → Unit test
├── test_connection.py           → System test
└── benchmarks/
    └── client_benchmark.cpp     → Performance test
```

### 2. **C++ Test Structure**
```cpp
int main() {
    try {
        std::cout << "=== Test Suite Name ===" << std::endl;

        // Test 1
        std::cout << "1. Testing feature X..." << std::endl;
        perform_test();
        std::cout << "   ✓ Test passed!" << std::endl;

        // Test 2
        std::cout << "2. Testing feature Y..." << std::endl;
        perform_test();
        std::cout << "   ✓ Test passed!" << std::endl;

        std::cout << "\n=== ALL TESTS PASSED! ===" << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "ERROR: " << e.what() << std::endl;
        return 1;
    }
}
```

### 3. **Python Test Structure**
```python
class ConnectionTester:
    def __init__(self):
        self.test_results = []

    def log_test(self, test_name, status, details=""):
        result = {'test': test_name, 'status': status, 'details': details}
        self.test_results.append(result)
        print(f"{'✅' if status == 'PASS' else '❌'} {test_name}: {details}")

    def run_all_tests(self):
        tests = [
            ("Test 1", self.test_function_1),
            ("Test 2", self.test_function_2),
        ]
        for name, func in tests:
            func()
```

### 4. **Graceful Failure Testing**
```cpp
// Pattern: Test both success and expected failure cases
try {
    std::string encrypted = pubWrapper.encrypt(testData);
    std::string decrypted = rsa.decrypt(encrypted);

    if (testData == decrypted) {
        std::cout << "   ✓ Test PASSED!" << std::endl;
    } else {
        std::cout << "   ✗ Test FAILED!" << std::endl;
        return 1;
    }
} catch (const std::exception& e) {
    std::cout << "   Note: Expected failure for small key: " << e.what() << std::endl;
    // This is acceptable - continue
}
```

---

## Documentation Patterns

### 1. **File Header Comments**
```cpp
// Client.cpp
// Encrypted File Backup System - Enhanced Client Implementation
// Fully compliant with project specifications
```

### 2. **Function Documentation**
```python
def _read_exact(self, sock: socket.socket, num_bytes: int) -> bytes:
    """
    Reads exactly `num_bytes` from the socket.

    Args:
        sock: The socket to read from.
        num_bytes: The number of bytes to read.

    Returns:
        The bytes read from the socket.

    Raises:
        ValueError: If `num_bytes` is negative.
        ProtocolError: If `num_bytes` exceeds limit.
        TimeoutError: If socket timeout occurs.
        ConnectionError: If socket closes unexpectedly.
    """
```

### 3. **Inline Comments for Complex Logic**
```cpp
// CRITICAL FIX: Manually construct header bytes in little-endian format
// The Python server expects little-endian format explicitly
std::vector<uint8_t> headerBytes(23);
std::copy(clientID.begin(), clientID.end(), headerBytes.begin());
headerBytes[16] = CLIENT_VERSION;
headerBytes[17] = code & 0xFF;        // Low byte
headerBytes[18] = (code >> 8) & 0xFF; // High byte
```

### 4. **TODO/NOTE Patterns**
```cpp
// NOTE: GUI initialization optional - graceful failure
// TODO: Implement chunked file transfer for large files
// FIXME: Static IV is a security limitation - document in specs
```

### 5. **README Structure**
```markdown
# Project Name

## Overview
Brief description

## Build Commands
### Primary Build
### Clean Build
### Test Builds

## Running the System
### Start Server
### Start Client

## Architecture
### Client (C++17)
### Server (Python)

## Critical Implementation Notes
```

---

## GUI Patterns

### 1. **Optional GUI with Stubs**
```cpp
// Pattern: Stub implementations for platforms without GUI
namespace ClientGUIHelpers {
    bool initializeGUI() {
        #ifdef _WIN32
            return ClientGUI::getInstance()->initialize();
        #else
            return true;  // Stub for non-Windows
        #endif
    }
}
```

### 2. **Singleton Pattern for GUI**
```cpp
class ClientGUI {
private:
    ClientGUI();  // Private constructor
    ~ClientGUI();
    ClientGUI(const ClientGUI&) = delete;
    ClientGUI& operator=(const ClientGUI&) = delete;

public:
    static ClientGUI* getInstance() {
        if (!g_clientGUI) {
            g_clientGUI = new ClientGUI();
        }
        return g_clientGUI;
    }
};
```

### 3. **Thread-Safe GUI Updates**
```cpp
void ClientGUI::updateProgress(int current, int total) {
    EnterCriticalSection(&statusLock);
    currentStatus.progress = current;
    currentStatus.totalProgress = total;
    LeaveCriticalSection(&statusLock);

    if (statusWindow) {
        PostMessage(statusWindow, WM_STATUS_UPDATE, 0, 0);
    }
}
```

### 4. **Python GUI Queue Pattern**
```python
class ServerGUI:
    def __init__(self):
        self.update_queue = queue.Queue()
        self.gui_thread = threading.Thread(target=self._gui_main_loop, daemon=True)

    def update_server_status(self, running: bool):
        self.update_queue.put({'type': 'server_status', 'running': running})

    def _process_updates(self):
        while True:
            update = self.update_queue.get_nowait()
            self._apply_update(update)
```

### 5. **System Tray Integration**
```cpp
// Pattern: Hidden window for tray messages
hTrayWnd_ = CreateWindowExW(0, TRAY_WINDOW_CLASS, L"HiddenWindow", 0,
                           0, 0, 0, 0, HWND_MESSAGE, nullptr,
                           GetModuleHandle(nullptr), this);

trayIcon.uCallbackMessage = WM_TRAYICON;
Shell_NotifyIconW(NIM_ADD, &trayIcon);
```

---

## Additional Best Practices

### 1. **Consistent Naming Conventions**
- **C++**: `camelCase` for functions, `PascalCase` for classes, `SCREAMING_SNAKE_CASE` for constants
- **Python**: `snake_case` for functions, `PascalCase` for classes, `SCREAMING_SNAKE_CASE` for constants
- **Files**: `snake_case.ext` for source files, `PascalCase.ext` for classes

### 2. **Magic Number Avoidance**
```cpp
// BAD
if (keylen != 162) { ... }

// GOOD
constexpr size_t RSA_KEY_SIZE_1024_DER = 162;
if (keylen != RSA_KEY_SIZE_1024_DER) { ... }
```

### 3. **String Safety**
```cpp
// Pattern: Use safe string operations
wcsncpy_s(buffer, ARRAYSIZE(buffer), source, _TRUNCATE);

// Not: strcpy, strncpy (unsafe)
```

### 4. **Performance-Critical Paths**
```cpp
// Pattern: Optimize hot paths
constexpr size_t OPTIMAL_BUFFER_SIZE = 64 * 1024;
while (bytesRead < size) {
    size_t toRead = std::min(OPTIMAL_BUFFER_SIZE, size - bytesRead);
    // Read in optimized chunks
}
```

### 5. **Version Compatibility**
```cpp
// Pattern: Document version requirements
// Requires: Windows 10+, C++17, Crypto++ 8.7+
// Requires: Python 3.11+, PyCryptodome 3.18+
```

---

## Anti-Patterns to Avoid

### ❌ **Don't Use struct Packing for Network Protocol**
```cpp
// AVOID - unreliable across compilers/platforms
struct NetworkPacket {
    uint16_t code;
    uint32_t size;
} __attribute__((packed));
```
**Use manual byte packing instead**

### ❌ **Don't Assume recv() Reads All Requested Bytes**
```python
# AVOID
data = sock.recv(expected_size)  # May return less!
```
**Use _read_exact() pattern**

### ❌ **Don't Store Sensitive Data Without Clearing**
```cpp
// AVOID
std::string password = get_password();
use_password(password);
// password still in memory!
```
**Use secure deletion or containers that clear on destruction**

### ❌ **Don't Block GUI Thread**
```cpp
// AVOID
void OnButtonClick() {
    PerformLongOperation();  // Freezes GUI!
}
```
**Use worker threads with message posting**

### ❌ **Don't Swallow Exceptions Silently**
```python
# AVOID
try:
    critical_operation()
except:
    pass  # Silent failure!
```
**Always log or handle appropriately**

---

## Summary

This document captures the proven patterns used in this codebase. When making changes:

1. **Follow existing patterns** for consistency
2. **Document deviations** with clear rationale
3. **Update this document** when establishing new patterns
4. **Prioritize safety** over cleverness
5. **Test edge cases** especially in protocol handling
6. **Consider cross-platform** compatibility even if primarily Windows

These patterns have been refined through solving real implementation challenges and should guide future development.
