# Quick Reference Guide

> Essential commands, configuration, and troubleshooting

## Quick Start

### 1. Start Server
```bash
.\start_server.bat
# OR
cd server && python server.py
```

### 2. Configure Client
Create `transfer.info` in project root:
```
127.0.0.1:1256
myusername
C:\path\to\file.txt
```

### 3. Start Client
```bash
.\start_client.bat
```

## Build Commands

| Command | Description |
|---------|-------------|
| `.\build.bat` | Compile C++ client |
| `.\clean.bat` | Remove build artifacts |
| `.\start_server.bat` | Start Python server |
| `.\start_client.bat` | Start C++ client |

### Test Builds
```bash
.\scripts\build_rsa_final_test.bat          # RSA tests
.\scripts\build_rsa_wrapper_final_test.bat  # Wrapper tests
```

### Run Tests
```bash
.\build\test_rsa_final.exe           # RSA implementation
.\build\test_rsa_wrapper_final.exe   # Wrapper layer
python tests\test_connection.py      # Protocol tests
python server\test_server.py         # Server unit tests
```

## Configuration Files

### `transfer.info` (Client Config)
```
<server_ip>:<port>
<username>
<file_path>
```

**Example:**
```
192.168.1.100:1256
john_doe
C:\Documents\backup.zip
```

### `me.info` (Client Credentials)
Auto-generated after registration:
```
<username>
<uuid_hex>
<base64_private_key>
```

### `port.info` (Server Port)
Single line with port number:
```
1256
```

### `priv.key` (RSA Private Key)
Binary file (162 bytes DER format) - auto-generated

## Directory Structure Quick View

```
project/
+-- build.bat           # Build client
+-- start_server.bat    # Run server
+-- start_client.bat    # Run client
+-- transfer.info       # Client config (create this)
+-- port.info           # Port config
+-- src/client/         # C++ source
+-- server/             # Python server
+-- build/              # Compiled binaries
+-- docs/               # Documentation
```

## Server Defaults

| Setting | Value |
|---------|-------|
| Port | 1256 |
| Database | `defensive.db` |
| File Storage | `received_files/` |
| Log File | `server.log` |
| Socket Timeout | 60 seconds |
| Session Timeout | 10 minutes |
| Max Clients | 50 concurrent |

## Protocol Constants

| Constant | Value |
|----------|-------|
| Protocol Version | 3 |
| Client ID Size | 16 bytes |
| Max Filename | 255 bytes |
| RSA Key Size | 162 bytes (DER) |
| AES Key Size | 32 bytes |
| Max Retries | 3 |

## Request/Response Codes

### Requests (Client -> Server)
| Code | Name |
|------|------|
| 1025 | Register |
| 1026 | Send Public Key |
| 1027 | Reconnect |
| 1028 | Send File |
| 1029 | CRC OK |
| 1030 | CRC Retry |
| 1031 | CRC Abort |

### Responses (Server -> Client)
| Code | Name |
|------|------|
| 1600 | Register OK |
| 1601 | Register Fail |
| 1602 | Public Key + AES |
| 1603 | File + CRC |
| 1604 | ACK |
| 1605 | Reconnect + AES |
| 1606 | Reconnect Fail |
| 1607 | Error |

## Common Issues & Solutions

### Build Errors

**"MSVC not found"**
```bash
# Install Visual Studio 2022 Build Tools
# Or run from Developer Command Prompt
```

**"Crypto++ linking errors"**
```bash
# Rebuild from clean state
.\clean.bat
.\build.bat
```

### Runtime Errors

**"Connection refused"**
```bash
# Ensure server is running
.\start_server.bat
# Check port in port.info matches transfer.info
```

**"Registration failed"**
```bash
# Username may already exist
# Delete me.info and priv.key, try new username
del me.info priv.key
```

**"CRC mismatch"**
```bash
# Network issue or file corruption
# Client auto-retries 3 times
# Check server logs: server/server.log
```

**"RSA key generation failed"**
```bash
# Fallback XOR encryption will be used
# Check docs/RSA_FIX_IMPLEMENTATION_REPORT.md
```

### Server Issues

**"Database locked"**
```bash
# Another process may be using defensive.db
# Restart server
```

**"Port already in use"**
```bash
# Change port in port.info
# Or kill existing process
netstat -ano | findstr :1256
taskkill /PID <pid> /F
```

## Log Locations

| Component | Log File |
|-----------|----------|
| Server | `server/server.log` |
| Client | Console output |
| Build | `docs/build_client_output.txt` |

## Development Requirements

### Windows Client
- Visual Studio 2022 Build Tools
- MSVC 19.44+
- Windows SDK

### Python Server
- Python 3.11+
- PyCryptodome: `pip install pycryptodome`

## File Size Limits

| Limit | Value |
|-------|-------|
| Max Payload | 16 MB |
| Max File Size | 4 GB |
| Max Filename | 250 characters |

## Useful Debug Commands

```bash
# Check server status
python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1',1256)); print('OK')"

# View server database
sqlite3 server/defensive.db ".tables"
sqlite3 server/defensive.db "SELECT name FROM clients"

# Test RSA
.\build\test_rsa_final.exe

# Debug client
.\debug_client.bat
```

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| (none required) | System uses config files | - |

## Security Notes

- RSA-1024 keys generated per client
- AES-256-CBC for file encryption
- Keys stored locally in `me.info` and `priv.key`
- Server stores public keys in SQLite
- CRC-32 for integrity (not cryptographic)

## Performance Tips

1. **Large files**: Single packet design, keep under 16MB for optimal transfer
2. **Network**: Local transfers fastest, remote may timeout
3. **Concurrent clients**: Server handles up to 50 simultaneous connections
