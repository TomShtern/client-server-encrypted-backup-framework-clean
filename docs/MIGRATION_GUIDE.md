# Migration Guide: Repository Reorganization

**Target Audience:** Developers working with the Client-Server Encrypted Backup Framework  
**Date:** 2025-08-09  
**Version:** 1.0

## Overview

This guide helps developers adapt to the new repository structure and canonical shared modules introduced in the reorganization.

## Quick Reference: New Structure

### Before → After
```
src/client/          → Client/cpp/
src/server/          → python_server/server/
src/shared/          → python_server/shared/
src/api/             → api-server/
include/             → Client/cpp/ and Client/deps/
cyberbackup_api_server.py → api-server/cyberbackup_api_server.py
```

## Import Changes Required

### Python Imports

#### Server Modules
```python
# OLD
from .database import DatabaseManager
from .file_transfer import FileTransferHandler

# NEW (no change needed - relative imports still work)
from .database import DatabaseManager
from .file_transfer import FileTransferHandler
```

#### Shared Modules
```python
# OLD
from src.shared.config_manager import ConfigManager

# NEW
from ..shared.config_manager import ConfigManager
```

#### New Canonical Modules
```python
# CRC Calculations
from ..shared.crc import calculate_crc32, CRC32Stream

# Filename Validation
from ..shared.filename_validator import validate_filename

# Configuration
from ..shared.config import get_config, get_server_config

# Header Canonicalization
from ..shared.canonicalize import canonicalize_headers_bhi
```

### C++ Includes

#### Client Headers
```cpp
// OLD
#include "include/client/client.h"
#include "include/wrappers/AESWrapper.h"

// NEW
#include "client.h"
#include "../deps/AESWrapper.h"
```

#### New Canonical Headers
```cpp
// CRC Calculations
#include "../deps/shared/crc.h"

// Configuration
#include "../deps/shared/config.h"
```

## API Changes

### CRC Calculation

#### Python
```python
# OLD (deprecated but still works)
crc = self._calculate_crc(data)
final_crc = self._finalize_crc(crc, len(data))

# NEW (recommended)
from ..shared.crc import calculate_crc32
crc = calculate_crc32(data)

# For streaming
from ..shared.crc import CRC32Stream
stream = CRC32Stream()
stream.update(chunk1)
stream.update(chunk2)
final_crc = stream.finalize()
```

#### C++
```cpp
// OLD (deprecated but still works)
uint32_t crc = calculateCRC(data, size);

// NEW (recommended)
#include "../deps/shared/crc.h"
using namespace client::shared;
uint32_t crc = calculate_crc32(data, size);

// For streaming
CRC32Stream stream;
stream.update(chunk1, size1);
stream.update(chunk2, size2);
uint32_t final_crc = stream.finalize();
```

### Filename Validation

#### Python
```python
# OLD (deprecated but still works)
if self._is_valid_filename_for_storage(filename):
    # process file

# NEW (recommended)
from ..shared.filename_validator import validate_filename
if validate_filename(filename):
    # process file

# With error handling
try:
    validate_filename(filename, strict=True)
    # process file
except FilenameValidationError as e:
    logger.error(f"Invalid filename: {e}")
```

### Configuration Management

#### Python
```python
# OLD
port = 1256  # hardcoded
database_path = "defensive.db"  # hardcoded

# NEW
from ..shared.config import get_server_config
config = get_server_config()
port = config.port
database_path = config.database_path
```

#### C++
```cpp
// OLD
const int DEFAULT_PORT = 1256;  // hardcoded

// NEW
#include "../deps/shared/config.h"
using namespace client::shared::config;
int port = get_config_int("server.port", DEFAULT_SERVER_PORT);
```

## Build System Updates

### CMakeLists.txt Changes
```cmake
# Update include directories
include_directories(
    Client/cpp
    Client/deps
    Client/deps/shared
)

# Update source file paths
set(CLIENT_SOURCES
    Client/cpp/main.cpp
    Client/cpp/client.cpp
    Client/cpp/WebServerBackend.cpp
    Client/deps/shared/crc.cpp
)
```

### Python Package Structure
```python
# Update setup.py or pyproject.toml
packages = [
    "python_server",
    "python_server.server",
    "python_server.server_gui", 
    "python_server.shared",
    "api_server"
]
```

## Testing Updates

### Python Tests
```python
# Update test imports
import sys
sys.path.append('python_server')

from python_server.shared.crc import calculate_crc32
from python_server.shared.filename_validator import validate_filename
```

### C++ Tests
```cpp
// Update test includes
#include "../Client/deps/shared/crc.h"
#include "../Client/cpp/client.h"
```

## Configuration File Updates

### New Configuration Format
```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 1256,
    "max_connections": 10,
    "database_path": "defensive.db"
  },
  "api_server": {
    "host": "127.0.0.1", 
    "port": 9090,
    "debug": false
  },
  "crypto": {
    "rsa_key_size": 2048,
    "aes_key_size": 256
  },
  "protocol": {
    "version": 3,
    "max_filename_length": 200
  }
}
```

## Deprecation Warnings

The following functions are deprecated but still work:

### Python
- `_calculate_crc()` → Use `calculate_crc32()`
- `_finalize_crc()` → Use `CRC32Stream.finalize()`
- `_is_valid_filename_for_storage()` → Use `validate_filename()`

### C++
- `calculateCRC()` → Use `calculate_crc32()`
- `calculateCRC32()` → Use `calculate_crc32()`

## Common Migration Issues

### Import Errors
**Problem:** `ModuleNotFoundError` or `ImportError`
**Solution:** Update import paths according to new structure

### CRC Mismatches
**Problem:** File transfer failures due to CRC differences
**Solution:** Ensure both client and server use canonical CRC implementation

### Configuration Not Found
**Problem:** Config files not loading
**Solution:** Update config file paths or use new configuration format

### Build Failures
**Problem:** Header files not found
**Solution:** Update include paths in build system

## Testing Your Migration

### 1. Python Tests
```bash
cd python_server
python -m pytest tests/
```

### 2. C++ Build
```bash
mkdir build && cd build
cmake ..
make
```

### 3. Integration Test
```bash
# Start server
python python_server/server/server.py

# Run client
./build/EncryptedBackupClient
```

### 4. CRC Compatibility Test
```python
# Test cross-language CRC compatibility
from python_server.shared.crc import calculate_crc32
test_data = b"Hello, World!"
python_crc = calculate_crc32(test_data)
print(f"Python CRC: {python_crc:08x}")

# Compare with C++ output
```

## Rollback Procedure

If issues arise:

1. **Revert file moves:**
   ```bash
   git mv Client/cpp/client.cpp src/client/client.cpp
   # ... repeat for other files
   ```

2. **Remove canonical modules:**
   ```bash
   rm -rf python_server/shared/crc.py
   rm -rf python_server/shared/filename_validator.py
   # ... etc
   ```

3. **Restore old imports:**
   - Revert import statements to original paths
   - Remove canonical module imports

## Support

For issues with migration:
1. Check this guide for common solutions
2. Review `REFORMAT_REPORT.md` for detailed changes
3. Check `refactor-report.json` for technical details
4. Test with the provided test vectors in `Shared/test_vectors/`

## Next Steps

After successful migration:
1. Update your development documentation
2. Train team members on new structure
3. Update CI/CD pipelines if needed
4. Consider removing deprecated functions after transition period
