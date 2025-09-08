---
description: Essential AI development guidance for the encrypted backup framework
globs: *
---

# Copilot Instructions - Encrypted Backup Framework

AI coding agents should follow these guidelines when working on this multi-component encrypted backup system.

## 🏗️ System Architecture

This is a **5-component encrypted backup framework**:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   C++ Client    │───▶│  Python Server   │───▶│    Database     │
│                 │    │                  │    │   (SQLite3)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Web GUI (JS)    │    │ Desktop GUI      │    │ Server Bridge   │
│ Tailwind CSS    │    │ (FletV2)         │    │ Communication   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Encryption**: RSA-1024 key exchange + AES-256-CBC file encryption
**Database**: SQLite3 with clients, files, logs tables
**Communication**: Socket-based with JSON protocol

## 🎯 Primary Development Directory

**CRITICAL**: Work exclusively with `FletV2/` directory for desktop GUI development.
- `flet_server_gui/` is obsolete and over-engineered
- Reference `CLAUDE.md` for detailed Flet patterns and best practices

## 🚀 Launch Commands

```bash
# FletV2 Development (Hot Reload)
cd FletV2 && flet run -r main.py

# FletV2 Production
cd FletV2 && python main.py

# System Integration Testing
python scripts/one_click_build_and_run.py
```

## 📁 Key Directories & Files

```
FletV2/                           # Desktop GUI (PRIMARY)
├── main.py                       # Application entry point
├── theme.py                      # Material Design 3 theming
├── views/                        # UI views (function-based)
│   ├── dashboard.py              # Server overview
│   ├── clients.py                # Client management
│   ├── files.py                  # File browser
│   └── database.py               # Database viewer
└── utils/                        # Helper utilities
    ├── server_bridge.py          # Server communication
    └── utf8_solution.py          # UTF-8 handling

python_server/                    # Backend server
Client/                           # C++ client application
api_server/                       # Flask web API bridge
scripts/                          # Automation tools
```

## 🔧 Critical Development Patterns

### **Framework Harmony (Flet)**
- Use `ft.NavigationRail` for navigation (not custom routers)
- Use `expand=True` + `ResponsiveRow` for layouts
- Use `control.update()` not `page.update()` for performance
- Prefer Flet built-ins over custom components

### **UTF-8 Handling**
```python
# ALWAYS import in files with subprocess/console I/O
import Shared.utils.utf8_solution
```

### **Server Bridge Pattern**
```python
# Enhanced bridge with fallback
from utils.server_bridge import ServerBridge
bridge = ServerBridge(real_server_instance=None)  # Auto-fallback to mock
```

### **File Size Guidelines**
- View files: ~200-500 lines maximum
- Component files: ~100-400 lines maximum
- If >600 lines: mandatory decomposition required

## 🚨 Anti-Patterns (Never Do These)

- Custom navigation managers (use `ft.NavigationRail`)
- Custom responsive systems (use `expand=True`)
- Complex theme managers (use `page.theme`)
- `page.update()` abuse (use `control.update()`)
- Hardcoded dimensions (use responsive patterns)

## 🔍 Integration Points

### **Database Schema**
- `clients` table: id, name, status, last_seen
- `files` table: id, client_id, filename, path, size, checksum
- `logs` table: id, timestamp, level, component, message

### **Communication Protocol**
- JSON-based socket communication
- Server bridge handles connection management
- Automatic fallback to mock data for development

### **Development Workflow**
1. Develop in `FletV2/` using hot reload
2. Test with mock data (automatic fallback)
3. Integration test with full system
4. Reference `CLAUDE.md` for detailed Flet guidance

## 💡 Quick Reference

- **Theme**: Material Design 3 with system detection
- **Colors**: Semantic color tokens (`ft.Colors.PRIMARY`)
- **Layout**: Responsive with `ft.ResponsiveRow`
- **Navigation**: `ft.NavigationRail` with 7 destinations
- **Data**: Server bridge with automatic mock fallback
- **Encryption**: RSA + AES for secure file transfer

Follow these patterns for consistent, maintainable code that works with the framework rather than against it.

│   ├── dashboard.py          # Server dashboard
│   ├── clients.py            # Client management
│   ├── files.py              # File browser
│   ├── database.py           # Database viewer
│   ├── analytics.py          # Analytics charts
│   ├── logs.py               # Log viewer
│   └── settings.py           # Configuration
└── utils/                     # Helper utilities
    ├── debug_setup.py        # Terminal debugging
    ├── server_bridge.py      # Full server integration
    └── simple_server_bridge.py # Fallback bridge
```

### **Launch Commands**
```bash
# FletV2 Desktop (Production/Testing)
cd FletV2 && python main.py

# FletV2 Development with Hot Reload (RECOMMENDED for development)
# Uses desktop for instant hot reload - identical runtime to desktop
cd FletV2
flet run -r main.py

# Alternative: Command-line hot reload
cd FletV2 && flet run --web main.py

# System integration testing (only after FletV2 is complete, and the user approved)
python scripts/one_click_build_and_run.py
```

### **Development Workflow (Desktop Apps)**
  ★ Insight ─────────────────────────────────────
  Hot Reload Validation: The WEB_BROWSER view for desktop development is a Flet best practice - it provides identical runtime behavior to native desktop while enabling instant hot reload. The workflow is: develop in browser → test in native desktop → deploy as desktop app.
  ─────────────────────────────────────────────────
**Recommended Pattern**: Develop in browser → Test in native desktop → Deploy as desktop app
- **Browser development**: Instant hot reload, identical Flet runtime, browser dev tools available
- **Native testing**: Final validation of desktop-specific features, window management, OS integration
- **Both modes**: Run the exact same Flet application code - no differences in functionality

---

## 🔧 SEARCH & DEVELOPMENT TOOLS

You have access to ast-grep for syntax-aware searching:
- **Structural matching**: `ast-grep --lang python -p 'class $NAME($BASE)'`
- **Fallback to ripgrep**: Only when ast-grep isn't applicable
- **Never use basic grep**: ripgrep is always better for codebase searches (basic grep when other tools fail)

---

## 💡 KEY INSIGHTS

**★ Framework Enlightenment**: Desktop resizable apps with navigation are trivial in Flet. The entire application can be ~700 lines instead of 10,000+ lines of framework-fighting code(not really, but to illustrate the point).

**★ The Semi-Nuclear Protocol**: When refactoring complex code, analyze first to understand TRUE intentions, then rebuild with simple Flet patterns while preserving valuable business logic, achieving feature parity.

**★ Performance Secret**: Replacing `page.update()` with `control.update()` can improve performance by 10x+ and eliminate UI flicker.

**The FletV2 directory is the CANONICAL REFERENCE** for proper Flet desktop development. When in doubt, follow its examples exactly.

---

## 📝 .gitignore Management
When modifying the `.gitignore` file, adhere to the following guidelines:
- **Avoid Duplication**: Ensure each ignore rule is unique and doesn't overlap with existing rules.
- **Consolidation**: Group related rules together (e.g., all `.vscode` related ignores should be under the `.vscode/*` section).
- **Clarity**: Use comments to explain complex or project-specific ignore rules.

---

## 💻 VS Code Configuration

### **Python Interpreter Path**
To ensure VS Code uses the correct Python interpreter for the FletV2 project, set the `python.defaultInterpreterPath` in `.vscode/settings.json` to the Flet virtual environment:

```jsonc
{
    // ...existing code...
    "python.defaultInterpreterPath": "./flet_venv/Scripts/python.exe",
    // ...existing code...
}
```