# Project Architecture

This document outlines the architecture of the CyberBackup system. The system is composed of four main components that work together to provide a web-based interface for a powerful C++ command-line client.

### Component Overview

```
┌──────────────────┐      (HTTP)      ┌───────────────────────────┐      (Custom TCP)      ┌────────────────────────┐
│                  │                  │                           │                        │                        │
│  Web UI (Browser)├─────────────────►│  Client GUI Backend       ├───────────────────────►│  Python Backup Server  │
│ (NewGUIforClient.html) │                  │  (cyberbackup_api_server.py) │                        │  (server.py)           │
│                  │◄─────────────────┤                           │                        │                        │
└──────────────────┘      (API Status)   └─────────────┬─────────────┘                        └────────────────────────┘
                                                      │
                                                      │ (Process Execution)
                                                      ▼
                                        ┌───────────────────────────┐
                                        │                           │
                                        │ C++ Client                │
                                        │ (EncryptedBackupClient.exe) │
                                        │                           │
                                        └───────────────────────────┘
```

### 1. Web UI (HTML/CSS/JavaScript)

*   **File:** `src/client/NewGUIforClient.html`
*   **Role:** This is the user-facing interface that runs in a standard web browser. It provides the user with controls to connect to the server, select a file, and start the backup process.
*   **Interaction:** It does not interact with the C++ client or the Python backup server directly. Instead, it communicates exclusively with the "Client GUI Backend" via HTTP requests (REST API).

### 2. Client GUI Backend (Python Flask Server)

*   **File:** `cyberbackup_api_server.py`
*   **Role:** This component acts as a vital bridge between the web interface and the native C++ client.
*   **Responsibilities:**
    *   Serves the `NewGUIforClient.html` file to the user's browser.
    *   Provides a REST API (e.g., `/api/start_backup`, `/api/status`) that the Web UI can call.
    *   Receives commands from the Web UI and, in response, executes the C++ client (`EncryptedBackupClient.exe`) as a local command-line process.
    *   Monitors the status of the C++ client and provides real-time progress updates back to the Web UI.

### 3. C++ Client (Command-Line Application)

*   **File:** `client/src/client.cpp` (compiled to `EncryptedBackupClient.exe`)
*   **Role:** This is the core engine of the client-side operations. It is a pure command-line application with no graphical interface of its own.
*   **Responsibilities:**
    *   Handles the entire client-side backup protocol (registration, key exchange, file encryption, etc.).
    *   Encrypts files using AES-256.
    *   Communicates directly with the Python Backup Server over the custom TCP protocol.

### 4. Python Backup Server

*   **Files:** `server/server.py` and other files in the `server/` directory.
*   **Role:** This is the main backend server that receives and stores the encrypted files.
*   **Responsibilities:**
    *   Listens for incoming connections from the C++ client.
    *   Manages client registration and authentication.
    *   Handles the server-side of the custom TCP protocol.
    *   Receives encrypted file data and saves it to disk.
