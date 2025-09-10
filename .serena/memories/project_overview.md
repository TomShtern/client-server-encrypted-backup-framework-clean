# Client-Server Encrypted Backup Framework - CORRECTED ARCHITECTURE

## Project Purpose
This is a secure client-server backup system with a three-tier architecture:
- **C++ Client**: Handles file encryption and transfer operations
- **Python Flask API Server**: Acts as middleware between C++ client and web GUI
- **JavaScript/HTML/TailwindCSS Web GUI**: Modern web interface for user interaction
- **Python Flet Desktop GUI**: Desktop management interface for the Python server
- **SQLite3 Database**: Local storage for backup metadata and configuration

## Tech Stack - CORRECTED
- **C++ Client**: Boost.Asio networking, Crypto++ encryption
- **Python Flask API Server**: RESTful API connecting C++ client to web GUI
- **Web GUI**: JavaScript/HTML/TailwindCSS for modern web interface
- **Desktop GUI**: Flet (Python) with Material Design 3 for server management
- **Database**: SQLite3 for local storage
- **Encryption**: RSA-1024 + AES-256-CBC for secure file transfers
- **Protocol**: Custom binary protocol with CRC verification

## Key Components - CORRECTED
- `src/client/`: C++ client application (file encryption/transfer)
- `server/`: Python Flask API server (middleware)
- `gui/`: JavaScript/HTML/TailwindCSS web interface
- `FletV2/`: Python Flet desktop GUI (server management)
- `Shared/`: Cross-project utilities and UTF-8 support
- `utils/`: Server bridge and state management
- `views/`: Flet GUI view components
- `theme/`: Modern theme system for Flet GUI

## Architecture Flow
1. **C++ Client** ↔ **Python Flask API Server** (binary protocol)
2. **Python Flask API Server** ↔ **JavaScript/HTML Web GUI** (REST API)
3. **Python Server** ↔ **Flet Desktop GUI** (direct integration)
4. **All Components** ↔ **SQLite3 Database** (local storage)