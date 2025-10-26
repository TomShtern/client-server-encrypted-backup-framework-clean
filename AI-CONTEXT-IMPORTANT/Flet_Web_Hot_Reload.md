# Flet Desktop App Hot-Reload in Web Mode (v0.28.3)

## Why Use Web Mode for Hot-Reload?

Web mode provides **more stable hot-reload** than desktop mode in Flet 0.28.3. Desktop mode can have connection issues and file watching problems, while web mode uses a robust web server architecture that handles file changes and reconnections more reliably.

## Benefits of Web Mode Hot-Reload

- ✅ **More reliable**: Consistent file change detection
- ✅ **Faster reloads**: Better connection handling
- ✅ **Same functionality**: Your desktop app works identically
- ✅ **Browser dev tools**: Access to debugging tools
- ✅ **Port consistency**: Fixed port for predictable development

## Quick Start

The fastest way to enable stable hot-reload for your desktop app:

```bash
flet run --web -d -r main.py
```

This command will:
- Launch your app in a web browser
- Watch your project directory (`-d`)
- Watch subdirectories recursively (`-r`)
- Enable automatic reloading on file changes

## Method 1: Command Line Configuration (Recommended)

### Basic Web Hot-Reload
```bash
flet run --web main.py
```

### Watch Project Directory
```bash
flet run --web -d main.py
```

### Watch Project + Subdirectories (Best for Multi-File Projects)
```bash
flet run --web -d -r main.py
```

### With Custom Port
```bash
flet run --web -p 8550 -d -r main.py
```

### With Host Configuration (Access from Other Devices)
```bash
flet run --web --host "*" -p 8550 -d -r main.py
```

## Method 2: Code Configuration

If you prefer to configure web mode in your Python code:

### Basic Setup

```python
import flet as ft

def main(page: ft.Page):
    page.title = "My Desktop App"
    page.window.width = 800
    page.window.height = 600

    # Your existing desktop app UI code here
    page.add(
        ft.Text("Hello from web mode!", size=20),
        ft.ElevatedButton("Click me!", on_click=lambda e: print("Clicked!"))
    )

# Configure for web browser view
ft.app(target=main, view=ft.AppView.WEB_BROWSER)
```

Run with:
```bash
flet run -d -r main.py
```

### With Fixed Port and Host

```python
import flet as ft

def main(page: ft.Page):
    page.title = "My Desktop App"
    # Your UI code here
    pass

# Configure with specific port and host
ft.app(
    target=main,
    view=ft.AppView.WEB_BROWSER,
    port=8550,
    host="localhost"  # or "*" for all interfaces
)
```

Run with:
```bash
flet run -d -r main.py
```

## Advanced Configuration

### Ignore Specific Directories

Improve performance by ignoring unnecessary directories:

```bash
flet run --web -d -r --ignore-dirs "__pycache__,venv,.git,node_modules" main.py
```

### Enable Verbose Logging

For debugging hot-reload issues:

```bash
flet run --web -d -r -v main.py
```

### Multiple Verbose Levels

```bash
flet run --web -d -r -vv main.py  # More detailed logging
```

## Converting Existing Desktop App

If you have an existing desktop app, here's how to convert it for web mode hot-reload:

### Before (Desktop Mode)
```python
import flet as ft

def main(page: ft.Page):
    page.title = "My App"
    # Your UI code
    pass

ft.app(target=main)  # Default is desktop
```

### After (Web Mode)
```python
import flet as ft

def main(page: ft.Page):
    page.title = "My App"
    # Same UI code - no changes needed!
    pass

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
```

## Project Structure Example

```
my-flet-app/
├── main.py                 # Your main app file
├── components/
│   ├── __init__.py
│   ├── sidebar.py
│   ├── header.py
│   └── dashboard.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── assets/
│   ├── images/
│   └── styles.css
└── requirements.txt
```

**Command to use:**
```bash
flet run --web -d -r -p 8550 main.py
```

## VS Code Integration

Create a launch configuration for VS Code with web mode hot-reload:

### .vscode/launch.json
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flet Web Hot-Reload",
            "type": "python",
            "request": "launch",
            "module": "flet",
            "args": [
                "run",
                "--web",
                "-d",
                "-r",
                "-p",
                "8550",
                "main.py"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

Now you can press **F5** to start debugging with web-based hot-reload.

## Common Command Patterns

### Development Mode (Most Common)
```bash
flet run --web -d -r main.py
```

### Development with Fixed Port
```bash
flet run --web -p 8550 -d -r main.py
```

### Testing on Network
```bash
flet run --web --host "*" -p 8550 -d -r main.py
```

### Single File Development
```bash
flet run --web main.py
```

### Production-Like Testing
```bash
flet run --web --host "0.0.0.0" -p 80 main.py
```

## Troubleshooting Web Mode Hot-Reload

### Issue: Port Already in Use
```bash
# Try a different port
flet run --web -p 8551 -d -r main.py
```

### Issue: Can't Access from Other Devices
```bash
# Use wildcard host
flet run --web --host "*" -p 8550 -d -r main.py
```

### Issue: Changes Not Detected
```bash
# Ensure you're watching directories
flet run --web -d -r main.py

# Or check file permissions
ls -la main.py
```

### Issue: Too Many File Watchers
```bash
# Ignore unnecessary directories
flet run --web -d -r --ignore-dirs "__pycache__,venv,.git" main.py
```

## Environment Variables

You can also set environment variables for consistent configuration:

```bash
export FLET_LOG_LEVEL=info
export FLET_WEB_HOST="localhost"
export FLET_WEB_PORT=8550

flet run --web -d -r main.py
```

## Performance Optimization

### 1. Ignore Large Directories
```bash
flet run --web -d -r --ignore-dirs "node_modules,venv,__pycache__,.git" main.py
```

### 2. Use Fixed Port
```bash
flet run --web -p 8550 -d -r main.py
```

### 3. Limit Watched Files
```bash
# Only watch specific directory
flet run --web -d components/main.py
```

## Browser Compatibility

Web mode hot-reload works with all modern browsers:
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge

## Key Differences from Desktop Mode

| Feature | Desktop Mode | Web Mode |
|---------|-------------|----------|
| Window Type | Native OS Window | Browser Window |
| Hot-Reload Stability | Sometimes Unstable | Very Stable |
| File Watching | Limited | Robust |
| Dev Tools | None | Browser Dev Tools |
| Network Access | Local Only | Can Share on Network |
| Performance | Native | Near-Native |

## Best Practices

1. **Always use directory watching**: `flet run --web -d -r main.py`
2. **Fix your port**: Use `-p 8550` for consistency
3. **Ignore unnecessary dirs**: Use `--ignore-dirs` for better performance
4. **Use verbose logging**: Add `-v` when debugging hot-reload issues
5. **Test in multiple browsers**: Ensure compatibility
6. **Keep port consistent**: Use the same port across development sessions

## Quick Reference Commands

| Purpose | Command |
|---------|---------|
| Basic web hot-reload | `flet run --web main.py` |
| Full directory watch | `flet run --web -d -r main.py` |
| With fixed port | `flet run --web -p 8550 -d -r main.py` |
| Network accessible | `flet run --web --host "*" -p 8550 -d -r main.py` |
| With debugging | `flet run --web -d -r -v main.py` |
| Ignore directories | `flet run --web -d -r --ignore-dirs "venv,__pycache__" main.py` |

## Conclusion

Web mode provides the most stable hot-reload experience for Flet desktop apps. Use `flet run --web -d -r main.py` as your go-to command for development. Your app will function identically to desktop mode but with much more reliable hot-reload capabilities.

The browser window behaves just like a desktop app window, and you get the added benefit of browser developer tools for debugging. This is the recommended approach for Flet 0.28.3 development.