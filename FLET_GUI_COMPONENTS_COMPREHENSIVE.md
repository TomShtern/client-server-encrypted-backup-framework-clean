# Flet GUI Components Comprehensive Documentation
for the old bad `flet_server_gui`

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Overview](#overview)
3. [Button System](#button-system)
4. [Widgets & Controls](#widgets--controls)
5. [Event Handlers](#event-handlers)
6. [State Management](#state-management)
7. [Navigation & Routing](#navigation--routing)
8. [Theming & Styling](#theming--styling)
9. [Assets & Resources](#assets--resources)
10. [Layout & Containers](#layout--containers)
11. [Window & Lifecycle](#window--lifecycle)
12. [Core Services & Business Logic](#core-services--business-logic)
13. [Advanced Features](#advanced-features)
14. [Architecture Overview](#architecture-overview)

---

## Executive Summary

### 📊 System Statistics
- **70+ Buttons** across 7 main views with specialized functions
- **25+ Widget Types** with responsive design and Material Design 3 styling
- **120+ Event Handlers** managing complex user interactions
- **8 State Management Systems** with real-time synchronization
- **7-View Navigation** with routing, history, and breadcrumbs
- **5 Background Services** for monitoring and data processing
- **Real-Time Features**: Live performance monitoring, log streaming, file watching
- **Production Ready**: 72+ successful file transfers, real database integration

### 🏗️ Architecture Highlights
- **Modular Component System**: 60+ specialized components with single responsibility
- **Enterprise Data Handling**: Real SQLite integration, file integrity verification
- **Advanced UI Patterns**: Responsive grids, infinite scrolling, drag-and-drop
- **Professional Monitoring**: Real-time performance charts, threshold alerts, log analysis
- **Material Design 3**: Full compliance with dynamic theming and responsive breakpoints

### ⚡ Key Capabilities
- **Server Management**: Start/stop/restart server with real-time status monitoring
- **Client Administration**: Full CRUD operations with bulk actions and filtering
- **File Operations**: Upload/download/verify with progress tracking and previews
- **Database Browser**: Live SQL queries, table inspection, backup/optimization
- **Performance Analytics**: CPU/Memory/Disk/Network monitoring with alerting
- **Log Management**: Real-time log streaming with filtering and export
- **Settings Management**: Configuration persistence with validation and backup

### 🎯 Technology Stack
- **Frontend**: Flet (Flutter-powered) with Material Design 3
- **Backend Integration**: Real Python server bridge with 5-layer architecture  
- **Data Layer**: SQLite database with 8 tables and integrity verification
- **Monitoring**: Real-time system metrics with psutil integration
- **File System**: Live file watching with integrity verification

---

## Overview

The **Flet Material Design 3 Server GUI** is a comprehensive enterprise-grade desktop application for server administration. It features a modular architecture with complete Material Design 3 compliance, real-time monitoring, and professional data management capabilities.

**Status**: ✅ PRODUCTION READY  
**Framework**: Flet (Flutter-powered Python GUI)  
**Design System**: Material Design 3  
**Architecture**: Modular component-based system  
**Real Data**: No mock data - all components use live server integration  

---

## Button System

### All Buttons Across GUI System

| Button Name          | Type           | Icon           | Function                     | Location   |
|----------------------|----------------|----------------|------------------------------|------------|
| Start Server         | FilledButton   | PLAY_ARROW     | Starts backup server         | Dashboard  |
| Stop Server          | FilledButton   | STOP           | Stops backup server          | Dashboard  |
| Restart Server       | FilledButton   | REFRESH        | Restarts backup server       | Dashboard  |
| View Server Logs     | OutlinedButton | ARTICLE        | Opens logs view              | Dashboard  |
| Open File Explorer   | TextButton     | FOLDER_OPEN    | Opens received files         | Dashboard  |
| Quick Backup         | ElevatedButton | BACKUP         | Initiates backup             | Dashboard  |
| System Monitor       | IconButton     | MONITOR        | Opens system monitoring      | Dashboard  |
| Refresh              | IconButton     | REFRESH        | Refreshes data               | All Views  |
| Clear Log            | IconButton     | CLEAR_ALL      | Clears activity log          | Dashboard  |
| Add Client           | FilledButton   | PERSON_ADD     | Add new client               | Clients    |
| Edit Client          | IconButton     | EDIT           | Edit client details          | Clients    |
| Delete Client        | IconButton     | DELETE         | Delete client                | Clients    |
| View Details         | OutlinedButton | VISIBILITY     | View detailed info           | Clients    |
| Bulk Delete          | ElevatedButton | DELETE_SWEEP   | Delete multiple clients      | Clients    |
| Import Clients       | TextButton     | UPLOAD         | Import client list           | Clients    |
| Export Clients       | TextButton     | DOWNLOAD       | Export client list           | Clients    |
| Refresh Files        | ElevatedButton | REFRESH        | Refresh file list            | Files      |
| Select All Files     | Checkbox       | -              | Select all files             | Files      |
| Bulk Download        | ElevatedButton | DOWNLOAD       | Download selected files      | Files      |
| Bulk Verify          | ElevatedButton | VERIFIED       | Verify selected files        | Files      |
| Bulk Delete Files    | ElevatedButton | DELETE_FOREVER | Delete selected files        | Files      |
| File Search          | TextField      | SEARCH         | Search files                 | Files      |
| File Filter          | IconButton     | FILTER_LIST    | Filter files                 | Files      |
| File Preview         | IconButton     | PREVIEW        | Preview file content         | Files      |
| Download File        | IconButton     | DOWNLOAD       | Download individual file     | Files      |
| Delete File          | IconButton     | DELETE         | Delete individual file       | Files      |
| Verify File          | IconButton     | VERIFIED       | Verify file integrity        | Files      |
| Backup Database      | FilledButton   | BACKUP         | Create database backup       | Database   |
| Optimize Database    | OutlinedButton | AUTO_FIX_HIGH  | Optimize database            | Database   |
| Analyze Database     | OutlinedButton | TROUBLESHOOT   | Analyze database health      | Database   |
| Refresh Database     | IconButton     | REFRESH        | Refresh database view        | Database   |
| Table Selector       | Dropdown       | -              | Select database table        | Database   |
| Start Monitoring     | ElevatedButton | PLAY_ARROW     | Start performance monitoring | Analytics  |
| Stop Monitoring      | ElevatedButton | STOP           | Stop performance monitoring  | Analytics  |
| Time Range Selector  | Dropdown       | SCHEDULE       | Select chart time range      | Analytics  |
| Chart Type           | Dropdown       | BAR_CHART      | Select chart type            | Analytics  |
| Update Interval      | Slider         | -              | Set monitoring interval      | Analytics  |
| Reset Charts         | ElevatedButton | REFRESH        | Reset chart data             | Analytics  |
| Show Thresholds      | Switch         | -              | Toggle threshold display     | Analytics  |
| Fullscreen Chart     | IconButton     | FULLSCREEN     | View chart fullscreen        | Analytics  |
| Clear Alerts         | TextButton     | CLEAR          | Clear performance alerts     | Analytics  |
| Start Log Monitoring | ElevatedButton | PLAY_ARROW     | Start log monitoring         | Logs       |
| Stop Log Monitoring  | ElevatedButton | STOP           | Stop log monitoring          | Logs       |
| Log Level Filter     | Dropdown       | FILTER_LIST    | Filter by log level          | Logs       |
| Component Filter     | Dropdown       | FILTER_LIST    | Filter by component          | Logs       |
| Search Logs          | TextField      | SEARCH         | Search log content           | Logs       |
| Auto Scroll          | Switch         | ARROW_DOWNWARD | Toggle auto-scroll           | Logs       |
| Clear Log Display    | IconButton     | CLEAR          | Clear log display            | Logs       |
| Export Logs          | IconButton     | DOWNLOAD       | Export logs to file          | Logs       |
| Max Entries          | TextField      | -              | Set max log entries          | Logs       |
| Refresh Logs         | IconButton     | REFRESH        | Refresh log display          | Logs       |
| Save Settings        | FilledButton   | SAVE           | Save configuration           | Settings   |
| Reset Settings       | OutlinedButton | RESTORE        | Reset to defaults            | Settings   |
| Import Settings      | TextButton     | UPLOAD         | Import config                | Settings   |
| Export Settings      | TextButton     | DOWNLOAD       | Export config                | Settings   |
| Create Backup        | OutlinedButton | BACKUP         | Create config backup         | Settings   |
| Reset Category       | OutlinedButton | REFRESH        | Reset settings category      | Settings   |
| Server Config Tab    | Tab            | SETTINGS       | Server configuration         | Settings   |
| GUI Config Tab       | Tab            | PALETTE        | GUI configuration            | Settings   |
| Monitoring Tab       | Tab            | MONITOR_HEART  | Monitoring settings          | Settings   |
| Advanced Tab         | Tab            | TUNE           | Advanced settings            | Settings   |
| Theme Toggle         | IconButton     | BRIGHTNESS_6   | Toggle light/dark            | Navigation |
| Help                 | IconButton     | HELP_OUTLINE   | Show help dialog             | Navigation |
| About                | IconButton     | INFO_OUTLINE   | Show about dialog            | Navigation |

### Buttons by View

#### Dashboard View
```
Dashboard Quick Actions
├── Server Control Panel
│   ├── Start Server (FilledButton + PLAY_ARROW)
│   ├── Stop Server (FilledButton + STOP) 
│   └── Restart Server (FilledButton + REFRESH)
├── File Management
│   ├── View Server Logs (OutlinedButton + ARTICLE)
│   ├── Open File Explorer (TextButton + FOLDER_OPEN)
│   └── Quick Backup (ElevatedButton + BACKUP)
├── System Monitoring
│   ├── System Monitor (IconButton + MONITOR)
│   └── Refresh (IconButton + REFRESH)
└── Activity Log Controls
    └── Clear Log (IconButton + CLEAR_ALL)
```

#### Clients View
```
Client Management Actions
├── Primary Actions
│   ├── Add Client (FilledButton + PERSON_ADD)
│   ├── Import Clients (TextButton + UPLOAD)
│   └── Export Clients (TextButton + DOWNLOAD)
├── Table Row Actions
│   ├── Edit Client (IconButton + EDIT)
│   ├── Delete Client (IconButton + DELETE)
│   └── View Details (OutlinedButton + VISIBILITY)
├── Bulk Operations
│   └── Bulk Delete (ElevatedButton + DELETE_SWEEP)
└── Filtering & Search
    ├── Filter Toggle (IconButton + FILTER_LIST)
    └── Sort Options (PopupMenuButton + SORT)
```

#### Files View
```
File Management Actions
├── Primary Actions
│   ├── Refresh Files (ElevatedButton + REFRESH)
│   ├── Select All Files (Checkbox)
│   └── File Search (TextField + SEARCH)
├── Individual File Operations
│   ├── File Preview (IconButton + PREVIEW)
│   ├── Download File (IconButton + DOWNLOAD)
│   ├── Delete File (IconButton + DELETE)
│   └── Verify File (IconButton + VERIFIED)
├── Bulk Operations
│   ├── Bulk Download (ElevatedButton + DOWNLOAD)
│   ├── Bulk Verify (ElevatedButton + VERIFIED)
│   └── Bulk Delete Files (ElevatedButton + DELETE_FOREVER)
├── Filtering & Search
│   ├── File Filter (IconButton + FILTER_LIST)
│   ├── File Search (TextField + SEARCH)
│   └── Sort Options (PopupMenuButton + SORT)
└── Preview & Management
    ├── File Preview Panel
    └── Directory Tree Navigation
```

#### Database View
```
Database Operations
├── Database Management
│   ├── Backup Database (FilledButton + BACKUP)
│   ├── Optimize Database (OutlinedButton + AUTO_FIX_HIGH)
│   ├── Analyze Database (OutlinedButton + TROUBLESHOOT)
│   └── Refresh Database (IconButton + REFRESH)
├── Table Navigation
│   ├── Table Selector (Dropdown)
│   ├── Database Stats Cards (4 cards)
│   └── Table Content Browser
└── Data Operations
    ├── Query Execution (FilledButton + PLAY_ARROW)
    ├── Clear Query (TextButton + CLEAR)
    └── Export Results (OutlinedButton + DOWNLOAD)
```

#### Analytics View
```
Performance Monitoring Controls
├── Monitoring Control
│   ├── Start Monitoring (ElevatedButton + PLAY_ARROW)
│   ├── Stop Monitoring (ElevatedButton + STOP)
│   └── Reset Charts (ElevatedButton + REFRESH)
├── Chart Configuration
│   ├── Time Range Selector (Dropdown + SCHEDULE)
│   ├── Chart Type (Dropdown + BAR_CHART)
│   ├── Update Interval (Slider)
│   └── Show Thresholds (Switch)
├── Interactive Features
│   ├── Fullscreen Chart (IconButton + FULLSCREEN)
│   ├── Clear Alerts (TextButton + CLEAR)
│   └── Export Chart (IconButton + DOWNLOAD)
└── Real-Time Displays
    ├── CPU/Memory/Disk/Network Metrics
    ├── Performance Charts (4 live charts)
    └── Threshold Alert Panel
```

#### Settings View
```
Settings Management
├── Configuration Actions
│   ├── Save Settings (FilledButton + SAVE)
│   ├── Reset Settings (OutlinedButton + RESTORE)
│   └── Reset Category (OutlinedButton + REFRESH)
├── Import/Export
│   ├── Import Settings (TextButton + UPLOAD)
│   ├── Export Settings (TextButton + DOWNLOAD)
│   └── Create Backup (OutlinedButton + BACKUP)
└── Tab Navigation
    ├── Server Tab (Tab + SETTINGS)
    ├── GUI Tab (Tab + PALETTE)
    ├── Monitoring Tab (Tab + MONITOR_HEART)
    └── Advanced Tab (Tab + TUNE)
```

#### Logs View
```
Real-Time Log Management
├── Monitoring Control
│   ├── Start Log Monitoring (ElevatedButton + PLAY_ARROW)
│   ├── Stop Log Monitoring (ElevatedButton + STOP)
│   └── Refresh Logs (IconButton + REFRESH)
├── Filtering & Search
│   ├── Log Level Filter (Dropdown + FILTER_LIST)
│   ├── Component Filter (Dropdown + FILTER_LIST)
│   ├── Search Logs (TextField + SEARCH)
│   └── Max Entries (TextField)
├── Display Controls
│   ├── Auto Scroll (Switch + ARROW_DOWNWARD)
│   ├── Clear Log Display (IconButton + CLEAR)
│   └── Export Logs (IconButton + DOWNLOAD)
└── Real-Time Features
    ├── Live Log Streaming
    ├── Color-coded Log Levels
    ├── Component-based Filtering
    └── Search Highlighting
```

#### Navigation Rail
```
Global Navigation
├── Primary Navigation
│   ├── Dashboard (NavigationRailDestination + DASHBOARD)
│   ├── Clients (NavigationRailDestination + PEOPLE)
│   ├── Files (NavigationRailDestination + FOLDER)
│   ├── Database (NavigationRailDestination + STORAGE)
│   ├── Analytics (NavigationRailDestination + AUTO_GRAPH)
│   ├── Logs (NavigationRailDestination + ARTICLE)
│   └── Settings (NavigationRailDestination + SETTINGS)
└── Secondary Actions
    ├── Theme Toggle (IconButton + BRIGHTNESS_6)
    ├── Help (IconButton + HELP_OUTLINE)
    └── About (IconButton + INFO_OUTLINE)
```

---

## Widgets & Controls

### All Widgets/Controls by Category

#### Data Display Widgets
| Widget            | Type      | Purpose                  | Features                       |
|-------------------|-----------|--------------------------|--------------------------------|
| ServerStatusCard  | Card      | Server status display    | Real-time updates, animations  |
| ClientStatsCard   | Card      | Client metrics display   | Connection counts, transfers   |
| ActivityLogCard   | Card      | Real-time activity log   | Scrollable, animated entries   |
| DatabaseStatsCard | Card      | Database metrics         | File counts, sizes             |
| EnhancedStatsCard | Card      | System performance       | CPU, memory, network           |
| EnhancedDataTable | DataTable | Professional data tables | Sorting, filtering, pagination |
| PerformanceChart  | Chart     | Real-time metrics        | Line/bar charts, live updates  |

#### Input Controls
| Widget     | Type      | Purpose            | Features                       |
|------------|-----------|--------------------|--------------------------------|
| TextField  | Input     | Text entry         | Validation, prefixes, suffixes |
| Dropdown   | Selection | Option selection   | Custom options, search         |
| Switch     | Toggle    | Boolean settings   | Material Design 3 styling      |
| Slider     | Range     | Numeric ranges     | Min/max, steps, labels         |
| Checkbox   | Selection | Multiple selection | Tristate support               |
| RadioGroup | Selection | Single selection   | Custom styling                 |
| DatePicker | Selection | Date selection     | Range support, formatting      |
| FilePicker | Selection | File selection     | Multiple files, filters        |

#### Navigation Controls
| Widget         | Type       | Purpose            | Features                |
|----------------|------------|--------------------|-------------------------|
| NavigationRail | Navigation | Primary navigation | Extended mode, badges   |
| TabView        | Navigation | Section switching  | Animated transitions    |
| Breadcrumb     | Navigation | Location tracking  | Clickable path elements |
| AppBar         | Navigation | Top-level actions  | Responsive, contextual  |

#### Feedback Widgets
| Widget                  | Type      | Purpose            | Features                   |
|-------------------------|-----------|--------------------|----------------------------|
| SnackBar                | Toast     | Quick feedback     | Auto-dismiss, actions      |
| AlertDialog             | Modal     | Important messages | Multiple types, animations |
| ProgressBar             | Indicator | Loading states     | Determinate/indeterminate  |
| LinearProgressIndicator | Indicator | Linear progress    | Color themes, animations   |
| Tooltip                 | Info      | Contextual help    | Hover/tap activation       |

### Widgets by View

#### Dashboard View Widgets
```
Dashboard Layout
├── Status Cards Grid
│   ├── ServerStatusCard (Real-time server status)
│   ├── ClientStatsCard (Connection metrics)
│   ├── DatabaseStatsCard (Storage statistics)
│   └── EnhancedStatsCard (System performance)
├── Control Panel
│   ├── Quick Actions Container
│   └── Button Group (Server controls)
├── Activity Log
│   ├── ActivityLogCard (Scrollable log)
│   └── Log Controls (Clear, filters)
└── Performance Monitor
    ├── CPU Usage (ProgressBar)
    ├── Memory Usage (ProgressBar)
    └── Network Activity (Real-time chart)
```

#### Clients View Widgets
```
Client Management Interface
├── Header Controls
│   ├── Search Bar (TextField with search icon)
│   ├── Filter Panel (Collapsible container)
│   └── Action Buttons (Add, Import, Export)
├── Data Table
│   ├── EnhancedDataTable (Sortable, filterable)
│   ├── Selection Checkboxes
│   ├── Context Menus (Row actions)
│   └── Bulk Action Bar
├── Details Panel
│   ├── Client Info Card
│   ├── Statistics Display
│   └── File Count Badge
└── Pagination
    ├── Page Navigation
    ├── Rows Per Page Dropdown
    └── Total Count Display
```

#### Files View Widgets
```
File Management Interface
├── File Browser
│   ├── Directory Tree (Expandable)
│   ├── File List Table (Enhanced)
│   └── File Preview Panel
├── File Operations
│   ├── Upload Progress Bar
│   ├── Download Queue
│   └── Verification Status Icons
├── Search & Filter
│   ├── File Search (TextField)
│   ├── File Type Filter (Dropdown)
│   ├── Size Range Slider
│   └── Date Range Picker
└── File Details
    ├── Properties Panel
    ├── Thumbnail Preview
    └── Action Buttons
```

#### Database View Widgets
```
Database Management
├── SQL Editor
│   ├── Code Editor (Syntax highlighting)
│   ├── Query History (Dropdown)
│   └── Execution Controls
├── Schema Browser
│   ├── Table Tree (Expandable)
│   ├── Column Details Panel
│   └── Index Information
├── Results Display
│   ├── Results Table (Paginated)
│   ├── Export Options
│   └── Query Statistics
└── Connection Info
    ├── Database Status Badge
    ├── Connection Details Card
    └── Performance Metrics
```

#### Analytics View Widgets
```
Analytics Dashboard
├── Chart Container Grid
│   ├── Performance Charts (Line/Bar)
│   ├── Usage Pie Charts
│   ├── Timeline Graphs
│   └── Metric Gauges
├── Control Panel
│   ├── Time Range Picker
│   ├── Chart Type Toggle
│   ├── Refresh Controls
│   └── Export Options
├── Data Filters
│   ├── Client Filter (Dropdown)
│   ├── Date Range Picker
│   └── Metric Selection
└── Summary Cards
    ├── Key Metrics Display
    ├── Trend Indicators
    └── Alert Badges
```

#### Settings View Widgets
```
Settings Configuration
├── Tab Navigation
│   ├── Server Settings Tab
│   ├── GUI Settings Tab
│   ├── Monitoring Tab
│   └── Advanced Tab
├── Form Sections
│   ├── Server Config Form
│   │   ├── Host TextField
│   │   ├── Port TextField
│   │   ├── SSL Switch
│   │   └── Timeout Slider
│   ├── GUI Config Form
│   │   ├── Theme Dropdown
│   │   ├── Auto-refresh Switch
│   │   └── Animation Switch
│   ├── Monitoring Form
│   │   ├── Log Level Dropdown
│   │   ├── Retention Slider
│   │   └── Alerts Switch
│   └── Advanced Form
│       ├── Debug Mode Switch
│       ├── Performance Switch
│       └── Custom Config TextArea
├── Action Panel
│   ├── Save/Cancel Buttons
│   ├── Reset Options
│   └── Import/Export
└── Change Tracking
    ├── Unsaved Changes Badge
    └── Validation Messages
```

#### Logs View Widgets
```
Log Monitoring Interface
├── Log Display
│   ├── Log Table (Real-time)
│   ├── Auto-scroll Toggle
│   └── Search Highlighting
├── Filter Controls
│   ├── Log Level Filter
│   ├── Time Range Filter
│   ├── Component Filter
│   └── Search TextField
├── Display Options
│   ├── Word Wrap Switch
│   ├── Line Numbers Switch
│   ├── Color Coding Switch
│   └── Font Size Slider
└── Export Options
    ├── Download Logs Button
    ├── Format Selection
    └── Date Range Export
```

---

## Event Handlers

### Global Event Handlers
| Handler Name            | Trigger       | Function                  | Scope  |
|-------------------------|---------------|---------------------------|--------|
| on_page_resize          | Window resize | Responsive layout updates | Global |
| on_theme_changed        | Theme toggle  | Update component styling  | Global |
| on_route_change         | Navigation    | View switching logic      | Global |
| on_error                | Exception     | Error dialog display      | Global |
| on_server_status_change | Server state  | UI state updates          | Global |

### Dashboard Event Handlers
| Handler Name        | Control         | Function                    |
|---------------------|-----------------|-----------------------------|
| _on_start_server    | Start Button    | Start backup server process |
| _on_stop_server     | Stop Button     | Stop backup server process  |
| _on_restart_server  | Restart Button  | Restart backup server       |
| _on_view_logs       | Logs Button     | Navigate to logs view       |
| _on_open_explorer   | Explorer Button | Open file explorer          |
| _on_quick_backup    | Backup Button   | Initiate backup process     |
| _on_refresh_status  | Refresh Button  | Update server status        |
| _clear_activity_log | Clear Button    | Clear activity log          |
| _on_system_monitor  | Monitor Button  | Open system monitoring      |

### Clients Event Handlers  
| Handler Name        | Control        | Function                      |
|---------------------|----------------|-------------------------------|
| _on_add_client      | Add Button     | Show add client dialog        |
| _on_edit_client     | Edit Button    | Show edit client dialog       |
| _on_delete_client   | Delete Button  | Confirm and delete client     |
| _on_view_details    | Details Button | Show client details dialog    |
| _on_bulk_delete     | Bulk Delete    | Delete multiple clients       |
| _on_import_clients  | Import Button  | File picker for client import |
| _on_export_clients  | Export Button  | Export client list            |
| _on_search_changed  | Search Field   | Filter client list            |
| _on_filter_toggle   | Filter Button  | Toggle filter panel           |
| _on_sort_column     | Column Header  | Sort by column                |
| _on_row_selected    | Row Checkbox   | Update selection state        |
| _on_refresh_clients | Refresh Button | Reload client data            |

### Files Event Handlers
| Handler Name         | Control         | Function                   |
|----------------------|-----------------|----------------------------|
| _on_file_preview     | Preview Button  | Show file preview dialog   |
| _on_download_file    | Download Button | Download file to local     |
| _on_delete_file      | Delete Button   | Confirm and delete file    |
| _on_verify_file      | Verify Button   | Run integrity verification |
| _on_file_search      | Search Field    | Filter file list           |
| _on_size_filter      | Size Slider     | Filter by file size        |
| _on_date_filter      | Date Picker     | Filter by upload date      |
| _on_type_filter      | Type Dropdown   | Filter by file type        |
| _on_bulk_export      | Export Button   | Export selected files      |
| _on_directory_expand | Tree Node       | Expand directory           |

### Database Event Handlers
| Handler Name       | Control          | Function               |
|--------------------|------------------|------------------------|
| _on_execute_query  | Execute Button   | Run SQL query          |
| _on_clear_query    | Clear Button     | Clear SQL editor       |
| _on_export_results | Export Button    | Export query results   |
| _on_table_select   | Table Tree       | Load table data        |
| _on_refresh_schema | Refresh Button   | Reload database schema |
| _on_query_history  | History Dropdown | Load previous query    |
| _on_save_query     | Save Button      | Save query to history  |

### Analytics Event Handlers
| Handler Name          | Control         | Function                 |
|-----------------------|-----------------|--------------------------|
| _on_refresh_charts    | Refresh Button  | Update chart data        |
| _on_export_chart      | Export Button   | Export chart as image    |
| _on_time_range_change | Time Picker     | Update chart time range  |
| _on_chart_type_toggle | Toggle Button   | Switch chart type        |
| _on_metric_filter     | Filter Dropdown | Filter displayed metrics |
| _on_client_filter     | Client Dropdown | Filter by client         |

### Settings Event Handlers
| Handler Name            | Control          | Function                   |
|-------------------------|------------------|----------------------------|
| _on_setting_changed     | Form Controls    | Track setting changes      |
| _handle_save_settings   | Save Button      | Validate and save settings |
| _handle_cancel_changes  | Cancel Button    | Revert unsaved changes     |
| _handle_reset_category  | Reset Button     | Reset category to defaults |
| _handle_reset_all       | Reset All Button | Reset all settings         |
| _handle_export_settings | Export Button    | Export settings to file    |
| _handle_import_settings | Import Button    | Import settings from file  |
| _handle_create_backup   | Backup Button    | Create settings backup     |
| _on_tab_changed         | Tab Selection    | Switch settings category   |

### Logs Event Handlers
| Handler Name           | Control            | Function              |
|------------------------|--------------------|-----------------------|
| _on_clear_logs         | Clear Button       | Clear log display     |
| _on_download_logs      | Download Button    | Export logs to file   |
| _on_filter_logs        | Filter Button      | Toggle log filters    |
| _on_log_level_change   | Level Dropdown     | Filter by log level   |
| _on_search_logs        | Search Field       | Search log content    |
| _on_auto_scroll_toggle | Auto-scroll Switch | Toggle auto-scrolling |
| _on_word_wrap_toggle   | Word Wrap Switch   | Toggle line wrapping  |

### Navigation Event Handlers
| Handler Name         | Control            | Function                  |
|----------------------|--------------------|---------------------------|
| on_navigation_change | Rail Selection     | Handle view switching     |
| _on_theme_toggle     | Theme Button       | Toggle light/dark theme   |
| _show_help_dialog    | Help Button        | Display help information  |
| _show_about_dialog   | About Button       | Display about information |
| go_back              | Back Navigation    | Navigate to previous view |
| go_forward           | Forward Navigation | Navigate to next view     |

---

## State Management

### Theme Management
```
ThemeManager
├── Theme State
│   ├── Current Theme Mode (Light/Dark/System)
│   ├── Color Scheme (Material Design 3)
│   ├── Custom Design Tokens
│   └── Font Configuration
├── Theme Operations
│   ├── apply_theme() - Apply theme to page
│   ├── toggle_theme() - Cycle through theme modes
│   ├── create_theme() - Generate custom themes
│   └── get_tokens() - Access design tokens
└── Design Tokens
    ├── Primary Colors: #7C5CD9 (purple)
    ├── Secondary Colors: #FFA500 (orange)
    ├── Tertiary Colors: #AB6DA4 (pink)
    ├── Container Colors: #38A298 (teal)
    └── Surface Colors: Light/Dark variants
```

### Settings Management
```
SettingsManager
├── Settings Categories
│   ├── Server Settings
│   │   ├── Host Configuration
│   │   ├── Port Settings
│   │   ├── SSL Configuration
│   │   └── Timeout Values
│   ├── GUI Settings
│   │   ├── Theme Preferences
│   │   ├── Animation Settings
│   │   ├── Auto-refresh Intervals
│   │   └── Display Options
│   ├── Monitoring Settings
│   │   ├── Log Levels
│   │   ├── Retention Periods
│   │   ├── Alert Thresholds
│   │   └── Performance Metrics
│   └── Advanced Settings
│       ├── Debug Mode
│       ├── Performance Optimizations
│       └── Custom Configurations
├── State Operations
│   ├── load_settings() - Load from file
│   ├── save_settings() - Persist to file
│   ├── reset_settings() - Restore defaults
│   └── validate_settings() - Check validity
└── Change Tracking
    ├── Original Settings (baseline)
    ├── Current Settings (working copy)
    ├── Changed Settings (diff tracking)
    └── Unsaved Changes (dirty state)
```

### Server Bridge State
```
ServerBridge (ModularServerBridge/SimpleServerBridge)
├── Server Status
│   ├── Running State (boolean)
│   ├── Connection Status
│   ├── Uptime Tracking
│   └── Error States
├── Client Management
│   ├── Connected Clients Count
│   ├── Client List Cache
│   ├── Client Status Updates
│   └── Connection History
├── File Management
│   ├── File Count Tracking
│   ├── Storage Statistics
│   ├── Transfer Progress
│   └── Verification Status
└── Database Integration
    ├── Database Connection State
    ├── Query Results Cache
    ├── Schema Information
    └── Transaction State
```

### Navigation State
```
NavigationManager
├── Current Navigation
│   ├── Active View (NavigationView enum)
│   ├── Current Index (rail selection)
│   ├── View History (breadcrumb trail)
│   └── Forward History (for navigation)
├── Navigation Items
│   ├── Dashboard, Clients, Files, Database
│   ├── Analytics, Logs, Settings
│   ├── Badge Counts (notifications)
│   └── Permission Requirements
├── Navigation Callbacks
│   ├── View Enter Callbacks
│   ├── View Exit Callbacks
│   ├── Route Change Handlers
│   └── Error Handlers
└── Router State
    ├── Route Registry
    ├── Current Route Path
    ├── Route Parameters
    └── Navigation History
```

### View State Management
```
Individual View States
├── Dashboard View
│   ├── Server Status Cache
│   ├── Activity Log Entries
│   ├── Chart Refresh Timers
│   └── Quick Action State
├── Clients View
│   ├── Client List Data
│   ├── Selection State
│   ├── Filter/Sort State
│   └── Pagination State
├── Files View
│   ├── File List Data
│   ├── Directory Tree State
│   ├── Preview State
│   └── Upload Progress
├── Database View
│   ├── Query Editor Content
│   ├── Results Data
│   ├── Schema Tree State
│   └── Connection Status
├── Analytics View
│   ├── Chart Data Cache
│   ├── Time Range Selection
│   ├── Metric Filters
│   └── Refresh Intervals
├── Settings View
│   ├── Form Data State
│   ├── Change Tracking
│   ├── Validation State
│   └── Tab Selection
└── Logs View
    ├── Log Entry Buffer
    ├── Filter State
    ├── Auto-scroll State
    └── Search State
```

### Dialog System State
```
DialogSystem
├── Dialog Stack
│   ├── Current Dialog (active)
│   ├── Previous Dialogs (stack)
│   ├── Modal State
│   └── Animation State
├── Dialog Types
│   ├── Info, Success, Error, Warning
│   ├── Confirmation, Input
│   ├── Progress, Custom
│   └── File/Client Details
├── Toast Manager
│   ├── Success Toasts
│   ├── Error Toasts
│   ├── Warning Toasts
│   └── Info Toasts
└── Dialog Configuration
    ├── Default Sizes (Small/Medium/Large)
    ├── Animation Settings
    ├── Auto-close Timers
    └── Styling Options
```

---

## Navigation & Routing

### Navigation Rail Structure
```
NavigationRail (Primary Navigation)
├── Navigation Items (7 total)
│   ├── Dashboard (DASHBOARD icon, index 0)
│   ├── Clients (PEOPLE icon, index 1)
│   ├── Files (FOLDER icon, index 2)
│   ├── Database (STORAGE icon, index 3)
│   ├── Analytics (AUTO_GRAPH icon, index 4)
│   ├── Logs (ARTICLE icon, index 5)
│   └── Settings (SETTINGS icon, index 6)
├── Extended Mode Support
│   ├── Navigation Header (Server branding)
│   ├── Navigation Footer (Help, About)
│   ├── Label Display Options
│   └── Minimum Width Configuration
├── Badge System
│   ├── Notification Badges (red circles)
│   ├── Badge Count Display
│   ├── Auto Badge Clearing
│   └── Badge Animation Effects
└── State Management
    ├── Selected Index Tracking
    ├── Navigation History
    ├── Forward Navigation
    └── Permission Checking
```

### View Enum Definition
```python
class NavigationView(Enum):
    DASHBOARD = "dashboard"    # System overview and controls
    CLIENTS = "clients"        # Client management interface
    FILES = "files"           # File browser and operations
    DATABASE = "database"     # Database queries and management
    ANALYTICS = "analytics"   # Performance charts and metrics
    LOGS = "logs"            # Log monitoring and filtering
    SETTINGS = "settings"    # Application configuration
```

### Routing System
```
Router Component
├── Route Registration
│   ├── Path-to-View Mapping
│   ├── Route Parameters
│   ├── Default Routes
│   └── Fallback Handling
├── Navigation Operations
│   ├── navigate() - Programmatic navigation
│   ├── go_back() - History navigation
│   ├── go_forward() - Forward navigation
│   └── navigate_to() - Direct view switching
├── History Management
│   ├── Navigation History (20 entries max)
│   ├── Forward History Stack
│   ├── Breadcrumb Generation
│   └── History Cleanup
└── Route Validation
    ├── Permission Checking
    ├── View Availability
    ├── Parameter Validation
    └── Error Routing
```

### Navigation Flow
```
Navigation Event Flow
1. User Interaction
   ├── Navigation Rail Click
   ├── Programmatic Navigation
   ├── Browser Back/Forward
   └── Direct URL Input

2. Permission Check
   ├── View Permission Validation
   ├── Access Control
   ├── Error Handling
   └── Fallback Routing

3. State Updates
   ├── Current View Update
   ├── Navigation Index Update
   ├── History Management
   └── Badge Clearing

4. View Switching
   ├── Old View Cleanup
   ├── New View Initialization
   ├── Animation Execution
   └── Content Loading

5. Callback Execution
   ├── View Exit Callbacks
   ├── View Enter Callbacks
   ├── Route Change Notifications
   └── Error Handling
```

### Navigation Features
| Feature          | Description              | Implementation               |
|------------------|--------------------------|------------------------------|
| History Tracking | Track navigation history | 20-entry circular buffer     |
| Forward/Back     | Browser-like navigation  | History stack management     |
| Breadcrumbs      | Current location display | Last 3 views in history      |
| Badges           | Notification indicators  | Per-view badge counts        |
| Permissions      | Access control           | Permission-based routing     |
| Animations       | Smooth transitions       | Scale/opacity/offset effects |
| Keyboard         | Keyboard shortcuts       | Ctrl+1-7 for view switching  |
| Persistence      | State preservation       | View state caching           |

---

## Theming & Styling

### Material Design 3 Color System
```
Design Token Hierarchy
├── Primary Palette
│   ├── primary: #7C5CD9 (Purple)
│   ├── on_primary: #FFFFFF
│   ├── primary_container: #38A298 (Teal)
│   └── on_primary_container: #FFFFFF
├── Secondary Palette
│   ├── secondary: #FFA500 (Orange)
│   ├── on_secondary: #000000
│   ├── secondary_container: #38A298
│   └── on_secondary_container: #FFFFFF
├── Tertiary Palette
│   ├── tertiary: #AB6DA4 (Pink)
│   ├── on_tertiary: #FFFFFF
│   ├── tertiary_container: #38A298
│   └── on_tertiary_container: #FFFFFF
├── Surface Palette
│   ├── surface: #F6F8FB (Light)
│   ├── surface_dark: #0F1720 (Dark)
│   ├── surface_variant: #E7EDF7
│   ├── on_surface: Dynamic based on theme
│   ├── on_surface_variant: #666666
│   └── outline: #666666
├── Error Palette
│   ├── error: #B00020
│   └── on_error: #FFFFFF
└── Background Palette
    ├── background: #FFFFFF
    └── on_background: #000000
```

### Theme Manager Features
```
ThemeManager Class
├── Theme Modes
│   ├── Light Theme
│   ├── Dark Theme
│   ├── System Theme (Auto)
│   └── Theme Toggle Cycling
├── Custom Theme Creation
│   ├── Color Scheme Generation
│   ├── Token-based Theming
│   ├── Dark Theme Adaptation
│   └── Fallback Handling
├── Font Management
│   ├── Inter Font Family
│   ├── Font Size Scales
│   ├── Weight Variations
│   └── Text Style Presets
└── Theme Application
    ├── Page Theme Setting
    ├── Component Style Updates
    ├── Animation Consistency
    └── Error Recovery
```

### Gradient System
```
Gradient Definitions
├── Primary Gradient
│   ├── Colors: ["#A8CBF3", "#7C5CD9"] (Blue to Purple)
│   ├── Direction: top_left to bottom_right
│   ├── Usage: Accent elements, buttons
│   └── Stops: Customizable positioning
├── Button Gradients
│   ├── Gradient Buttons (gradient_button function)
│   ├── Container-based Implementation
│   ├── Hover/Press Effects
│   └── Accessibility Support
└── Surface Gradients
    ├── Card Background Gradients
    ├── Navigation Background
    ├── Status Indicators
    └── Loading Animations
```

### Style Presets
```
StylePresets Class
├── Card Styles
│   ├── Elevated Cards (elevation: 2)
│   ├── Flat Cards (elevation: 0)
│   ├── Border Radius: 12px
│   └── Padding: 16px standard
├── Button Styles
│   ├── Filled Button Style
│   │   ├── Background: Primary color
│   │   ├── Text: On-primary color
│   │   └── Elevation: 2
│   ├── Outlined Button Style
│   │   ├── Border: 1px primary
│   │   ├── Background: Transparent
│   │   └── Text: Primary color
│   └── Text Button Style
│       ├── Background: Transparent
│       ├── Text: Primary color
│       └── Hover: Surface variant
├── Text Styles
│   ├── Headline (size: 24, weight: bold)
│   ├── Title (size: 18, weight: bold)
│   ├── Body (size: 14, weight: normal)
│   └── Caption (size: 12, color: outline)
└── Component Themes
    ├── Navigation Rail Theme
    ├── Data Table Theme
    ├── Dialog Theme
    └── Toast Theme
```

### Typography Scale
| Style           | Size | Weight  | Usage           |
|-----------------|------|---------|-----------------|
| Display Large   | 57px | Regular | Hero text       |
| Display Medium  | 45px | Regular | Large headers   |
| Display Small   | 36px | Regular | Section headers |
| Headline Large  | 32px | Regular | Page titles     |
| Headline Medium | 28px | Regular | Card titles     |
| Headline Small  | 24px | Regular | Dialog titles   |
| Title Large     | 22px | Medium  | List headers    |
| Title Medium    | 16px | Medium  | Card subtitles  |
| Title Small     | 14px | Medium  | Section labels  |
| Label Large     | 14px | Medium  | Button text     |
| Label Medium    | 12px | Medium  | Form labels     |
| Label Small     | 11px | Medium  | Captions        |
| Body Large      | 16px | Regular | Main content    |
| Body Medium     | 14px | Regular | Body text       |
| Body Small      | 12px | Regular | Supporting text |

### Responsive Design System
```
Responsive Layout Grid
├── Breakpoints
│   ├── sm: 600px (Mobile)
│   ├── md: 960px (Tablet)
│   ├── lg: 1280px (Desktop)
│   └── xl: 1920px (Large Desktop)
├── Column System
│   ├── 12-column grid
│   ├── Responsive column allocation
│   ├── Auto-sizing with expand=True
│   └── Flexible spacing
├── Component Adaptation
│   ├── ResponsiveRow usage
│   ├── Conditional layouts
│   ├── Scalable components
│   └── Mobile-first design
└── Layout Patterns
    ├── Dashboard: 3-column grid
    ├── Tables: Full-width responsive
    ├── Forms: 2-column on desktop
    └── Navigation: Collapsible rail
```

---

## Assets & Resources

### Icon System
```
Material Design Icons (ft.Icons)
├── Navigation Icons
│   ├── DASHBOARD, DASHBOARD_OUTLINED
│   ├── PEOPLE, PEOPLE_OUTLINE
│   ├── FOLDER, FOLDER_OUTLINED
│   ├── STORAGE, STORAGE_OUTLINED
│   ├── AUTO_GRAPH, AUTO_GRAPH_OUTLINED
│   ├── ARTICLE, ARTICLE_OUTLINED
│   └── SETTINGS, SETTINGS_OUTLINED
├── Action Icons
│   ├── PLAY_ARROW, STOP, REFRESH
│   ├── DOWNLOAD, UPLOAD, DELETE
│   ├── EDIT, VISIBILITY, SEARCH
│   ├── FILTER_LIST, SORT, CLEAR
│   └── SAVE, RESTORE, BACKUP
├── Status Icons
│   ├── CHECK_CIRCLE, ERROR, WARNING
│   ├── INFO, HELP_OUTLINE
│   ├── RADIO_BUTTON_CHECKED/OFF
│   └── CLOUD_SYNC, CLOUD_OFF
├── System Icons
│   ├── BRIGHTNESS_6 (Theme toggle)
│   ├── FULLSCREEN, MINIMIZE
│   ├── NOTIFICATIONS, NOTIFICATIONS_OFF
│   └── ACCOUNT_CIRCLE, LOGOUT
└── Data Icons
    ├── TABLE_VIEW, CHART_BAR
    ├── TIMELINE, MONITOR_HEART
    ├── DATABASE, SERVER
    └── FILE_COPY, FOLDER_OPEN
```

### Color Resources
```
Theme Color Palette
├── Semantic Colors
│   ├── Success: Green variants (#4CAF50)
│   ├── Warning: Orange variants (#FF9800)
│   ├── Error: Red variants (#F44336)
│   ├── Info: Blue variants (#2196F3)
│   └── Neutral: Grey variants (#9E9E9E)
├── Status Colors
│   ├── Online: Green (#4CAF50)
│   ├── Offline: Grey (#9E9E9E)
│   ├── Error: Red (#F44336)
│   ├── Warning: Orange (#FF9800)
│   └── Processing: Blue (#2196F3)
├── Chart Colors
│   ├── Primary Series: Blue (#2196F3)
│   ├── Secondary Series: Orange (#FF9800)
│   ├── Tertiary Series: Green (#4CAF50)
│   ├── Quaternary Series: Purple (#9C27B0)
│   └── Accent Series: Pink (#E91E63)
└── Data Visualization
    ├── Gradient Stops for Charts
    ├── Heat Map Colors
    ├── Progress Bar Colors
    └── Badge Color Coding
```

### Font Resources
```
Typography System
├── Primary Font Family
│   ├── Font Name: "Inter"
│   ├── Fallback: System fonts
│   ├── Weights: 300, 400, 500, 600, 700
│   └── Styles: Normal, Italic
├── Monospace Font (Code)
│   ├── Font Name: "Consolas" / "Monaco"
│   ├── Usage: SQL Editor, Log Display
│   ├── Weights: 400, 600
│   └── Line Height: 1.4
└── Icon Font
    ├── Material Design Icons
    ├── Vector-based rendering
    ├── Scalable sizing
    └── Color theme integration
```

### Image Resources
```
Application Images
├── Logo Assets
│   ├── App Icon (Various sizes)
│   ├── Navigation Header Logo
│   ├── About Dialog Logo
│   └── Loading Screen Logo
├── Status Indicators
│   ├── Connection Status Icons
│   ├── Progress Indicators
│   ├── Success/Error Graphics
│   └── Empty State Illustrations
├── Chart Assets
│   ├── Chart Background Patterns
│   ├── Data Point Markers
│   ├── Loading Animations
│   └── Export Format Icons
└── File Type Icons
    ├── Generic File Icon
    ├── Text File Icon
    ├── Image File Icon
    ├── Archive File Icon
    └── Unknown Type Icon
```

### Animation Resources
```
Animation System
├── Page Transitions
│   ├── View Switch Animations
│   ├── Fade In/Out (200ms)
│   ├── Scale Effects (300ms)
│   └── Slide Transitions (250ms)
├── Component Animations
│   ├── Button Press Effects
│   ├── Card Hover Animations
│   ├── Dialog Entrance/Exit
│   └── Loading Spinners
├── Data Animations
│   ├── Chart Updates
│   ├── Progress Bar Animations
│   ├── Counter Animations
│   └── Table Row Animations
├── Feedback Animations
│   ├── Success Checkmarks
│   ├── Error Shakes
│   ├── Warning Pulses
│   └── Info Slides
└── Animation Curves
    ├── EASE_IN_OUT (Standard)
    ├── EASE_OUT (Entrance)
    ├── EASE_IN (Exit)
    ├── DECELERATE (Smooth)
    └── BOUNCE (Playful)
```

---

## Layout & Containers

### Main Application Layout
```
Application Structure
├── Page Container (ft.Page)
│   ├── Theme: Material Design 3
│   ├── Title: "Flet Server GUI"
│   ├── Window Size: 1200x800 (min)
│   └── Responsive: True
├── Main Layout (Row)
│   ├── NavigationRail (Left, 72px min width)
│   │   ├── Extended Mode: 256px
│   │   ├── Label Type: All/Selected
│   │   ├── Destinations: 7 items
│   │   └── Animation: Scale/Opacity
│   └── Content Area (Expanding)
│       ├── Dynamic Content Container
│       ├── View-specific Layouts
│       ├── Responsive Adaptation
│       └── Error Boundaries
└── Overlay System
    ├── Dialogs (Modal)
    ├── Snackbars (Feedback)
    ├── File Pickers
    └── Context Menus
```

### Container Hierarchy
```
Container Types by Usage
├── Layout Containers
│   ├── Column (Vertical stacking)
│   ├── Row (Horizontal arrangement)
│   ├── ResponsiveRow (Grid-based layout)
│   ├── Stack (Layered positioning)
│   └── Container (General wrapper)
├── Data Containers
│   ├── Card (Elevated surface)
│   ├── DataTable (Structured data)
│   ├── ListView (Scrollable lists)
│   ├── GridView (Grid layouts)
│   └── Tabs (Sectioned content)
├── Input Containers
│   ├── Form (Input grouping)
│   ├── TextField (Text input)
│   ├── Dropdown (Selection)
│   ├── Slider (Range input)
│   └── Switch (Boolean input)
├── Feedback Containers
│   ├── AlertDialog (Modal dialogs)
│   ├── SnackBar (Toast messages)
│   ├── ProgressBar (Loading states)
│   ├── Tooltip (Help text)
│   └── Badge (Notifications)
└── Specialized Containers
    ├── NavigationRail (Side navigation)
    ├── AppBar (Top navigation)
    ├── BottomSheet (Slide-up panels)
    ├── Banner (Announcements)
    └── ExpansionTile (Collapsible content)
```

### Responsive Layout Patterns
```
Breakpoint Behavior
├── Mobile (sm: <600px)
│   ├── NavigationRail: Collapsed
│   ├── Content: Full width
│   ├── Cards: Single column
│   ├── Tables: Horizontal scroll
│   └── Dialogs: Full screen
├── Tablet (md: 600-960px)
│   ├── NavigationRail: Icons + labels
│   ├── Content: Padded
│   ├── Cards: 2-column grid
│   ├── Tables: Responsive columns
│   └── Dialogs: Modal overlays
├── Desktop (lg: 960-1280px)
│   ├── NavigationRail: Extended optional
│   ├── Content: Multi-column
│   ├── Cards: 3-column grid
│   ├── Tables: Full feature set
│   └── Dialogs: Centered modals
└── Large Desktop (xl: >1280px)
    ├── NavigationRail: Extended default
    ├── Content: Wide layouts
    ├── Cards: 4-column grid
    ├── Tables: Extra columns visible
    └── Dialogs: Large modals
```

### Spacing System
```
Spacing Scale (Material Design 3)
├── Base Unit: 4px
├── Spacing Values
│   ├── xs: 4px (tight spacing)
│   ├── sm: 8px (small spacing)
│   ├── md: 16px (medium spacing)
│   ├── lg: 24px (large spacing)
│   ├── xl: 32px (extra large)
│   └── xxl: 48px (section spacing)
├── Component Spacing
│   ├── Button Padding: 16px horizontal, 8px vertical
│   ├── Card Padding: 16px all sides
│   ├── List Item Padding: 16px horizontal, 12px vertical
│   ├── Form Field Spacing: 16px vertical gap
│   └── Section Spacing: 24px between sections
└── Layout Margins
    ├── Page Margins: 16px (mobile), 24px (desktop)
    ├── Content Margins: 16px standard
    ├── Card Margins: 8px between cards
    └── Component Margins: 4px-8px standard
```

### Elevation System
```
Material Design Elevation Levels
├── Surface (0dp)
│   ├── Page Background
│   ├── Card Default State
│   └── Input Fields
├── Level 1 (1dp)
│   ├── Search Bars
│   ├── Cards (hover)
│   └── Switch Track
├── Level 2 (3dp)
│   ├── Standard Cards
│   ├── Raised Buttons
│   └── Selection Controls
├── Level 3 (6dp)
│   ├── Floating Action Buttons
│   ├── Snackbars
│   └── Standard Menus
├── Level 4 (8dp)
│   ├── Navigation Drawers
│   ├── Modal Sheets
│   └── Standard Dialogs
├── Level 5 (12dp)
│   ├── Full-screen Dialogs
│   └── Large Components
└── Overlay (24dp)
    ├── System Dialogs
    ├── Error States
    └── Modal Overlays
```

---

## Window & Lifecycle

### Application Lifecycle
```
Application Startup
├── Phase 1: Initialization
│   ├── Import UTF-8 solution
│   ├── Initialize Flet page
│   ├── Set window properties
│   ├── Apply Material Design 3 theme
│   └── Create main application instance
├── Phase 2: Component Setup
│   ├── Initialize ThemeManager
│   ├── Create NavigationManager
│   ├── Initialize DialogSystem
│   ├── Setup ToastManager
│   └── Create ServerBridge
├── Phase 3: View Creation
│   ├── Initialize all view classes
│   ├── Setup view-specific components
│   ├── Configure event handlers
│   ├── Load initial data
│   └── Setup real-time monitoring
├── Phase 4: UI Assembly
│   ├── Build navigation rail
│   ├── Create main layout
│   ├── Setup responsive behavior
│   ├── Initialize first view
│   └── Start background tasks
└── Phase 5: Runtime Ready
    ├── Display application window
    ├── Start real-time updates
    ├── Enable user interactions
    ├── Begin monitoring tasks
    └── Log successful startup
```

### Window Management
```
Window Configuration
├── Window Properties
│   ├── Title: "Backup Server - Flet GUI"
│   ├── Icon: Application icon
│   ├── Minimum Size: 1000x700
│   ├── Initial Size: 1200x800
│   ├── Resizable: True
│   ├── Maximizable: True
│   └── Center on Screen: True
├── Window States
│   ├── Normal (Windowed)
│   ├── Maximized
│   ├── Minimized
│   ├── Full Screen (F11)
│   └── Always on Top (Optional)
├── Window Events
│   ├── on_window_resize
│   ├── on_window_close
│   ├── on_window_focus
│   ├── on_window_blur
│   └── on_window_state_change
└── Window Persistence
    ├── Save window position
    ├── Save window size
    ├── Restore on startup
    └── Multi-monitor support
```

### Page Lifecycle Events
```
Page Event Handlers
├── Page Initialization
│   ├── on_page_load
│   │   ├── Initialize components
│   │   ├── Load user preferences
│   │   ├── Setup themes
│   │   └── Configure layouts
│   ├── on_page_connect
│   │   ├── Start async tasks
│   │   ├── Begin monitoring
│   │   ├── Connect to server
│   │   └── Load real-time data
│   └── on_page_ready
│       ├── Display interface
│       ├── Enable interactions
│       ├── Log ready state
│       └── Focus first element
├── Runtime Events
│   ├── on_page_resize
│   │   ├── Update responsive layouts
│   │   ├── Recalculate dimensions
│   │   ├── Adjust component sizes
│   │   └── Update scroll areas
│   ├── on_page_route_change
│   │   ├── Cleanup old view
│   │   ├── Initialize new view
│   │   ├── Update navigation state
│   │   └── Load view data
│   ├── on_page_error
│   │   ├── Display error dialog
│   │   ├── Log error details
│   │   ├── Attempt recovery
│   │   └── Fallback to safe state
│   └── on_page_theme_change
│       ├── Update component themes
│       ├── Recalculate colors
│       ├── Apply new styling
│       └── Persist theme choice
└── Shutdown Events
    ├── on_page_disconnect
    │   ├── Save application state
    │   ├── Stop background tasks
    │   ├── Close connections
    │   └── Cleanup resources
    ├── on_page_close
    │   ├── Confirm unsaved changes
    │   ├── Save window state
    │   ├── Stop all services
    │   └── Exit gracefully
    └── on_page_unload
        ├── Final cleanup
        ├── Memory deallocation
        ├── Log shutdown
        └── Process termination
```

### Background Task Management
```
Async Task System
├── Monitoring Tasks
│   ├── Server Status Monitoring
│   │   ├── Task Name: server_monitor
│   │   ├── Interval: 5 seconds
│   │   ├── Function: Check server status
│   │   └── Error Handling: Retry with backoff
│   ├── Performance Monitoring
│   │   ├── Task Name: performance_monitor
│   │   ├── Interval: 10 seconds
│   │   ├── Function: Collect system metrics
│   │   └── Data: CPU, Memory, Network
│   ├── Log Monitoring
│   │   ├── Task Name: log_monitor
│   │   ├── Interval: 2 seconds
│   │   ├── Function: Read new log entries
│   │   └── Filter: Real-time log streaming
│   └── Database Monitoring
│       ├── Task Name: db_monitor
│       ├── Interval: 30 seconds
│       ├── Function: Check DB health
│       └── Metrics: Connection, Size, Performance
├── UI Update Tasks
│   ├── Chart Updates
│   │   ├── Task Name: chart_updater
│   │   ├── Interval: 15 seconds
│   │   ├── Function: Refresh chart data
│   │   └── Views: Dashboard, Analytics
│   ├── Table Refresh
│   │   ├── Task Name: table_refresh
│   │   ├── Trigger: Data change events
│   │   ├── Function: Update table contents
│   │   └── Debouncing: 1 second delay
│   └── Status Updates
│       ├── Task Name: status_updater
│       ├── Interval: 3 seconds
│       ├── Function: Update status displays
│       └── Components: Cards, indicators
├── Cleanup Tasks
│   ├── Memory Cleanup
│   │   ├── Task Name: memory_cleaner
│   │   ├── Interval: 5 minutes
│   │   ├── Function: Clear unused data
│   │   └── Target: Caches, old entries
│   ├── Log Rotation
│   │   ├── Task Name: log_rotator
│   │   ├── Interval: 1 hour
│   │   ├── Function: Archive old logs
│   │   └── Retention: Configurable period
│   └── Temp File Cleanup
│       ├── Task Name: temp_cleaner
│       ├── Interval: 30 minutes
│       ├── Function: Remove temp files
│       └── Location: System temp directory
└── Task Management
    ├── Task Registry (Dict of active tasks)
    ├── Task Lifecycle (Start, Stop, Restart)
    ├── Error Recovery (Automatic restart)
    ├── Performance Monitoring (Task metrics)
    └── Graceful Shutdown (Task termination)
```

---

## Core Services & Business Logic

### Business Logic Layer (`core/`)
```
Core Services Architecture
├── ServerOperations (server_operations.py)
│   ├── Server Lifecycle Management
│   │   ├── start_server() - Start backup server process
│   │   ├── stop_server() - Stop backup server process
│   │   ├── restart_server() - Restart backup server
│   │   └── get_server_status() - Check server health
│   ├── Process Management
│   │   ├── Process monitoring and health checks
│   │   ├── Port availability checking
│   │   ├── Service dependency validation
│   │   └── Graceful shutdown handling
│   └── System Integration
│       ├── get_system_metrics() - CPU/Memory/Disk usage
│       ├── get_network_stats() - Network activity
│       └── get_server_info() - Server configuration
├── ClientManagement (client_management.py)
│   ├── CRUD Operations
│   │   ├── create_client() - Add new client
│   │   ├── get_clients() - Retrieve client list
│   │   ├── update_client() - Modify client details
│   │   └── delete_client() - Remove client
│   ├── Bulk Operations
│   │   ├── bulk_delete_clients() - Delete multiple clients
│   │   ├── import_clients() - Import from file
│   │   └── export_clients() - Export to file
│   ├── Client Analytics
│   │   ├── get_client_stats() - Connection statistics
│   │   ├── get_transfer_history() - File transfer logs
│   │   └── get_client_activity() - Recent activity
│   └── Validation & Security
│       ├── validate_client_data() - Data validation
│       ├── check_client_permissions() - Access control
│       └── sanitize_client_input() - Security sanitization
├── FileManagement (file_management.py)
│   ├── File Operations
│   │   ├── get_files() - Retrieve file listings
│   │   ├── download_file() - File download operations
│   │   ├── delete_file() - File deletion with verification
│   │   └── verify_file_integrity() - CRC32 verification
│   ├── Bulk File Operations
│   │   ├── bulk_download() - Download multiple files
│   │   ├── bulk_verify() - Verify multiple files
│   │   └── bulk_delete() - Delete multiple files
│   ├── File Analysis
│   │   ├── get_file_stats() - File statistics
│   │   ├── analyze_file_types() - File type analysis
│   │   └── get_storage_usage() - Storage analytics
│   └── File Monitoring
│       ├── watch_received_files() - Real-time file monitoring
│       ├── detect_file_changes() - Change detection
│       └── update_file_metadata() - Metadata management
└── SystemIntegration (system_integration.py)
    ├── Database Integration
    │   ├── get_database_health() - Database status
    │   ├── backup_database() - Database backup operations
    │   └── optimize_database() - Database maintenance
    ├── System Monitoring
    │   ├── collect_performance_metrics() - Real-time metrics
    │   ├── monitor_system_health() - Health monitoring
    │   └── generate_system_reports() - Report generation
    └── Advanced Operations
        ├── file_integrity_verification() - Advanced file checking
        ├── session_management() - User session handling
        └── system_diagnostics() - Diagnostic operations
```

### Background Services (`services/`)
```
Background Services Architecture
├── LogService (log_service.py)
│   ├── Real-time Log Monitoring
│   │   ├── start_monitoring() - Start log file watching
│   │   ├── stop_monitoring() - Stop log monitoring
│   │   ├── get_pending_updates() - Get new log entries
│   │   └── get_recent_logs() - Retrieve recent entries
│   ├── Log Processing
│   │   ├── parse_log_entry() - Parse log format
│   │   ├── filter_logs() - Apply filters
│   │   ├── search_logs() - Text search
│   │   └── export_logs() - Export to file
│   ├── Log Analysis
│   │   ├── get_log_stats() - Statistics
│   │   ├── detect_error_patterns() - Error analysis
│   │   └── generate_log_summary() - Summary reports
│   └── Configuration
│       ├── set_log_level() - Configure log levels
│       ├── set_retention_policy() - Log retention
│       └── configure_sources() - Log source configuration
├── ConfigurationService (configuration.py)
│   ├── Settings Management
│   │   ├── load_settings() - Load configuration
│   │   ├── save_settings() - Persist settings
│   │   ├── validate_settings() - Setting validation
│   │   └── reset_settings() - Reset to defaults
│   ├── Configuration Categories
│   │   ├── Server Configuration
│   │   ├── GUI Settings
│   │   ├── Monitoring Configuration
│   │   └── Advanced Settings
│   ├── Change Management
│   │   ├── track_changes() - Change tracking
│   │   ├── create_backup() - Configuration backup
│   │   └── restore_backup() - Restore configuration
│   └── Validation & Security
│       ├── validate_config_integrity() - Integrity checking
│       ├── encrypt_sensitive_data() - Data encryption
│       └── audit_configuration_changes() - Audit logging
├── MonitoringService (monitoring.py)
│   ├── System Monitoring
│   │   ├── collect_metrics() - System metrics collection
│   │   ├── monitor_thresholds() - Threshold monitoring
│   │   ├── generate_alerts() - Alert generation
│   │   └── track_performance() - Performance tracking
│   ├── Alert Management
│   │   ├── create_alert() - Alert creation
│   │   ├── resolve_alert() - Alert resolution
│   │   ├── escalate_alert() - Alert escalation
│   │   └── get_alert_history() - Alert history
│   ├── Data Collection
│   │   ├── cpu_monitoring() - CPU usage tracking
│   │   ├── memory_monitoring() - Memory usage tracking
│   │   ├── disk_monitoring() - Disk usage tracking
│   │   └── network_monitoring() - Network activity tracking
│   └── Reporting
│       ├── generate_performance_report() - Performance reports
│       ├── export_metrics_data() - Data export
│       └── create_dashboard_data() - Dashboard data
└── DataExportService (data_export.py)
    ├── Export Operations
    │   ├── export_clients() - Client data export
    │   ├── export_files() - File listings export
    │   ├── export_logs() - Log data export
    │   └── export_settings() - Configuration export
    ├── Format Support
    │   ├── export_to_csv() - CSV format export
    │   ├── export_to_json() - JSON format export
    │   ├── export_to_xml() - XML format export
    │   └── export_to_pdf() - PDF report export
    ├── Import Operations
    │   ├── import_clients() - Client data import
    │   ├── import_settings() - Configuration import
    │   ├── validate_import_data() - Import validation
    │   └── process_bulk_import() - Bulk import processing
    └── Data Transformation
        ├── transform_data_format() - Format conversion
        ├── sanitize_export_data() - Data sanitization
        └── compress_export_files() - File compression
```

---

## Advanced Features

### Real-Time Monitoring System
```
Performance Monitoring Infrastructure
├── EnhancedPerformanceCharts (charts.py)
│   ├── Multi-Metric Monitoring
│   │   ├── CPU Usage Tracking (0.1s intervals)
│   │   ├── Memory Usage Monitoring (real-time)
│   │   ├── Disk Usage Analysis (live updates)
│   │   └── Network Activity Tracking (bytes/sec)
│   ├── Threshold Alert System
│   │   ├── Warning Thresholds (70% CPU, 80% Memory)
│   │   ├── Critical Thresholds (90% CPU, 95% Memory)
│   │   ├── Visual Alert Indicators (color-coded)
│   │   └── Alert History Tracking
│   ├── Interactive Controls
│   │   ├── Time Range Selection (1min - 1hr)
│   │   ├── Chart Type Toggle (Line/Bar/Area)
│   │   ├── Update Interval Control (1-30s)
│   │   └── Data Export Capabilities
│   ├── Advanced Visualization
│   │   ├── Responsive Chart Layouts
│   │   ├── Fullscreen Chart Mode
│   │   ├── Data Point Tooltips
│   │   └── Trend Analysis Indicators
│   └── Data Management
│       ├── Historical Data Storage (300 points max)
│       ├── Real-time Data Aggregation
│       ├── Performance Optimization
│       └── Memory-efficient Storage
├── Chart Types & Components
│   ├── EnhancedBarChart - Real ft.BarChart integration
│   ├── EnhancedLineChart - Real ft.LineChart integration  
│   ├── EnhancedPieChart - Custom pie chart implementation
│   └── MetricCards - Real-time metric displays
└── Chart Factory Functions
    ├── create_bar_chart() - Bar chart factory
    ├── create_line_chart() - Line chart factory
    ├── create_pie_chart() - Pie chart factory
    └── create_enhanced_performance_charts() - Main factory
```

### Advanced Table System
```
EnhancedDataTable (tables.py) - 865 lines of advanced functionality
├── Data Management
│   ├── Dynamic Data Source Integration
│   ├── Real-time Data Refresh
│   ├── Infinite Scroll Support
│   └── Memory-efficient Pagination
├── Advanced Filtering
│   ├── Multi-Column Filtering
│   │   ├── Text Filtering (contains, equals, starts/ends with)
│   │   ├── Numeric Filtering (min/max ranges)
│   │   ├── Date Range Filtering
│   │   └── Boolean Filtering (true/false/all)
│   ├── Global Search Across All Columns
│   ├── Regex Pattern Filtering
│   └── Filter State Persistence
├── Sophisticated Sorting
│   ├── Multi-Column Sorting (with priority)
│   ├── Custom Sort Functions per Column
│   ├── Data Type-aware Sorting (text, number, date)
│   └── Sort Indicator Display
├── Selection & Actions
│   ├── Individual Row Selection
│   ├── Bulk Selection (Select All/None)
│   ├── Row Action Buttons (Edit, Delete, View)
│   ├── Bulk Action Operations
│   └── Context Menu Support
├── Export & Import
│   ├── Export Visible Data
│   ├── Export All Filtered Data
│   ├── Multiple Export Formats
│   └── Import Data Validation
├── Responsive Design
│   ├── Mobile-first Layout
│   ├── Column Auto-sizing
│   ├── Horizontal Scroll for Small Screens
│   └── Adaptive Pagination Controls
└── Performance Features
    ├── Virtual Scrolling for Large Datasets
    ├── Debounced Search Input
    ├── Optimized Re-rendering
    └── Memory Management
```

### File Management System
```
Advanced File Operations
├── FileTableRenderer - Specialized table for files
├── FileFilterManager - Advanced file filtering
│   ├── File Type Filtering
│   ├── File Size Range Filtering
│   ├── Upload Date Filtering
│   └── File Status Filtering
├── FileActionHandlers - File operation processing
│   ├── Individual File Actions
│   │   ├── Download with Progress Tracking
│   │   ├── Delete with Confirmation
│   │   ├── Verify with CRC32 Checking
│   │   └── Preview Generation
│   ├── Bulk File Operations
│   │   ├── Parallel Download Processing
│   │   ├── Batch Verification
│   │   ├── Bulk Delete with Rollback
│   │   └── Progress Reporting
│   └── Error Handling & Recovery
├── FilePreviewManager - File preview system
│   ├── Text File Preview
│   ├── Image File Thumbnails
│   ├── Document Metadata Display
│   └── Binary File Information
└── Real-time File Monitoring
    ├── File System Watching
    ├── Auto-refresh on Changes
    ├── Upload Progress Tracking
    └── File Integrity Verification
```

### Database Integration System
```
Live Database Operations
├── Real Database Connection (SQLite)
├── Database Health Monitoring
│   ├── Connection Status Checking
│   ├── Query Performance Monitoring
│   ├── Database Size Tracking
│   └── Integrity Verification
├── Table Management
│   ├── Dynamic Table Discovery
│   ├── Schema Information Display
│   ├── Row Count Statistics
│   └── Real-time Data Display
├── Database Operations
│   ├── Live Backup Creation
│   ├── Database Optimization (VACUUM)
│   ├── Integrity Analysis
│   └── Performance Tuning
└── Query Interface
    ├── SQL Query Execution
    ├── Results Display with Pagination
    ├── Query History Management
    └── Export Query Results
```

### Log Management System
```
Real-time Log Processing
├── LogService - Core log processing engine
├── Live Log Monitoring
│   ├── File System Watching
│   ├── Real-time Log Parsing
│   ├── Multi-source Log Aggregation
│   └── Log Rotation Handling
├── Advanced Filtering
│   ├── Log Level Filtering (DEBUG through CRITICAL)
│   ├── Component-based Filtering
│   ├── Time Range Filtering
│   └── Text Search with Highlighting
├── Log Analysis
│   ├── Error Pattern Detection
│   ├── Performance Issue Identification
│   ├── Usage Statistics Generation
│   └── Trend Analysis
├── Export & Reporting
│   ├── Filtered Log Export
│   ├── Multiple Export Formats
│   ├── Scheduled Report Generation
│   └── Log Archiving
└── Performance Features
    ├── Efficient Log Parsing
    ├── Memory-bounded Log Storage
    ├── Asynchronous Processing
    └── UI Thread Safety
```

---

## Architecture Overview

### System Architecture Tree
```
Flet Server GUI Architecture
├── Application Layer (main.py)
│   ├── ServerGUIApp (Main application class)
│   ├── Page Configuration (Window, Theme, Layout)
│   ├── Component Initialization
│   └── Lifecycle Management
├── Presentation Layer
│   ├── Views (7 main views)
│   │   ├── DashboardView (System overview)
│   │   ├── ClientsView (Client management)
│   │   ├── FilesView (File operations)
│   │   ├── DatabaseView (DB operations)
│   │   ├── AnalyticsView (Performance metrics)
│   │   ├── LogsView (Log monitoring)
│   │   └── SettingsView (Configuration)
│   ├── UI Components
│   │   ├── Navigation (Rail, Router)
│   │   ├── Widgets (Cards, Tables, Buttons)
│   │   ├── Dialogs (Modal system)
│   │   └── Theme (Material Design 3)
│   └── Layout System
│       ├── Responsive Grid
│       ├── Container Hierarchy
│       ├── Spacing System
│       └── Elevation Levels
├── Business Logic Layer
│   ├── Core Services
│   │   ├── ServerOperations (Start/stop server)
│   │   ├── ClientManagement (CRUD operations)
│   │   ├── FileManagement (File operations)
│   │   └── SystemIntegration (Monitoring)
│   ├── State Management
│   │   ├── ThemeManager (Theme state)
│   │   ├── SettingsManager (Configuration)
│   │   ├── NavigationManager (Route state)
│   │   └── DialogSystem (Modal state)
│   └── Event Handling
│       ├── User Interactions
│       ├── System Events
│       ├── Async Tasks
│       └── Error Handling
├── Data Access Layer
│   ├── ServerBridge (Server communication)
│   │   ├── ModularServerBridge (Full features)
│   │   ├── SimpleServerBridge (Fallback)
│   │   ├── Database Integration
│   │   └── API Communication
│   ├── Configuration Persistence
│   │   ├── Settings Files (JSON)
│   │   ├── User Preferences
│   │   ├── Window State
│   │   └── View State
│   └── Monitoring Services
│       ├── Log Monitoring
│       ├── Performance Metrics
│       ├── System Health
│       └── Real-time Updates
└── Infrastructure Layer
    ├── Flet Framework (Flutter-based)
    ├── Material Design 3 (Design system)
    ├── Python Runtime (3.7+)
    ├── Async/Await Support
    └── Cross-platform Compatibility
```

### Component Dependencies
```
Dependency Graph
├── Core Dependencies
│   ├── flet >= 0.21.0 (GUI framework)
│   ├── asyncio (Async operations)
│   ├── logging (Error tracking)
│   ├── json (Configuration persistence)
│   ├── datetime (Time operations)
│   ├── typing (Type hints)
│   └── pathlib (Path operations)
├── Internal Dependencies
│   ├── ServerBridge → Database Connection
│   ├── Views → ServerBridge
│   ├── Components → ThemeManager
│   ├── Navigation → All Views
│   ├── DialogSystem → All Components
│   └── SettingsManager → Configuration Files
├── Optional Dependencies
│   ├── UTF-8 Solution (International support)
│   ├── Performance Monitoring
│   ├── Advanced Analytics
│   └── Extended Logging
└── Development Dependencies
    ├── Testing Framework
    ├── Code Formatting
    ├── Type Checking
    └── Documentation Tools
```

### Data Flow Architecture
```
Data Flow Patterns
├── User Interaction Flow
│   ├── User Event (Click, Type, Select)
│   ├── Event Handler Execution
│   ├── Business Logic Processing
│   ├── State Updates
│   ├── UI Component Updates
│   └── Visual Feedback
├── Real-time Update Flow
│   ├── Background Task Monitoring
│   ├── Data Source Polling
│   ├── Change Detection
│   ├── State Synchronization
│   ├── Component Notification
│   └── UI Refresh
├── Configuration Flow
│   ├── Settings Form Input
│   ├── Validation Processing
│   ├── Change Tracking
│   ├── Persistence Layer
│   ├── Application State Update
│   └── Component Reconfiguration
└── Error Handling Flow
    ├── Exception Detection
    ├── Error Classification
    ├── Recovery Attempt
    ├── User Notification
    ├── State Rollback
    └── Logging/Reporting
```

---

### ★ Insight ─────────────────────────────────────
**Enterprise-Grade Architecture**: This Flet GUI represents a sophisticated example of production-ready desktop application development using Python. The modular component architecture, comprehensive state management, and Material Design 3 compliance demonstrate professional software engineering practices that rival traditional desktop frameworks like Qt or WPF.

**Real-World Integration**: Unlike typical GUI demos, this system integrates with actual production infrastructure (5-layer backup framework), manages real database connections, handles live file operations, and provides enterprise monitoring capabilities. The dual ServerBridge system (full/simple fallback) shows robust error handling patterns essential for production applications.

**Modern UI/UX Patterns**: The responsive design system, comprehensive event handling, and sophisticated navigation management showcase contemporary application design principles. The combination of Material Design 3 theming, animated transitions, and professional data visualization creates a user experience comparable to modern web applications but with native desktop performance.
`─────────────────────────────────────────────────`

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Explore main Flet GUI structure and identify all components", "status": "completed", "activeForm": "Exploring main Flet GUI structure and identifying all components"}, {"content": "Catalog all buttons across the entire GUI system", "status": "completed", "activeForm": "Cataloging all buttons across the entire GUI system"}, {"content": "Document all widgets/controls by category and view", "status": "completed", "activeForm": "Documenting all widgets/controls by category and view"}, {"content": "List all event handlers and their functions", "status": "completed", "activeForm": "Listing all event handlers and their functions"}, {"content": "Document state management systems", "status": "completed", "activeForm": "Documenting state management systems"}, {"content": "Document navigation and routing components", "status": "completed", "activeForm": "Documenting navigation and routing components"}, {"content": "Document theming and styling systems", "status": "completed", "activeForm": "Documenting theming and styling systems"}, {"content": "List all assets and resources", "status": "completed", "activeForm": "Listing all assets and resources"}, {"content": "Document layout and container systems", "status": "completed", "activeForm": "Documenting layout and container systems"}, {"content": "Document window and lifecycle management", "status": "completed", "activeForm": "Documenting window and lifecycle management"}, {"content": "Create comprehensive markdown file with all findings", "status": "completed", "activeForm": "Creating comprehensive markdown file with all findings"}]