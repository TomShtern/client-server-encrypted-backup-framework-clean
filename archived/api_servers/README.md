# Archived API Server Implementations

This directory contains obsolete and duplicate API server implementations that have been archived to maintain a clean project structure.

## Current Canonical API Server

**✅ ACTIVE:** `cyberbackup_api_server.py` (project root)
- This is the **ONLY** API server that should be used
- Contains all latest features and enhancements
- Used by `one_click_build_and_run.py`
- Includes observability, performance monitoring, and enhanced logging
- Fully integrated with the complete CyberBackup 3.0 system

## Archived Files

### cyberbackup_api_server_fixed.py
- **Archived Date:** 2025-01-09
- **Reason:** Obsolete "fixed" version superseded by main implementation
- **Issues:** 
  - Outdated import paths (`from shared.logging_utils` instead of `from src.shared.logging_utils`)
  - Missing observability features
  - Missing performance monitoring
  - Missing enhanced error handling
- **Status:** No longer maintained, replaced by canonical version

### minimal_api_server.py
- **Archived Date:** 2025-01-09
- **Reason:** Testing/debugging tool, not production server
- **Purpose:** Was used for UUID fix testing
- **Issues:**
  - Minimal functionality only
  - No real backup integration
  - Simulation-only implementation
- **Status:** Debugging artifact, no longer needed

### debug_server.py
- **Archived Date:** 2025-01-09
- **Reason:** Debugging tool for isolating 500 errors
- **Purpose:** Was used to debug /api/status endpoint issues
- **Issues:**
  - Runs on different port (9091) to avoid conflicts
  - Limited functionality
  - Debug-only implementation
- **Status:** Debugging artifact, issues resolved in main server

## Migration History

### What Was Unified
1. **Single Entry Point:** All API server functionality consolidated into `cyberbackup_api_server.py`
2. **Feature Integration:** All features from various implementations merged into canonical version
3. **Import Fixes:** Corrected import paths and dependencies
4. **Enhanced Functionality:** Added observability, performance monitoring, structured logging

### What Was Removed
1. **Duplicate Implementations:** Multiple API server files causing confusion
2. **Outdated Code:** Legacy implementations with known issues
3. **Debug Artifacts:** Temporary debugging servers no longer needed
4. **Inconsistent Interfaces:** Varying API implementations

## Usage Guidelines

### ✅ DO
- Use `cyberbackup_api_server.py` for all API server needs
- Reference the canonical server in documentation
- Start the server via `one_click_build_and_run.py` or directly: `python cyberbackup_api_server.py`

### ❌ DON'T
- Use any files in this archived directory
- Create new duplicate API server implementations
- Reference archived files in new code
- Attempt to run archived servers (they may have broken dependencies)

## Technical Details

### Canonical Server Features
- **Port:** 9090 (standard)
- **WebSocket Support:** Real-time communication
- **Observability:** Structured logging, metrics, health checks
- **Performance Monitoring:** Request timing, resource usage
- **Error Handling:** Comprehensive error reporting and recovery
- **File Transfer:** Complete integration with C++ client and Python server
- **Security:** CORS configuration, singleton management

### Archived Server Limitations
- **cyberbackup_api_server_fixed.py:** Missing modern features, import errors
- **minimal_api_server.py:** No real backup functionality, testing only
- **debug_server.py:** Limited endpoints, different port, debug-only

## Recovery Information

If you need to reference archived implementations for historical purposes:

1. **Git History:** Full implementation history available in git commits
2. **Feature Comparison:** Compare archived vs canonical to see improvements
3. **Migration Notes:** See `chat_change_log.md` for detailed migration information

## Future Maintenance

- **No Updates:** Archived files will not receive updates or bug fixes
- **Deprecation:** These files are considered deprecated and unsupported
- **Removal:** May be permanently deleted in future major versions

## Contact

For questions about API server functionality or this archival process, refer to:
- Project documentation
- `chat_change_log.md` for implementation details
- Integration tests in `tests/integration/` for usage examples

---

**Last Updated:** 2025-01-09  
**Archival Reason:** Unify API server entrypoint and eliminate duplicates  
**Canonical Server:** `cyberbackup_api_server.py` (project root)
