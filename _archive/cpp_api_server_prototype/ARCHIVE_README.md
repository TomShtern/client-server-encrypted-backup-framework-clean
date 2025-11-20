# C++ API Server Prototype - ARCHIVED

**Status**: ARCHIVED (Not in active development)
**Date Archived**: 2025-11-20
**Original Purpose**: C++ implementation of the API server using Drogon framework

## Why was this archived?

This was an experimental attempt to replace the Python Flask API server with a C++ implementation using the Drogon web framework. The goal was potentially better performance and lower resource usage.

**Decision**: The project was abandoned in favor of keeping the Flask API server because:
- The Flask API server is mature, stable, and well-integrated with the rest of the system
- Python provides better development velocity and maintainability
- The performance gains from C++ were not critical for this use case
- Development effort was better spent on other priorities

## Current Architecture

The **active API server** is the **Flask-based Python API server** located in `api_server/cyberbackup_api_server.py`.

### Architecture Overview:
- **Flask API Server** (`api_server/`) - Connects the C++ client to the web-based GUI in the browser
- **FletV2 GUI** (`FletV2/`) - Desktop dashboard for managing the Python backup server with SQLite3 database
- **Python Backup Server** (`python_server/`) - Core backup server that handles file transfers and encryption
- **C++ Client** (`Client/`) - Native client for file encryption and transfer

## preservation

This directory is kept for historical reference and in case the C++ API approach is revisited in the future. However, there are **no current plans** to resume development on this component.

## Contents

- `CMakeLists.txt` - CMake build configuration for the C++ server
- `config/drogon.config.json` - Drogon framework configuration
- `README.md` - Original project documentation (if available)

## Notes

If you need to understand the current API architecture, please refer to:
- `api_server/cyberbackup_api_server.py` - The active Flask API server
- `api_server/web_ui/` - Web-based user interface
- Main project README.md for overall architecture documentation
