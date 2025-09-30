# Flet Hot-Reload Setup Guide (v0.28.3)

## Overview

Hot-reload is a development feature that allows you to see code changes in your Flet app instantly without manually restarting the application. When you save your Python file, the app automatically updates to reflect the changes, greatly improving development workflow and productivity.

## Prerequisites

- Python 3.8+ (tested with Python 3.13.5)
- Flet 0.28.3 installed
- Basic Flet app structure

## Installation

Ensure you have Flet installed with all optional dependencies:

```bash
pip install flet[all]
```

## Basic Hot-Reload Setup

### Method 1: Desktop App (Recommended)

The simplest way to enable hot-reload for desktop applications:

```bash
flet run main.py
```

Replace `main.py` with your actual Python script name. This will:
- Launch your app in a native OS window
- Enable automatic reloading when you save changes to `main.py`
- Watch only the main script file by default

### Method 2: Directory Watching

To watch your entire project directory for changes:

```bash
flet run -d main.py
```

The `-d` or `--directory` flag watches the script's directory for changes.

### Method 3: Recursive Directory Watching

To watch your project directory and all subdirectories:

```bash
flet run -d -r main.py
```

The `-r` or `--recursive` flag watches subdirectories recursively. This is useful for multi-file projects.

## Advanced Hot-Reload Options

### Web Browser Mode

For more stable hot-reload experience, you can run your app in web browser mode:

```bash
flet run --web main.py
```

Or with directory watching:

```bash
flet run --web -d -r main.py
```

### Fixed Port Configuration

Specify a custom port for consistency:

```bash
flet run --web -p 8550 -d main.py
```

### Code-Based Web Browser Configuration

If hot-reload is unstable in desktop mode, configure your app to use web browser view:

```python
import flet as ft

def main(page: ft.Page):
    page.title = "My Hot-Reload App"
    # Your UI code here
    page.add(ft.Text("Hello, Hot-Reload!"))

# Configure for web browser view with fixed port
ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
```

Then run:

```bash
flet run -d main.py
```

## Command Line Options Reference

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message |
| `--verbose` | `-v` | Enable verbose output (`-vv` for more detailed) |
| `--port PORT` | `-p` | Custom TCP port for the app |
| `--host HOST` | | Host to run web app on (use "*" for all IPs) |
| `--name APP_NAME` | | App name to distinguish from others on same port |
| `--module` | `-m` | Treat script as Python module path |
| `--directory` | `-d` | Watch script directory for changes |
| `--recursive` | `-r` | Watch script directory and subdirectories |
| `--hidden` | `-n` | Hide application window on startup |
| `--web` | `-w` | Open app in web browser |
| `--assets ASSETS_DIR` | `-a` | Path to assets directory |
| `--ignore-dirs DIRS` | | Directories to ignore during watch |

## Common Usage Patterns

### Single File Project
```bash
flet run app.py
```

### Multi-File Project
```bash
flet run -d -r main.py
```

### Web Development Mode
```bash
flet run --web -p 8080 -d -r main.py
```

### Production-Like Testing
```bash
flet run --web --host "*" -p 8080 main.py
```

## Troubleshooting Hot-Reload Issues

### Issue: Hot-Reload Not Working

**Solution 1: Use Web Browser Mode**
If desktop hot-reload is unstable, switch to web browser mode:

```python
import flet as ft

def main(page: ft.Page):
    # Your app code here
    pass

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
```

Run with:
```bash
flet run -d main.py
```

**Solution 2: Specify Fixed Port**
Add port configuration to stabilize connection:

```bash
flet run -p 8550 -d main.py
```

**Solution 3: Check File Permissions**
Ensure your Python files have proper read/write permissions.

### Issue: Changes Not Detected in Subdirectories

**Solution**: Use recursive watching:
```bash
flet run -d -r main.py
```

### Issue: Too Many File Watchers

**Solution**: Ignore unnecessary directories:
```bash
flet run -d -r --ignore-dirs "__pycache__,venv,.git" main.py
```

### Issue: Port Already in Use

**Solution**: Use a different port:
```bash
flet run -p 8551 main.py
```

## Best Practices

1. **Use Directory Watching**: Always use `-d` flag for project-wide changes
2. **Recursive Watching**: Use `-r` for multi-file projects
3. **Fixed Ports**: Use `-p` for consistent development environment
4. **Web Mode**: Switch to web browser mode if desktop hot-reload is unstable
5. **Ignore Directories**: Exclude unnecessary directories to improve performance
6. **Version Control**: Don't commit hot-reload configuration files

## Example Project Structure

```
my-flet-app/
├── main.py
├── components/
│   ├── header.py
│   └── sidebar.py
├── utils/
│   └── helpers.py
├── assets/
│   └── images/
└── requirements.txt
```

For this structure, use:
```bash
flet run -d -r main.py
```

## VS Code Integration

If you're using VS Code, you can create a launch configuration:

1. Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flet Hot-Reload",
            "type": "python",
            "request": "launch",
            "module": "flet",
            "args": ["run", "-d", "-r", "main.py"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

2. Use F5 to start debugging with hot-reload enabled

## Environment Variables

You can also control Flet behavior with environment variables:

```bash
export FLET_LOG_LEVEL=debug
export FLET_LOG_TO_FILE=true
flet run -d main.py
```

## Performance Tips

1. **Limit Watched Directories**: Only watch necessary directories
2. **Use Ignore Patterns**: Exclude build, cache, and version control directories
3. **Fixed Ports**: Avoid random port allocation for faster startup
4. **Minimal Logging**: Use appropriate log levels for better performance

## Conclusion

Hot-reload significantly improves Flet development workflow by providing instant feedback on code changes. Start with basic `flet run main.py` and add options as needed for your specific project requirements. For most projects, `flet run -d -r main.py` provides the best balance of functionality and performance.