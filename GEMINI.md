# GEMINI Code Context for Client-Server Encrypted Backup Framework

## 🎯 Project Overview

This project implements a **secure encrypted backup system** with a multi-component architecture designed for robustness, performance, and a modern user experience. It features a C++ client for native encryption, a Python server for backup storage, a Flask API server for web integration, and a Flet-based desktop GUI for comprehensive server management.

The system prioritizes data security through RSA and AES encryption, file integrity via CRC verification, and a unified approach to configuration and logging.

The current development focus is on the **FletV2 desktop GUI**, which is a new, clean implementation aiming for a modern user experience with Material Design 3, Neumorphism, and Glassmorphism.

## 🏗️ Architecture

The system is composed of several interconnected components:

1.  **C++ Client (`Client/`)**:
    *   **Purpose**: Handles native encryption (RSA-1024 + AES-256-CBC) and file transfer using a custom binary protocol with CRC verification.
    *   **Build System**: Uses CMake (`CMakeLists.txt`) and vcpkg for dependency management.
    *   **Interaction**: Executed by the Flask API server (`api_server/cyberbackup_api_server.py`) via `RealBackupExecutor` for actual backup operations.

2.  **Python Backup Server (`python_server/`)**:
    *   **Purpose**: The core backend server that listens for client connections, processes backup requests, performs encryption/decryption, stores files, and manages client/file metadata in an SQLite database.
    *   **Key Files**: `python_server/server/server.py` (main server logic), `python_server/server/database.py` (SQLite interactions).
    *   **Features**: Multi-threaded, integrated GUI (`GUIManager`), periodic maintenance (client session timeouts, partial file cleanup), and extensive logging.
    *   **Dependencies**: Managed via `python_server/requirements.txt` (and implicitly the root `requirements.txt`).

3.  **Flask API Server (`api_server/`)**:
    *   **Purpose**: Acts as an HTTP API bridge, coordinating between the web UI, the FletV2 GUI, and the native C++ client/Python backup server.
    *   **Key File**: `api_server/cyberbackup_api_server.py`.
    *   **Features**: RESTful API endpoints, WebSocket support (`flask-socketio`) for real-time updates, serves the web UI assets, robust error handling, performance monitoring, and Sentry integration.
    *   **Interaction**: Calls the C++ client via `RealBackupExecutor` and communicates with the Python backup server.

4.  **FletV2 Desktop GUI (`FletV2/`)**:
    *   **Purpose**: A cross-platform desktop application built with Flet for managing and monitoring the backup server. This is the primary focus of current development.
    *   **Key Files**: `FletV2/main.py` (application entry point), `FletV2/theme.py` (sophisticated theming), `FletV2/views/dashboard.py` (server overview), `FletV2/views/settings.py` (configuration management).
    *   **Design**: Adheres to Material Design 3 principles, incorporating Neumorphism and Glassmorphism for a modern aesthetic.
    *   **Communication**: Uses a `ServerBridge` (`FletV2/utils/server_bridge.py`) to interact with the Flask API server.

5.  **Web UI (`Client/Client-gui/`)**:
    *   **Purpose**: A browser-based interface for file selection and initiating backups, served by the Flask API server.

6.  **Shared Utilities (`Shared/`)**:
    *   **Purpose**: Contains common modules and utilities used across multiple components.
    *   **Key Files**:
        *   `Shared/config_manager.py`: Base class for robust configuration loading, merging, and validation.
        *   `Shared/utils/unified_config.py`: Extends `config_manager` to handle all configuration formats (JSON, legacy `.info` files, environment variables) and provides migration tools.
        *   `Shared/utils/utf8_solution.py`: Critical for ensuring consistent UTF-8 encoding across the entire project, especially for subprocess communication and console output. Integrates with `python-bidi`, `rich`, and `wcwidth`.
        *   Other utilities for logging, observability, performance monitoring, and Sentry integration.

## 🚀 Building and Running

The entire system can be built and run using a single orchestration script.

### Quick Start

To build and run the complete system, including the C++ client, Python server, Flask API, and Web UI, use the following command:

```bash
python scripts/one_click_build_and_run.py
```

This script will:
1.  Verify environment and dependencies.
2.  Build the C++ client (via CMake & vcpkg).
3.  Launch the Python backup server (with integrated GUI).
4.  Launch the Flask API server.
5.  Open the Web UI in a browser.

### FletV2 GUI Development

For developing the FletV2 GUI in isolation with hot-reloading:

```bash
cd FletV2
flet run main.py
```

## 💻 Core Technologies

*   **Languages**: Python 3.13+, C++20, JavaScript
*   **GUI Frameworks**: Flet 0.28.3 (for FletV2 desktop GUI), HTML/CSS/JavaScript (for Web UI)
*   **Backend Frameworks**: Flask (for API server)
*   **Build System**: CMake with vcpkg (for C++ client)
*   **Crypto Libraries**: Crypto++ (C++), PyCryptodome (Python)
*   **Database**: SQLite3
*   **Real-time Communication**: Flask-SocketIO
*   **System Monitoring**: `psutil`, `watchdog`
*   **Logging/Observability**: `sentry-sdk`, `loguru`, `rich`
*   **Text Handling**: `python-bidi`, `wcwidth` (for UTF-8 and bidirectional text)

## 📁 Key Directories

*   `Client/`: C++ client source code and build artifacts.
*   `api_server/`: Flask API server implementation.
*   `python_server/`: Python backup server implementation.
*   `FletV2/`: New Flet-based desktop GUI (current development focus).
*   `Shared/`: Shared utilities, configuration management, and common modules.
*   `scripts/`: Automation scripts, including `one_click_build_and_run.py`.
*   `config/`: Centralized JSON configuration files.
*   `data/`: Stores RSA keys, `transfer.info`, and other runtime data.
*   `received_files/`: Directory where backed-up files are stored.
*   `logs/`: Application log files.

## ⚙️ Development Conventions

*   **Unified Configuration**: All configuration is managed through `Shared/utils/unified_config.py`, which centralizes settings from JSON files, environment variables, and legacy `.info` files.
*   **UTF-8 Support**: The `Shared/utils/utf8_solution.py` module is critical for ensuring consistent UTF-8 encoding across all components, especially when dealing with subprocesses and diverse character sets. It should be imported early in any script that handles console I/O or subprocesses.
*   **FletV2 Design Principles**:
    *   **Framework Harmony**: Favor Flet's built-in features over custom solutions.
    *   **Modular Views**: Views are typically function-based, returning `ft.Control` objects.
    *   **Sophisticated Theming**: Utilizes `FletV2/theme.py` for Material Design 3, Neumorphism, and Glassmorphism.
    *   **ServerBridge**: Communication with the backend is abstracted through a `ServerBridge` interface.
*   **Logging & Observability**: The project uses enhanced dual logging (console + file), Sentry for error tracking, and performance monitoring across components.
*   **Dependency Management**: Python dependencies are primarily managed via the root `requirements.txt` and component-specific `requirements.txt` files. C++ dependencies are managed with vcpkg.