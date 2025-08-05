# CyberBackup Framework - AI Coding Agent Instructions

## Architecture Overview
This is a **4-layer encrypted backup system** with hybrid web-to-native architecture:

```
Web UI → Flask API Bridge → C++ Client (subprocess) → Python Server
  ↓           ↓                    ↓                     ↓
HTTP      RealBackupExecutor    --batch mode       Custom Binary
requests  process management   + transfer.info     TCP Protocol
```

**Critical Understanding**: Flask API Bridge (`cyberbackup_api_server.py` + `real_backup_executor.py`) is the coordination hub. Web UI communicates ONLY with Flask API, never directly with C++ client or Python server.

**Key Client Components**:
- **Web Client**: Single 8000+ line HTML file with modular JavaScript classes (ApiClient, FileManager, App, ThemeManager, ParticleSystem, etc.)
- **C++ Client**: Production-ready executable with RSA/AES encryption, CRC verification, and --batch mode for subprocess integration
- **Both clients** connect to the same Python server but through different pathways (web→Flask→C++→server vs direct C++→server)

## Essential Development Workflows

### Quick System Startup
```bash
# Single command to start entire system (RECOMMENDED)
python launch_gui.py
# Starts Flask API server + opens browser to http://localhost:9090/
# Automatically handles port checking and server readiness

python one_click_build_and_run.py  # Full build + deploy + launch
```

### Build System (CMake + vcpkg)
```bash
# CRITICAL: Must use vcpkg toolchain - builds fail without it
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg\scripts\buildsystems\vcpkg.cmake"
cmake --build build --config Release
# Output: build/Release/EncryptedBackupClient.exe
```

### Manual Service Management
```bash
# 1. Start Python backup server (must start FIRST)
python src/server/server.py    # Port 1256

# 2. Start Flask API bridge  
python cyberbackup_api_server.py    # Port 9090

# 3. Build C++ client (after any C++ changes)
cmake --build build --config Release
```

### Testing & Verification
```bash
# Integration tests (test complete web→API→C++→server chain)
python tests/test_gui_upload.py      # Full integration test via GUI API
python tests/test_upload.py          # Direct server test
python tests/test_client.py          # C++ client validation

# Verify real file transfers (CRITICAL verification pattern)
# Check: server/received_files/ OR received_files/ for actual transferred files
# Pattern: {username}_{timestamp}_{filename}
```

## Critical Integration Patterns

### Subprocess Management (ESSENTIAL PATTERN)
The system's core integration relies on subprocess execution:

```python
# RealBackupExecutor launches C++ client with --batch mode
self.backup_process = subprocess.Popen(
    [self.client_exe, "--batch"],  # --batch prevents hanging in subprocess
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=os.path.dirname(os.path.abspath(self.client_exe))  # CRITICAL: Working directory
)
```

**Why this matters**: C++ client expects `transfer.info` in working directory. Without `--batch` mode, client waits for user input and hangs the subprocess.

### Configuration Generation Pattern
```python
# transfer.info must be generated per operation (3-line format)
def _generate_transfer_info(self, server_ip, server_port, username, file_path):
    with open("transfer.info", 'w') as f:
        f.write(f"{server_ip}:{server_port}\n")  # Line 1: server endpoint
        f.write(f"{username}\n")                 # Line 2: username  
        f.write(f"{file_path}\n")                # Line 3: absolute file path
```

### Web Client Architecture Pattern (CRITICAL)
The HTML file contains a complete modular JavaScript application:

```javascript
// Class hierarchy for 8000+ line single-file SPA
class App {
    constructor() {
        this.apiClient = new ApiClient();           // Flask API communication
        this.system = new SystemManager();          // Core system management
        this.buttonStateManager = new ButtonStateManager();  // UI state
        this.particleSystem = new ParticleSystem(); // Visual effects
        this.errorBoundary = new ErrorBoundary(this); // Error handling
        // + 10 more manager classes
    }
}

// Key JavaScript Classes:
// - ApiClient: HTTP communication with Flask bridge
// - FileManager: File validation, preview, drag-drop
// - ThemeManager: Cyberpunk/Matrix/Dark theme switching
// - ParticleSystem: Performance-optimized visual effects
// - ErrorBoundary: Global error handling and recovery
// - ButtonStateManager: Loading/success/error button states
```

### File Verification Pattern (CRITICAL)
Always verify transfers through multiple layers:
```python
def _verify_file_transfer(self, original_file, username):
    # 1. Check server/received_files/ for actual file
    # 2. Compare file sizes
    # 3. Compare SHA256 hashes  
    # 4. Verify network activity on port 1256
    verification = {
        'transferred': file_exists_in_server_dir,
        'size_match': original_size == received_size,
        'hash_match': original_hash == received_hash,
        'network_activity': check_port_1256_connections()
    }
```

## Binary Protocol & Security

### Custom TCP Protocol (Port 1256)
- **Protocol Version**: 3 (both client and server)
- **Request Codes**: `REQ_REGISTER(1025)`, `REQ_SEND_PUBLIC_KEY(1026)`, `REQ_SEND_FILE(1028)`
- **Response Codes**: `RESP_REG_OK(1600)`, `RESP_PUBKEY_AES_SENT(1602)`, `RESP_FILE_CRC(1603)`
- **Header Format**: 23-byte requests, 7-byte responses (little-endian)
- **CRC Verification**: Linux `cksum` compatible CRC32 algorithm

### Security Implementation
- **RSA-1024**: Key exchange (Crypto++ with OAEP padding)  
- **AES-256-CBC**: File encryption (32-byte keys)
- **Fixed IV Issue**: ⚠️ Static zero IV allows pattern analysis (HIGH PRIORITY FIX)
- **CRC32 vs HMAC**: ⚠️ No tampering protection (MEDIUM PRIORITY FIX)

## Critical Dependencies & Requirements

### Build Dependencies
- **CMake**: 4.0.3+ (minimum 3.15 required)
- **vcpkg**: Package manager with boost-asio, boost-beast, cryptopp, zlib
- **MSVC**: Visual Studio 2022 Build Tools
- **Python**: 3.8+ with Flask, psutil, cryptography

### Port Usage
- **9090**: Flask API server (web GUI communication)
- **1256**: Python backup server (C++ client connections)

### Key File Locations
```
build/Release/EncryptedBackupClient.exe    # Main C++ executable
server/received_files/                     # Backup storage location  
transfer.info                              # Generated per operation
client_debug.log                           # C++ client activity log
server.log                                 # Python server activity log
```

## Common Issues & Critical Gotchas

### Build System Issues
- **vcpkg Toolchain**: Builds fail without `-DCMAKE_TOOLCHAIN_FILE="vcpkg\scripts\buildsystems\vcpkg.cmake"`
- **Windows Defines**: Must include `WIN32_LEAN_AND_MEAN`, `NOMINMAX` for Boost compatibility
- **Path Spaces**: Use existing `build/` directory; new directories may fail due to path issues

### Process Integration Failures
- **Missing --batch**: C++ client hangs waiting for user input in subprocess
- **Wrong Working Directory**: Client must run from directory containing `transfer.info`
- **Executable Path**: `RealBackupExecutor` searches multiple paths: `build/Release/`, `client/`, etc.

### Configuration Issues
- **transfer.info Format**: Must be exactly 3 lines: server:port, username, filepath
- **Port Conflicts**: Check port availability before starting (1256, 9090)
- **Absolute Paths**: Use absolute file paths to avoid working directory confusion

### Testing & Verification Failures
- **False Success**: Zero exit code doesn't guarantee successful transfer
- **Missing Files**: Always verify actual files appear in `server/received_files/`
- **Hash Verification**: Compare SHA256 hashes of original vs transferred files
- **Network Activity**: Verify TCP connections to port 1256 during transfers

### Unicode & Console Issues
- **Windows Console**: Some validation scripts fail with `UnicodeEncodeError`
- **Workaround**: Run individual tests instead of master test suite
- **Log Encoding**: Monitor logs through file reads, not console output

## Integration Testing Pattern (CRITICAL)
```python
# Always test the complete web→API→C++→server chain
def test_full_backup_chain():
    1. Start backup server (python server/server.py)
    2. Start API server (python cyberbackup_api_server.py)  
    3. Create test file with unique content
    4. Upload via /api/start_backup
    5. Monitor process execution and logs
    6. Verify file appears in server/received_files/
    7. Compare file hashes for integrity
    8. Check network activity and exit codes
```

**Essential Truth**: Component isolation testing misses critical integration issues. Real verification happens through actual file transfers and hash comparison, not just API responses or exit codes.

## Project-Specific Conventions

- **File Structure**: C++ client expects `transfer.info` in working directory, not executable directory
- **Batch Mode**: Always use `--batch` flag for C++ client in subprocess to prevent hanging
- **Port Usage**: Server (1256), API (9090) - check both for conflicts
- **File Verification**: Success = actual file appears in `received_files/` with correct content
- **Build Dependencies**: vcpkg toolchain required for C++ build, Flask + flask-cors for API
- **Process Management**: Use SynchronizedFileManager for `transfer.info` to prevent race conditions
- **API Communication**: REST endpoints for operations, WebSocket (`/ws`) for real-time progress updates
- **Error Propagation**: C++ client logs → subprocess stdout → RealBackupExecutor → Flask API → Web UI

## Quick Reference Commands
```bash
# Check system health
netstat -an | findstr ":9090\|:1256"    # Port availability
tasklist | findstr "python\|Encrypted"   # Process status

# Emergency cleanup
taskkill /f /im python.exe               # Kill Python processes
taskkill /f /im EncryptedBackupClient.exe # Kill C++ client

# Verify file transfers  
dir "server\received_files"              # Check received files
python -c "import hashlib; print(hashlib.sha256(open('file.txt','rb').read()).hexdigest())"

# Build troubleshooting
cmake --version                          # Check CMake version
vcpkg list                              # Check installed packages
```

When modifying this system, always test the complete integration chain. The unique hybrid architecture means changes in one layer can break communication patterns in unexpected ways.

````
