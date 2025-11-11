# Client-Server Encrypted Backup Framework - Complete Multi-Layer Architecture

**Current Status**: Core components operational, Flask/Web/Flet layers planned for integration
**Last Updated**: 2025-11-11
**Architecture Version**: 3.0 (Enhanced Multi-Layer)

---

## Table of Contents

1. [Executive Architecture Overview](#executive-architecture-overview)
2. [Current Implementation State](#current-implementation-state)
3. [Layer 1: C++ Client & Flask API Server](#layer-1-cpp-client--flask-api-server)
4. [Layer 2: Web-Based Client GUI](#layer-2-web-based-client-gui)
5. [Layer 3: Python Server with Flet GUI](#layer-3-python-server-with-flet-gui)
6. [Data Flow Architecture](#data-flow-architecture)
7. [Integration Points](#integration-points)
8. [Technology Stack](#technology-stack)
9. [Implementation Roadmap](#implementation-roadmap)

---

## Executive Architecture Overview

### Multi-Layer System Design

```
┌──────────────────────────────────────────────────────────────────┐
│           ENCRYPTED BACKUP FRAMEWORK - MULTI-LAYER SYSTEM        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ LAYER 1: CLIENT ACCESS                                      │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │                                                               │ │
│  │  ┌────────────────────┐    ┌────────────────────────────┐  │ │
│  │  │  C++ Client        │◄──►│  Flask API Server          │  │ │
│  │  │  (Windows Console) │    │  (HTTP/REST Endpoints)    │  │ │
│  │  │  - RSA encryption  │    │  - Request routing        │  │ │
│  │  │  - AES encryption  │    │  - Protocol translation   │  │ │
│  │  │  - File selection  │    │  - Session management     │  │ │
│  │  └────────────────────┘    └────────────────────────────┘  │ │
│  │                                     │                        │ │
│  │                                     ▼                        │ │
│  │                            ┌────────────────────┐           │ │
│  │                            │ Web-Based Client   │           │ │
│  │                            │ GUI                │           │ │
│  │                            │ (HTML/JS/React)    │           │ │
│  │                            │ - Status display   │           │ │
│  │                            │ - Progress tracking│           │ │
│  │                            │ - File management  │           │ │
│  │                            └────────────────────┘           │ │
│  │                                                               │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                           ▲                                       │
│                           │ (Custom Binary Protocol)              │
│                           │ or (HTTP/REST + WebSocket)           │
│                           ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ LAYER 2: SERVER BACKEND                                     │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │                                                               │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │  Python Server                                         │ │ │
│  │  │  ┌──────────────────┐  ┌──────────────────────────┐  │ │ │
│  │  │  │ Flask API Layer  │  │ Flet Desktop GUI 0.28.3 │  │ │ │
│  │  │  │ - REST endpoints │  │ - Real-time monitoring  │  │ │ │
│  │  │  │ - Protocol bridge│  │ - Server dashboard      │  │ │ │
│  │  │  │ - Request handler│  │ - Client statistics     │  │ │ │
│  │  │  └──────────────────┘  └──────────────────────────┘  │ │ │
│  │  │           │                       │                    │ │ │
│  │  │           └───────────┬───────────┘                    │ │ │
│  │  │                       ▼                                │ │ │
│  │  │  ┌────────────────────────────────────────────────┐   │ │ │
│  │  │  │ Core Server Logic                              │   │ │ │
│  │  │  │ - Client management                            │   │ │ │
│  │  │  │ - Key exchange (RSA-1024)                      │   │ │ │
│  │  │  │ - File transfer (AES-256-CBC)                 │   │ │ │
│  │  │  │ - CRC verification (Linux cksum)              │   │ │ │
│  │  │  │ - Multi-threaded request handling             │   │ │ │
│  │  │  └────────────────────────────────────────────────┘   │ │ │
│  │  │           │                                            │ │ │
│  │  │           ▼                                            │ │ │
│  │  │  ┌────────────────────────────────────────────────┐   │ │ │
│  │  │  │ SQLite3 Database (defensive.db)                │   │ │ │
│  │  │  │ - clients table (ID, Name, PublicKey, AESKey) │   │ │ │
│  │  │  │ - files table (ID, FileName, Verified)        │   │ │ │
│  │  │  └────────────────────────────────────────────────┘   │ │ │
│  │  │           │                                            │ │ │
│  │  │           ▼                                            │ │ │
│  │  │  ┌────────────────────────────────────────────────┐   │ │ │
│  │  │  │ File Storage (received_files/)                 │   │ │ │
│  │  │  │ - Encrypted files from clients                │   │ │ │
│  │  │  │ - Zero-knowledge encryption                   │   │ │ │
│  │  │  │ - Server has no plaintext access              │   │ │ │
│  │  │  └────────────────────────────────────────────────┘   │ │ │
│  │  │                                                        │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  │                                                               │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Current Implementation State

### Existing Components (100% Complete)

#### 1. C++ Client (`src/client/client.cpp` - 1,702 lines)
**Status**: ✅ Production Ready

**Architecture**:
- Windows console application
- Native Windows GUI integration (system tray, status window)
- RSA-1024 key pair generation and storage
- AES-256-CBC file encryption
- Custom binary protocol implementation
- Multi-threaded async operations

**Current Capabilities**:
- User registration with server
- RSA key exchange (OAEP-SHA256)
- File encryption and transfer
- CRC verification with automatic retry (3 attempts)
- Connection management with keep-alive
- GUI status updates with progress tracking

**Configuration Files**:
- `transfer.info` - Server address, username, file path
- `me.info` - Client credentials (username, client_id, private key)
- `port.info` - Server port override

**Protocol Used**: Custom Binary TCP Protocol v3
- 23-byte request headers (little-endian)
- 7-byte response headers
- Codes 1025-1031 (requests), 1600-1607 (responses)

#### 2. Python Server (`server/server.py` - 1,581 lines)
**Status**: ✅ Production Ready

**Architecture**:
- Multi-threaded TCP socket server
- Port: 1256 (configurable via port.info)
- SQLite3 database for persistence
- Session management with timeouts
- Graceful shutdown with signal handlers

**Core Features**:
- Client registration (generates UUID)
- RSA public key import and validation
- AES-256 session key generation and distribution
- Multi-packet file reassembly
- AES-256-CBC decryption (maintains zero-knowledge)
- CRC-32 verification using Linux cksum
- Automatic session cleanup (10-min timeout)

**Database Schema**:
```python
clients table:
  ID (BLOB[16]) - Primary Key, UUID
  Name (VARCHAR[255]) - Unique username
  PublicKey (BLOB[162]) - RSA public key (DER)
  LastSeen (TEXT) - ISO8601 timestamp
  AESKey (BLOB[32]) - Current session AES key

files table:
  ID (BLOB[16]) - Foreign Key to clients
  FileName (VARCHAR[255]) - Original filename
  PathName (VARCHAR[255]) - Full storage path
  Verified (BOOLEAN) - CRC verification status
  PRIMARY KEY (ID, FileName)
```

**Storage**:
- Location: `received_files/` directory
- Encryption: AES-256-CBC (zero-knowledge)
- Verification: Linux cksum CRC-32

#### 3. GUI Components (Current)

**A. Server GUI** (`server/ServerGUI.py` - 656 lines)
**Status**: ✅ Production Ready (Tkinter)

- Cross-platform monitoring dashboard
- Tkinter framework (not Flet)
- System tray integration via pystray
- Real-time status updates:
  - Server running status
  - Connected clients count
  - Active transfers
  - Bytes transferred
  - Maintenance statistics
- Thread-safe queue-based updates

**B. Client GUI** (`src/client/ClientGUI.cpp` - 658 lines)
**Status**: ✅ Production Ready (Windows Native)

- Windows API implementation
- System tray icon with context menu
- Status window with real-time updates
- Progress bar rendering
- Color-coded error display
- Notifications and popups
- Critical section synchronization for thread safety

#### 4. Cryptography Implementation
**Status**: ✅ Production Ready

**C++ Side** (Crypto++):
- RSA-1024 OAEP with SHA-256
- AES-256-CBC with PKCS7 padding
- CRC-32 (Linux cksum compatible)
- Base64 encoding for key storage
- Static zero IV for protocol compliance

**Python Side** (PyCryptodome):
- RSA-1024 OAEP with SHA-256
- AES-256-CBC with PKCS7 padding
- CRC-32 (Linux cksum compatible)
- Crypto compatibility layer with fallback support

---

## Layer 1: C++ Client & Flask API Server

### Current State
- C++ Client connects directly to Python Server via TCP binary protocol
- No intermediary layer

### Proposed Implementation

#### 1.1 Flask API Server Architecture

**Purpose**: Bridge between C++ client and web/API consumers

**File Structure** (to be created):
```
/api/
  ├── app.py                 # Flask application entry point
  ├── config.py              # Configuration (host, port, database)
  ├── requirements.txt       # Python dependencies
  ├── routes/
  │   ├── __init__.py
  │   ├── registration.py    # /api/register endpoints
  │   ├── authentication.py  # /api/auth endpoints
  │   ├── key_exchange.py    # /api/keys endpoints
  │   ├── file_transfer.py   # /api/files endpoints
  │   └── status.py          # /api/status endpoints
  ├── models/
  │   ├── __init__.py
  │   ├── client_model.py    # Client entity
  │   ├── file_model.py      # File entity
  │   └── session_model.py   # Session management
  ├── services/
  │   ├── __init__.py
  │   ├── client_service.py  # Client business logic
  │   ├── encryption_service.py
  │   ├── file_service.py
  │   └── server_proxy.py    # Proxy to main server
  └── utils/
      ├── __init__.py
      ├── auth.py            # Authentication/JWT
      ├── error_handler.py   # Error responses
      └── validators.py      # Input validation
```

#### 1.2 REST API Endpoints

**Core Endpoints**:

```
POST /api/v1/auth/register
  Request:
    {
      "username": "john_doe",
      "client_type": "cpp_client"  or "web_client"
    }
  Response:
    {
      "client_id": "0a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
      "status": "registered"
    }

POST /api/v1/auth/login
  Request:
    {
      "username": "john_doe"
    }
  Response:
    {
      "session_token": "jwt_token_here",
      "expires_in": 3600
    }

POST /api/v1/keys/public
  Request:
    {
      "client_id": "uuid",
      "public_key_der": "base64_encoded_162_bytes"
    }
  Response:
    {
      "aes_key_encrypted": "rsa_encrypted_aes_key_base64",
      "key_size": 128
    }

POST /api/v1/files/upload
  Request:
    {
      "client_id": "uuid",
      "filename": "backup.zip",
      "encrypted_data": "base64_encoded_encrypted_data",
      "original_size": 1048576,
      "packet_number": 1,
      "total_packets": 3
    }
  Response:
    {
      "packet_received": 1,
      "awaiting_packets": [2, 3]
    }

POST /api/v1/files/verify
  Request:
    {
      "client_id": "uuid",
      "filename": "backup.zip",
      "client_crc": "0x12345678"
    }
  Response:
    {
      "server_crc": "0x12345678",
      "verified": true,
      "status": "crc_match"
    }

GET /api/v1/status
  Response:
    {
      "server_running": true,
      "clients_connected": 5,
      "total_registered": 12,
      "database": "operational",
      "storage": "operational"
    }
```

#### 1.3 Flask Application Structure

**`app.py` (Main Entry Point)**:
```python
from flask import Flask, jsonify
from flask_cors import CORS
import logging
import signal

app = Flask(__name__)
CORS(app)

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server proxy for backend connection
from services.server_proxy import ServerProxy
server_proxy = ServerProxy(host='localhost', port=1256)

# Register blueprints
from routes import registration, authentication, key_exchange, file_transfer, status

app.register_blueprint(registration.bp, url_prefix='/api/v1')
app.register_blueprint(authentication.bp, url_prefix='/api/v1')
app.register_blueprint(key_exchange.bp, url_prefix='/api/v1')
app.register_blueprint(file_transfer.bp, url_prefix='/api/v1')
app.register_blueprint(status.bp, url_prefix='/api/v1')

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': str(error)}), 401

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal Server Error', 'message': 'An error occurred'}), 500

# Signal handlers for graceful shutdown
def signal_handler(sig, frame):
    logger.info("Shutting down Flask server...")
    server_proxy.disconnect()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    logger.info("Starting Flask API Server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
```

**`requirements.txt`**:
```
Flask==2.3.0
Flask-CORS==4.0.0
requests==2.31.0
pycryptodome==3.18.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

#### 1.4 Server Proxy Service

**`services/server_proxy.py`**:
```python
import socket
import struct
import threading

class ServerProxy:
    def __init__(self, host='localhost', port=1256):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.lock = threading.Lock()

    def connect(self):
        """Connect to the main TCP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False

    def disconnect(self):
        """Disconnect from the main TCP server"""
        if self.socket:
            self.socket.close()
            self.connected = False

    def send_request(self, code, payload):
        """Send raw protocol request to server"""
        with self.lock:
            if not self.connected:
                if not self.connect():
                    raise Exception("Cannot connect to server")

            # Build 23-byte header (little-endian)
            client_id = b'\x00' * 16
            version = 3

            # Encode payload as bytes
            if isinstance(payload, str):
                payload_bytes = payload.encode('utf-8')
            else:
                payload_bytes = payload

            payload_size = len(payload_bytes)

            # Create header
            header = bytearray(23)
            header[0:16] = client_id
            header[16] = version
            struct.pack_into('<H', header, 17, code)  # Little-endian uint16
            struct.pack_into('<I', header, 19, payload_size)  # Little-endian uint32

            # Send header + payload
            self.socket.send(bytes(header) + payload_bytes)

            # Receive response (7-byte header + payload)
            response_header = self.socket.recv(7)
            if len(response_header) < 7:
                raise Exception("Incomplete response header")

            # Parse response header
            resp_version = response_header[0]
            resp_code = struct.unpack('<H', response_header[1:3])[0]
            resp_payload_size = struct.unpack('<I', response_header[3:7])[0]

            # Receive response payload
            response_payload = b''
            while len(response_payload) < resp_payload_size:
                chunk = self.socket.recv(resp_payload_size - len(response_payload))
                if not chunk:
                    break
                response_payload += chunk

            return {
                'code': resp_code,
                'payload': response_payload,
                'payload_size': resp_payload_size
            }
```

#### 1.5 C++ Client Modifications

**Current**: Connects directly to server via custom binary protocol

**Modification Path 1 - Keep Binary Protocol**:
- C++ Client continues using custom binary protocol
- Flask API Server becomes a proxy:
  - Accepts HTTP requests from web/other clients
  - Translates HTTP to binary protocol
  - Forwards to main Python server
  - Translates responses back to JSON/HTTP

**Modification Path 2 - Switch to HTTP**:
- Modify C++ client to use HTTP instead of TCP sockets
- Use libcurl or similar
- Send requests as JSON payloads
- Receive responses as JSON

**Recommended**: Path 1 (backward compatible, minimal changes)

---

## Layer 2: Web-Based Client GUI

### Current State
- No web-based GUI exists

### Proposed Implementation

#### 2.1 Web GUI Architecture

**Technology Stack**:
- Frontend: React.js 18.x (or Vue 3.x / Angular 16.x)
- Styling: Tailwind CSS or Material-UI
- HTTP Client: Axios or Fetch API
- State Management: Redux or Zustand
- Build Tool: Webpack or Vite

**Directory Structure** (to be created):
```
/client-web-gui/
  ├── package.json
  ├── package-lock.json
  ├── webpack.config.js        (or vite.config.js)
  ├── tsconfig.json            (if using TypeScript)
  ├── .env.example
  ├── public/
  │   ├── index.html
  │   ├── favicon.ico
  │   └── manifest.json
  ├── src/
  │   ├── index.jsx
  │   ├── App.jsx
  │   ├── App.css
  │   ├── components/
  │   │   ├── Dashboard.jsx         # Main dashboard
  │   │   ├── FileUploader.jsx      # File selection/upload
  │   │   ├── ProgressBar.jsx       # Transfer progress
  │   │   ├── StatusIndicator.jsx   # Connection status
  │   │   ├── ClientList.jsx        # Registered clients
  │   │   └── Settings.jsx          # Client configuration
  │   ├── pages/
  │   │   ├── LoginPage.jsx
  │   │   ├── DashboardPage.jsx
  │   │   ├── TransferPage.jsx
  │   │   └── SettingsPage.jsx
  │   ├── services/
  │   │   ├── api.js               # API client service
  │   │   ├── auth.js              # Authentication service
  │   │   └── storage.js           # Local storage service
  │   ├── hooks/
  │   │   ├── useAuth.js
  │   │   ├── useApi.js
  │   │   └── useFileUpload.js
  │   ├── context/
  │   │   ├── AuthContext.jsx
  │   │   └── AppContext.jsx
  │   ├── utils/
  │   │   ├── constants.js
  │   │   ├── formatters.js
  │   │   └── validators.js
  │   └── styles/
  │       ├── global.css
  │       ├── components.css
  │       └── theme.css
  └── build/                   (generated by build process)
```

#### 2.2 Frontend Components

**`src/components/Dashboard.jsx`**:
```jsx
import React, { useState, useEffect } from 'react';
import FileUploader from './FileUploader';
import ProgressBar from './ProgressBar';
import StatusIndicator from './StatusIndicator';
import { useApi } from '../hooks/useApi';

export default function Dashboard() {
  const [files, setFiles] = useState([]);
  const [transferring, setTransferring] = useState(false);
  const [progress, setProgress] = useState(0);
  const [serverStatus, setServerStatus] = useState('disconnected');

  const { uploadFile, getStatus } = useApi();

  useEffect(() => {
    // Poll server status every 5 seconds
    const interval = setInterval(async () => {
      const status = await getStatus();
      setServerStatus(status.connected ? 'connected' : 'disconnected');
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleFileSelect = async (file) => {
    setTransferring(true);
    setProgress(0);

    try {
      // Upload file with progress tracking
      const result = await uploadFile(file, (progress) => {
        setProgress(Math.round(progress));
      });

      if (result.success) {
        alert(`File uploaded successfully! CRC: ${result.crc}`);
      } else {
        alert(`Upload failed: ${result.error}`);
      }
    } finally {
      setTransferring(false);
      setProgress(0);
    }
  };

  return (
    <div className="dashboard">
      <h1>Encrypted Backup Client</h1>

      <StatusIndicator status={serverStatus} />

      <div className="content">
        <FileUploader
          onFileSelect={handleFileSelect}
          disabled={transferring || serverStatus === 'disconnected'}
        />

        {transferring && (
          <ProgressBar
            current={progress}
            total={100}
            label={`${progress}% - Uploading...`}
          />
        )}

        <div className="file-list">
          <h3>Upload History</h3>
          {files.map(file => (
            <div key={file.id} className="file-item">
              <span>{file.name}</span>
              <span className={`status ${file.status}`}>{file.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

**`src/services/api.js`**:
```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add JWT token to requests
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('session_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const apiService = {
  // Authentication
  register: (username) => apiClient.post('/auth/register', { username }),
  login: (username) => apiClient.post('/auth/login', { username }),

  // Key Exchange
  sendPublicKey: (clientId, publicKey) =>
    apiClient.post('/keys/public', { client_id: clientId, public_key_der: publicKey }),

  // File Transfer
  uploadFile: (filename, encryptedData, originalSize, packetNumber, totalPackets) =>
    apiClient.post('/files/upload', {
      filename,
      encrypted_data: encryptedData,
      original_size: originalSize,
      packet_number: packetNumber,
      total_packets: totalPackets
    }),

  verifyFile: (filename, clientCrc) =>
    apiClient.post('/files/verify', { filename, client_crc: clientCrc }),

  // Status
  getStatus: () => apiClient.get('/status')
};
```

**`src/hooks/useApi.js`**:
```javascript
import { useCallback, useState } from 'react';
import { apiService } from '../services/api';

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const uploadFile = useCallback(async (file, onProgress) => {
    setLoading(true);
    setError(null);

    try {
      // Read file
      const arrayBuffer = await file.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);

      // Encrypt file (client-side encryption)
      const encryptedData = await encryptAES(uint8Array);

      // Upload with progress tracking
      const uploadSize = encryptedData.length;
      const result = await apiService.uploadFile(
        file.name,
        btoa(String.fromCharCode(...encryptedData)), // Base64 encode
        file.size,
        1,
        1
      );

      // Verify CRC
      const crc = calculateCRC32(arrayBuffer);
      const verifyResult = await apiService.verifyFile(file.name, crc);

      onProgress?.(100);
      return { success: true, crc: verifyResult.server_crc };
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  }, []);

  return { uploadFile, loading, error };
}
```

#### 2.3 Client-Side Encryption

**Important**: File encryption happens in the browser before sending to API

```javascript
// src/utils/encryption.js

// AES-256-CBC encryption
export async function encryptAES(plaintext, key) {
  const keyBuffer = await crypto.subtle.importKey(
    'raw', key, { name: 'AES-CBC' }, false, ['encrypt']
  );

  const iv = new Uint8Array(16).fill(0); // Protocol requirement: zero IV
  const encrypted = await crypto.subtle.encrypt(
    { name: 'AES-CBC', iv: iv }, keyBuffer, plaintext
  );

  return new Uint8Array(encrypted);
}

// CRC-32 calculation (Linux cksum compatible)
export function calculateCRC32(data) {
  const table = [...]; // 256-entry CRC table

  let crc = 0;

  // Process data
  for (let i = 0; i < data.length; i++) {
    crc = (crc << 8) ^ table[(crc >> 24) ^ data[i]];
  }

  // Process length
  let length = data.length;
  while (length > 0) {
    crc = (crc << 8) ^ table[(crc >> 24) ^ (length & 0xFF)];
    length >>= 8;
  }

  return ~crc >>> 0; // One's complement
}
```

#### 2.4 Deployment

**Production Build**:
```bash
npm run build
# Creates /build directory with optimized assets
```

**Serve with Flask**:
```python
# In Flask app.py
from flask import send_from_directory

@app.route('/')
@app.route('/<path:path>')
def serve_static(path='index.html'):
    if path and os.path.exists(f'client-web-gui/build/{path}'):
        return send_from_directory('client-web-gui/build', path)
    return send_from_directory('client-web-gui/build', 'index.html')
```

---

## Layer 3: Python Server with Flet GUI

### Current State
- Server using Tkinter GUI

### Proposed Implementation

#### 3.1 Flet 0.28.3 Desktop GUI

**Installation**:
```bash
pip install flet==0.28.3
```

**File Structure** (to be created):
```
/server_gui_flet/
  ├── main.py              # Flet application entry point
  ├── config.py            # GUI configuration
  ├── pages/
  │   ├── __init__.py
  │   ├── dashboard.py     # Main dashboard page
  │   ├── clients.py       # Clients management page
  │   ├── transfers.py     # File transfers page
  │   ├── settings.py      # Settings page
  │   └── status.py        # Server status page
  ├── components/
  │   ├── __init__.py
  │   ├── status_card.py
  │   ├── client_list.py
  │   ├── transfer_progress.py
  │   └── charts.py
  ├── services/
  │   ├── __init__.py
  │   ├── server_monitor.py
  │   └── database.py
  └── utils/
      ├── __init__.py
      ├── formatters.py
      └── constants.py
```

#### 3.2 Flet Application

**`server_gui_flet/main.py`**:
```python
import flet as ft
from datetime import datetime
import threading
from pages import dashboard, clients, transfers, settings

class ServerGUIApp:
    def __init__(self, server_instance):
        self.server = server_instance
        self.page = None
        self.running = True

    def build(self, page: ft.Page):
        self.page = page
        page.title = "Encrypted Backup Server - Flet 0.28.3"
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True
        page.theme_mode = ft.ThemeMode.DARK

        # Navigation
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD,
                    label="Dashboard"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PEOPLE,
                    label="Clients"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.UPLOAD_FILE,
                    label="Transfers"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS,
                    label="Settings"
                ),
            ],
            on_change=self.on_nav_change
        )

        # Main content area
        self.content = ft.Column(expand=True)
        self.show_dashboard()

        # Layout
        page.add(
            ft.Row([
                self.nav_rail,
                ft.VerticalDivider(width=1),
                ft.Column([self.content], expand=True)
            ], expand=True)
        )

        # Start monitoring thread
        self.start_monitoring()

    def show_dashboard(self):
        self.content.clean()
        dashboard_page = dashboard.DashboardPage(self.server, self.page)
        self.content.controls.append(dashboard_page.build())
        self.page.update()

    def show_clients(self):
        self.content.clean()
        clients_page = clients.ClientsPage(self.server, self.page)
        self.content.controls.append(clients_page.build())
        self.page.update()

    def show_transfers(self):
        self.content.clean()
        transfers_page = transfers.TransfersPage(self.server, self.page)
        self.content.controls.append(transfers_page.build())
        self.page.update()

    def show_settings(self):
        self.content.clean()
        settings_page = settings.SettingsPage(self.server, self.page)
        self.content.controls.append(settings_page.build())
        self.page.update()

    def on_nav_change(self, e):
        selected = self.nav_rail.selected_index
        if selected == 0:
            self.show_dashboard()
        elif selected == 1:
            self.show_clients()
        elif selected == 2:
            self.show_transfers()
        elif selected == 3:
            self.show_settings()

    def start_monitoring(self):
        def monitor():
            while self.running:
                # Update UI with server stats
                stats = self.server.get_statistics()
                # Push updates to Flet UI
                threading.Event().wait(1)  # Update every 1 second

        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

def main():
    # Import server instance
    from server import EncryptedBackupServer

    server = EncryptedBackupServer()
    app = ServerGUIApp(server)

    # Start server in background
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()

    # Start Flet GUI
    ft.app(target=app.build)

if __name__ == '__main__':
    main()
```

**`server_gui_flet/pages/dashboard.py`**:
```python
import flet as ft
from datetime import datetime

class DashboardPage:
    def __init__(self, server, page):
        self.server = server
        self.page = page

    def build(self) -> ft.Control:
        # Server status card
        status_card = self.build_status_card()

        # Statistics cards
        stats_row = self.build_stats_row()

        # Recent activity
        activity = self.build_activity_feed()

        return ft.Column([
            ft.Text("Server Dashboard", size=24, weight="bold"),
            ft.Divider(),
            status_card,
            ft.Divider(),
            ft.Text("Statistics", size=18, weight="bold"),
            stats_row,
            ft.Divider(),
            ft.Text("Recent Activity", size=18, weight="bold"),
            activity,
        ], expand=True, scroll=ft.ScrollMode.AUTO)

    def build_status_card(self) -> ft.Control:
        stats = self.server.get_statistics()

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=30, color="green"),
                        ft.Column([
                            ft.Text("Server Status", size=12, color="gray"),
                            ft.Text("Online", size=18, weight="bold", color="green")
                        ])
                    ]),
                    ft.Divider(),
                    ft.Row([
                        ft.Column([
                            ft.Text("Address", size=12, color="gray"),
                            ft.Text("0.0.0.0:1256", size=14)
                        ], expand=True),
                        ft.Column([
                            ft.Text("Uptime", size=12, color="gray"),
                            ft.Text(f"{stats.get('uptime', 'N/A')}", size=14)
                        ], expand=True),
                        ft.Column([
                            ft.Text("Database", size=12, color="gray"),
                            ft.Text("Connected", size=14, color="green")
                        ], expand=True),
                    ])
                ], spacing=10),
                padding=20
            )
        )

    def build_stats_row(self) -> ft.Control:
        stats = self.server.get_statistics()

        return ft.Row([
            self.stat_card("Connected Clients", stats.get('connected_clients', 0), "blue"),
            self.stat_card("Total Registered", stats.get('total_clients', 0), "purple"),
            self.stat_card("Active Transfers", stats.get('active_transfers', 0), "orange"),
            self.stat_card("Bytes Transferred", self.format_bytes(stats.get('bytes_transferred', 0)), "green"),
        ], expand=True)

    def stat_card(self, title: str, value, color: str) -> ft.Control:
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(title, size=12, color="gray"),
                    ft.Text(str(value), size=24, weight="bold", color=color)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                alignment=ft.alignment.center,
                expand=True
            ),
            expand=True
        )

    def build_activity_feed(self) -> ft.Control:
        activities = self.server.get_recent_activities(limit=10)

        activity_items = []
        for activity in activities:
            activity_items.append(
                ft.Row([
                    ft.Icon(self.get_activity_icon(activity['type']), size=20),
                    ft.Column([
                        ft.Text(activity['description'], weight="bold"),
                        ft.Text(activity['timestamp'], size=10, color="gray")
                    ], expand=True),
                    ft.Text(activity['status'], size=12, color="green")
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
            )

        return ft.Column(activity_items, expand=True, scroll=ft.ScrollMode.AUTO)

    @staticmethod
    def get_activity_icon(activity_type: str):
        icons = {
            'registration': ft.Icons.PERSON_ADD,
            'upload': ft.Icons.UPLOAD_FILE,
            'verification': ft.Icons.CHECK_CIRCLE,
            'error': ft.Icons.ERROR,
        }
        return icons.get(activity_type, ft.Icons.INFO)

    @staticmethod
    def format_bytes(bytes_val: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} TB"
```

#### 3.3 Integration with Python Server

**Modify `server/server.py`**:
```python
import threading
import sys

class EncryptedBackupServer:
    def __init__(self, use_flet_gui=False):
        # ... existing initialization ...
        self.use_flet_gui = use_flet_gui
        self.gui_app = None

    def start(self):
        """Start the server with optional GUI"""
        if self.use_flet_gui:
            # Import Flet GUI
            from server_gui_flet import ServerGUIApp
            self.gui_app = ServerGUIApp(self)

            # Start server in background thread
            server_thread = threading.Thread(target=self._run_server, daemon=True)
            server_thread.start()

            # Start Flet GUI in main thread
            self.gui_app.run()
        else:
            # Run server without GUI
            self._run_server()

    def _run_server(self):
        """Internal server loop"""
        # ... existing server implementation ...
        pass

if __name__ == '__main__':
    use_gui = '--gui' in sys.argv
    server = EncryptedBackupServer(use_flet_gui=use_gui)
    server.start()
```

---

## Data Flow Architecture

### Complete Multi-Layer Data Flow

```
┌─ CLIENT INITIATES BACKUP ──────────────────────────────────────┐
│                                                                  │
│  WEB GUI (Browser)              C++ CLIENT                      │
│  ├─ User selects file       ┌─> Reads transfer.info            │
│  ├─ Clicks "Upload"         │   Loads RSA key pair             │
│  └─ Sends to Flask API      │   Prepares file                  │
│       │                      │                                  │
│       ▼                      ▼                                  │
│  ┌─ FLASK API SERVER ────────────────────────────────────────┐ │
│  │ POST /api/v1/auth/register                                 │ │
│  │ ├─ Extract username                                        │ │
│  │ ├─ Forward to main server via ServerProxy                 │ │
│  │ ├─ Receive client_id                                      │ │
│  │ └─ Return JSON response                                   │ │
│  │       │                                                    │ │
│  │       ▼                                                    │ │
│  │ POST /api/v1/keys/public                                  │ │
│  │ ├─ Extract RSA public key                                │ │
│  │ ├─ Forward to server via ServerProxy                     │ │
│  │ ├─ Receive encrypted AES key                            │ │
│  │ └─ Return encrypted_aes in JSON                          │ │
│  │       │                                                    │ │
│  │       ▼                                                    │ │
│  │ POST /api/v1/files/upload                                │ │
│  │ ├─ Extract encrypted file data                           │ │
│  │ ├─ Extract packet metadata                               │ │
│  │ ├─ Forward via ServerProxy (translate to binary)         │ │
│  │ ├─ Receive acknowledgment                                │ │
│  │ └─ Return status JSON                                    │ │
│  │       │                                                    │ │
│  │       ▼                                                    │ │
│  │ POST /api/v1/files/verify                               │ │
│  │ ├─ Extract CRC from client                               │ │
│  │ ├─ Get CRC from server                                   │ │
│  │ ├─ Compare CRCs                                          │ │
│  │ └─ Return verification result                            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                      │                                         │
│                      ▼                                         │
│            MAIN PYTHON SERVER                                 │
│            ├─ Client management                               │
│            ├─ Key exchange (RSA-1024 OAEP-SHA256)           │
│            ├─ AES session key generation                      │
│            ├─ Multi-packet file reassembly                    │
│            ├─ AES-256-CBC decryption                          │
│            ├─ CRC-32 verification (Linux cksum)              │
│            ├─ Database operations (SQLite3)                   │
│            └─ File storage (received_files/)                  │
│                      │                                         │
│                      ▼                                         │
│            FLET 0.28.3 DESKTOP GUI                           │
│            ├─ Real-time status updates                        │
│            ├─ Connected clients display                       │
│            ├─ Transfer progress monitoring                    │
│            ├─ File verification status                        │
│            └─ Server statistics dashboard                     │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### 1. C++ Client → Flask API Server
- **Protocol**: HTTP/REST (instead of raw TCP)
- **Port**: 5000 (Flask) instead of 1256 (direct)
- **Modifications**:
  - Replace socket.h with libcurl or similar
  - JSON serialization for requests/responses
  - HTTP headers and error handling

### 2. Flask API Server → Main Python Server
- **Protocol**: Custom binary TCP (unchanged)
- **Implementation**: ServerProxy service
- **Maintains backward compatibility with existing server

### 3. Web GUI → Flask API Server
- **Protocol**: HTTP/JSON + optional WebSocket
- **Port**: 5000 (same as Flask)
- **Real-time updates**: EventSource or WebSocket

### 4. Main Server ↔ Flet GUI
- **Protocol**: Direct method calls (same process)
- **Threading**: Queue-based updates
- **Real-time display**: Automatic UI refresh

---

## Technology Stack

| Layer | Component | Current | Proposed |
|-------|-----------|---------|----------|
| **Client** | Desktop App | C++17 + Windows API | C++17 + libcurl (optional) |
| **API** | Web Service | None | Flask 2.3.0 |
| **Web GUI** | Frontend | None | React 18.x / Vue 3.x |
| **Server** | Backend | Python 3.11 + Tkinter | Python 3.11 + Flet 0.28.3 |
| **Database** | Persistence | SQLite3 | SQLite3 (unchanged) |
| **Crypto** | Security | Crypto++ + PyCryptodome | Crypto++ + PyCryptodome (unchanged) |

---

## Implementation Roadmap

### Phase 1: Flask API Layer (Foundation)
- [ ] Create `/api/` directory structure
- [ ] Implement `app.py` with Flask initialization
- [ ] Implement ServerProxy service
- [ ] Create registration endpoint
- [ ] Create authentication endpoint
- [ ] Create key exchange endpoint
- [ ] Create file transfer endpoint
- [ ] Create verification endpoint
- [ ] Create status endpoint
- [ ] Implement error handling
- [ ] Add CORS support
- [ ] Write unit tests

### Phase 2: Web-Based Client GUI
- [ ] Create `/client-web-gui/` directory
- [ ] Setup React/Vue project
- [ ] Implement Dashboard component
- [ ] Implement FileUploader component
- [ ] Implement ProgressBar component
- [ ] Implement StatusIndicator component
- [ ] Implement client-side AES encryption
- [ ] Implement CRC-32 calculation
- [ ] Setup API service
- [ ] Implement authentication flow
- [ ] Build production bundle
- [ ] Setup static file serving in Flask

### Phase 3: Flet Desktop GUI
- [ ] Create `/server_gui_flet/` directory
- [ ] Implement Flet app main.py
- [ ] Implement Dashboard page
- [ ] Implement Clients page
- [ ] Implement Transfers page
- [ ] Implement Settings page
- [ ] Implement real-time monitoring
- [ ] Add charting/graphs
- [ ] Setup statistics collection
- [ ] Integrate with main server

### Phase 4: Testing & Integration
- [ ] End-to-end integration tests
- [ ] Load testing
- [ ] Security testing
- [ ] Performance benchmarking
- [ ] Documentation
- [ ] Deployment procedures

### Phase 5: Deployment
- [ ] Docker containerization
- [ ] Environment configuration
- [ ] Production deployment
- [ ] Monitoring and logging

---

## Summary

This multi-layer architecture provides:
- **Client Access**: C++ desktop client + web-based client GUI
- **API Gateway**: Flask server for protocol translation and REST endpoints
- **Server Backend**: Python server with SQLite database and Flet GUI
- **Security**: Maintained end-to-end encryption throughout all layers
- **Scalability**: Separates concerns for easier scaling
- **Flexibility**: Multiple client types (desktop, web, API)
- **Monitoring**: Real-time status via Flet desktop GUI

All layers maintain the core security properties:
- ✅ RSA-1024 OAEP-SHA256 key exchange
- ✅ AES-256-CBC file encryption
- ✅ Linux cksum CRC-32 verification
- ✅ Zero-knowledge encryption (server never has plaintext)
- ✅ Session-based ephemeral keys
- ✅ Multi-threaded concurrent client support

