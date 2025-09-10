# Project Structure Overview - CORRECTED ARCHITECTURE

## Root Directory Structure - CORRECTED
```
Client_Server_Encrypted_Backup_Framework/
├── src/                      # C++ Client Components
│   ├── client/              # C++ client application (encryption/transfer)
│   └── wrappers/            # Crypto wrappers for C++
├── server/                   # Python Flask API Server (middleware)
│   ├── main.py              # Flask API server entry point
│   ├── routes/              # API endpoints
│   └── models/              # Data models
├── gui/                      # JavaScript/HTML/TailwindCSS Web GUI
│   ├── static/              # CSS, JS, images
│   ├── templates/           # HTML templates
│   └── js/                  # JavaScript files
├── FletV2/                   # Python Flet Desktop GUI (server management)
│   ├── main.py              # Desktop GUI entry point
│   ├── views/               # GUI view components
│   │   ├── dashboard.py     # Server dashboard
│   │   ├── clients.py       # Connected clients view
│   │   ├── files.py         # File management view
│   │   ├── database.py      # Database management view
│   │   ├── analytics.py     # Analytics view
│   │   ├── logs.py          # Server logs view
│   │   └── settings.py      # Server settings view
│   └── utils/               # Utility modules
│       ├── server_bridge.py # Communication with Flask API
│       ├── state_manager.py # State management system
│       └── debug_setup.py   # Logging and debugging setup
├── Shared/                   # Cross-project shared utilities
│   └── utils/
│       └── utf8_solution.py # UTF-8 support for subprocess
├── include/                  # C++ header files
├── tests/                    # Test suite for all components
├── docs/                     # Documentation
├── theme/                    # Theme system for Flet GUI
├── requirements.txt          # Python dependencies
├── package.json              # JavaScript dependencies
├── build.bat                # Build script for C++ components
├── start_server.bat         # Start Flask API server
├── start_client.bat          # Start C++ client
├── transfer.info            # Client configuration
└── flet_venv/               # Python virtual environment
```

## Architecture Components - CORRECTED

### C++ Client Layer
- **Purpose**: File encryption, transfer operations
- **Technology**: C++ with Boost.Asio, Crypto++
- **Communication**: Binary protocol to Flask API server
- **Database**: SQLite3 for local client state

### Python Flask API Server Layer
- **Purpose**: Middleware between C++ client and web GUI
- **Technology**: Python Flask, RESTful API
- **Communication**: Receives binary protocol from C++, serves JSON to web GUI
- **Database**: SQLite3 for backup metadata and configuration

### JavaScript/HTML Web GUI Layer
- **Purpose**: User interface for backup operations
- **Technology**: JavaScript, HTML, TailwindCSS
- **Communication**: REST API calls to Flask server
- **Features**: Modern web interface, real-time updates

### Python Flet Desktop GUI Layer
- **Purpose**: Desktop management interface for server administration
- **Technology**: Python Flet with Material Design 3
- **Communication**: Direct integration with Python server components
- **Features**: Server monitoring, configuration, analytics

### Shared Components
- **UTF-8 Support**: Cross-platform text encoding
- **Database Layer**: SQLite3 wrapper for all components
- **Crypto Utilities**: Shared encryption functions
- **Logging**: Unified logging system

## Data Flow - CORRECTED
1. **User** → **Web GUI** (JavaScript/HTML)
2. **Web GUI** → **Flask API Server** (REST API)
3. **Flask API Server** → **C++ Client** (binary protocol)
4. **C++ Client** ↔ **File System** (encrypted backup operations)
5. **All Layers** ↔ **SQLite3 Database** (persistent storage)
6. **Flet Desktop GUI** ↔ **Flask API Server** (direct management)