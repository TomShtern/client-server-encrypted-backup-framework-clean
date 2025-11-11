# Flask API Server - Detailed Architecture & Integration Guide

**Status**: Documentation for Proposed Implementation
**Target Version**: Flask 2.3.0
**Purpose**: REST API bridge between HTTP clients and encrypted backup system
**Date**: 2025-11-11

---

## Table of Contents

1. [Executive Overview](#executive-overview)
2. [Architecture & Components](#architecture--components)
3. [How It Works](#how-it-works)
4. [Integration Points](#integration-points)
5. [REST API Endpoints](#rest-api-endpoints)
6. [Data Flow Specifications](#data-flow-specifications)
7. [Configuration & Deployment](#configuration--deployment)
8. [Error Handling](#error-handling)
9. [Security Considerations](#security-considerations)
10. [Comparison to Current System](#comparison-to-current-system)

---

## Executive Overview

### Purpose

The Flask API Server serves as a **protocol translation layer** that converts HTTP/REST requests from web browsers, mobile apps, and third-party integrations into the **custom binary TCP protocol** used by the core encrypted backup server.

### Current System (Without Flask API)

```
┌─────────────────────┐
│   C++ Client        │
│  (Understands TCP   │
│   Binary Protocol)  │
└──────────┬──────────┘
           │ (Binary Protocol, Port 1256)
           ▼
┌──────────────────────┐
│  Python Server       │
│  (TCP Binary Proto)  │
└──────────────────────┘
```

**Limitation**: Only C++ clients can connect directly; web browsers cannot use raw TCP

### Enhanced System (With Flask API)

```
┌──────────────────────┐        ┌──────────────────────┐
│  Web Browser         │        │  Mobile App          │
│  (HTTP/JSON)         │        │  (HTTP/JSON)         │
└──────────┬───────────┘        └──────────┬───────────┘
           │                               │
           └───────────────┬───────────────┘
                           │ (HTTP, Port 5000)
                           ▼
        ┌──────────────────────────────────┐
        │   Flask API Server               │
        │  (REST Endpoints, CORS Support)  │
        │  (Request Validation)            │
        │  (Error Handling)                │
        └──────────────┬───────────────────┘
                       │ (Binary Protocol, Port 1256)
                       ▼
        ┌──────────────────────────────────┐
        │   Python Server                  │
        │  (TCP Binary Protocol Handler)   │
        │  (File Storage)                  │
        │  (Database Management)           │
        └──────────────────────────────────┘

Existing C++ Client can continue to use direct TCP connection:

┌──────────────────────┐
│   C++ Client         │
└──────────┬───────────┘
           │ (Binary Protocol, Port 1256)
           ▼
    [Python Server]
```

**Benefit**: Supports HTTP/REST clients while maintaining backward compatibility with C++ client

---

## Architecture & Components

### Multi-Layered Design

```
┌─────────────────────────────────────────────────────┐
│  PRESENTATION LAYER (HTTP)                          │
│  ├─ CORS Headers                                    │
│  ├─ JSON Request/Response                           │
│  └─ Error Messages                                  │
├─────────────────────────────────────────────────────┤
│  FLASK API LAYER (Rest Endpoints)                  │
│  ├─ app.py (Main Application)                       │
│  ├─ config.py (Configuration)                       │
│  ├─ routes/ (Endpoint Modules)                      │
│  │   ├─ registration.py                             │
│  │   ├─ authentication.py                           │
│  │   ├─ key_exchange.py                             │
│  │   ├─ file_transfer.py                            │
│  │   └─ status.py                                   │
│  └─ utils/error_handler.py                          │
├─────────────────────────────────────────────────────┤
│  SERVICE LAYER (Business Logic)                     │
│  ├─ ServerProxy (TCP Protocol Translation)          │
│  ├─ Session Management                              │
│  └─ Request Validation                              │
├─────────────────────────────────────────────────────┤
│  PROTOCOL TRANSLATION LAYER                         │
│  ├─ Binary Protocol Header Creation                 │
│  ├─ Payload Encoding/Decoding                       │
│  └─ Request/Response Code Mapping                   │
├─────────────────────────────────────────────────────┤
│  NETWORK LAYER (TCP Socket)                         │
│  ├─ Socket Connection Management                    │
│  ├─ TCP Communication with Python Server            │
│  └─ Error Recovery                                  │
├─────────────────────────────────────────────────────┤
│  BACKEND LAYER (Core Encrypted Backup System)       │
│  ├─ Python Server (server.py)                       │
│  ├─ SQLite Database (defensive.db)                  │
│  └─ File Storage (received_files/)                  │
└─────────────────────────────────────────────────────┘
```

### File Structure

```
api/
│
├── app.py                      Main Flask Application
│   └─ Entry point
│   └─ Blueprint registration
│   └─ Error handlers
│   └─ CORS configuration
│   └─ Signal handlers (graceful shutdown)
│
├── config.py                   Configuration Management
│   └─ DevelopmentConfig (debug enabled)
│   └─ ProductionConfig (secure, optimized)
│   └─ TestingConfig (fast, in-memory)
│
├── requirements.txt            Python Dependencies
│   └─ Flask 2.3.0
│   └─ Flask-CORS 4.0.0
│   └─ pycryptodome 3.18.0
│   └─ gunicorn 21.2.0
│   └─ And others...
│
├── routes/                     Endpoint Blueprint Modules
│   ├── __init__.py
│   ├── registration.py         Client registration endpoints
│   ├── authentication.py        Login/logout/session endpoints
│   ├── key_exchange.py          RSA public key exchange endpoints
│   ├── file_transfer.py         File upload/verify endpoints
│   └── status.py                Health check/stats endpoints
│
├── services/                   Business Logic Layer
│   ├── __init__.py
│   └── server_proxy.py          TCP protocol translator
│
├── models/                     Data Models (Future Expansion)
│   ├── __init__.py
│   ├── client_model.py          Client entity definition
│   ├── file_model.py            File entity definition
│   └── session_model.py         Session management model
│
└── utils/                      Utility Functions
    ├── __init__.py
    ├── error_handler.py         Custom exceptions & error responses
    ├── auth.py                  Authentication utilities (Future)
    └── validators.py            Input validation (Future)
```

### Core Components

#### 1. **Main Application (app.py)**

**Responsibility**: Flask application initialization, routing, middleware

**Handles**:
- Blueprint registration (5 modules: registration, authentication, key_exchange, file_transfer, status)
- CORS (Cross-Origin Resource Sharing) configuration for web clients
- Error handlers (400, 401, 403, 404, 500)
- Signal handlers for graceful shutdown
- Logging configuration
- Configuration loading based on environment

**Configuration Options**:
- `FLASK_ENV`: development, production, or testing
- `DEBUG`: Enable/disable debug mode
- `CORS_ORIGINS`: List of allowed origins for web clients
- `BACKEND_HOST`: Address of Python backup server
- `BACKEND_PORT`: Port of Python backup server (default: 1256)
- `SECRET_KEY`: Flask secret key for sessions

#### 2. **ServerProxy Service (services/server_proxy.py)**

**Responsibility**: Translate REST requests to binary TCP protocol and vice versa

**Key Responsibilities**:
- Create 23-byte request headers (little-endian format)
- Encode payloads to binary format
- Send requests to Python server via socket
- Receive and parse response headers (7 bytes)
- Decode response payloads
- Handle connection lifecycle (connect, keep-alive, disconnect)
- Thread-safe operation for concurrent requests

**Request Translation Example**:
```
REST Request:                    Binary Protocol:
{                               [16-byte Client ID]
  "username": "john",           [4-byte Request Code: 1025]
  "client_type": "web"          [4-byte Payload Size: 255]
}                               [255-byte Username String]
    ↓                                ↓
ServerProxy.register_client()    Python Server Receives
    ↓                                ↓
Response:                        [4-byte Response Code: 1600]
{                               [4-byte Payload Size: 0]
  "status": "success"
}
```

#### 3. **Route Modules (routes/)**

**Responsibility**: Handle specific endpoint groups

Each module is a Flask Blueprint that handles a category of endpoints:

**registration.py**:
- `POST /api/v1/auth/register` - Register new client
- `GET /api/v1/auth/register/<client_id>` - Check registration status

**authentication.py**:
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - Session termination
- `POST /api/v1/auth/validate` - Session validation

**key_exchange.py**:
- `POST /api/v1/keys/public` - Send public key
- `GET /api/v1/keys/status` - Get key status

**file_transfer.py**:
- `POST /api/v1/files/upload` - Upload encrypted file
- `POST /api/v1/files/verify` - Verify with CRC
- `GET /api/v1/files/status` - Get transfer status

**status.py**:
- `GET /api/v1/status` - System status
- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - Server statistics
- `GET /api/v1/version` - Version info

#### 4. **Error Handler (utils/error_handler.py)**

**Responsibility**: Standardized error handling and JSON responses

**Custom Exception Classes**:
- `APIError`: Base exception (400)
- `ValidationError`: Invalid input (400)
- `AuthenticationError`: Auth failed (401)
- `AuthorizationError`: Not authorized (403)
- `NotFoundError`: Resource not found (404)
- `ServerConnectionError`: Backend unavailable (503)
- `InternalServerError`: Unexpected error (500)

**Response Format**:
```json
{
  "status": "error",
  "error": "ValidationError",
  "message": "Username is required",
  "status_code": 400
}
```

---

## How It Works

### Request/Response Cycle

#### Step 1: HTTP Request Arrives at Flask

```
Client (Web Browser)
    │
    ├─ Method: POST
    ├─ URL: /api/v1/auth/register
    ├─ Headers: Content-Type: application/json
    │          CORS headers
    └─ Body: {"username": "john", "client_type": "web_client"}
         ↓
    Flask App (app.py)
         ↓
    CORS Middleware (Check origin allowed)
         ↓
    Route Dispatcher (Find matching route)
         ↓
    registration.py:register() endpoint handler
```

#### Step 2: Validate Request

```
registration.py:register()
    │
    ├─ Check Content-Type: application/json ✓
    ├─ Parse JSON body
    ├─ Extract username, client_type
    ├─ Validate username:
    │   ├─ Not empty? ✓
    │   ├─ Max 255 chars? ✓
    │   └─ Valid characters? ✓
    ├─ Validate client_type:
    │   └─ "cpp_client" or "web_client"? ✓
    │
    ├─ If invalid → Raise ValidationError → Error Handler
    └─ If valid → Continue to next step
```

#### Step 3: Generate Client ID

```
Generate New UUID:
    └─ Example: 550e8400-e29b-41d4-a716-446655440000
    └─ Convert to 16-byte binary: [16 bytes]
```

#### Step 4: Create Binary Protocol Request

```
ServerProxy.register_client():
    │
    ├─ Create 23-byte header:
    │   ├─ Bytes 0-15: 16-byte Client ID (from UUID)
    │   ├─ Bytes 16-19: Request Code 1025 (REGISTER)
    │   ├─ Bytes 20-23: Payload Size (255 bytes for username)
    │   └─ Bytes 24-26: Padding (zeros)
    │
    ├─ Create payload (255 bytes):
    │   ├─ Username string (up to 255 chars)
    │   └─ Pad with zeros to exactly 255 bytes
    │
    ├─ Combine: Header + Payload = 23 + 255 = 278 bytes
    └─ Ready to send to Python Server
```

#### Step 5: Send to Python Server

```
ServerProxy._send_request():
    │
    ├─ Connect to Python Server (localhost:1256) if not connected
    ├─ Send 23-byte header via socket
    ├─ Send 255-byte payload via socket
    ├─ Receive response header (7 bytes)
    │   ├─ Bytes 0-3: Response Code (e.g., 1600 = REG_OK)
    │   └─ Bytes 4-7: Payload Size
    ├─ Receive response payload (if any)
    └─ Return (response_code, payload)
```

#### Step 6: Parse Python Server Response

```
Python Server Response:
    │
    ├─ Response Code 1600 (REG_OK): Success
    │   └─ return {"status": "success", ...}
    ├─ Response Code 1601 (REG_FAIL): Failure
    │   └─ return {"status": "failed", ...}
    └─ Other codes: Handle accordingly
```

#### Step 7: Return JSON Response to Client

```
registration.py:register():
    │
    ├─ Build JSON response:
    │   {
    │     "status": "success",
    │     "message": "Client registered",
    │     "data": {
    │       "client_id": "550e8400-e29b-41d4-a716-446655440000",
    │       "username": "john",
    │       "client_type": "web_client"
    │     }
    │   }
    │
    ├─ Set HTTP status code: 201 (Created)
    └─ Return JSON response
         ↓
    Flask App
         ↓
    JSON Serialization
         ↓
    HTTP Response (Content-Type: application/json)
         ↓
    Client (Web Browser)
         ↓
    JavaScript receives JSON, updates UI
```

### Key Protocols & Conversions

#### UUID to Binary Conversion

```
UUID String:    550e8400-e29b-41d4-a716-446655440000
                ↓ (16-byte binary representation)
16 Bytes:       [0x55, 0x0e, 0x84, 0x00, 0xe2, 0x9b, ...]
                ↓ (little-endian in protocol)
```

#### Integer to Binary Conversion (Little-Endian)

```
Request Code 1025:
    Decimal:    1025
    Binary:     0000 0000 0000 0000 0000 0100 0000 0001
    Little-Endian (4 bytes): [0x01, 0x04, 0x00, 0x00]

Payload Size 255:
    Decimal:    255
    Binary:     0000 0000 0000 0000 0000 0000 1111 1111
    Little-Endian (4 bytes): [0xFF, 0x00, 0x00, 0x00]
```

#### Base64 Encoding/Decoding

```
Binary Data (RSA Public Key):
    [162 bytes of raw binary data]
    ↓ (Base64 encode for JSON)
JSON String:
    "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQK..."
    ↓ (Base64 decode for binary protocol)
Binary Data:
    [162 bytes sent to Python server]
```

---

## Integration Points

### 1. How Flask Connects to Python Server

```
┌─────────────────────────────────────────────────────┐
│ Flask API Server                                    │
│                                                     │
│  ServerProxy Service                                │
│  ├─ Host: localhost                                 │
│  ├─ Port: 1256 (configurable)                       │
│  ├─ Protocol: Raw TCP socket                        │
│  ├─ Format: Binary protocol v3                      │
│  └─ Encoding: Little-endian                         │
│                                                     │
│         TCP Socket Connection                       │
│         ↓                                           │
│         Persistent Connection (kept open)           │
│         ├─ Send request bytes                       │
│         ├─ Receive response bytes                   │
│         └─ Multi-threaded safe                      │
│                                                     │
│  Handles all protocol details:                      │
│  ├─ Header creation (23 bytes)                      │
│  ├─ Payload encoding                                │
│  ├─ Response parsing (7-byte header)                │
│  ├─ Connection errors                               │
│  └─ Timeout handling                                │
└────────────────────┬────────────────────────────────┘
                     │ Binary Protocol v3
                     │ Port 1256
                     ▼
        ┌─────────────────────────────────┐
        │ Python Server (server.py)       │
        │                                 │
        │ ├─ Receive binary request       │
        │ ├─ Parse headers & payload      │
        │ ├─ Process request              │
        │ ├─ Generate binary response     │
        │ └─ Send response                │
        │                                 │
        │ Client Management               │
        │ ├─ Register clients             │
        │ ├─ Manage sessions              │
        │ └─ Store client keys            │
        │                                 │
        │ Database & Storage              │
        │ ├─ SQLite (defensive.db)        │
        │ └─ File storage (received_files)│
        └─────────────────────────────────┘
```

### 2. Request Code Mapping

Flask Endpoints → Binary Request Codes:

| Flask Endpoint | Request Code | Python Server Handler |
|---|---|---|
| POST /auth/register | 1025 | _handle_registration() |
| POST /keys/public | 1026 | _handle_send_public_key() |
| POST /auth/reconnect | 1027 | _handle_reconnect() |
| POST /files/upload | 1028 | _handle_send_file() |
| POST /files/verify (CRC OK) | 1029 | _handle_crc_ok() |
| POST /files/verify (CRC RETRY) | 1030 | _handle_crc_retry() |
| POST /files/abort | 1031 | _handle_crc_abort() |

### 3. Response Code Mapping

Binary Response Codes → Flask Response:

| Response Code | Status | Flask Response |
|---|---|---|
| 1600 | REG_OK | {"status": "success", ...} |
| 1601 | REG_FAIL | {"status": "failed", "message": "..."} |
| 1602 | PUBKEY_AES_SENT | {"status": "success", "encrypted_aes_key": "..."} |
| 1603 | FILE_CRC | {"status": "crc_pending", ...} |
| 1604 | ACK | {"status": "success", ...} |
| 1605 | RECONNECT_AES_SENT | {"status": "success", ...} |
| 1606 | RECONNECT_FAIL | {"status": "error", ...} |
| 1607 | ERROR | {"status": "error", "message": "..."} |

---

## REST API Endpoints

### 1. Authentication Endpoints

#### Register New Client

```
Endpoint:   POST /api/v1/auth/register
Purpose:    Create new client account
Auth:       None required

Request:
{
  "username": "john_doe",
  "client_type": "web_client"  // "cpp_client" or "web_client"
}

Success Response (201 Created):
{
  "status": "success",
  "message": "Client registered successfully",
  "data": {
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "client_type": "web_client"
  }
}

Error Response (400 Bad Request):
{
  "status": "error",
  "error": "ValidationError",
  "message": "Username is required",
  "status_code": 400
}

Error Response (503 Service Unavailable):
{
  "status": "error",
  "error": "ServerConnectionError",
  "message": "Backend server unavailable",
  "status_code": 503
}
```

#### Login

```
Endpoint:   POST /api/v1/auth/login
Purpose:    Authenticate user and get session token
Auth:       None required

Request:
{
  "username": "john_doe"
}

Success Response (200 OK):
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "session_token": "550e8400-e29b-41d4-a716-446655440000",
    "client_id": "550e8400-e29b-41d4-a716-446655440001",
    "username": "john_doe",
    "expires_in": 3600  // seconds until expiration
  }
}
```

#### Validate Session

```
Endpoint:   POST /api/v1/auth/validate
Purpose:    Check if session token is still valid
Auth:       None required

Request:
{
  "session_token": "550e8400-e29b-41d4-a716-446655440000"
}

Success Response (200 OK):
{
  "status": "success",
  "data": {
    "valid": true,
    "client_id": "550e8400-e29b-41d4-a716-446655440001",
    "username": "john_doe",
    "expires_in": 3500  // remaining time
  }
}

Expired Response (200 OK):
{
  "status": "success",
  "data": {
    "valid": false,
    "message": "Session expired"
  }
}
```

### 2. Key Exchange Endpoints

#### Send Public Key

```
Endpoint:   POST /api/v1/keys/public
Purpose:    Send RSA public key, receive encrypted AES key
Auth:       None (should use session token in future)

Request:
{
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "public_key_der": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQK..." // base64
}

Success Response (200 OK):
{
  "status": "success",
  "message": "Key exchange successful",
  "data": {
    "encrypted_aes_key": "base64_encoded_128_byte_encrypted_key",
    "key_size": 256  // key size in bits
  }
}

Explanation of key_size: Indicates the AES key is 256 bits (32 bytes)
```

### 3. File Transfer Endpoints

#### Upload File (Encrypted)

```
Endpoint:   POST /api/v1/files/upload
Purpose:    Upload encrypted file data to server
Auth:       None (should use session token)

Request:
{
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "backup.zip",
  "encrypted_data": "base64_encoded_encrypted_file_bytes",
  "original_size": 1048576,  // size before encryption
  "packet_number": 1,        // for multi-packet uploads
  "total_packets": 1         // total expected packets
}

Success Response (200 OK):
{
  "status": "success",
  "message": "File received",
  "data": {
    "filename": "backup.zip",
    "packet_received": 1,
    "awaiting_packets": [],  // empty if all packets received
    "transfer_status": "success"
  }
}

Partial Response (200 OK - waiting for more packets):
{
  "status": "success",
  "message": "Packet received",
  "data": {
    "filename": "backup.zip",
    "packet_received": 1,
    "awaiting_packets": [2, 3],  // waiting for packets 2 and 3
    "transfer_status": "in_progress"
  }
}

Flow:
1. Client encrypts file with AES key (received from key exchange)
2. Client encodes encrypted bytes as base64
3. Client sends to Flask API
4. Flask forwards to Python server via binary protocol
5. Python server decrypts and stores file
6. Response indicates if more packets needed
```

#### Verify File (CRC Check)

```
Endpoint:   POST /api/v1/files/verify
Purpose:    Verify file integrity with CRC-32 checksum
Auth:       None (should use session token)

Request:
{
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "backup.zip",
  "client_crc": "0x12345678"  // hex or decimal
}

Success Response (200 OK):
{
  "status": "success",
  "message": "File verification completed",
  "data": {
    "filename": "backup.zip",
    "client_crc": "0x12345678",
    "verified": true,
    "status": "crc_match"
  }
}

Failure Response (200 OK - CRC mismatch):
{
  "status": "success",
  "message": "File verification completed",
  "data": {
    "filename": "backup.zip",
    "client_crc": "0x12345678",
    "verified": false,
    "status": "crc_mismatch",
    "server_crc": "0x87654321"
  }
}

CRC Calculation:
- Uses Linux cksum algorithm (CRC-32, polynomial 0x04C11DB7)
- Client calculates CRC on original plaintext file
- Server calculates CRC on received encrypted file (before decryption)
- Both should match if transfer was successful
```

### 4. Status Endpoints

#### Get System Status

```
Endpoint:   GET /api/v1/status
Purpose:    Get overall system health and status
Auth:       None

Response (200 OK):
{
  "status": "success",
  "message": "System status retrieved",
  "data": {
    "api_server": {
      "running": true,
      "version": "v1",
      "timestamp": "2025-11-11T12:34:56.789Z"
    },
    "backend_server": {
      "running": true,
      "host": "localhost",
      "port": 1256,
      "connected": true
    }
  }
}
```

#### Health Check

```
Endpoint:   GET /api/v1/health
Purpose:    Quick health check (used for monitoring)
Auth:       None

Response (200 OK):
{
  "status": "success",
  "message": "API server is healthy",
  "data": {
    "healthy": true,
    "timestamp": "2025-11-11T12:34:56.789Z"
  }
}
```

#### Server Statistics

```
Endpoint:   GET /api/v1/stats
Purpose:    Get server statistics and metrics
Auth:       None

Response (200 OK):
{
  "status": "success",
  "message": "Statistics retrieved",
  "data": {
    "api_stats": {
      "requests_total": 1234,
      "requests_successful": 1200,
      "requests_failed": 34,
      "uptime_seconds": 86400
    },
    "timestamp": "2025-11-11T12:34:56.789Z"
  }
}
```

#### Version Information

```
Endpoint:   GET /api/v1/version
Purpose:    Get API and system version info
Auth:       None

Response (200 OK):
{
  "status": "success",
  "message": "Version information retrieved",
  "data": {
    "api_version": "v1",
    "api_title": "Encrypted Backup Framework API",
    "api_description": "REST API for secure file backup and transfer",
    "python_version": "3.11.4",
    "timestamp": "2025-11-11T12:34:56.789Z"
  }
}
```

---

## Data Flow Specifications

### Complete Registration Flow

```
Web Client                    Flask API                  Python Server
    │                            │                             │
    ├─ POST /auth/register       │                             │
    │  (username, client_type)   │                             │
    ├───────────────────────────>│                             │
    │                            │ Validate input               │
    │                            │ Generate UUID               │
    │                            │                             │
    │                            │ Create request (1025)       │
    │                            │ Header: [client_id][1025]   │
    │                            │ Payload: [username]         │
    │                            │                             │
    │                            ├─── TCP Binary Protocol ────>│
    │                            │                             │
    │                            │                             │ Parse request
    │                            │                             │ Store client
    │                            │                             │ Generate response (1600)
    │                            │                             │
    │                            │<─── TCP Binary Protocol ────┤
    │                            │                             │
    │                            │ Parse response (1600=OK)    │
    │                            │ Build JSON response         │
    │                            │                             │
    │ Success JSON Response      │                             │
    │<───────────────────────────┤                             │
    │                            │                             │
```

### Complete File Upload with CRC Verification

```
Web Client                    Flask API                  Python Server
    │                            │                             │
    ├─ POST /keys/public         │                             │
    │  (client_id, public_key)   │                             │
    ├───────────────────────────>│                             │
    │                            │ Create request (1026)       │
    │                            ├─────────────────────────────>│
    │                            │                             │
    │                            │                             │ Send encrypted AES key
    │                            │<─────────────────────────────┤
    │<─ encrypted_aes_key ───────┤                             │
    │                            │                             │
    │ (Client decrypts AES key using private key)             │
    │                            │                             │
    │                            │                             │
    ├─ POST /files/upload        │                             │
    │  (client_id, filename,     │                             │
    │   encrypted_file)          │                             │
    ├───────────────────────────>│                             │
    │                            │ Encode as base64           │
    │                            │ Create request (1028)       │
    │                            ├─────────────────────────────>│
    │                            │                             │
    │                            │                             │ Receive file
    │                            │                             │ Store encrypted file
    │                            │<─ Ack (1604) ──────────────┤
    │                            │                             │
    │<─ {packet_received:1} ─────┤                             │
    │                            │                             │
    │ (Client calculates CRC-32 on original file)             │
    │                            │                             │
    ├─ POST /files/verify        │                             │
    │  (client_id, filename,     │                             │
    │   client_crc)              │                             │
    ├───────────────────────────>│                             │
    │                            │ Create request (1029)       │
    │                            ├─────────────────────────────>│
    │                            │                             │
    │                            │                             │ Decrypt file
    │                            │                             │ Calculate server CRC
    │                            │                             │ Compare CRCs
    │                            │<─ Ack (1604) ──────────────┤
    │                            │                             │
    │<─ {verified: true} ────────┤                             │
    │                            │                             │
```

### Multi-Packet File Upload

```
Large File (100 MB) encrypted by client:
    │
    ├─ Split into packets (e.g., 30 MB each)
    │   ├─ Packet 1: 30 MB
    │   ├─ Packet 2: 30 MB
    │   ├─ Packet 3: 30 MB
    │   └─ Packet 4: 10 MB
    │
    ├─ Upload Packet 1:
    │   POST /files/upload
    │   {
    │     "packet_number": 1,
    │     "total_packets": 4,
    │     "encrypted_data": "base64(30MB)"
    │   }
    │   Response: {awaiting_packets: [2,3,4]}
    │
    ├─ Upload Packet 2:
    │   POST /files/upload
    │   {
    │     "packet_number": 2,
    │     "total_packets": 4,
    │     "encrypted_data": "base64(30MB)"
    │   }
    │   Response: {awaiting_packets: [3,4]}
    │
    ├─ Upload Packet 3:
    │   POST /files/upload
    │   {
    │     "packet_number": 3,
    │     "total_packets": 4,
    │     "encrypted_data": "base64(30MB)"
    │   }
    │   Response: {awaiting_packets: [4]}
    │
    ├─ Upload Packet 4:
    │   POST /files/upload
    │   {
    │     "packet_number": 4,
    │     "total_packets": 4,
    │     "encrypted_data": "base64(10MB)"
    │   }
    │   Response: {awaiting_packets: []}
    │
    └─ All packets received, verify file with CRC
```

---

## Configuration & Deployment

### Environment Variables

```
# Flask Configuration
FLASK_ENV=development          # development, production, testing
DEBUG=False                    # Enable/disable debug mode
SECRET_KEY=your-secret-key     # Required for sessions

# Backend Connection
BACKEND_HOST=localhost         # Python server hostname
BACKEND_PORT=1256              # Python server port
BACKEND_TIMEOUT=30             # Connection timeout (seconds)

# Logging
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR

# CORS
CORS_ORIGINS=*                 # Allowed origins (development)
CORS_ORIGINS=https://example.com  # Specific origins (production)
```

### Development Setup

```
1. Install Python 3.11+
2. Create virtual environment:
   python -m venv venv
   source venv/bin/activate  (Linux/Mac)
   venv\Scripts\activate     (Windows)

3. Install dependencies:
   pip install -r api/requirements.txt

4. Set environment:
   export FLASK_ENV=development

5. Ensure Python server running:
   python server/server.py

6. Start Flask API:
   cd api
   python app.py

7. API accessible at: http://localhost:5000
```

### Production Deployment

```
1. Install Python 3.11+ on production server
2. Use gunicorn (WSGI application server):
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app

3. Use nginx as reverse proxy
4. Enable HTTPS/TLS
5. Set FLASK_ENV=production
6. Configure CORS for specific origins
7. Use environment variables for secrets
8. Enable logging to files
9. Setup monitoring and alerts
```

### Database Configuration

Flask API can use SQLite database (same as Python server) or PostgreSQL for production:

```
SQLite (Development):
  DATABASE_URL=sqlite:///defensive.db

PostgreSQL (Production):
  DATABASE_URL=postgresql://user:password@host:port/dbname
```

---

## Error Handling

### Error Categories

#### 1. Validation Errors (400)
- Invalid request format
- Missing required fields
- Invalid data types
- Out-of-range values

#### 2. Authentication Errors (401)
- Invalid credentials
- Expired session token
- Missing authentication

#### 3. Authorization Errors (403)
- Insufficient permissions
- Client not authorized
- Access denied

#### 4. Not Found Errors (404)
- Client not found
- File not found
- Resource not found

#### 5. Server Errors (500+)
- Backend server unavailable (503)
- Database errors
- Unexpected errors

### Error Response Format

```json
{
  "status": "error",
  "error": "ErrorType",
  "message": "Human-readable description",
  "status_code": 400
}
```

### Retry Logic

```
Client receives error response:

├─ 400/401/403/404 → Don't retry (client error)
├─ 503 → Retry with exponential backoff
│         Try 1: immediate
│         Try 2: wait 2 seconds
│         Try 3: wait 4 seconds
│         Try 4: wait 8 seconds
│         Try 5: wait 16 seconds
│         Give up: after 5 attempts
└─ 500 → Log error, notify administrator
```

---

## Security Considerations

### Data Encryption

```
Request:                           Response:
{                                 {
  "public_key_der": "base64"       "encrypted_aes_key": "base64"
}                                 }

┌─────────────────────────────────┐
│ IMPORTANT: Data Flow             │
├─────────────────────────────────┤
│                                  │
│ 1. Flask receives public key     │
│    in JSON (not encrypted yet)   │
│                                  │
│ 2. Send to Python server via     │
│    TCP socket (should use TLS!)  │
│                                  │
│ 3. Python server generates AES   │
│    key and encrypts with public  │
│    key (RSA-OAEP-SHA256)         │
│                                  │
│ 4. Return encrypted AES key      │
│    to Flask via TCP              │
│                                  │
│ 5. Flask sends encrypted key     │
│    to client in JSON (safe!)     │
│                                  │
│ 6. Client decrypts with private  │
│    key to get AES key            │
│                                  │
│ 7. Client uses AES key to        │
│    encrypt file before upload    │
│                                  │
└─────────────────────────────────┘
```

### Security Recommendations

1. **Use HTTPS/TLS** in production
   - Encrypt all Flask API traffic
   - Use valid certificates

2. **Implement JWT Authentication**
   - Replace in-memory sessions with JWT tokens
   - Include token in all requests (Authorization header)

3. **Rate Limiting**
   - Limit requests per IP/client
   - Prevent brute force attacks

4. **CORS Configuration**
   - Restrict to specific origins in production
   - Don't use wildcard "*" in production

5. **Input Validation**
   - Validate all inputs
   - Sanitize strings
   - Check data types

6. **Error Handling**
   - Don't expose internal details in error messages
   - Log errors securely
   - Monitor for suspicious patterns

7. **Backend Security**
   - Use TLS for Flask→Python server communication
   - Implement authentication between Flask and Python server
   - Use firewall rules to limit access

---

## Comparison to Current System

### Current System (Without Flask API)

```
┌──────────────────────┐
│  C++ Client          │
│ (understands TCP)    │
└──────────┬───────────┘
           │ (Binary Protocol)
           ▼
┌──────────────────────┐
│  Python Server       │
│ (port 1256)          │
└──────────────────────┘

Limitations:
- Only C++ can connect
- No web browser support
- No third-party API access
- No RESTful interface
- Mobile apps cannot connect
```

### Enhanced System (With Flask API)

```
┌──────────────────────┐
│  Web Browser         │
│  (HTTP/JSON)         │
└──────────┬───────────┘
           │
┌──────────────────────┐     ┌──────────────────────┐
│  Flask API Server    │◄───►│  Python Server       │
│  (port 5000)         │     │ (port 1256)          │
│ (REST, CORS)         │     │ (Binary Protocol)    │
└──────────┬───────────┘     └──────────────────────┘
           │
┌──────────────────────┐
│  C++ Client          │
│ (can use Flask or    │
│  direct TCP)         │
└──────────────────────┘

Benefits:
✅ Web browsers can connect
✅ Third-party integrations
✅ RESTful JSON API
✅ Mobile app support
✅ Standard HTTP tooling
✅ Backward compatible (C++ still works)
```

### Feature Comparison

| Feature | Current | With Flask |
|---------|---------|-----------|
| C++ Client Direct | ✅ | ✅ |
| Web Browser | ❌ | ✅ |
| REST API | ❌ | ✅ |
| JSON Format | ❌ | ✅ |
| Mobile Apps | ❌ | ✅ |
| Standard HTTP Tools | ❌ | ✅ |
| CORS Support | ❌ | ✅ |
| Third-party Integration | ❌ | ✅ |

---

## Summary

The Flask API Server provides a modern REST/HTTP interface to the encrypted backup framework while maintaining full backward compatibility with the existing C++ client. It translates HTTP requests to the binary TCP protocol transparently, enabling web browsers, mobile apps, and third-party systems to access the secure backup system through standard REST APIs.

**Key Benefits**:
- Separates protocol complexity from client logic
- Enables web-based interfaces
- Supports modern API standards
- Maintains security through end-to-end encryption
- Provides clear integration points
- Easy to test and maintain

**Next Phase**: The Web-Based Client GUI will consume these REST APIs to provide a browser-based backup interface, making the system accessible to non-technical users.
