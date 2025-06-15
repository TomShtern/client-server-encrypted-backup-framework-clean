# Encrypted File Backup System

A secure client-server backup system with RSA-1024 + AES-256-CBC encryption.

## Overview

This project implements a robust encrypted backup system featuring:
- **Client**: C++ application with modern GUI interface
- **Server**: Python server for handling backup storage
- **Encryption**: RSA-1024 for key exchange, AES-256-CBC for file encryption
- **Protocol**: Custom binary protocol with CRC verification

## Quick Start

### Prerequisites
- Windows with MSVC Build Tools
- Python 3.x
- Boost.Asio library

### Building the Client
```batch
.\build.bat
```

### Running the System
1. Start the server:
   ```batch
   .\start_server.bat
   ```

2. Configure client settings in `transfer.info`:
   ```
   127.0.0.1:1256
   your_username
   path\to\file\to\backup.txt
   ```

3. Run the client:
   ```batch
   .\start_client.bat
   ```

## Project Structure

```
├── src/                # Source code
│   ├── client/         # Client application
│   └── wrappers/       # Crypto wrappers
├── include/            # Header files
├── server/             # Python server
├── gui/               # Web-based GUI
├── tests/             # Test suite
├── docs/              # Documentation
├── build/             # Build artifacts
├── client/            # Client executable output
├── third_party/       # External libraries
├── build.bat          # Main build script
├── clean.bat          # Cleanup script
└── transfer.info      # Client configuration
```

## Features

- **Modern GUI**: File-based web interface with real-time progress
- **Secure Protocol**: Binary protocol with proper error handling
- **File Integrity**: CRC32 verification for transferred files
- **Key Management**: Automatic RSA key generation and storage
- **Progress Tracking**: Real-time transfer statistics
- **Error Recovery**: Automatic retry mechanisms

## Configuration

Edit `transfer.info` to configure:
- Server address and port
- Username for authentication
- File path to backup

## Testing

Run the consolidated test suite:
```python
python tests\consolidated_tests.py
```

## Development

The project uses:
- **Build System**: Custom batch files with MSVC
- **Crypto**: Crypto++ library for encryption
- **Networking**: Boost.Asio for cross-platform networking
- **GUI**: Modern web-based interface

## License

See project documentation for license information.
