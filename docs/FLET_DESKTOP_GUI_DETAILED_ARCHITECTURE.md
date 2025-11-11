# Flet Desktop GUI (0.28.3) - Detailed Architecture & Design

**Status**: Documentation for Proposed Implementation
**Target Framework**: Flet 0.28.3
**Purpose**: Native desktop application for server monitoring and administration
**Date**: 2025-11-11
**Replaces**: Current Tkinter-based ServerGUI.py

---

## Executive Overview

### Purpose

The Flet Desktop GUI is a **native desktop application** for monitoring and administering the encrypted backup server. It replaces the current Tkinter-based GUI with a modern, cross-platform desktop application built with Flet.

### Current System (Tkinter)

```
Current ServerGUI.py (Tkinter):
    ├─ Platform: Cross-platform (Python + Tk)
    ├─ Performance: Moderate
    ├─ Visual: Basic, dated appearance
    ├─ Features: Simple monitoring
    ├─ Dependencies: tkinter (standard library)
    └─ Limitations: Limited customization, dated look
```

### Enhanced System (Flet 0.28.3)

```
New ServerGUI (Flet):
    ├─ Platform: Native desktop (Windows, Mac, Linux)
    ├─ Performance: Fast, responsive
    ├─ Visual: Modern Material Design
    ├─ Features: Rich monitoring dashboard
    ├─ Dependencies: flet==0.28.3
    ├─ Benefits: Modern UI, better UX, cross-platform
    └─ Integration: Runs alongside main server.py
```

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                  FLET DESKTOP APPLICATION                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          USER INTERFACE (Material Design)             │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │ Header/Navigation Bar                        │    │  │
│  │  │ ├─ Application Title                         │    │  │
│  │  │ ├─ Theme Toggle (Light/Dark)                 │    │  │
│  │  │ └─ Settings/About Menu                       │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │ Left Navigation Rail                         │    │  │
│  │  │ ├─ Dashboard (Home Icon)                     │    │  │
│  │  │ ├─ Clients (People Icon)                     │    │  │
│  │  │ ├─ Transfers (Upload Icon)                   │    │  │
│  │  │ ├─ Database (Database Icon)                  │    │  │
│  │  │ ├─ Logs (Logs Icon)                          │    │  │
│  │  │ └─ Settings (Gear Icon)                      │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │ Main Content Area (Pages)                    │    │  │
│  │  │                                              │    │  │
│  │  │ ┌─ Dashboard Page                           │    │  │
│  │  │ │  ├─ Server Status Card                    │    │  │
│  │  │ │  ├─ Client Statistics                     │    │  │
│  │  │ │  ├─ Active Transfers Chart                │    │  │
│  │  │ │  ├─ Recent Activity Log                   │    │  │
│  │  │ │  └─ Quick Stats (Total Files, Size)       │    │  │
│  │  │ │                                           │    │  │
│  │  │ ├─ Clients Page                            │    │  │
│  │  │ │  ├─ Clients Table/List                   │    │  │
│  │  │ │  ├─ Client Details View                  │    │  │
│  │  │ │  └─ Action Buttons (Remove, Ban, etc)    │    │  │
│  │  │ │                                           │    │  │
│  │  │ ├─ Transfers Page                          │    │  │
│  │  │ │  ├─ Active Transfers List                │    │  │
│  │  │ │  ├─ Transfer Progress Bars               │    │  │
│  │  │ │  ├─ Speed/Time Remaining                 │    │  │
│  │  │ │  └─ Pause/Cancel Buttons                 │    │  │
│  │  │ │                                           │    │  │
│  │  │ ├─ Database Page                           │    │  │
│  │  │ │  ├─ DB Statistics                        │    │  │
│  │  │ │  ├─ Table Size Info                      │    │  │
│  │  │ │  ├─ Backup/Restore Controls              │    │  │
│  │  │ │  └─ Cleanup Utilities                    │    │  │
│  │  │ │                                           │    │  │
│  │  │ ├─ Logs Page                               │    │  │
│  │  │ │  ├─ Real-time Log Viewer                 │    │  │
│  │  │ │  ├─ Filter/Search Controls               │    │  │
│  │  │ │  └─ Export Logs Button                   │    │  │
│  │  │ │                                           │    │  │
│  │  │ └─ Settings Page                           │    │  │
│  │  │    ├─ Server Configuration                 │    │  │
│  │  │    ├─ Network Settings                     │    │  │
│  │  │    ├─ Database Settings                    │    │  │
│  │  │    ├─ Notification Preferences             │    │  │
│  │  │    └─ About/Version Info                   │    │  │
│  │  │                                              │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │ Footer/Status Bar                           │    │  │
│  │  │ ├─ Server Status: Running/Stopped           │    │  │
│  │  │ ├─ Connection: Connected/Disconnected       │    │  │
│  │  │ ├─ Last Update: timestamp                   │    │  │
│  │  │ └─ Messages: Current operation status       │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  │                                                        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │        BACKGROUND SERVICES (Threading)               │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │                                                        │  │
│  │  ├─ Server Monitor Thread                            │  │
│  │  │   └─ Connects to localhost:1256 (Python Server)   │  │
│  │  │   └─ Reads server statistics every 1 second       │  │
│  │  │   └─ Updates UI with latest data                  │  │
│  │  │                                                    │  │
│  │  ├─ Database Query Thread                            │  │
│  │  │   └─ Queries SQLite database                      │  │
│  │  │   └─ Updates client/file statistics               │  │
│  │  │                                                    │  │
│  │  ├─ Log Watcher Thread                               │  │
│  │  │   └─ Reads server log files                       │  │
│  │  │   └─ Updates log display in real-time             │  │
│  │  │                                                    │  │
│  │  └─ Notification Engine Thread                       │  │
│  │      └─ Sends desktop notifications                  │  │
│  │      └─ Alerts on important events                   │  │
│  │                                                        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└──────────────────────────────────────────────────────────────┘

         ▼ (Local TCP Connection)

┌──────────────────────────────────────────────────────────────┐
│         PYTHON ENCRYPTED BACKUP SERVER                       │
│                                                               │
│  ├─ Port: 1256 (TCP Socket Server)                           │
│  ├─ Database: SQLite (defensive.db)                          │
│  ├─ Storage: Encrypted files (received_files/)               │
│  └─ Clients: Connected C++ clients (+ Flask API)             │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
server_gui_flet/
│
├── main.py                       # Application entry point
│
├── config.py                     # Configuration management
│   └─ Server address, theme settings, preferences
│
├── pages/                        # Page/Screen components
│   ├── __init__.py
│   ├── dashboard_page.py         # Dashboard page
│   ├── clients_page.py           # Clients management page
│   ├── transfers_page.py         # Transfer monitoring page
│   ├── database_page.py          # Database management page
│   ├── logs_page.py              # Log viewer page
│   └── settings_page.py          # Settings page
│
├── components/                   # Reusable UI components
│   ├── __init__.py
│   ├── header.py                 # Top navigation bar
│   ├── nav_rail.py               # Left navigation rail
│   ├── status_card.py            # Status display card
│   ├── client_table.py           # Clients list table
│   ├── transfer_progress.py       # Transfer progress widget
│   ├── chart.py                  # Charts and graphs
│   └── dialogs.py                # Dialog/modal components
│
├── services/                     # Business logic
│   ├── __init__.py
│   ├── server_api.py             # Python server communication
│   ├── database.py               # SQLite database access
│   ├── log_reader.py             # Log file reading
│   └── notifications.py          # Desktop notifications
│
├── models/                       # Data models
│   ├── __init__.py
│   ├── client_model.py           # Client data structure
│   ├── transfer_model.py         # Transfer data structure
│   └── server_status_model.py   # Server status model
│
├── utils/                        # Utility functions
│   ├── __init__.py
│   ├── formatters.py             # Data formatting helpers
│   ├── validators.py             # Input validation
│   └── constants.py              # Application constants
│
├── assets/                       # Application resources
│   ├── icons/                    # Icon files
│   ├── images/                   # Image files
│   └── themes/                   # Color themes
│
├── requirements.txt              # Python dependencies
│   └─ flet==0.28.3
│   └─ sqlite3
│   └─ And others...
│
├── .env                          # Environment variables
├── README.md                     # Documentation
└── setup.py                      # Installation script
```

---

## Pages & Components

### 1. Dashboard Page

**Purpose**: Overview of system status and recent activity

**Key Elements**:
```
┌──────────────────────────────────────┐
│ DASHBOARD                            │
├──────────────────────────────────────┤
│                                      │
│ Server Status                        │
│ ┌─────────────────────────────────┐ │
│ │ Status: ● Running               │ │
│ │ Uptime: 7 days, 3 hours         │ │
│ │ Port: 1256                      │ │
│ │ Database: Connected             │ │
│ └─────────────────────────────────┘ │
│                                      │
│ Statistics  (4-column grid)          │
│ ┌─────────────┐ ┌─────────────────┐ │
│ │ Total Clients│ │ Connected       │ │
│ │      12     │ │      3          │ │
│ └─────────────┘ └─────────────────┘ │
│ ┌─────────────┐ ┌─────────────────┐ │
│ │ Total Files │ │ Total Size      │ │
│ │    456      │ │    1.2 TB       │ │
│ └─────────────┘ └─────────────────┘ │
│                                      │
│ Active Transfers (Last 6 hours)      │
│ ┌─────────────────────────────────┐ │
│ │ [Line Chart]                    │ │
│ │ Files transferred over time     │ │
│ └─────────────────────────────────┘ │
│                                      │
│ Recent Activity                      │
│ ┌─────────────────────────────────┐ │
│ │ 12:34 - client_1 registered     │ │
│ │ 12:30 - client_2 uploaded file  │ │
│ │ 12:25 - crc_verify success      │ │
│ │ 12:20 - client_3 connected      │ │
│ │ 12:15 - database backup started │ │
│ └─────────────────────────────────┘ │
│                                      │
└──────────────────────────────────────┘
```

### 2. Clients Page

**Purpose**: View and manage connected clients

**Key Elements**:
```
┌──────────────────────────────────────┐
│ CLIENTS                              │
├──────────────────────────────────────┤
│ [Add Client] [Refresh]               │
│                                      │
│ Client List (Sortable Table)         │
│ ┌────────────────────────────────┐   │
│ │ Name      │ Status  │ Files │ │ │   │
│ ├────────────────────────────────┤   │
│ │ client_1  │ ● Online│  45  │ │ │   │
│ │ client_2  │ ● Online│  32  │ │ │   │
│ │ client_3  │ ○ Offline │ 28 │ │ │   │
│ │ client_4  │ ● Online│  51  │ │ │   │
│ └────────────────────────────────┘   │
│                                      │
│ Client Details (Below or Side Panel) │
│ ┌────────────────────────────────┐   │
│ │ Client: client_1               │   │
│ │ Status: Online                 │   │
│ │ Last Seen: 2 mins ago          │   │
│ │ IP Address: 192.168.1.100      │   │
│ │ Files: 45                      │   │
│ │ Total Size: 500 MB             │   │
│ │ Last Upload: 1 hour ago        │   │
│ │ [Remove] [Ban] [Export Key]    │   │
│ └────────────────────────────────┘   │
│                                      │
└──────────────────────────────────────┘
```

### 3. Transfers Page

**Purpose**: Monitor active and historical file transfers

**Key Elements**:
```
┌──────────────────────────────────────┐
│ TRANSFERS                            │
├──────────────────────────────────────┤
│ [Clear History]                      │
│                                      │
│ Active Transfers                     │
│ ┌────────────────────────────────┐   │
│ │ client_2 → backup.zip          │   │
│ │ ████████░░ 85% - 2.1 MB/s     │   │
│ │ ETA: 30 seconds                │   │
│ │ [Pause] [Cancel]               │   │
│ │                                │   │
│ │ client_1 → archive.tar         │   │
│ │ █████░░░░░░ 52% - 1.8 MB/s    │   │
│ │ ETA: 1 minute 15 seconds       │   │
│ │ [Pause] [Cancel]               │   │
│ └────────────────────────────────┘   │
│                                      │
│ Transfer History (Last 24 hours)     │
│ ┌────────────────────────────────┐   │
│ │ Time     │ Client │ File │ Size│   │
│ ├────────────────────────────────┤   │
│ │ 12:45    │ cl_2   │ backup   │   │
│ │ 12:30    │ cl_1   │ archive  │   │
│ │ 12:10    │ cl_3   │ data.zip │   │
│ │ 11:55    │ cl_2   │ backup   │   │
│ └────────────────────────────────┘   │
│                                      │
└──────────────────────────────────────┘
```

### 4. Database Page

**Purpose**: View database statistics and perform maintenance

**Key Elements**:
```
┌──────────────────────────────────────┐
│ DATABASE                             │
├──────────────────────────────────────┤
│                                      │
│ Database: defensive.db               │
│ ┌────────────────────────────────┐   │
│ │ Total Size: 512 MB             │   │
│ │ Last Backup: 2025-11-11 10:00 │   │
│ │ Status: Healthy                │   │
│ └────────────────────────────────┘   │
│                                      │
│ Tables Statistics                    │
│ ┌────────────────────────────────┐   │
│ │ Table    │ Rows │ Size       │   │
│ ├────────────────────────────────┤   │
│ │ clients  │ 12   │ 2 MB       │   │
│ │ files    │ 456  │ 510 MB     │   │
│ └────────────────────────────────┘   │
│                                      │
│ Maintenance                          │
│ ┌────────────────────────────────┐   │
│ │ [Backup Database] [Auto 0:00]  │   │
│ │ [Vacuum DB] [Clean Old Logs]   │   │
│ │ [Repair DB] [Export Data]      │   │
│ └────────────────────────────────┘   │
│                                      │
│ Recent Operations                    │
│ ┌────────────────────────────────┐   │
│ │ 12:00 - Vacuum DB              │   │
│ │ 11:00 - Database backup        │   │
│ │ 10:00 - Index rebuild          │   │
│ └────────────────────────────────┘   │
│                                      │
└──────────────────────────────────────┘
```

### 5. Logs Page

**Purpose**: View and search server logs in real-time

**Key Elements**:
```
┌──────────────────────────────────────┐
│ LOGS                                 │
├──────────────────────────────────────┤
│ [Filter] [Level: ▼] [Search] [Export]│
│                                      │
│ Real-Time Log Viewer                 │
│ ┌────────────────────────────────┐   │
│ │ 2025-11-11 12:45:30 [INFO]     │   │
│ │   client_1 registered          │   │
│ │                                │   │
│ │ 2025-11-11 12:40:15 [INFO]     │   │
│ │   File transfer completed      │   │
│ │   Client: client_2             │   │
│ │   File: backup.zip             │   │
│ │   Size: 100 MB                 │   │
│ │   Duration: 45 seconds         │   │
│ │                                │   │
│ │ 2025-11-11 12:35:00 [WARNING]  │   │
│ │   High memory usage detected   │   │
│ │   Memory: 85% of available     │   │
│ │                                │   │
│ │ 2025-11-11 12:30:45 [ERROR]    │   │
│ │   Connection timeout           │   │
│ │   Client: client_3             │   │
│ │   Attempting reconnect...      │   │
│ │                                │   │
│ │ [Auto-scroll] [Pause] [Clear]  │   │
│ └────────────────────────────────┘   │
│                                      │
└──────────────────────────────────────┘
```

### 6. Settings Page

**Purpose**: Configure application and server settings

**Key Elements**:
```
┌──────────────────────────────────────┐
│ SETTINGS                             │
├──────────────────────────────────────┤
│                                      │
│ Application Settings                 │
│ ┌────────────────────────────────┐   │
│ │ Theme: [● Light / ○ Dark]      │   │
│ │ Language: [English ▼]          │   │
│ │ Auto-refresh: ○ 1s  ● 2s ○ 5s │   │
│ │ Startup: [✓] Run at login      │   │
│ │ Notifications: [✓] Enabled     │   │
│ │ Sound: [✓] Enabled             │   │
│ └────────────────────────────────┘   │
│                                      │
│ Server Connection                    │
│ ┌────────────────────────────────┐   │
│ │ Host: [localhost______]        │   │
│ │ Port: [1256__________]         │   │
│ │ Timeout: [30________] seconds  │   │
│ │ [Test Connection]              │   │
│ └────────────────────────────────┘   │
│                                      │
│ Data & Privacy                       │
│ ┌────────────────────────────────┐   │
│ │ [Clear Cache] [Clear Logs]     │   │
│ │ [Export Settings] [Reset to    │   │
│ │  Default]                      │   │
│ └────────────────────────────────┘   │
│                                      │
│ About                                │
│ ┌────────────────────────────────┐   │
│ │ Flet Server GUI v1.0.0         │   │
│ │ Based on Flet 0.28.3           │   │
│ │ (c) 2025 Encrypted Backup Sys  │   │
│ │ [Check for Updates]            │   │
│ │ [View Changelog]               │   │
│ └────────────────────────────────┘   │
│                                      │
│ [Save Settings] [Cancel]             │
│                                      │
└──────────────────────────────────────┘
```

---

## How It Works

### Threading Model

Flet runs the UI in the main thread. All background work (server communication, database queries, log reading) happens in separate threads to keep UI responsive:

```
Main Thread (Flet UI):
    ├─ Renders UI components
    ├─ Handles user interactions
    ├─ Updates displayed data
    └─ Runs continuously

Background Threads:
    ├─ Server Monitor Thread (updates every 1 second)
    │   ├─ Query Python server for status
    │   ├─ Get connected clients
    │   ├─ Get active transfers
    │   ├─ Get recent activity
    │   └─ Queue updates for UI
    │
    ├─ Database Query Thread
    │   ├─ Query SQLite database
    │   ├─ Get client statistics
    │   ├─ Get file statistics
    │   └─ Queue updates for UI
    │
    ├─ Log Reader Thread
    │   ├─ Read server log files
    │   ├─ Parse new log entries
    │   ├─ Apply filters/search
    │   └─ Queue updates for UI
    │
    └─ Notification Thread
        ├─ Monitor for important events
        ├─ Show desktop notifications
        ├─ Play notification sounds
        └─ Log notification events

Communication:
    Background Threads ──(Queue)──> Main Thread ──(Update UI)──> User
```

### Real-Time Update Flow

```
1. Server Monitor Thread (every 1 second):
   │
   ├─ Try to connect to Python server (localhost:1256)
   │
   ├─ If connected:
   │   ├─ Send query request: "GET /status"
   │   │   (or custom protocol request)
   │   │
   │   ├─ Receive response:
   │   │   {
   │   │     "server_running": true,
   │   │     "clients_connected": 3,
   │   │     "total_files": 456,
   │   │     "total_size": 1200000000,
   │   │     "uptime": 604800,
   │   │     "recent_activity": [...]
   │   │   }
   │   │
   │   └─ Put data in update queue
   │
   ├─ If not connected:
   │   ├─ Show "Server Offline" warning
   │   └─ Retry connection in 5 seconds
   │
   └─ Sleep for 1 second, repeat

2. Main Thread (continuously):
   │
   ├─ Check update queue for new data
   │
   ├─ If data received:
   │   ├─ Update page.status = data
   │   ├─ Refresh UI components
   │   │   ├─ Update status cards
   │   │   ├─ Refresh charts
   │   │   ├─ Update client list
   │   │   └─ Refresh statistics
   │   │
   │   └─ User sees live updates
   │
   └─ Continue rendering frame
```

### User Interaction Flow

```
1. User clicks "Clients" in navigation rail
   │
   ├─ Navigation event → main.py
   │
   ├─ Switch to clients_page
   │
   ├─ Clients page onload event:
   │   ├─ Start loading spinner
   │   ├─ Query database for clients
   │   ├─ Populate clients table
   │   └─ Stop loading spinner
   │
   └─ User sees clients list

2. User clicks client row
   │
   ├─ Selection event → clients_page.py
   │
   ├─ Get client_id from selected row
   │
   ├─ Query database for client details:
   │   {
   │     "id": "550e8400-...",
   │     "name": "client_1",
   │     "status": "online",
   │     "files": 45,
   │     "total_size": 500000000,
   │     "last_seen": "2025-11-11T12:34:56Z"
   │   }
   │
   ├─ Show details panel:
   │   ├─ Client name
   │   ├─ Status with indicator
   │   ├─ Files count
   │   ├─ Last seen time
   │   └─ Action buttons
   │
   └─ User sees details

3. User clicks "Remove Client" button
   │
   ├─ Click event → on_remove_click()
   │
   ├─ Show confirmation dialog:
   │   "Are you sure? This will remove all associated files."
   │
   ├─ If user confirms:
   │   ├─ Call database.delete_client(client_id)
   │   ├─ Show success message
   │   ├─ Refresh clients list
   │   └─ Log action to server logs
   │
   └─ User sees updated list
```

---

## Integration with Python Server

### Communication Protocol

The Flet GUI communicates with the Python server via:

```
Method 1: HTTP Requests (Recommended for Future)
    ├─ Server exposes HTTP endpoints
    ├─ GUI sends HTTP requests
    └─ Easy to test and debug

Method 2: Direct TCP Protocol (Current)
    ├─ Implement custom TCP client
    ├─ Send binary protocol requests
    ├─ Parse binary protocol responses
    └─ More complex but zero overhead

Method 3: SQLite Database Direct Access
    ├─ GUI connects directly to SQLite
    ├─ Read-only or read-write
    ├─ Fast local access
    └─ For statistics and monitoring
```

### Data Access Patterns

```
Real-Time Status:
    Flet GUI ──(TCP/HTTP query)──> Python Server
                                     │
                                     ├─ Get current stats
                                     ├─ Get connected clients
                                     ├─ Get active transfers
                                     │
    Flet GUI <─(status response)───┘

Historical Data:
    Flet GUI ──(direct access)──> SQLite Database
                                     │
                                     ├─ clients table
                                     ├─ files table
                                     │
    Flet GUI <─(query result)───────┘

Activity/Logs:
    Flet GUI ──(file read)──> Server log files
                                 │
                                 ├─ server.log
                                 ├─ error.log
                                 │
    Flet GUI <─(log content)────┘
```

---

## Key Features

### 1. Real-Time Monitoring

```
✓ Live client connection status
✓ Active transfer progress bars
✓ Server resource usage (CPU, Memory)
✓ Database size and growth
✓ Real-time activity log
✓ Error and warning alerts
```

### 2. Client Management

```
✓ View all registered clients
✓ See client connection status
✓ View client file count and size
✓ Remove or ban clients
✓ Export client public keys
✓ Search and filter clients
```

### 3. Transfer Monitoring

```
✓ View active transfers in progress
✓ See transfer speed and ETA
✓ Pause/resume transfers
✓ Cancel transfers
✓ View transfer history
✓ Statistics on successful/failed transfers
```

### 4. Database Management

```
✓ View database statistics
✓ Manual backup/restore
✓ Database optimization (VACUUM)
✓ Cleanup old logs
✓ Database repair utilities
✓ Export database data
```

### 5. Logging & Diagnostics

```
✓ Real-time log viewer
✓ Filter by log level (INFO, WARNING, ERROR)
✓ Search logs by keywords
✓ Export logs to file
✓ Clear old logs
✓ Colorized output
```

### 6. Notifications

```
✓ Desktop notifications for events
✓ Sound alerts for important events
✓ Notification preferences
✓ Do Not Disturb mode
✓ Event history log
```

---

## Styling & Theming

### Material Design Integration

Flet 0.28.3 uses Material Design 3 natively:

```
Color Scheme:
    Primary:    Blue (#007BFF)
    Secondary:  Indigo (#6C63FF)
    Tertiary:   Purple (#A855F7)
    Error:      Red (#DC3545)
    Neutral:    Gray (#6C757D)
    Success:    Green (#28A745)
    Warning:    Amber (#FFC107)

Typography:
    Display:    Large headings
    Headline:   Page titles
    Title:      Section titles
    Body:       Regular text
    Label:      UI labels
    Code:       Monospace text

Spacing:
    Small:      4px
    Medium:     8px
    Large:      16px
    XLarge:     24px
    XXLarge:    32px

Components:
    Cards:      Rounded corners, shadow
    Buttons:    Filled, outlined, text variants
    Text Fields: With icons and error states
    Tables:     Sortable columns, selection
    Charts:     Line, bar, pie charts
```

### Dark Mode Support

```
Light Theme (Default):
    ├─ White background
    ├─ Dark text
    ├─ Bright colors
    └─ High contrast

Dark Theme (Optional):
    ├─ Dark background (#121212)
    ├─ Light text
    ├─ Muted colors
    └─ Reduced eye strain

User Can Toggle:
    ├─ Settings page
    ├─ Save preference
    ├─ Apply on startup
    └─ Smooth transition
```

---

## Deployment & Distribution

### Package as Standalone Application

```
Windows:
    ├─ py2exe / PyInstaller
    ├─ Create .exe installer
    ├─ Sign executable
    └─ Distribute via website

macOS:
    ├─ py2app / PyInstaller
    ├─ Create .dmg package
    ├─ Sign with Apple certificate
    └─ Submit to App Store (optional)

Linux:
    ├─ PyInstaller
    ├─ Create .AppImage or .deb
    ├─ Distribute via package manager
    └─ Support for popular distros
```

### Installation Methods

```
Method 1: Standalone Executable
    Download: backup-gui-1.0.0.exe
    Run: Double-click to install
    Launch: Desktop shortcut or Start menu

Method 2: Python Package
    pip install backup-gui
    backup-gui  (command line)

Method 3: Package Manager
    Ubuntu:   sudo apt install backup-gui
    Fedora:   sudo dnf install backup-gui
    MacOS:    brew install backup-gui
```

### System Requirements

```
Windows:
    ├─ Windows 7 or later
    ├─ 50 MB disk space
    ├─ .NET Runtime (included in installer)
    └─ No additional dependencies

macOS:
    ├─ macOS 10.13 or later
    ├─ 50 MB disk space
    ├─ Intel or Apple Silicon
    └─ No additional dependencies

Linux:
    ├─ Python 3.8 or later
    ├─ GTK library (usually pre-installed)
    ├─ 50 MB disk space
    └─ Installed via: pip or package manager
```

---

## Summary

The Flet 0.28.3 Desktop GUI provides a modern, native desktop application for administering the encrypted backup server. It features:

✅ **Cross-Platform**: Windows, macOS, Linux
✅ **Modern Design**: Material Design 3 with light/dark mode
✅ **Real-Time Updates**: Live monitoring with 1-second refresh
✅ **Responsive UI**: Smooth interactions, no freezing
✅ **Rich Features**: Comprehensive monitoring and management
✅ **Easy Deployment**: Standalone executable or package
✅ **Professional Look**: Modern Material Design interface

It replaces the current Tkinter GUI with a more capable, visually appealing alternative while maintaining the same monitoring and administration functionality.

**Integration**: Runs alongside existing Python server.py on same machine, communicates via TCP/HTTP and direct SQLite database access.
