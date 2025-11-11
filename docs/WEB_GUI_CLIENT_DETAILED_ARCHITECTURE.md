# Web-Based Client GUI - Detailed Architecture & Design

**Status**: Documentation for Proposed Implementation
**Target Stack**: React/Vue.js with Webpack/Vite
**Purpose**: Browser-based client for encrypted backup system
**Date**: 2025-11-11

---

## Table of Contents

1. [Executive Overview](#executive-overview)
2. [Architecture & Design](#architecture--design)
3. [Component Structure](#component-structure)
4. [User Interface Design](#user-interface-design)
5. [Integration with Flask API](#integration-with-flask-api)
6. [Client-Side Encryption](#client-side-encryption)
7. [Data Flow](#data-flow)
8. [Authentication & Sessions](#authentication--sessions)
9. [Security Considerations](#security-considerations)
10. [Deployment & Hosting](#deployment--hosting)

---

## Executive Overview

### Purpose

The Web-Based Client GUI provides a **browser-based interface** for users to backup files to the encrypted backup system. It replaces the need for a native C++ application with a modern web application accessible from any browser.

### Current System

```
User Computer
    │
    ├─ C++ Client Application (Windows only)
    │   ├─ Download executable
    │   ├─ Install on computer
    │   └─ Configure settings
    │
    └─ Runs backup process (console-based)
```

**Limitation**: Only Windows; requires installation; not user-friendly

### Enhanced System (With Web GUI)

```
User Computer (Any OS)
    │
    ├─ Web Browser (Chrome, Firefox, Safari, Edge)
    │   │
    │   ├─ Go to: http://backup.example.com
    │   │
    │   ├─ Web UI loads instantly (no installation)
    │   │
    │   └─ Modern, intuitive interface
    │        ├─ Drag & drop file upload
    │        ├─ Real-time progress bar
    │        ├─ Status dashboard
    │        └─ File management
```

**Benefit**: Cross-platform; no installation; modern UX; instant access

### Key Differences from C++ Client

| Aspect | C++ Client | Web Client |
|--------|-----------|-----------|
| Platform | Windows only | Any OS (browser) |
| Installation | Required | None (browser) |
| Interface | Console-based | Modern GUI |
| File Selection | Config file | Drag & drop |
| Real-time Progress | Limited | Full streaming |
| User Experience | Technical | Intuitive |
| Accessibility | Local | Remote (HTTPS) |

---

## Architecture & Design

### System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      USER BROWSER                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                 Web Application                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ User Interface (React/Vue Components)                │ │ │
│  │  │ ├─ Dashboard Page                                   │ │ │
│  │  │ ├─ File Upload Component                            │ │ │
│  │  │ ├─ Progress Monitor                                 │ │ │
│  │  │ ├─ Settings Page                                    │ │ │
│  │  │ └─ Navigation Menu                                  │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ JavaScript Application Logic                         │ │ │
│  │  │ ├─ State Management (Redux/Vuex)                    │ │ │
│  │  │ ├─ API Service (HTTP Client)                        │ │ │
│  │  │ ├─ Encryption Service (Web Crypto API)             │ │ │
│  │  │ ├─ CRC Calculator                                  │ │ │
│  │  │ └─ Event Handlers & Logic                          │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Browser APIs                                         │ │ │
│  │  │ ├─ Web Crypto API (AES, RSA)                       │ │ │
│  │  │ ├─ File API (File Reading)                         │ │ │
│  │  │ ├─ Local Storage (Session Data)                    │ │ │
│  │  │ └─ XMLHttpRequest / Fetch (HTTP)                   │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│               HTTP/HTTPS (Port 443 / 5000)                     │
│                        (JSON)                                  │
└─────────────────────────────┬─────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │   Flask API Server (Port 5000)      │
        │                                     │
        │  ├─ Authentication Endpoints        │
        │  ├─ Key Exchange Endpoints          │
        │  ├─ File Upload Endpoints           │
        │  └─ Status Endpoints                │
        │                                     │
        │  ServerProxy Service                │
        │  └─ TCP Binary Protocol             │
        └──────────────┬──────────────────────┘
                       │
                       │ Binary Protocol (Port 1256)
                       ▼
        ┌─────────────────────────────────────┐
        │   Python Server                     │
        │                                     │
        │  ├─ Client Management               │
        │  ├─ Key Exchange (RSA-1024)        │
        │  ├─ File Storage                    │
        │  └─ Database (SQLite)               │
        └─────────────────────────────────────┘
```

### Technology Stack

**Frontend** (Browser-based):
- **React 18** or **Vue.js 3** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Webpack** or **Vite** - Build tool
- **Redux** or **Vuex** - State management
- **Axios** - HTTP client
- **Web Crypto API** - Client-side encryption
- **Bootstrap** or **Tailwind CSS** - Styling

**Server**:
- **Flask** (Python) - REST API
- **Python Server** - Backup core system

**Hosting**:
- **Nginx** or **Apache** - Web server
- **HTTPS/TLS** - Secure communication

### Project Structure

```
client-web-gui/
│
├── public/
│   ├── index.html                 Main HTML entry point
│   ├── favicon.ico
│   └── manifest.json              PWA manifest
│
├── src/
│   ├── index.html                 Bootstrap HTML
│   ├── main.tsx / main.js          Application entry point
│   │
│   ├── components/                React/Vue components
│   │   ├── Dashboard.tsx           Main dashboard page
│   │   ├── FileUploader.tsx        File upload component
│   │   ├── ProgressBar.tsx         Upload progress display
│   │   ├── StatusIndicator.tsx     Connection status
│   │   ├── Navigation.tsx          Top navigation
│   │   ├── Settings.tsx            Settings page
│   │   └── AuthForm.tsx            Login form
│   │
│   ├── pages/
│   │   ├── HomePage.tsx            Home page layout
│   │   ├── UploadPage.tsx          Upload page layout
│   │   ├── HistoryPage.tsx         File history page
│   │   ├── SettingsPage.tsx        Settings page layout
│   │   └── ProfilePage.tsx         User profile page
│   │
│   ├── services/
│   │   ├── api.ts                  Flask API client
│   │   ├── encryption.ts           AES encryption service
│   │   ├── crc.ts                  CRC-32 calculator
│   │   ├── storage.ts              Local storage service
│   │   └── crypto.ts               RSA key handling
│   │
│   ├── stores/ (or reducers/)
│   │   ├── userStore.ts            User state management
│   │   ├── uploadStore.ts          Upload state management
│   │   └── appStore.ts             App-wide state
│   │
│   ├── styles/
│   │   ├── main.css                Main stylesheet
│   │   ├── components.css           Component styles
│   │   └── responsive.css           Mobile responsive styles
│   │
│   ├── utils/
│   │   ├── validators.ts            Input validation
│   │   ├── formatters.ts            String formatting utilities
│   │   ├── constants.ts             Application constants
│   │   └── helpers.ts               Helper functions
│   │
│   └── types/
│       ├── index.ts                TypeScript type definitions
│       ├── api.ts                  API response types
│       └── models.ts               Data model types
│
├── tests/
│   ├── components/                Component tests
│   ├── services/                  Service tests
│   └── utils/                     Utility function tests
│
├── config/
│   ├── webpack.config.js           Webpack configuration
│   ├── jest.config.js              Test configuration
│   └── .env.example                Environment variables template
│
├── package.json                   Dependencies & scripts
├── tsconfig.json                  TypeScript configuration
├── .env                           Environment variables (gitignored)
├── .gitignore
└── README.md                      Documentation
```

---

## Component Structure

### Page Components (Top-level)

#### 1. Dashboard Page

**Purpose**: Main application dashboard showing status, recent uploads, and quick actions

**Features**:
- Welcome message with username
- Server connection status
- Recent file uploads list
- Quick upload button
- Storage statistics
- User profile dropdown

**Data Requirements**:
- Current user info
- Server status
- List of recent uploads
- Storage usage

```
Dashboard
├── Header
│   ├── Logo/Title
│   ├── User Menu (Dropdown)
│   └── Connection Status Indicator
├── Main Content
│   ├── Welcome Section
│   ├── Recent Uploads (Table/List)
│   │   ├── Filename
│   │   ├── Upload Date
│   │   ├─ Status (Success/Pending/Failed)
│   │   └─ Action (Re-upload/Delete)
│   └── Upload Statistics
│       ├─ Total Files
│       ├─ Total Size
│       └─ This Month
└── Bottom Banner
    └─ Latest News/Updates
```

#### 2. File Uploader Component

**Purpose**: Allow users to select and upload files

**Features**:
- Drag & drop area
- File selection button (native file picker)
- File list preview before upload
- Start/Cancel buttons
- Real-time progress per file

**Data Requirements**:
- Selected files list
- Upload progress
- File validation status

```
FileUploader
├── Drop Zone (Drag & Drop Area)
│   └─ "Drag files here or click to browse"
├── File Input (Hidden)
├── Selected Files List
│   ├─ Filename
│   ├─ File Size
│   ├─ Validation Status (✓/✗)
│   └─ Remove Button
├── Upload Configuration
│   ├─ Compression (Optional)
│   ├─ Encryption Level
│   └─ Backup Category
└── Action Buttons
    ├─ Upload All
    └─ Cancel
```

#### 3. Progress Monitor Component

**Purpose**: Display real-time upload progress and status

**Features**:
- Progress bar per file
- Speed indicator (MB/s)
- Time remaining estimation
- Upload status messages
- Pause/Resume (if applicable)
- Cancel button

```
ProgressMonitor
├─ Overall Progress (All Files)
│   ├─ Progress Bar (X% complete)
│   ├─ Bytes Transferred / Total
│   └─ Time Remaining
│
├─ Per-File Progress
│   ├─ File 1: filename.zip
│   │   ├─ Progress Bar (50%)
│   │   ├─ Speed: 5.2 MB/s
│   │   └─ Pause | Cancel
│   ├─ File 2: document.docx
│   │   ├─ Progress Bar (Waiting)
│   │   └─ Cancel
│   └─ File 3: archive.tar.gz
│       ├─ Progress Bar (100%, Verifying CRC)
│       └─ Status: CRC ✓
│
└─ Summary
    ├─ Files Uploaded: 3/3
    ├─ Total Size: 1.2 GB
    └─ Duration: 00:45:30
```

#### 4. Settings Page

**Purpose**: Allow users to configure application settings

**Features**:
- Account settings (username, password)
- Encryption settings (key management)
- Notification preferences
- About section

```
Settings
├─ Account
│   ├─ Username: [Display]
│   ├─ Email: [Display]
│   └─ Change Password [Button]
│
├─ Encryption
│   ├─ Public Key Status: [Display]
│   ├─ Export Key [Button]
│   ├─ Re-generate Keys [Button]
│   └─ Key Algorithm: RSA-1024 [Display]
│
├─ Application
│   ├─ Theme: [Light/Dark]
│   ├─ Language: [English/...]
│   ├─ Auto-upload on change: [Toggle]
│   └─ Verify CRC: [Toggle]
│
├─ Notifications
│   ├─ Email notifications: [Toggle]
│   ├─ Browser notifications: [Toggle]
│   └─ Notify on completion: [Toggle]
│
└─ About
    ├─ Application Version: v1.0.0
    ├─ API Server: [Display]
    ├─ Backup Server: [Display]
    └─ Backend System: [Display]
```

### Reusable UI Components

#### StatusIndicator Component

Displays connection status to server

```
StatusIndicator
├─ Dot (green/red/yellow)
├─ Text ("Connected" / "Disconnecting" / "Offline")
└─ Tooltip (details on hover)
```

#### ProgressBar Component

Displays progress as percentage

```
ProgressBar
├─ Background bar
├─ Filled bar (% width)
├─ Percentage text (center)
└─ Optional: Speed & time remaining below
```

#### FileListTable Component

Displays list of files

```
FileListTable
├─ Column: Filename
├─ Column: Size
├─ Column: Date
├─ Column: Status
└─ Column: Actions (delete/re-upload/download)
```

#### NotificationBanner Component

Displays messages and alerts

```
NotificationBanner
├─ Icon (info/warning/error/success)
├─ Message text
├─ Close button
└─ Auto-dismiss after 5 seconds
```

---

## User Interface Design

### User Workflows

#### Workflow 1: New User Registration

```
1. User visits: https://backup.example.com
   │
2. UI detects no local session
   │
3. Show Registration Form:
   ├─ Username field
   ├─ Confirm Agreement checkbox
   └─ Register button
   │
4. User fills in username: "john_doe"
   │
5. Click Register button
   │
6. Frontend:
   ├─ Call POST /api/v1/auth/register
   ├─ Receive client_id from Flask API
   ├─ Generate RSA-1024 key pair (Web Crypto API)
   ├─ Save client_id and private key to local storage
   ├─ Perform key exchange:
   │   ├─ Call POST /api/v1/keys/public (send public key)
   │   ├─ Receive encrypted AES key
   │   └─ Decrypt with private key
   └─ Display success message
   │
7. Redirect to Dashboard
   │
8. User ready to upload files
```

#### Workflow 2: File Upload

```
1. User on Dashboard, clicks "Upload Files"
   │
2. FileUploader component displays
   │
3. User drags files (or clicks to browse)
   │
4. Files appear in "Selected Files" list
   │
5. User reviews files, clicks "Upload All"
   │
6. For each file:
   ├─ Show in ProgressMonitor (Queued)
   │
7. Frontend downloads file content:
   ├─ Uses File API to read file
   ├─ Shows progress in UI
   │
8. Encrypt file:
   ├─ Generate random IV (initialization vector)
   ├─ Use AES-256-CBC (key from key exchange)
   ├─ Encrypt file content
   ├─ Calculate CRC-32 on ORIGINAL (plaintext) file
   ├─ Append CRC to metadata
   │
9. Encode encrypted file:
   ├─ Base64 encode encrypted bytes
   ├─ Now safe to send in JSON
   │
10. Send to Flask API:
    ├─ Call POST /api/v1/files/upload
    ├─ Include client_id, filename, encrypted_data
    ├─ Update ProgressMonitor with upload speed
    │
11. Flask forwards to Python Server via binary protocol
    │
12. Python Server:
    ├─ Receives encrypted file
    ├─ Stores file to disk
    ├─ Returns ACK (1604)
    │
13. Frontend receives ACK:
    ├─ Update UI to "Uploaded, Verifying CRC"
    │
14. Frontend verifies with CRC:
    ├─ Call POST /api/v1/files/verify (client_crc value)
    │
15. Python Server:
    ├─ Decrypts file with AES key
    ├─ Calculates CRC-32 on decrypted file
    ├─ Compares with client CRC
    ├─ If match: Returns success (1604)
    ├─ If mismatch: Returns failure (1606)
    │
16. Frontend shows:
    ├─ ✓ "File Uploaded Successfully" (if CRC matched)
    └─ ✗ "Upload Failed - CRC Mismatch" (if CRC failed)
```

#### Workflow 3: View Upload History

```
1. User clicks "History" in navigation
   │
2. HistoryPage loads
   │
3. Frontend calls GET /api/v1/status (or custom endpoint)
   │
4. Get list of user's files from server
   │
5. Display in table:
   ├─ Filename
   ├─ Upload Date
   ├─ File Size
   ├─ Verification Status (✓/✗)
   └─ Actions (Download / Re-upload)
   │
6. User can:
   ├─ Sort by column
   ├─ Filter by date range
   ├─ Search by filename
   └─ Delete file (confirm dialog)
```

### Visual Design

#### Color Scheme

```
Primary:      Blue (#007BFF) - Actions, links
Success:      Green (#28A745) - Confirmations, complete
Warning:      Yellow (#FFC107) - Caution, warnings
Error:        Red (#DC3545) - Errors, failed
Neutral:      Gray (#6C757D) - Disabled, secondary
Background:   White/Light Gray - Main surface
```

#### Typography

```
Headings:     Sans-serif, bold, large (24px - 36px)
Body Text:    Sans-serif, regular, medium (14px - 16px)
Labels:       Sans-serif, bold, small (12px - 14px)
Code:         Monospace, small (11px - 13px)
```

#### Responsive Design

```
Desktop (1024px+):
├─ Full sidebar navigation
├─ Multi-column layouts
└─ Expanded details

Tablet (768px - 1023px):
├─ Collapsible sidebar
├─ 2-column layouts
└─ Moderate details

Mobile (< 768px):
├─ Bottom navigation
├─ Single column layouts
├─ Minimal details
└─ Large touch targets (48px min)
```

---

## Integration with Flask API

### API Communication

#### Authentication Flow

```
Browser                        Flask API
  │                              │
  ├─ User enters username        │
  ├─ Click "Register"            │
  ├─ POST /api/v1/auth/register  │
  ├─ {username: "john"}          │
  ├─────────────────────────────>│
  │                              │ Validate input
  │                              │ Call Python Server
  │<───── {client_id, status} ───┤
  │                              │
  ├─ Save client_id locally      │
  ├─ Generate RSA key pair       │
  ├─ POST /api/v1/keys/public    │
  ├─ {client_id, public_key}     │
  ├─────────────────────────────>│
  │                              │ Send to Python Server
  │                              │ Get encrypted AES key
  │<── {encrypted_aes_key} ──────┤
  │                              │
  ├─ Decrypt AES key locally     │
  ├─ Save to local storage       │
  ├─ Redirect to Dashboard       │
  │                              │
```

#### File Upload Flow

```
Browser                        Flask API           Python Server
  │                              │                     │
  ├─ Read file locally           │                     │
  ├─ Encrypt with AES key        │                     │
  ├─ Base64 encode                │                     │
  │                              │                     │
  ├─ POST /api/v1/files/upload   │                     │
  ├─ {encrypted_data, CRC}       │                     │
  ├─────────────────────────────>│ Binary Protocol    │
  │                              ├───────────────────>│
  │                              │                     │ Store file
  │                              │<─────────────────┤
  │<───── {packet_received} ─────┤                     │
  │                              │                     │
  ├─ All packets sent            │                     │
  ├─ POST /api/v1/files/verify   │                     │
  ├─ {client_crc}                │                     │
  ├─────────────────────────────>│ Binary Protocol    │
  │                              ├───────────────────>│
  │                              │                     │ Decrypt
  │                              │                     │ Calculate CRC
  │                              │<─────────────────┤
  │<───── {verified: true} ──────┤                     │
  │                              │                     │
```

### HTTP Headers

```
Request Headers (Browser → Flask):
├─ Content-Type: application/json
├─ Accept: application/json
├─ Authorization: Bearer <session_token> (future)
├─ Origin: https://example.com
└─ User-Agent: Mozilla/5.0...

Response Headers (Flask → Browser):
├─ Content-Type: application/json
├─ Access-Control-Allow-Origin: https://example.com
├─ Access-Control-Allow-Methods: GET, POST, OPTIONS
├─ Access-Control-Allow-Headers: Content-Type, Authorization
├─ Cache-Control: no-cache, no-store, must-revalidate
└─ X-Frame-Options: DENY (security)
```

---

## Client-Side Encryption

### Encryption Process

#### Step 1: Generate RSA Key Pair (On Registration)

```
Browser (Web Crypto API):
    │
    ├─ Generate RSA-1024 key pair
    │   ├─ Public key: 162 bytes (DER format)
    │   └─ Private key: Stored securely in local storage
    │
    ├─ Export public key to DER format
    │
    └─ Send public key to Flask API
        │
        └─ Flask sends to Python Server
            │
            └─ Python Server generates AES key
                └─ Encrypts with public key (RSA-OAEP-SHA256)
                    │
                    └─ Returns encrypted AES key to Flask
                        │
                        └─ Flask sends to Browser
```

#### Step 2: Key Exchange (Get AES Key)

```
Browser:
    │
    ├─ Receive encrypted AES key from Flask API
    │
    ├─ Decrypt with private RSA key (Web Crypto API)
    │
    ├─ Extract AES key (32 bytes for AES-256)
    │
    ├─ Store in memory (not persistent for security)
    │
    └─ Ready for file encryption
```

#### Step 3: File Encryption (For Each Upload)

```
Browser (For each file):
    │
    ├─ Read file content (File API)
    │   └─ Example: 50 MB file
    │
    ├─ Generate random IV (initialization vector)
    │   └─ 16 bytes of cryptographic random data
    │
    ├─ Encrypt file with AES-256-CBC:
    │   ├─ Algorithm: AES (Advanced Encryption Standard)
    │   ├─ Key Size: 256 bits (32 bytes)
    │   ├─ Mode: CBC (Cipher Block Chaining)
    │   ├─ Key: From key exchange
    │   ├─ IV: Randomly generated
    │   ├─ Input: Original file plaintext
    │   └─ Output: Encrypted binary data
    │
    ├─ Add PKCS7 padding (if needed)
    │
    ├─ Result: 50 MB encrypted file
    │
    └─ Store in memory, ready to upload
```

#### Step 4: Calculate CRC-32

```
Browser:
    │
    ├─ Calculate CRC-32 on ORIGINAL plaintext file
    │   ├─ Algorithm: CRC-32 (polynomial 0x04C11DB7)
    │   ├─ Lookup table: 256 entries
    │   ├─ Process: Byte-by-byte through file
    │   ├─ Then: Process file length in bytes
    │   └─ Finally: Invert result (~crc)
    │
    ├─ Result: 32-bit CRC value (4 bytes)
    │   └─ Example: 0x12345678
    │
    └─ Store CRC for later verification
```

#### Step 5: Prepare for Upload

```
Browser:
    │
    ├─ Have:
    │   ├─ Original file (plaintext, 50 MB)
    │   ├─ CRC-32 (4 bytes)
    │   ├─ Encrypted file (50 MB)
    │   └─ IV used for encryption (16 bytes)
    │
    ├─ Base64 encode encrypted file
    │   ├─ Expands size by ~33% (50 MB → 67 MB in JSON)
    │   └─ Safe to send in JSON
    │
    └─ Prepare JSON payload:
        {
          "client_id": "...",
          "filename": "backup.zip",
          "encrypted_data": "base64_encoded_67MB_string",
          "original_size": 50000000,
          "client_crc": "0x12345678"
        }
```

### Encryption Security

```
┌─────────────────────────────────────────────────────┐
│ IMPORTANT: Security Properties                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 1. Key Generation (RSA)                             │
│    ├─ Browser generates unique key pair             │
│    ├─ Private key never leaves browser              │
│    ├─ Public key sent to server                     │
│    └─ Server encrypts AES key with public key       │
│                                                     │
│ 2. Key Exchange (AES)                               │
│    ├─ Server generates random AES key               │
│    ├─ Encrypts with client's public key             │
│    ├─ Client decrypts with private key              │
│    ├─ Only client knows AES key                     │
│    └─ Server never has plaintext AES key            │
│                                                     │
│ 3. File Encryption (AES-256-CBC)                    │
│    ├─ Browser encrypts file locally                 │
│    ├─ Server never sees plaintext file              │
│    ├─ Only encrypted bytes transmitted              │
│    ├─ Random IV for each file                       │
│    └─ Server stores encrypted file only             │
│                                                     │
│ 4. Verification (CRC-32)                            │
│    ├─ Client calculates CRC on plaintext            │
│    ├─ Server decrypts and calculates CRC            │
│    ├─ Both compare values                           │
│    ├─ Proves transfer integrity                     │
│    └─ Proves server has correct key                 │
│                                                     │
│ Result: Zero-knowledge encryption                   │
│ - Server stores encrypted files                     │
│ - Server cannot read file contents                  │
│ - Only client can decrypt files                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Data Flow

### Complete Request/Response Flow

#### Registration Request

```
User Input (Browser)
    │
    └─> {username: "john_doe"}
        │
        ├─ Validation
        │   └─ Check: not empty, < 255 chars
        │
        └─ HTTP POST /api/v1/auth/register
            {
              "username": "john_doe",
              "client_type": "web_client"
            }
            │
            ▼ (HTTPS, JSON)
        Flask API Server
            │
            ├─ Validate input
            ├─ Generate UUID
            ├─ Create binary protocol request
            └─ Send to Python Server
                │
                ▼ (Binary TCP)
            Python Server
                │
                ├─ Parse binary protocol
                ├─ Extract username
                ├─ Store client in database
                ├─ Create response (1600)
                └─ Send back via TCP
                │
                ▼
            Flask API Server
                │
                ├─ Parse response
                ├─ Build JSON response
                └─ Send to Browser
                    {
                      "status": "success",
                      "data": {
                        "client_id": "550e...",
                        "username": "john_doe"
                      }
                    }
                    │
                    ▼
        Browser JavaScript
            │
            ├─ Receive response
            ├─ Extract client_id
            ├─ Save client_id to localStorage
            ├─ Generate RSA key pair
            └─ Show success message to user
```

### State Management (Redux/Vuex)

```
Browser Application State:

{
  user: {
    username: "john_doe",
    client_id: "550e8400-...",
    session_token: "abc123...",
    is_authenticated: true
  },
  encryption: {
    private_key: <PrivateKey object>,
    public_key: <PublicKey object>,
    aes_key: <AES key bytes>,
    has_key_pair: true
  },
  uploads: {
    current_upload: {
      files: [
        {
          name: "backup.zip",
          size: 1048576,
          progress: 75,
          status: "uploading",
          crc: null
        }
      ],
      total_progress: 75,
      total_speed: "5.2 MB/s"
    },
    history: [
      {
        name: "archive.tar.gz",
        date: "2025-11-11T12:34:56Z",
        size: 2097152,
        verified: true
      }
    ]
  },
  ui: {
    current_page: "upload",
    notifications: [
      {
        id: 1,
        type: "success",
        message: "File uploaded successfully",
        timeout: 5000
      }
    ],
    theme: "light"
  },
  api: {
    server_url: "https://api.backup.example.com",
    connected: true,
    last_sync: "2025-11-11T12:34:56Z"
  }
}
```

---

## Authentication & Sessions

### Session Management

#### Initial Login (First Visit)

```
1. User visits: https://backup.example.com
   │
2. Browser checks localStorage for:
   ├─ client_id
   ├─ session_token
   └─ private_key
   │
3. If not found → Show Registration Form
4. User enters username → Register
   │
5. Browser:
   ├─ Calls POST /api/v1/auth/register
   ├─ Receives client_id
   ├─ Generates RSA key pair
   ├─ Calls POST /api/v1/keys/public (exchange keys)
   ├─ Receives encrypted AES key
   ├─ Decrypts AES key with private RSA key
   │
6. Save to localStorage:
   {
     "client_id": "550e8400-...",
     "private_key": "exported PEM format",
     "aes_key": "base64 encoded",
     "username": "john_doe"
   }
   │
7. Redirect to Dashboard
   │
8. User is logged in (session persists)
```

#### Subsequent Visits

```
1. User visits: https://backup.example.com
   │
2. Browser checks localStorage
   │
3. If client_id exists:
   ├─ Load client_id from localStorage
   ├─ Load private_key from localStorage
   ├─ Load aes_key from localStorage
   │
4. Verify session:
   ├─ Call POST /api/v1/auth/validate
   ├─ Send client_id
   │
5. Server responds: {valid: true}
   │
6. User is authenticated → Show Dashboard
```

#### Session Expiration

```
1. User's session expires (server-side timeout)
   │
2. User tries to upload file
   │
3. Frontend receives: {valid: false}
   │
4. App logic:
   ├─ Clear localStorage
   ├─ Redirect to login/register
   └─ Show message: "Session expired, please re-register"
```

### Local Storage Structure

```
localStorage {
  // User Information
  "backup_user_client_id": "550e8400-e29b-41d4-a716-446655440000",
  "backup_user_username": "john_doe",

  // Encryption Keys
  "backup_user_private_key": "-----BEGIN RSA PRIVATE KEY-----\n...",
  "backup_user_aes_key": "base64_encoded_aes_key_32_bytes",

  // Session
  "backup_session_token": "550e8400-e29b-41d4-a716-446655440001",
  "backup_session_expires": "1699771200000",  // timestamp

  // Preferences
  "backup_theme": "light",
  "backup_language": "en",
  "backup_auto_verify_crc": true,

  // App State
  "backup_api_url": "https://api.backup.example.com",
  "backup_last_login": "2025-11-11T12:34:56Z"
}
```

---

## Security Considerations

### Frontend Security

1. **XSS (Cross-Site Scripting) Prevention**
   - Use React/Vue which auto-escapes content
   - Never use `innerHTML` with user input
   - Validate and sanitize all inputs
   - Content Security Policy headers

2. **CSRF (Cross-Site Request Forgery) Prevention**
   - Use HTTPS only
   - Include CSRF tokens in requests
   - SameSite cookie attribute

3. **Secure Key Storage**
   - Private key stored in localStorage (not ideal)
   - Future: Use IndexedDB with encryption
   - Never send private key to server
   - Never expose in network requests

4. **HTTPS/TLS**
   - All communication must be HTTPS
   - Valid SSL certificates
   - HSTS headers

### Data Security

1. **Client-Side Encryption**
   - Files encrypted BEFORE upload
   - Server never sees plaintext
   - Uses Web Crypto API (browser native)

2. **CRC Verification**
   - Ensures file integrity
   - Detects transmission errors
   - Can detect some types of tampering

3. **No Sensitive Data in URLs**
   - Never put keys/tokens in query strings
   - Use HTTP POST body for sensitive data
   - Use HTTPS headers for authentication

### Best Practices

```
✅ DO:
├─ Use HTTPS for all connections
├─ Encrypt files before upload
├─ Validate all user inputs
├─ Use strong Content Security Policy
├─ Hash passwords server-side
├─ Log security events
├─ Update dependencies regularly
├─ Use secure random generators
└─ Implement rate limiting

❌ DON'T:
├─ Store secrets in code
├─ Use HTTP (unencrypted)
├─ Trust client-side validation alone
├─ Store plaintext private keys
├─ Hardcode API credentials
├─ Expose error details to users
├─ Use weak encryption
├─ Skip HTTPS in production
├─ Trust localStorage security
└─ Ignore OWASP recommendations
```

---

## Deployment & Hosting

### Build & Bundling

```
Development:
    npm run dev
    ├─ Hot module reloading
    ├─ Source maps for debugging
    └─ Runs on localhost:3000 (dev server)

Production Build:
    npm run build
    ├─ Minification & compression
    ├─ Code splitting
    ├─ Asset optimization
    ├─ Source maps (optional)
    └─ Output: /dist folder

Bundle Output:
    dist/
    ├─ index.html              (1 file)
    ├─ js/
    │   ├─ main-[hash].js      (bundled code)
    │   ├─ vendor-[hash].js    (dependencies)
    │   └─ runtime-[hash].js   (webpack runtime)
    ├─ css/
    │   └─ main-[hash].css     (bundled styles)
    └─ assets/
        ├─ logo.png
        └─ favicon.ico
```

### Hosting Options

#### Option 1: Static Hosting (Simple)

```
Provider: Netlify, Vercel, GitHub Pages

Process:
    ├─ npm run build
    ├─ Upload /dist folder
    ├─ Configure DNS
    ├─ Enable HTTPS
    └─ Auto-deploy on git push

Limitations:
    └─ Frontend must be on same domain as Flask API
        (or use CORS carefully)
```

#### Option 2: Nginx Server

```
Configuration:
    /etc/nginx/sites-available/backup.conf

    server {
      listen 443 ssl http2;
      server_name backup.example.com;

      # SSL certificates
      ssl_certificate /path/to/cert.pem;
      ssl_certificate_key /path/to/key.pem;

      # Serve frontend
      location / {
        root /var/www/backup-gui/dist;
        try_files $uri $uri/ /index.html;  # SPA routing
        expires 1h;  # Cache static assets
      }

      # Proxy API requests to Flask
      location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
      }
    }
```

#### Option 3: Docker Container

```
Dockerfile:
    FROM node:18 AS build
    WORKDIR /app
    COPY package*.json ./
    RUN npm install
    COPY . .
    RUN npm run build

    FROM nginx:latest
    COPY --from=build /app/dist /usr/share/nginx/html
    COPY nginx.conf /etc/nginx/nginx.conf
    EXPOSE 443
    CMD ["nginx", "-g", "daemon off;"]

Build & Run:
    docker build -t backup-gui:latest .
    docker run -d -p 443:443 backup-gui:latest
```

### Environment Configuration

```
.env.production:
    REACT_APP_API_URL=https://api.backup.example.com
    REACT_APP_VERSION=1.0.0
    REACT_APP_LOG_LEVEL=warn
    REACT_APP_MAX_FILE_SIZE=1000000000  # 1 GB

.env.development:
    REACT_APP_API_URL=http://localhost:5000
    REACT_APP_VERSION=1.0.0-dev
    REACT_APP_LOG_LEVEL=debug
    REACT_APP_MAX_FILE_SIZE=1000000000
```

### Performance Optimization

```
1. Code Splitting
   ├─ Lazy load components
   ├─ Separate vendor bundle
   └─ Dynamic imports

2. Asset Optimization
   ├─ Compress images
   ├─ Minify CSS/JS
   ├─ Gzip compression
   └─ Cache busting with hashes

3. Browser Caching
   ├─ Cache static assets (1 year)
   ├─ Don't cache index.html (no-cache)
   ├─ Use CDN for assets
   └─ Service Worker for offline support

4. Network Optimization
   ├─ Compress responses (gzip)
   ├─ HTTP/2 push
   ├─ Prefetch DNS
   └─ Lazy load images
```

---

## Summary

The Web-Based Client GUI provides a modern, user-friendly browser-based interface for file backup. It features:

✅ **Cross-Platform**: Works on any browser (Windows, Mac, Linux, iOS, Android)
✅ **No Installation**: Instant access from web browser
✅ **Modern UI**: Intuitive drag-and-drop interface
✅ **Client-Side Encryption**: Files encrypted before upload
✅ **Real-Time Feedback**: Progress bars and status updates
✅ **Secure**: HTTPS, Web Crypto API, CRC verification
✅ **Responsive**: Works on desktop, tablet, and mobile

The GUI integrates seamlessly with the Flask API Server, which translates HTTP requests to the binary TCP protocol used by the core backup system, maintaining end-to-end encryption and security throughout the entire process.

**Next Phase**: Flet Desktop GUI will provide a native desktop application alternative to the web interface, offering similar functionality with deeper OS integration.
