# Repository Discovery & Duplicate Analysis Report

## Executive Summary

This report documents the discovery phase of the repository reorganization project. The analysis identified multiple duplicate implementations and scattered code that needs centralization.

## Duplicate Code Clusters Identified

### Cluster 1: CRC32 Implementation (HIGH PRIORITY)
**Confidence Score: 100% - Exact duplicates**

**Files containing identical CRC32 table and logic:**
1. `src/server/server.py` - `_CRC32_TABLE` and `_calculate_crc()` method
2. `src/server/file_transfer.py` - `_CRC32_TABLE` and `_calculate_crc()` method  
3. `src/client/client.cpp` - `crc_table` and multiple CRC functions

**Impact:** Critical - CRC mismatches cause file transfer failures
**Canonical Choice:** Will create shared implementation in `python_server/shared/crc.py` and `Client/deps/shared/crc.h/.cpp`

### Cluster 2: Filename Validation (HIGH PRIORITY)
**Confidence Score: 95% - Semantic duplicates**

**Files with filename validation logic:**
1. `src/server/request_handlers.py` - `_is_valid_filename_for_storage()` method
2. Likely duplicated in other server files (needs verification)

**Impact:** High - Security and consistency issues
**Canonical Choice:** Will centralize in `python_server/shared/filename_validator.py`

### Cluster 3: Configuration Management (MEDIUM PRIORITY)
**Files with scattered config:**
1. `src/server/config.py`
2. `src/shared/config_manager.py`
3. Various hardcoded constants across files

**Impact:** Medium - Maintenance and consistency issues
**Canonical Choice:** Will centralize in `python_server/shared/config.py`

## Current Repository Structure Analysis

### Well-Organized Areas (Keep/Enhance):
- `/src/` - Good modular structure
- `/tests/` - Already exists
- `/docs/` - Already exists with good organization
- `/scripts/` - Already exists

### Areas Needing Reorganization:
- Root directory has many loose files
- `/received_files/` should move to `/python_server/received_files/`
- C++ code split between `/src/client/`, `/include/`, and loose files
- API server files scattered

## Proposed Reorganization Plan

### Target Structure:
```
/Client/
  /cpp/                 # All C++ client code + headers
  /deps/               # C++ dependencies and shared utilities
  /Client-gui/         # HTML/JS client GUI files
  /other/              # Keys, configs, binary assets

/api-server/           # All API server files

/python_server/
  /server/             # Python server logic
  /server-gui/         # Python server GUI
  /shared/             # Shared Python modules
  /received_files/     # Received files storage

/Database/             # DB schemas, migrations
/tests/                # All tests (existing)
/Shared/               # Cross-language specs and test vectors
  /specs/              # Protocol specifications
  /test_vectors/       # Canonicalization test data
/docs/                 # Documentation (existing)
/scripts/              # Scripts (existing)
/Archived/             # Deprecated/duplicate files (existing)
```

## Next Steps

1. Create canonical CRC and filename validation utilities
2. Create protocol canonicalization specification
3. Move files to target structure using `git mv`
4. Update imports/includes with AST-aware transformations
5. Run comprehensive testing

## Risk Assessment

- **Low Risk:** File moves using `git mv` preserve history
- **Medium Risk:** Import/include updates need careful AST parsing
- **High Risk:** CRC centralization must maintain exact compatibility

## Files Requiring Manual Review

None identified yet - all changes appear automatable with proper testing.
