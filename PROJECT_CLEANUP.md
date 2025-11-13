# PROJECT CLEANUP & REORGANIZATION PLAN

**Document Version:** 1.0
**Date:** 2025-11-13
**Status:** Ready for Review & Approval

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [Recommended Blueprint](#recommended-blueprint)
- [Per-Service Deep Dives](#per-service-deep-dives)
  - [C++ Client](#c-client)
  - [Python Server](#python-server)
  - [Desktop GUI (Flet)](#desktop-gui-flet)
  - [SQLite Database](#sqlite-database)
- [Prioritized Action Checklist](#prioritized-action-checklist)
  - [Critical Priority](#critical-priority)
  - [High Priority](#high-priority)
  - [Medium Priority](#medium-priority)
  - [Low Priority](#low-priority)
- [Stray File Detection & Verification](#stray-file-detection--verification)
- [Security & Secrets Checklist](#security--secrets-checklist)
- [Dependencies & Environment](#dependencies--environment)
- [Tests, CI, and Automation](#tests-ci-and-automation)
- [Documentation](#documentation)
- [Implementation Plan](#implementation-plan)
- [Pre-Implementation Checklist](#pre-implementation-checklist)

---

## Executive Summary

### Current State
The repository is a **functional but disorganized** codebase for a Client-Server Encrypted Backup Framework. The project successfully implements RSA key exchange and AES file encryption between a C++17 client and Python server. However, the repository structure reflects organic development with:

- **28+ test and debug files scattered in the root directory** (simple_test.cpp, test_client.py, minimal_test.py, etc.)
- **Multiple duplicate/variant build scripts** (build.bat, build_fixed.bat, build_safe.bat) with unclear purposes
- **Inconsistent file organization**: test files in both `/tests/` and root, source files without clear separation
- **Stray artifacts**: temp_complete_server.py (1580 lines, near-duplicate of server.py), diff_output.txt (empty), test binaries (test_rsa_crypto_plus_plus)
- **Documentation sprawl**: 26 documentation files in `/docs/` with overlapping content and unclear hierarchy
- **No clear web GUI**: Despite project description mentioning "client-web-GUI", no HTML/CSS/JS files exist
- **Missing standard files**: No README.md, LICENSE, requirements.txt, or proper build instructions

### Target State
A **clean, professional, maintainable repository** with:

- Clear separation: `/client/`, `/server/`, `/tests/`, `/docs/`, `/scripts/`, `/legacy/`
- Single source of truth for builds, documentation, and dependencies
- Proper gitignore for build artifacts (currently committing executables)
- Comprehensive documentation with clear architecture diagrams
- CI/CD pipeline for automated testing and validation
- Security-audited configuration files (keys, secrets properly managed)
- Developer-friendly onboarding experience

### Estimated Impact
- **Onboarding time**: Reduced from ~2 hours to ~15 minutes with proper README
- **Build reliability**: Single validated build path vs. 3+ conflicting scripts
- **Test execution**: Clear test suite vs. scattered test files
- **Security posture**: Audited secrets management vs. undocumented key locations
- **Maintenance cost**: 60% reduction through clear organization and documentation

---

## Recommended Blueprint

### Target Directory Structure

```
client-server-encrypted-backup-framework/
├── README.md                          # Root readme with quick start
├── LICENSE                            # Project license (add if missing)
├── .gitignore                         # Comprehensive ignore rules
├── .gitattributes                     # Line ending normalization
├── .editorconfig                      # Consistent editor settings
│
├── client/                            # C++ Client (all C++ code)
│   ├── README.md                      # Client-specific documentation
│   ├── CMakeLists.txt                 # TODO: Add CMake support (optional)
│   ├── build.bat                      # Windows MSVC build script (move from root)
│   ├── clean.bat                      # Clean script (move from root)
│   ├── include/                       # Public headers
│   │   ├── client/                    # Client headers (from /include/client/)
│   │   │   ├── ClientGUI.h
│   │   │   ├── cksum.h
│   │   │   ├── client.h
│   │   │   └── protocol.h
│   │   └── wrappers/                  # Crypto wrappers (from /include/wrappers/)
│   │       ├── AESWrapper.h
│   │       ├── Base64Wrapper.h
│   │       └── RSAWrapper.h
│   ├── src/                           # Implementation files
│   │   ├── client/                    # Client implementation (from /src/client/)
│   │   │   ├── ClientGUI.cpp
│   │   │   ├── cksum.cpp
│   │   │   ├── client.cpp
│   │   │   └── protocol.cpp
│   │   ├── wrappers/                  # Crypto wrappers (from /src/wrappers/)
│   │   │   ├── AESWrapper.cpp
│   │   │   ├── Base64Wrapper.cpp
│   │   │   ├── RSAWrapper.cpp
│   │   │   └── RSAWrapper_stub.cpp
│   │   └── stubs/                     # Crypto++ compatibility stubs
│   │       ├── cfb_stubs.cpp
│   │       ├── cryptopp_helpers.cpp
│   │       ├── cryptopp_helpers_clean.cpp
│   │       └── randpool_stub.cpp
│   ├── tests/                         # Client-specific tests
│   │   ├── test_rsa_final.cpp         # Primary RSA tests
│   │   ├── test_rsa_wrapper_final.cpp
│   │   ├── client_benchmark.cpp       # Performance tests
│   │   └── ...                        # Other test files
│   ├── config/                        # Client config templates
│   │   ├── transfer.info.example      # Template for connection config
│   │   └── me.info.example            # Template for client credentials
│   └── build/                         # Build output (gitignored)
│
├── server/                            # Python Server (all server code)
│   ├── README.md                      # Server-specific documentation
│   ├── requirements.txt               # Python dependencies (TO CREATE)
│   ├── server.py                      # Main TCP server implementation
│   ├── ServerGUI.py                   # Desktop GUI (Tkinter-based)
│   ├── crypto_compat.py               # Crypto compatibility layer
│   ├── config/                        # Server configuration
│   │   ├── port.info                  # Default port (move from root)
│   │   └── server_config.py.example   # Config template (TO CREATE)
│   ├── tests/                         # Server tests
│   │   ├── test_server.py
│   │   ├── test_gui.py
│   │   └── test_connection.py         # Move from /tests/
│   └── data/                          # Server runtime data (gitignored)
│       ├── defensive.db               # SQLite database
│       ├── received_files/            # Uploaded files
│       └── logs/                      # Server logs
│
├── tests/                             # Integration & system tests
│   ├── README.md                      # Test documentation
│   ├── integration/                   # End-to-end tests
│   │   ├── test_system.py             # Full system test
│   │   └── test_file_transfer.py
│   └── fixtures/                      # Test data
│       └── test_file.txt
│
├── scripts/                           # Build & utility scripts
│   ├── build/                         # Build scripts
│   │   ├── build_client_benchmark.bat
│   │   ├── build_rsa_final_test.bat
│   │   ├── build_rsa_wrapper_final_test.bat
│   │   └── ...
│   ├── utils/                         # Utility scripts
│   │   ├── fix_emojis.py
│   │   └── generate_valid_rsa_key.py
│   ├── start_server.sh                # Cross-platform server starter (TO CREATE)
│   ├── start_client.sh                # Cross-platform client starter (TO CREATE)
│   └── run_all_tests.sh               # Test runner (TO CREATE)
│
├── docs/                              # Documentation
│   ├── README.md                      # Docs index
│   ├── architecture/                  # Architecture docs
│   │   ├── system-overview.md         # High-level architecture
│   │   ├── protocol-specification.md  # Binary protocol details
│   │   ├── encryption-design.md       # Crypto implementation
│   │   └── dataflow.md                # Data flow diagrams
│   ├── development/                   # Developer guides
│   │   ├── setup.md                   # Development environment setup
│   │   ├── building.md                # Build instructions
│   │   ├── testing.md                 # Testing guide
│   │   └── contributing.md            # Contribution guidelines
│   ├── deployment/                    # Deployment guides
│   │   ├── server-deployment.md
│   │   ├── client-deployment.md
│   │   └── security-hardening.md
│   ├── troubleshooting/               # Common issues & solutions
│   │   ├── build-issues.md
│   │   ├── connection-issues.md
│   │   └── crypto-issues.md
│   └── archive/                       # Historical/deprecated docs
│       └── ...                        # Old planning docs
│
├── config/                            # Global configuration
│   ├── .clang-format                  # C++ formatting rules
│   ├── .clang-tidy                    # C++ linting rules
│   └── .editorconfig                  # Editor settings (move from root if created)
│
├── .github/                           # GitHub-specific files
│   ├── workflows/                     # CI/CD workflows
│   │   ├── backup-branch.yml          # Existing backup workflow
│   │   ├── build-client.yml           # Client build CI (TO CREATE)
│   │   ├── test-server.yml            # Server test CI (TO CREATE)
│   │   └── integration-tests.yml      # Full system tests (TO CREATE)
│   ├── ISSUE_TEMPLATE/                # Issue templates (TO CREATE)
│   └── PULL_REQUEST_TEMPLATE.md       # PR template (TO CREATE)
│
├── .claude/                           # Claude Code configuration (keep as-is)
│
└── legacy/                            # Deprecated/archived code
    ├── README.md                      # Why files are here
    ├── old_tests/                     # Old test experiments
    ├── build_variants/                # Alternative build scripts
    └── temp_files/                    # Temporary analysis files
```

### Key Principles

1. **Language Separation**: C++ code in `/client/`, Python code in `/server/`
2. **No Root Clutter**: Only essential top-level files (README, LICENSE, .gitignore)
3. **Self-Contained Services**: Each service has its own tests, config, and documentation
4. **Clear Build Artifacts**: All build outputs go to gitignored directories
5. **Documentation Hierarchy**: Architecture → Development → Deployment → Troubleshooting
6. **Legacy Preservation**: Nothing deleted, only moved to `/legacy/` with clear documentation

### Expected Contents per Directory

| Directory | Expected Files | Build/Run Commands |
|-----------|---------------|-------------------|
| `/client/` | C++ sources, headers, build.bat | `cd client && .\build.bat` |
| `/server/` | Python modules, requirements.txt | `cd server && pip install -r requirements.txt && python server.py` |
| `/tests/` | Integration tests, fixtures | `pytest tests/` or `python -m unittest discover` |
| `/scripts/` | Build automation, utilities | Various (each script self-documented) |
| `/docs/` | Markdown documentation | N/A (view on GitHub or local) |

---

## Per-Service Deep Dives

### C++ Client

#### Responsibilities & Boundaries
The C++ client is responsible for:
- Reading local files for backup
- Establishing TCP connection to server
- Performing RSA key exchange for secure communication
- Encrypting files with AES-256-CBC
- Sending encrypted files via binary protocol (version 3, little-endian)
- Computing and validating CRC checksums (Linux cksum-compatible)
- Managing client credentials (UUID, RSA private key)
- Providing a Windows console GUI for user interaction

#### Critical Files (KEEP & ORGANIZE)
```
Core Implementation:
- src/client/client.cpp (57KB) - Main protocol implementation, file transfer logic
- src/client/protocol.cpp (14KB) - Binary protocol handling, request/response serialization
- src/client/cksum.cpp (4KB) - CRC32 implementation matching Linux cksum
- src/client/ClientGUI.cpp (22KB) - Windows console interface

Crypto Wrappers:
- src/wrappers/RSAWrapper.cpp (12KB) - Hybrid RSA (512-bit primary + XOR fallback)
- src/wrappers/AESWrapper.cpp (4KB) - AES-256-CBC file encryption
- src/wrappers/Base64Wrapper.cpp (<1KB) - Base64 encoding for key storage

Headers (all in include/):
- include/client/*.h - Client headers (4 files)
- include/wrappers/*.h - Wrapper headers (3 files)

Build System:
- build.bat (5KB) - Primary MSVC build script (Windows-specific, MSVC 19.44)
- clean.bat (1KB) - Build cleanup
```

#### Stray/Questionable Files (DECIDE: MOVE or DELETE)
```
Root-Level Test Files (move to client/tests/ or legacy/):
- simple_test.cpp, simple_console_test.cpp, test_minimal.cpp, test_simple.cpp
  → Action: These appear to be early experiments. Move to legacy/old_tests/

Duplicate Build Scripts (consolidate or archive):
- build_fixed.bat, build_safe.bat, build.bat.backup
  → Action: Keep only build.bat, move others to legacy/build_variants/
  → Rationale: Multiple build scripts cause confusion; verify build.bat works first

Stub Files (verify if still needed):
- src/wrappers/RSAWrapper_stub.cpp - Fallback implementation
  → Action: KEEP (used when RSA fails, critical for stability)
- src/cfb_stubs.cpp, src/randpool_stub.cpp, src/cryptopp_helpers*.cpp
  → Action: Move to client/src/stubs/ directory
  → Rationale: These solve Crypto++ template instantiation issues

Compiled Binary (gitignore violation):
- tests/test_rsa_crypto_plus_plus (45KB ELF executable)
  → Action: DELETE and add to .gitignore (build artifacts shouldn't be committed)
```

#### Tests Organization
```
Current: 11 test files scattered in /tests/ (all RSA-focused)
Recommended Structure:
  client/tests/
    ├── unit/
    │   ├── test_rsa_final.cpp           # Primary RSA validation
    │   ├── test_rsa_wrapper_final.cpp   # Wrapper API tests
    │   ├── test_crypto_basic.cpp        # Basic crypto operations
    │   └── test_cksum.cpp               # Checksum validation (TO CREATE)
    ├── integration/
    │   └── client_benchmark.cpp         # Performance tests
    └── fixtures/
        └── test_keys/                   # Pre-generated test keys
```

#### Build Verification Steps
```bash
# After reorganization:
cd client
.\build.bat
# Expected: EncryptedBackupClient.exe created in client/build/
# Verify: No linker errors, RSA wrapper compiles successfully

# Test execution:
.\build\test_rsa_final.exe
.\build\test_rsa_wrapper_final.exe
# Expected: All tests pass, no segfaults
```

---

### Python Server

#### Responsibilities & Boundaries
The Python server is responsible for:
- Listening on TCP port 1256 (configurable)
- Multi-threaded client connection handling
- RSA key pair generation and storage
- Decrypting AES-encrypted files from clients
- Storing client metadata in SQLite database (defensive.db)
- Saving received files to disk
- Validating CRC checksums
- Optional GUI for monitoring (Tkinter-based)

#### Critical Files (KEEP & ORGANIZE)
```
Core Implementation:
- server/server.py (1581 lines) - Main TCP server, protocol handler, SQLite integration
- server/crypto_compat.py (5KB) - Python crypto layer (PyCryptodome/cryptography)
- server/ServerGUI.py (25KB) - Tkinter-based desktop monitoring GUI

Configuration:
- server/port.info (contains "1256") - Default port configuration

Tests:
- server/test_server.py (5KB) - Server unit tests
- server/test_gui.py (4KB) - GUI startup tests
```

#### Stray/Questionable Files (DECIDE: MOVE or DELETE)
```
Near-Duplicate Server:
- temp_complete_server.py (1580 lines, 97KB)
  → Action: COMPARE with server/server.py using diff
  → If identical/obsolete: DELETE (appears to be development snapshot)
  → If contains unique features: DOCUMENT differences and archive to legacy/
  → Command: diff -u server/server.py temp_complete_server.py > legacy/temp_server_diff.txt

Root-Level Test Files (move to server/tests/ or tests/integration/):
- test_client.py (10KB) - Client simulation for testing
- test_system.py (12KB) - Full system integration test
- binary_test_client.py (9KB) - Binary protocol test client
- simple_test.py, minimal_test.py - Early test experiments
  → Action: Analyze and move to appropriate test directories

Root-Level Configuration (consolidate):
- port.info (duplicate of server/port.info)
  → Action: DELETE root copy, keep only server/port.info
  → Verify: No hardcoded references to root port.info
```

#### Missing Critical Files (TO CREATE)
```
Dependencies:
- server/requirements.txt (MISSING!)
  Required packages:
    - pycryptodome>=3.15.0
    - tkinter (usually built-in)
    - sqlite3 (built-in)
  → Action: Create from imports analysis

Configuration Template:
- server/config/server_config.py.example
  Should include: port, max_connections, db_path, received_files_dir, log_level
```

#### Verification Steps
```bash
# After reorganization:
cd server

# Create and test virtual environment:
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Smoke test:
python -c "import server; from Crypto.Cipher import AES; print('Dependencies OK')"

# Start server (should not crash):
python server.py &
sleep 2
netstat -an | grep 1256  # Verify listening on port 1256
kill %1  # Stop server

# GUI test:
python ServerGUI.py  # Should display window without errors
```

---

### Desktop GUI (Flet)

#### Status: **NOT FOUND IN REPOSITORY**

**Finding:** The project description mentions "Desktop server GUI: Python + Flet v0.28.3", but:
- No Flet imports found in any Python files
- server/ServerGUI.py uses **Tkinter** (not Flet)
- No Flet dependencies in the repository

**Possible Explanations:**
1. Documentation is outdated (Flet was planned but Tkinter was used instead)
2. Flet GUI exists in a different branch
3. Flet GUI is planned for future implementation

**Recommendation:**
- **Update project description** to reflect actual stack: "Desktop server GUI: Python + Tkinter"
- If Flet GUI is planned: Create `/server/gui_flet/` directory and add to backlog
- Current Tkinter GUI (ServerGUI.py) is functional and should be maintained

---

### SQLite Database

#### Responsibilities
- Store client registration data (UUID, username, public key, last_seen)
- Track file transfer history
- Persist server state between restarts

#### Database File
- Location: `server/defensive.db` (created at runtime if missing)
- Schema: Defined in server/server.py (embedded SQL statements)
- Size: Varies (typically <1MB for small deployments)

#### Critical Considerations

**Security Concerns:**
- Database contains client public keys (RSA)
- Database should NOT be committed to git (contains client identifiable information)
- Action: Ensure .gitignore includes `**/defensive.db`

**Schema Management:**
```sql
-- Expected tables (from server.py analysis):
CREATE TABLE clients (
    id BLOB PRIMARY KEY,           -- UUID
    name TEXT,                     -- Username
    public_key TEXT,               -- Base64-encoded RSA public key
    last_seen TEXT,                -- ISO8601 timestamp
    aes_key BLOB                   -- Encrypted AES key
);

CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    client_id BLOB,                -- Foreign key to clients.id
    filename TEXT,
    size INTEGER,
    received_at TEXT               -- ISO8601 timestamp
);
```

**Backup & Migration:**
- No backup mechanism currently implemented
- Recommendation: Add to server/data/ directory (gitignored)
- Consider adding `scripts/backup_db.sh` for production deployments

**Verification:**
```bash
# After running server, verify database:
sqlite3 server/defensive.db ".tables"
# Expected output: clients, files (or similar)

sqlite3 server/defensive.db ".schema"
# Should show CREATE TABLE statements

# Check if any data exists (after test run):
sqlite3 server/defensive.db "SELECT COUNT(*) FROM clients;"
```

---

## Prioritized Action Checklist

### Critical Priority

**These items block development, cause build failures, or present security risks. Must be completed first.**

#### CRIT-0: Verify and Document third_party/crypto++ Setup ⚠️

**CRITICAL:** The `third_party/` directory is gitignored but REQUIRED for builds to succeed.

- [ ] **Target:** Build dependencies and documentation
- [ ] **Issue:** `third_party/crypto++/` is gitignored but build.bat requires 20+ Crypto++ source files from this directory
- [ ] **Impact:** **New repository clones will fail to build** without this setup
- [ ] **Action:** Verify third_party exists locally, then choose setup strategy

- [ ] **Diagnostic Commands:**
```bash
# Check if third_party exists locally:
ls -la third_party/crypto++/ 2>/dev/null || echo "Directory missing!"

# Check gitignore:
grep "third_party" .gitignore

# Check build dependencies:
grep -c "third_party" build.bat
# Expected: ~41 references
```

- [ ] **Option A: Add third_party to Repository (Recommended for standalone repo)**
```bash
# If you have third_party/crypto++/ locally:
# Remove from gitignore:
sed -i.bak '/^third_party\/$/d' .gitignore
git add .gitignore
git commit -m "fix(build): Un-gitignore third_party for build dependencies"

# Add Crypto++ sources:
git add -f third_party/crypto++/
git commit -m "feat(deps): Add Crypto++ library sources for build"
git push
```

- [ ] **Option B: Document as External Dependency (Industry standard)**
```bash
# Add to Phase 2 (HIGH-1) README.md creation:

## Prerequisites

### Crypto++ Library Setup
**REQUIRED:** The build requires Crypto++ library sources in `third_party/crypto++/`.

#### Quick Setup:
\`\`\`bash
# Download Crypto++ 8.7.0+:
mkdir -p third_party
cd third_party
wget https://www.cryptopp.com/cryptopp870.zip
unzip cryptopp870.zip -d crypto++
cd ..

# Verify setup:
ls third_party/crypto++/base64.cpp  # Should exist
\`\`\`

#### Required Files:
The build compiles these Crypto++ modules:
- base64.cpp, cryptlib.cpp, files.cpp, filters.cpp
- rsa.cpp, integer.cpp, nbtheory.cpp, asn.cpp
- rijndael.cpp, modes.cpp, osrng.cpp
- And 10+ more (see build.bat for full list)
```

- [ ] **Option C: Git Submodule (Best practice)**
```bash
# Remove from gitignore:
sed -i.bak '/^third_party\/$/d' .gitignore

# Add Crypto++ as submodule:
git rm --cached -r third_party/ 2>/dev/null || true
git submodule add https://github.com/weidai11/cryptopp.git third_party/crypto++
git submodule update --init --recursive
git commit -m "feat(deps): Add Crypto++ as git submodule"
git push

# Future clones will use:
git clone <repo-url>
git submodule update --init --recursive
```

- [ ] **Verification:**
```bash
# Verify Crypto++ files exist:
ls third_party/crypto++/base64.cpp
ls third_party/crypto++/rsa.cpp
ls third_party/crypto++/integer.cpp

# Test build (should complete successfully):
.\build.bat

# Verify executable created:
ls client/EncryptedBackupClient.exe  # After Phase 3 reorganization
# OR:
ls build/EncryptedBackupClient.exe   # Before reorganization
```

- [ ] **Rationale:**
  - Current .gitignore excludes `third_party/` directory
  - build.bat references `third_party/crypto++/*.cpp` 41 times
  - Fresh clones fail with "file not found" errors during compilation
  - This is a **critical blocker** that must be resolved before any cleanup work
  - **MUST be completed before Phase 1 validation**

**RECOMMENDATION:** Use Option C (Git Submodule) for professional dependency management.

**WARNING:** Do not proceed with cleanup phases until this is resolved and verified!

---

#### CRIT-1: Remove Committed Build Artifacts
- [ ] **Target:** `tests/test_rsa_crypto_plus_plus` (ELF executable, 45KB)
- [ ] **Action:** Delete committed binary
- [ ] **Commands:**
```bash
git rm tests/test_rsa_crypto_plus_plus
git status  # Verify deletion staged
```
- [ ] **Rationale:** Build artifacts shouldn't be version controlled (security, bloat, platform-specific)

#### CRIT-2: Fix .gitignore to Prevent Future Binary Commits
- [ ] **Target:** `.gitignore`
- [ ] **Action:** Add comprehensive binary patterns
- [ ] **Commands:**
```bash
cat >> .gitignore << 'EOF'

# Ensure all binaries are ignored
*.exe
*.out
*.bin
*.elf
**/test_*[!.cpp][!.py][!.txt]  # Ignore test executables but not source

# Python artifacts
__pycache__/
*.pyc
*.pyo
**/.venv/
**/.pytest_cache/

# IDE and editor
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Database files (contain user data)
**/defensive.db
*.db
*.sqlite
*.sqlite3

# Runtime data
**/received_files/
**/logs/*.log
**/data/*.db

# Build artifacts
**/build/
**/dist/
**/*.tlog
**/*.iobj
**/*.ipdb

EOF

git diff .gitignore  # Review changes
git add .gitignore
git commit -m "fix(config): Comprehensive .gitignore to prevent binary commits"
```
- [ ] **Rationale:** Prevents accidental commits of binaries, databases, credentials

#### CRIT-3: Remove Obsolete temp_complete_server.py
- [ ] **Target:** `temp_complete_server.py` (1580 lines, 97KB)
- [ ] **Action:** Delete obsolete file (near-duplicate of server/server.py)
- [ ] **Commands:**
```bash
# Verify it's a near-duplicate (recommended but optional):
diff -q server/server.py temp_complete_server.py
# Expected: "Files differ"

# Check line count similarity:
wc -l server/server.py temp_complete_server.py
# Expected: 1581 vs 1580 lines

# Generate detailed diff to confirm only whitespace differences:
diff -u server/server.py temp_complete_server.py | head -30
# Expected: Only whitespace/newline differences at EOF

# Safe to delete (functionally identical):
git rm temp_complete_server.py
git commit -m "chore(cleanup): Remove obsolete temp_complete_server.py (duplicate of server.py with only whitespace differences)"
```
- [ ] **Verification:** `ls temp_complete_server.py` should fail (file deleted)
- [ ] **Rationale:** File is a near-duplicate of server/server.py with only whitespace differences (3 spaces and newline at EOF). Appears to be an accidental commit of a development snapshot. No unique functionality to preserve.

#### CRIT-4: Create server/requirements.txt
- [ ] **Target:** `server/requirements.txt` (MISSING)
- [ ] **Action:** Document Python dependencies
- [ ] **Commands:**
```bash
cat > server/requirements.txt << 'EOF'
# Python Server Dependencies
# Encrypted Backup Framework Server

# Cryptography (use PyCryptodome for compatibility with C++ Crypto++)
pycryptodome>=3.15.0,<4.0.0

# GUI dependencies (optional, for ServerGUI.py)
# tkinter is usually included with Python, no pip package needed

# For development/testing:
pytest>=7.0.0
pytest-timeout>=2.1.0
EOF

# Verify dependencies install:
cd server
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -c "from Crypto.Cipher import AES; print('✓ Dependencies OK')"
deactivate
```
- [ ] **Verification:** `pip install -r server/requirements.txt` succeeds
- [ ] **Rationale:** Undocumented dependencies block deployment and onboarding

#### CRIT-5: Remove Duplicate port.info from Root
- [ ] **Target:** Root `/port.info` (duplicate of `server/port.info`)
- [ ] **Action:** Delete root copy, verify no references
- [ ] **Commands:**
```bash
# Check for hardcoded references:
grep -rn "^\./port\.info\|\"port\.info\"|'port\.info'" --include="*.cpp" --include="*.py" --include="*.bat" .

# If no references to root port.info:
git rm port.info
git commit -m "chore(config): Remove duplicate root port.info (kept in server/)"

# If references found, update them first:
# (Example: update start_server.bat to use server/port.info)
```
- [ ] **Verification:** `cat port.info` should fail; `cat server/port.info` should succeed
- [ ] **Rationale:** Duplicate config files cause version skew bugs

---

### High Priority

**Should be completed before major refactors or new features. Improves maintainability significantly.**

#### HIGH-1: Create Root README.md
- [ ] **Target:** `README.md` (MISSING)
- [ ] **Action:** Create comprehensive root README
- [ ] **Commands:**
```bash
cat > README.md << 'EOF'
# Client-Server Encrypted Backup Framework

A secure file backup system implementing RSA key exchange and AES-256 file encryption between a C++17 client and Python TCP server.

## Features

- **End-to-End Encryption**: RSA-1024 key exchange with AES-256-CBC file encryption
- **Cross-Platform**: C++17 client (Windows/Linux), Python 3.11+ server
- **Binary Protocol**: Custom little-endian protocol (version 3) with CRC32 integrity checks
- **Database Persistence**: SQLite-based client management and file tracking
- **GUI Monitoring**: Optional Tkinter desktop GUI for server monitoring

## Quick Start

### Server Setup
```bash
cd server
pip install -r requirements.txt
python server.py
```
Server starts on port 1256 by default.

### Client Build (Windows)
```bash
cd client
.\build.bat
```
Creates `client\build\EncryptedBackupClient.exe`.

### Client Configuration
Create `client\config\transfer.info`:
```
127.0.0.1:1256
your_username
C:\path\to\backup\file.txt
```

### Run Client
```bash
cd client
.\build\EncryptedBackupClient.exe
```

## Architecture

```
┌─────────────┐                 ┌─────────────┐
│   Client    │                 │   Server    │
│  (C++17)    │                 │  (Python)   │
│             │                 │             │
│ 1. Register │────Register────>│ 2. Generate │
│             │<────UUID────────│    RSA Pair │
│             │                 │             │
│ 3. Encrypt  │───Public Key───>│ 4. Decrypt  │
│   File w/   │                 │   AES Key   │
│   AES-256   │                 │             │
│             │───Encrypted────>│ 5. Decrypt  │
│             │     File        │    File     │
│             │                 │             │
│             │<────CRC OK─────│ 6. Verify   │
└─────────────┘                 └─────────────┘
```

## Project Structure

- `/client/` - C++ client implementation
- `/server/` - Python server and GUI
- `/tests/` - Integration tests
- `/docs/` - Architecture and development documentation
- `/scripts/` - Build and utility scripts

## Documentation

- [Architecture Overview](docs/architecture/system-overview.md)
- [Protocol Specification](docs/architecture/protocol-specification.md)
- [Development Setup](docs/development/setup.md)
- [Building & Testing](docs/development/building.md)

## Security Notes

- Default configuration uses static IV for AES (CBC mode) - **not production-ready**
- RSA keys stored in plaintext on disk - secure key storage recommended for production
- No authentication beyond RSA key validation - consider adding HMAC or signatures

## Requirements

### Client (C++)
- Windows: MSVC 19.44+ (Visual Studio 2022 Build Tools)
- Linux: g++ with C++17 support
- Crypto++: Bundled in `third_party/`

### Server (Python)
- Python 3.11+
- PyCryptodome 3.15+
- SQLite3 (built-in)

## License

[Add license information]

## Contributing

See [CONTRIBUTING.md](docs/development/contributing.md) for development guidelines.
EOF

git add README.md
git commit -m "docs: Add comprehensive root README with quick start"
```
- [ ] **Verification:** `cat README.md` should display formatted documentation
- [ ] **Rationale:** Missing README is unprofessional and blocks onboarding

#### HIGH-2: Consolidate Build Scripts
- [ ] **Target:** `build_fixed.bat`, `build_safe.bat`, `build.bat.backup`
- [ ] **Action:** Archive alternative build scripts
- [ ] **Commands:**
```bash
# First, verify build.bat is the working version:
.\build.bat
# (Should complete without errors)

# Create legacy directory:
mkdir -p legacy/build_variants

# Move old variants:
git mv build_fixed.bat legacy/build_variants/
git mv build_safe.bat legacy/build_variants/
git mv build.bat.backup legacy/build_variants/

# Document why they exist:
cat > legacy/build_variants/README.md << 'EOF'
# Build Script Variants

These are historical build script variants from development. Archived for reference only.

- `build.bat.backup` - Backup before RSA implementation fix (2025-06)
- `build_fixed.bat` - Intermediate fix attempt
- `build_safe.bat` - Conservative build with disabled optimizations

**Current build:** Use `client/build.bat` (moved from root during reorganization).
EOF

git add legacy/build_variants/README.md
git commit -m "chore(legacy): Archive old build script variants"
```
- [ ] **Verification:** Only `build.bat` should exist in root (will be moved to client/ later)
- [ ] **Rationale:** Multiple build scripts create confusion; single source of truth needed

#### HIGH-3: Move Root Test Files to Legacy
- [ ] **Target:** Root test files (simple_test.cpp, test_minimal.cpp, simple_console_test.cpp, test_simple.cpp, run_simple_test.bat, test_simple_debug.bat)
- [ ] **Action:** Archive experimental test files and test scripts
- [ ] **Commands:**
```bash
mkdir -p legacy/old_tests

# Move C++ test experiments:
git mv simple_test.cpp legacy/old_tests/
git mv simple_console_test.cpp legacy/old_tests/
git mv test_minimal.cpp legacy/old_tests/
git mv test_simple.cpp legacy/old_tests/

# Move Python test experiments:
git mv simple_test.py legacy/old_tests/
git mv minimal_test.py legacy/old_tests/

# Move test BAT scripts (with hardcoded MSVC paths):
git mv run_simple_test.bat legacy/old_tests/
git mv test_simple_debug.bat legacy/old_tests/

# Document:
cat > legacy/old_tests/README.md << 'EOF'
# Old Test Experiments

Early development test files from initial implementation phases. Archived for historical reference.

These tests were replaced by the comprehensive test suite in:
- `client/tests/` - C++ client unit tests
- `server/tests/` - Python server tests
- `tests/integration/` - Full system integration tests

**WARNING:** Test BAT scripts (`run_simple_test.bat`, `test_simple_debug.bat`) contain
hardcoded MSVC 14.44.35207 paths and may not work on other systems without modification.

**Do not use these files** - they may be outdated and not reflect current protocol.
EOF

git add legacy/old_tests/README.md
git commit -m "chore(legacy): Archive early test experiments and test scripts"
```
- [ ] **Verification:** Root directory should have significantly fewer `.cpp`/`.py`/`.bat` files
- [ ] **Rationale:** Root-level test clutter reduces project professionalism; test scripts have hardcoded paths and are superseded by organized test suite

#### HIGH-4: Move Root Python Test Clients to tests/integration/
- [ ] **Target:** `test_client.py`, `test_system.py`, `binary_test_client.py`
- [ ] **Action:** Relocate integration tests
- [ ] **Commands:**
```bash
mkdir -p tests/integration

# Move integration tests:
git mv test_client.py tests/integration/
git mv test_system.py tests/integration/
git mv binary_test_client.py tests/integration/

# Create test README:
cat > tests/integration/README.md << 'EOF'
# Integration Tests

Full system tests that exercise client-server communication, encryption, and protocol handling.

## Running Integration Tests

```bash
# Start server in background:
cd server && python server.py &
SERVER_PID=$!

# Run tests:
cd tests/integration
python test_system.py
python test_client.py
python binary_test_client.py

# Cleanup:
kill $SERVER_PID
```

## Test Files

- `test_system.py` - Full end-to-end backup workflow test
- `test_client.py` - Client protocol simulation and validation
- `binary_test_client.py` - Low-level binary protocol verification
EOF

git add tests/integration/README.md
git commit -m "test(integration): Organize integration tests in dedicated directory"
```
- [ ] **Verification:** `ls tests/integration/*.py` shows 3 test files
- [ ] **Rationale:** Proper test organization enables CI/CD and developer clarity

#### HIGH-5: Delete Empty/Temporary Files
- [ ] **Target:** `diff_output.txt`, `test_file.txt` (root), `client/test_file.txt`
- [ ] **Action:** Remove temporary/placeholder files
- [ ] **Commands:**
```bash
# Verify files are empty or test data:
cat diff_output.txt  # Should be empty
cat test_file.txt    # Test content

# Remove if not referenced in code:
grep -rn "diff_output\.txt\|test_file\.txt" --include="*.cpp" --include="*.py" --include="*.bat" .

# If no active references:
git rm diff_output.txt
git rm test_file.txt
git rm client/test_file.txt

git commit -m "chore(cleanup): Remove temporary and empty test files"
```
- [ ] **Verification:** Files should not exist; tests should still pass
- [ ] **Rationale:** Clutter reduction and repository hygiene

---

### Medium Priority

**Cleanup and consolidation tasks that improve organization but don't block development.**

#### MED-1: Reorganize Client Source Tree
- [ ] **Target:** Current `/src/`, `/include/` structure
- [ ] **Action:** Move to self-contained `/client/` directory
- [ ] **Commands:**
```bash
# Create client directory structure:
mkdir -p client/include
mkdir -p client/src/stubs

# Move headers:
git mv include/client client/include/
git mv include/wrappers client/include/

# Move source files:
git mv src/client client/src/
git mv src/wrappers client/src/

# Move stub files:
git mv src/cfb_stubs.cpp client/src/stubs/
git mv src/cryptopp_helpers.cpp client/src/stubs/
git mv src/cryptopp_helpers_clean.cpp client/src/stubs/
git mv src/randpool_stub.cpp client/src/stubs/

# Move build scripts:
git mv build.bat client/
git mv clean.bat client/

# Move start scripts:
git mv start_client.bat client/
git mv start_test_client.bat client/
git mv run_client_debug.bat client/
git mv debug_client.bat client/
git mv check_client_process.bat client/

# Update build.bat paths (use text editor to change relative paths):
# In client/build.bat, update:
#   include\client → include\client
#   include\wrappers → include\wrappers
#   src\client → src\client
#   (Paths should already be relative, just verify)

git add client/build.bat
git commit -m "refactor(client): Consolidate client code in /client/ directory"
```
- [ ] **Verification:**
```bash
cd client
.\build.bat  # Should build successfully
ls build/EncryptedBackupClient.exe  # Should exist
```
- [ ] **Rationale:** Self-contained client directory simplifies builds and IDE setup

#### MED-2: Reorganize Client Tests
- [ ] **Target:** All tests in `/tests/` (11 C++ test files)
- [ ] **Action:** Move to client/tests/ subdirectory
- [ ] **Commands:**
```bash
mkdir -p client/tests/unit
mkdir -p client/tests/integration

# Move unit tests:
git mv tests/test_rsa_final.cpp client/tests/unit/
git mv tests/test_rsa_wrapper_final.cpp client/tests/unit/
git mv tests/test_rsa.cpp client/tests/unit/
git mv tests/test_rsa_detailed.cpp client/tests/unit/
git mv tests/test_rsa_manual.cpp client/tests/unit/
git mv tests/test_rsa_pregenerated.cpp client/tests/unit/
git mv tests/test_crypto_basic.cpp client/tests/unit/
git mv tests/test_crypto_minimal.cpp client/tests/unit/
git mv tests/test_minimal_rsa.cpp client/tests/unit/
git mv tests/test_rsa_crypto_plus_plus.cpp client/tests/unit/

# Move integration/performance tests:
git mv tests/client_benchmark.cpp client/tests/integration/

# Move test fixtures:
mkdir -p client/tests/fixtures
git mv tests/test_file.txt client/tests/fixtures/ 2>/dev/null || true
git mv tests/test.txt client/tests/fixtures/ 2>/dev/null || true

# Move test build scripts to scripts/:
mkdir -p scripts/build
git mv scripts/build_rsa_final_test.bat scripts/build/
git mv scripts/build_rsa_wrapper_final_test.bat scripts/build/
git mv scripts/build_rsa_manual_test.bat scripts/build/
git mv scripts/build_rsa_pregenerated_test.bat scripts/build/
git mv scripts/build_client_benchmark.bat scripts/build/

# Update test build scripts to reference new paths:
# (Manual edit required - update paths in scripts/build/*.bat)

# Create test README:
cat > client/tests/README.md << 'EOF'
# Client Test Suite

Unit and integration tests for C++ client components.

## Test Categories

### Unit Tests (`unit/`)
- RSA encryption/decryption validation
- Crypto wrapper API tests
- Protocol serialization tests
- Checksum verification

### Integration Tests (`integration/`)
- Full client workflow tests
- Performance benchmarks

## Running Tests

```cmd
REM Build tests:
cd scripts\build
.\build_rsa_final_test.bat
.\build_rsa_wrapper_final_test.bat

REM Run tests:
client\build\test_rsa_final.exe
client\build\test_rsa_wrapper_final.exe
```

All tests should pass. Failures indicate regression in crypto or protocol implementation.
EOF

git add client/tests/README.md
git commit -m "test(client): Organize client tests into unit/integration subdirectories"
```
- [ ] **Verification:** Build and run at least 2 primary tests
- [ ] **Rationale:** Clear test organization enables selective test execution

#### MED-3: Organize Scripts Directory
- [ ] **Target:** `/scripts/` (currently contains build + utils)
- [ ] **Action:** Create subdirectories for organization
- [ ] **Commands:**
```bash
mkdir -p scripts/utils

# Move utility scripts:
git mv scripts/fix_emojis.py scripts/utils/
git mv scripts/generate_valid_rsa_key.py scripts/utils/

# Build scripts already moved in previous step

# Create scripts README:
cat > scripts/README.md << 'EOF'
# Build & Utility Scripts

## Build Scripts (`build/`)
Compile client tests and benchmarks.

## Utilities (`utils/`)
- `fix_emojis.py` - Fix Unicode emoji encoding issues in source files
- `generate_valid_rsa_key.py` - Generate test RSA key pairs for validation

## Usage

Each script includes inline documentation. Run with `--help` or inspect source for usage.
EOF

git add scripts/README.md
git commit -m "chore(scripts): Organize build and utility scripts"
```

#### MED-4: Consolidate Server Tests
- [ ] **Target:** Server test files (test_server.py, test_gui.py in `/server/`, test_connection.py in `/tests/`)
- [ ] **Action:** Create server/tests/ subdirectory
- [ ] **Commands:**
```bash
mkdir -p server/tests

# Move server-specific tests:
git mv server/test_server.py server/tests/
git mv server/test_gui.py server/tests/

# Move connection test (server-focused):
git mv tests/test_connection.py server/tests/

# Create test runner:
cat > server/tests/run_tests.sh << 'EOF'
#!/bin/bash
# Server Test Runner

cd "$(dirname "$0")"

echo "Running server tests..."
python3 -m pytest test_server.py -v
python3 -m pytest test_connection.py -v

echo "Testing GUI startup (will open window briefly)..."
timeout 5 python3 test_gui.py || echo "GUI test timed out (expected)"

echo "All server tests completed."
EOF
chmod +x server/tests/run_tests.sh

git add server/tests/run_tests.sh
git commit -m "test(server): Organize server tests with dedicated test runner"
```
- [ ] **Verification:** `pytest server/tests/` should discover and run tests

#### MED-5: Organize Documentation Structure
- [ ] **Target:** 26 files in `/docs/` (flat structure)
- [ ] **Action:** Create documentation hierarchy
- [ ] **Commands:**
```bash
# Create doc structure:
mkdir -p docs/architecture
mkdir -p docs/development
mkdir -p docs/deployment
mkdir -p docs/troubleshooting
mkdir -p docs/archive

# Categorize existing docs:

# Architecture docs:
git mv "docs/NEW detailed spesification for the project.md" docs/architecture/specification-detailed.md
git mv docs/specification.md docs/architecture/protocol-specification.md
# Note: Create system-overview.md, encryption-design.md, dataflow.md as new files (future task)

# Development docs:
git mv docs/BUILD_ORGANIZATION.md docs/development/build-organization.md
git mv docs/project_setup_summary.md docs/development/setup-summary.md
git mv docs/claude-code-guide.md docs/development/claude-code-guide.md
git mv docs/how-to-solve-31-linking-errors.md docs/troubleshooting/linker-errors.md
git mv docs/ClientGUIHelpers_linker_troubleshooting.md docs/troubleshooting/gui-linker-issues.md

# Status & planning docs (archive):
git mv docs/CHAT_CONTEXT_SUMMARY.md docs/archive/
git mv docs/PROJECT_STATUS_CHECKPOINT.md docs/archive/
git mv docs/SYSTEM_COMPLETION_PLAN.md docs/archive/
git mv docs/suggestions.md docs/archive/
git mv "docs/new suggestions 09062025.md" docs/archive/
git mv "docs/08.06.2025 suggestions on whats next.md" docs/archive/
git mv docs/last_context.md docs/archive/
git mv docs/task_dependencies.md docs/archive/
git mv docs/07.06.2025 docs/archive/  # (if it's a log file)

# Cleanup reports (archive):
git mv docs/PROJECT_CLEANUP_REPORT.md docs/archive/
git mv docs/CLEANUP_SUMMARY.md docs/archive/
git mv docs/FINAL_CLEANUP_REPORT.md docs/archive/

# Implementation reports (keep visible):
git mv docs/RSA_FIX_IMPLEMENTATION_REPORT.md docs/development/rsa-implementation.md
git mv docs/GUI_BASIC_CAPABILITIES.md docs/development/gui-capabilities.md
git mv docs/GUI_INTEGRATION_STATUS.md docs/development/gui-integration-status.md

# Deployment docs:
git mv docs/DEPLOYMENT_SUMMARY.md docs/deployment/summary.md

# Build outputs (remove or archive):
git rm docs/build_client_output.txt  # Build log, not documentation

# Duplicate CLAUDE.md (keep root, remove docs copy):
git rm docs/CLAUDE.md

# Create docs index:
cat > docs/README.md << 'EOF'
# Documentation Index

## Architecture
- [Detailed Specification](architecture/specification-detailed.md) - Complete system specification
- [Protocol Specification](architecture/protocol-specification.md) - Binary protocol details
- [RSA Implementation](development/rsa-implementation.md) - Hybrid RSA approach and fixes

## Development
- [Setup Summary](development/setup-summary.md) - Development environment setup
- [Build Organization](development/build-organization.md) - Build system structure
- [GUI Capabilities](development/gui-capabilities.md) - Client GUI features
- [Claude Code Guide](development/claude-code-guide.md) - AI assistant guidelines

## Deployment
- [Summary](deployment/summary.md) - Deployment overview and steps

## Troubleshooting
- [Linker Errors](troubleshooting/linker-errors.md) - Solving linking issues (31 errors)
- [GUI Linker Issues](troubleshooting/gui-linker-issues.md) - ClientGUIHelpers specific issues

## Archive
Historical planning documents, status reports, and deprecated guides.
EOF

git add docs/README.md
git commit -m "docs: Reorganize documentation into architecture/development/deployment hierarchy"
```
- [ ] **Verification:** `tree docs/` shows organized structure
- [ ] **Rationale:** Hierarchical docs are easier to navigate and maintain

---

### Low Priority

**Nice-to-have improvements that enhance developer experience but are not urgent.**

#### LOW-1: Add .editorconfig
- [ ] **Target:** Root `.editorconfig` (missing)
- [ ] **Action:** Add editor consistency configuration
- [ ] **Commands:**
```bash
cat > .editorconfig << 'EOF'
# EditorConfig for Encrypted Backup Framework
# https://editorconfig.org/

root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{cpp,h,hpp}]
indent_style = tab
indent_size = 4

[*.{py,yml,yaml,json}]
indent_style = space
indent_size = 4

[*.{bat,cmd}]
end_of_line = crlf

[*.md]
trim_trailing_whitespace = false
EOF

git add .editorconfig
git commit -m "chore(config): Add EditorConfig for consistent code style"
```

#### LOW-2: Add .gitattributes
- [ ] **Target:** Root `.gitattributes` (missing)
- [ ] **Action:** Normalize line endings and diff behavior
- [ ] **Commands:**
```bash
cat > .gitattributes << 'EOF'
# Auto-detect text files and normalize line endings to LF
* text=auto

# Force CRLF for Windows batch files
*.bat text eol=crlf
*.cmd text eol=crlf

# Force LF for shell scripts
*.sh text eol=lf

# Binary files
*.exe binary
*.dll binary
*.so binary
*.a binary
*.o binary
*.obj binary
*.db binary
*.sqlite binary
*.sqlite3 binary
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary

# Source files
*.cpp text diff=cpp
*.h text diff=cpp
*.hpp text diff=cpp
*.py text diff=python
*.md text diff=markdown
*.json text
*.yml text
*.yaml text
EOF

git add .gitattributes
git commit -m "chore(config): Add .gitattributes for line ending normalization"
```

#### LOW-3: Create LICENSE File
- [ ] **Target:** Root `LICENSE` (missing)
- [ ] **Action:** Add project license (select appropriate license)
- [ ] **Commands:**
```bash
# Example: MIT License (adjust as needed)
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 [Your Name/Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[Full MIT License text...]
EOF

git add LICENSE
git commit -m "docs: Add MIT License"
```

#### LOW-4: Create Configuration Examples
- [ ] **Target:** Client configuration templates (missing)
- [ ] **Action:** Create example config files
- [ ] **Commands:**
```bash
mkdir -p client/config

cat > client/config/transfer.info.example << 'EOF'
# Client Connection Configuration
# Format: 3 lines (server:port, username, file_path)

127.0.0.1:1256
example_user
C:\path\to\backup\file.txt
EOF

cat > client/config/me.info.example << 'EOF'
# Client Credentials (auto-generated on first registration)
# Format: 3 lines (username, UUID, Base64-encoded RSA private key)
#
# WARNING: This file contains your private RSA key. Keep it secure!
#
# [This file is generated automatically - do not create manually]
EOF

cat > server/config/server_config.py.example << 'EOF'
# Server Configuration Example
# Copy to server_config.py and customize

SERVER_PORT = 1256
MAX_CONNECTIONS = 10
DB_PATH = "data/defensive.db"
RECEIVED_FILES_DIR = "data/received_files"
LOG_LEVEL = "INFO"
LOG_FILE = "data/logs/server.log"

# Security Settings
RSA_KEY_SIZE = 1024  # Bits (matches client expectation)
AES_KEY_SIZE = 32    # Bytes (256-bit)

# Protocol Settings
PROTOCOL_VERSION = 3
MAX_PAYLOAD_SIZE = 104857600  # 100 MB
EOF

git add client/config/*.example server/config/*.example
git commit -m "docs: Add configuration file examples"
```

#### LOW-5: Create CONTRIBUTING.md
- [ ] **Target:** `docs/development/contributing.md` (missing)
- [ ] **Action:** Add contribution guidelines
- [ ] **Commands:**
```bash
cat > docs/development/contributing.md << 'EOF'
# Contributing Guidelines

## Development Setup

1. Clone repository
2. Install dependencies (see docs/development/setup-summary.md)
3. Build client: `cd client && .\build.bat`
4. Run tests: See client/tests/README.md and server/tests/

## Coding Standards

### C++ (Client)
- Style: Use .clang-format (config in /config/)
- Naming: PascalCase for classes, camelCase for functions
- Headers: Include guards mandatory
- Testing: Add unit tests for new crypto/protocol code

### Python (Server)
- Style: PEP 8
- Type hints: Preferred for public APIs
- Docstrings: Google style
- Testing: pytest for all new features

## Commit Messages

Format: `type(scope): description`

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- test: Tests
- refactor: Code refactoring
- chore: Maintenance

Example: `fix(client): Correct CRC32 endianness in protocol.cpp`

## Pull Request Process

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes with clear commits
3. Run tests: Client + Server + Integration
4. Update documentation if needed
5. Submit PR with description of changes
6. Await review

## Security

- **Never commit**: Private keys, credentials, database files
- **Always**: Use .gitignore, rotate exposed secrets
- **Report**: Security issues privately to [contact]

## Questions?

Open an issue or reach out to maintainers.
EOF

git add docs/development/contributing.md
git commit -m "docs: Add contributing guidelines"
```

---

## Stray File Detection & Verification

### Automated Detection Commands

#### Find Build Artifacts
```bash
# Object files, binaries, libraries:
find . -type f \( -name '*.o' -o -name '*.obj' -o -name '*.exe' -o -name '*.so' -o -name '*.dll' -o -name '*.a' -o -name '*.lib' -o -name '*.ilk' -o -name '*.pdb' \) ! -path '*/third_party/*'

# Python bytecode:
find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -o -type d -name '__pycache__'

# IDE artifacts:
find . -type d \( -name '.vscode' -o -name '.idea' -o -name '.vs' \)

# Temporary files:
find . -type f \( -name '*~' -o -name '*.swp' -o -name '*.swo' -o -name '*.bak' -o -name '*.tmp' \)
```

#### Find Large Files (Potential Artifacts)
```bash
# Files > 5MB (likely binaries or logs):
find . -type f -size +5M -exec ls -lh {} \; | awk '{print $9, $5}'

# Files > 1MB (check if needed):
find . -type f -size +1M -size -5M -exec ls -lh {} \; | awk '{print $9, $5}'
```

#### Find Unused Files (Reference Search)
```bash
# Example: Check if a file is referenced anywhere:
FILE="temp_complete_server.py"
grep -r "$FILE" --include="*.cpp" --include="*.py" --include="*.bat" --include="*.md" --include="*.txt" . | grep -v "Binary file"

# Check imports for Python files:
FILE="crypto_compat.py"
grep -r "import crypto_compat\|from crypto_compat" --include="*.py" .

# Check includes for C++ files:
FILE="ClientGUI.h"
grep -r "#include.*ClientGUI\.h" --include="*.cpp" --include="*.h" .
```

#### Find Potential Secrets
```bash
# Files that might contain secrets (DO NOT print contents):
find . -type f \( -name '*.key' -o -name '*.pem' -o -name '*.der' -o -name '*.crt' -o -name '*.env' -o -name '*secret*' -o -name '*password*' -o -name 'me.info' -o -name 'transfer.info' \) ! -name '*.example'

# Search for patterns that look like secrets (be careful with false positives):
grep -r "BEGIN.*PRIVATE KEY\|password\s*=\|secret\s*=\|api_key\s*=" --include="*.py" --include="*.cpp" --include="*.txt" . | head -20

# Check for hardcoded IPs and ports:
grep -rn "127\.0\.0\.1\|localhost\|192\.168\|10\.\|172\." --include="*.cpp" --include="*.py" --include="*.bat" . | grep -v "comment\|#"
```

### Safe Archiving Procedure

**Never immediately delete** questionable files. Follow this workflow:

```bash
# Step 1: Create legacy branch for archiving
git checkout -b legacy-archive-$(date +%Y%m%d)

# Step 2: Create legacy directories
mkdir -p legacy/{old_tests,build_variants,temp_files,deprecated_docs}

# Step 3: Move (don't delete) questionable files
git mv <file> legacy/<category>/

# Step 4: Add README explaining why
echo "# Legacy Files - $(date)" > legacy/<category>/README.md
echo "Archived during cleanup on $(date). Preserved for historical reference." >> legacy/<category>/README.md

# Step 5: Commit archival
git add legacy/
git commit -m "archive: Move <category> to legacy ($(date +%Y-%m-%d))"

# Step 6: Verify builds/tests still work
cd client && .\build.bat
cd ../server && python -m pytest tests/

# Step 7: If everything works, merge to main
git checkout main
git merge legacy-archive-$(date +%Y%m%d)

# Step 8: After 30 days of verification, consider permanent deletion
# (Optional) git rm -r legacy/<category> && git commit -m "cleanup: Remove archived <category>"
```

### Verification Checklist for Each File

Before moving/deleting any file, verify:

- [ ] **Not referenced in code**: `grep -r "filename" --include="*.cpp" --include="*.py" --include="*.bat" .`
- [ ] **Not in CMakeLists/Makefile**: Check build system files
- [ ] **Not in requirements.txt**: Check Python dependencies
- [ ] **Not in package.json**: Check JS dependencies (if applicable)
- [ ] **Not critical config**: Not referenced in CLAUDE.md or documentation
- [ ] **Builds still work**: Run `build.bat` or relevant build command
- [ ] **Tests still pass**: Run test suite
- [ ] **Has replacement**: If removing, confirm equivalent exists elsewhere

---

## Security & Secrets Checklist

### Current Security Posture Assessment

#### Known Security Issues (from CLAUDE.md)
1. **Static IV for AES-CBC**: AES encryption uses zero IV (not production-ready)
2. **Plaintext key storage**: RSA private keys stored unencrypted in `me.info`
3. **No HMAC/signatures**: Protocol relies solely on RSA key validation
4. **No authentication**: Beyond RSA key, no user authentication mechanism

#### Files That May Contain Secrets

```bash
# Check for secret-containing files (DO NOT cat/print in scripts):
ls -la me.info transfer.info client/me.info client/transfer.info data/priv.key 2>/dev/null

# These files MUST be in .gitignore:
- me.info (contains RSA private key in Base64)
- transfer.info (contains server connection details, may include credentials)
- client/priv.key (deprecated key storage location)
- data/priv.key (deprecated key storage location)
- server/defensive.db (contains client UUIDs and public keys)
- **/received_files/* (user data)
```

### Secret Detection Commands

```bash
# DO NOT run these commands in CI or share output publicly:

# 1. Check for private keys in repo:
git log --all --full-history --source --find-copies-harder -S "BEGIN PRIVATE KEY" | head -20

# 2. Check .gitignore coverage:
cat .gitignore | grep -E "\.key|\.pem|me\.info|transfer\.info|defensive\.db"

# 3. Verify secrets are gitignored:
git ls-files | grep -E "\.key$|me\.info$|transfer\.info$|priv\.key$"
# (Should return nothing - if files appear, they're tracked!)

# 4. Check for hardcoded credentials:
grep -rn "password\s*=.*['\"]" --include="*.py" --include="*.cpp" . | grep -v "example\|template\|comment"
```

### Secrets Remediation Plan

#### CRIT: If Secrets Found in Git History

```bash
# If private keys or credentials were committed:

# 1. IMMEDIATELY rotate all affected keys
#    - Regenerate RSA key pairs
#    - Change any passwords/tokens that were exposed
#    - Notify all users to regenerate their client credentials

# 2. Use git-filter-repo (or BFG Repo Cleaner) to remove from history:
# WARNING: This rewrites history - coordinate with all developers first!

# Install git-filter-repo:
pip install git-filter-repo

# Remove specific file from all history:
git filter-repo --invert-paths --path me.info --path transfer.info --force

# 3. Force push (DANGEROUS - requires team coordination):
git push origin --force --all

# 4. All developers must re-clone:
# git clone <repo-url>  # Fresh clone required after history rewrite
```

#### HIGH: Ensure .gitignore Completeness

```bash
# Add to .gitignore (if not already present):
cat >> .gitignore << 'EOF'

# Secret and credential files
me.info
transfer.info
priv.key
*.key
*.pem
*.der
*.crt
**/client/me.info
**/client/transfer.info
**/data/priv.key

# Database files (contain user data)
**/defensive.db
*.db
*.sqlite
*.sqlite3

# User data
**/received_files/
**/data/

# Environment files
.env
.env.local
.env.*.local

EOF

git add .gitignore
git commit -m "security: Ensure secrets are gitignored"
```

### Security Best Practices (Future Implementation)

Recommendations for production deployment:

1. **Key Storage**: Use OS keychain (Windows Credential Manager, macOS Keychain, Linux Secret Service)
2. **Key Rotation**: Implement automatic key rotation every 90 days
3. **Authentication**: Add HMAC-SHA256 for message authentication
4. **IV Generation**: Use cryptographically secure random IV for each AES encryption
5. **TLS/SSL**: Wrap TCP connection in TLS for defense-in-depth
6. **Access Control**: Add user authentication (OAuth2, JWT, or similar)
7. **Audit Logging**: Log all file transfers and key exchanges

---

## Dependencies & Environment

### Current Dependency State

#### C++ Client Dependencies

**Compiler:**
- Windows: MSVC 19.44.35207 (Visual Studio 2022 Build Tools)
- Linux: g++ with C++17 support (not fully tested per current setup)

**Libraries:**
- Crypto++ (bundled in `third_party/crypto++/`)
- Boost headers (referenced in build.bat: `C:\Users\tom7s\Downloads\boost_1_88_0\boost_1_88_0`)
  - **ISSUE**: Hardcoded absolute path in build.bat - needs to be made configurable

**System Libraries:**
- ws2_32.lib (Windows Sockets)
- advapi32.lib (Windows Crypto API)
- user32.lib (Windows GUI)

#### Python Server Dependencies

**Python Version:** 3.11.4 (per CLAUDE.md)

**Required Packages** (TO DOCUMENT in requirements.txt):
```
pycryptodome>=3.15.0,<4.0.0  # Crypto primitives (AES, RSA, PKCS1_OAEP)
pytest>=7.0.0                # Testing framework
pytest-timeout>=2.1.0        # Test timeouts
```

**Optional Packages:**
```
# For GUI (usually built-in):
tkinter  # Comes with Python, no pip install needed

# For development:
black>=23.0.0         # Code formatter
mypy>=1.0.0           # Type checking
pylint>=2.17.0        # Linter
```

**Standard Library** (no installation needed):
- socket, threading, struct, uuid, os, time, logging, sqlite3, datetime

### Dependency Consolidation Plan

#### Action 1: Create Comprehensive requirements.txt

```bash
cat > server/requirements.txt << 'EOF'
# Production Dependencies
pycryptodome>=3.15.0,<4.0.0

# Development Dependencies
pytest>=7.0.0
pytest-timeout>=2.1.0
black>=23.0.0
mypy>=1.0.0
pylint>=2.17.0

# Testing Dependencies
pytest-cov>=4.0.0  # Code coverage

# Note: tkinter (for ServerGUI.py) is included with Python, no pip package needed
EOF
```

#### Action 2: Create requirements-dev.txt (Optional)

```bash
cat > server/requirements-dev.txt << 'EOF'
-r requirements.txt

# Additional dev tools
ipython>=8.0.0
ipdb>=0.13.0
pytest-watch>=4.2.0

# Documentation
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0
EOF
```

#### Action 3: Fix Hardcoded Paths in build.bat

```bash
# In client/build.bat, replace:
# set "BOOST_INCLUDE=C:\Users\tom7s\Downloads\boost_1_88_0\boost_1_88_0"

# With environment variable check:
set "BOOST_INCLUDE=%BOOST_ROOT%"
if "%BOOST_INCLUDE%"=="" (
    echo ERROR: BOOST_ROOT environment variable not set
    echo Please set BOOST_ROOT to your Boost installation directory
    echo Example: set BOOST_ROOT=C:\path\to\boost_1_88_0
    exit /b 1
)
```

#### Action 4: Create Environment Setup Script

```bash
# server/setup_env.sh (Linux/Mac):
cat > server/setup_env.sh << 'EOF'
#!/bin/bash
# Server environment setup script

echo "Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Environment ready. Activate with: source .venv/bin/activate"
EOF
chmod +x server/setup_env.sh

# server/setup_env.bat (Windows):
cat > server/setup_env.bat << 'EOF'
@echo off
REM Server environment setup script

echo Setting up Python virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Environment ready. Activate with: .venv\Scripts\activate.bat
EOF
```

### Development Environment Files

#### Recommended .editorconfig (Already in LOW-1)

#### Recommended .gitattributes (Already in LOW-2)

#### Recommended devcontainer.json (Optional - for VSCode)

```bash
mkdir -p .devcontainer
cat > .devcontainer/devcontainer.json << 'EOF'
{
  "name": "Encrypted Backup Framework",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {},
    "ghcr.io/devcontainers/features/git:1": {}
  },
  "postCreateCommand": "cd server && pip install -r requirements.txt",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-vscode.cpptools"
      ]
    }
  }
}
EOF
```

#### Recommended Dockerfile (Optional - for server deployment)

```bash
cat > server/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py ServerGUI.py crypto_compat.py ./

# Expose default port
EXPOSE 1256

# Create data directory
RUN mkdir -p data/received_files data/logs

# Run server
CMD ["python", "server.py"]
EOF
```

---

## Tests, CI, and Automation

### Current Test Coverage

#### C++ Client Tests (11 files in /tests/)
- **RSA Tests**: test_rsa_final.cpp, test_rsa_wrapper_final.cpp (primary validation)
- **Crypto Tests**: test_crypto_basic.cpp, test_crypto_minimal.cpp
- **RSA Variants**: test_rsa.cpp, test_rsa_detailed.cpp, test_rsa_manual.cpp, test_rsa_pregenerated.cpp, test_minimal_rsa.cpp, test_rsa_crypto_plus_plus.cpp
- **Performance**: client_benchmark.cpp

#### Python Server Tests (3 files)
- server/test_server.py - Server unit tests
- server/test_gui.py - GUI startup tests
- tests/test_connection.py - Client-server connection tests

#### Integration Tests (3 files in root)
- test_system.py - Full end-to-end workflow
- test_client.py - Client simulation
- binary_test_client.py - Protocol validation

### Recommended Test Organization (Post-Cleanup)

```
client/tests/
├── unit/
│   ├── test_rsa_final.cpp          # Primary RSA validation
│   ├── test_rsa_wrapper_final.cpp  # Wrapper API tests
│   ├── test_crypto_basic.cpp       # Crypto primitives
│   ├── test_cksum.cpp              # Checksum validation (TO CREATE)
│   └── test_protocol.cpp           # Protocol serialization (TO CREATE)
└── integration/
    └── client_benchmark.cpp        # Performance tests

server/tests/
├── test_server.py          # Server logic unit tests
├── test_gui.py             # GUI component tests
└── test_connection.py      # Connection handling tests

tests/integration/
├── test_system.py          # Full backup workflow
├── test_client.py          # Client protocol simulation
└── binary_test_client.py   # Binary protocol validation
```

### Test Execution Commands

#### C++ Client Tests
```cmd
REM Build tests:
cd scripts\build
.\build_rsa_final_test.bat
.\build_rsa_wrapper_final_test.bat

REM Run primary tests:
cd ..\..\client\build
test_rsa_final.exe
test_rsa_wrapper_final.exe

REM Expected: All tests pass, exit code 0
```

#### Python Server Tests
```bash
cd server
python -m pytest tests/ -v --tb=short

# With coverage:
python -m pytest tests/ -v --cov=. --cov-report=html
```

#### Integration Tests
```bash
# Start server:
cd server && python server.py &
SERVER_PID=$!

# Run integration tests:
cd tests/integration
python test_system.py
python test_client.py
python binary_test_client.py

# Cleanup:
kill $SERVER_PID
```

### Smoke Test Script (Quick Validation)

```bash
cat > scripts/smoke_test.sh << 'EOF'
#!/bin/bash
# Quick smoke test for CI/CD

set -e  # Exit on any error

echo "=== Smoke Test Suite ==="

# 1. Check Python dependencies
echo "[1/5] Checking Python dependencies..."
cd server
python -c "from Crypto.Cipher import AES; print('✓ PyCryptodome OK')"
cd ..

# 2. Check Python syntax
echo "[2/5] Checking Python syntax..."
python -m py_compile server/server.py
python -m py_compile server/ServerGUI.py
python -m py_compile server/crypto_compat.py

# 3. Run Python unit tests
echo "[3/5] Running server unit tests..."
cd server
python -m pytest tests/test_server.py -v --tb=line
cd ..

# 4. Start server briefly
echo "[4/5] Testing server startup..."
cd server
timeout 5 python server.py &
sleep 2
netstat -an | grep 1256 || (echo "✗ Server not listening"; exit 1)
pkill -f "python server.py"
cd ..

# 5. Verify file structure
echo "[5/5] Verifying project structure..."
test -f README.md || (echo "✗ Missing README.md"; exit 1)
test -f server/requirements.txt || (echo "✗ Missing requirements.txt"; exit 1)
test -d client/ || (echo "✗ Missing client/ directory"; exit 1)
test -d server/ || (echo "✗ Missing server/ directory"; exit 1)

echo "✓ All smoke tests passed!"
EOF
chmod +x scripts/smoke_test.sh
```

### Continuous Integration (GitHub Actions)

#### Recommended CI Workflow: Build Client

```bash
mkdir -p .github/workflows
cat > .github/workflows/build-client.yml << 'EOF'
name: Build C++ Client

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'client/**'
      - 'include/**'
      - 'src/**'
      - 'tests/**/*.cpp'
  pull_request:
    branches: [ main ]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup MSVC
        uses: microsoft/setup-msbuild@v1.1

      - name: Build Client
        run: |
          cd client
          .\build.bat

      - name: Run Tests
        run: |
          cd client\build
          .\test_rsa_final.exe
          .\test_rsa_wrapper_final.exe

      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: client-windows
          path: client/build/EncryptedBackupClient.exe
EOF
```

#### Recommended CI Workflow: Test Server

```bash
cat > .github/workflows/test-server.yml << 'EOF'
name: Test Python Server

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'server/**'
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          cd server
          pip install -r requirements.txt

      - name: Run linting
        run: |
          pip install pylint
          pylint server/*.py --disable=C,R

      - name: Run tests
        run: |
          cd server
          python -m pytest tests/ -v --tb=short

      - name: Test server startup
        run: |
          cd server
          timeout 5 python server.py &
          sleep 2
          netstat -tuln | grep 1256
EOF
```

#### Recommended CI Workflow: Integration Tests

```bash
cat > .github/workflows/integration-tests.yml << 'EOF'
name: Integration Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  integration:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd server
          pip install -r requirements.txt

      - name: Start server
        run: |
          cd server
          python server.py &
          echo $! > server.pid
          sleep 3

      - name: Run integration tests
        run: |
          cd tests/integration
          python test_system.py
          python test_client.py

      - name: Stop server
        if: always()
        run: |
          if [ -f server/server.pid ]; then
            kill $(cat server/server.pid) || true
          fi
EOF
```

### Test Acceptance Criteria

For each PR/commit, the following must pass:

- [ ] **C++ Build**: Client builds without errors on Windows (MSVC)
- [ ] **C++ Tests**: `test_rsa_final.exe` and `test_rsa_wrapper_final.exe` pass
- [ ] **Python Syntax**: All Python files pass `python -m py_compile`
- [ ] **Python Tests**: `pytest server/tests/` passes with 0 failures
- [ ] **Server Startup**: Server starts and listens on port 1256
- [ ] **Integration**: At least one end-to-end test passes
- [ ] **No Secrets**: `git diff` contains no private keys or credentials

---

## Documentation

### Current Documentation State

**26 files in /docs/** (flat structure, overlapping content):
- Specifications, status reports, troubleshooting guides, planning documents, build logs
- No clear index or hierarchy
- Multiple docs with similar purposes (e.g., 4+ status/checkpoint files)
- Duplicate CLAUDE.md in both root and /docs/

### Recommended Documentation Structure

```
docs/
├── README.md                          # Documentation index
├── architecture/
│   ├── system-overview.md             # High-level architecture (TO CREATE)
│   ├── protocol-specification.md      # Binary protocol details (existing)
│   ├── specification-detailed.md      # Complete spec (existing)
│   ├── encryption-design.md           # Crypto implementation (TO CREATE)
│   └── dataflow.md                    # Data flow diagrams (TO CREATE)
├── development/
│   ├── setup.md                       # Dev environment setup (TO CREATE)
│   ├── setup-summary.md               # Existing setup summary
│   ├── building.md                    # Build instructions (TO CREATE)
│   ├── build-organization.md          # Build system structure (existing)
│   ├── testing.md                     # Testing guide (TO CREATE)
│   ├── contributing.md                # Contribution guidelines (LOW-5)
│   ├── rsa-implementation.md          # RSA fix details (existing)
│   ├── gui-capabilities.md            # GUI features (existing)
│   └── claude-code-guide.md           # AI assistant guide (existing)
├── deployment/
│   ├── server-deployment.md           # Server deployment (TO CREATE)
│   ├── client-deployment.md           # Client deployment (TO CREATE)
│   ├── summary.md                     # Deployment summary (existing)
│   └── security-hardening.md          # Production security (TO CREATE)
├── troubleshooting/
│   ├── linker-errors.md               # Linker issues (existing)
│   ├── gui-linker-issues.md           # GUI linker issues (existing)
│   ├── connection-issues.md           # Network troubleshooting (TO CREATE)
│   └── crypto-issues.md               # Crypto troubleshooting (TO CREATE)
└── archive/
    └── [historical planning docs]     # Moved in MED-5
```

### Documentation To Create

#### HIGH: System Overview Diagram

```bash
cat > docs/architecture/system-overview.md << 'EOF'
# System Architecture Overview

## Components

### C++ Client
- **Purpose**: Securely backup files to remote server
- **Key Files**: client.cpp, protocol.cpp, RSAWrapper.cpp, AESWrapper.cpp
- **Responsibilities**:
  - File reading and AES-256-CBC encryption
  - RSA key exchange with server
  - Binary protocol communication (version 3, little-endian)
  - CRC32 checksum computation (Linux cksum-compatible)
  - Local credential management (UUID, RSA private key)

### Python Server
- **Purpose**: Receive and store encrypted backups
- **Key Files**: server.py, crypto_compat.py, ServerGUI.py
- **Responsibilities**:
  - TCP server on port 1256
  - Multi-threaded client connection handling
  - RSA key pair generation and management
  - AES decryption and file storage
  - SQLite database for client metadata
  - Optional Tkinter GUI for monitoring

### SQLite Database
- **File**: server/defensive.db
- **Tables**: clients (UUID, username, public_key, last_seen, aes_key), files (client_id, filename, size, received_at)
- **Purpose**: Persist client registrations and file transfer history

## Communication Flow

```
┌────────────────┐                                   ┌────────────────┐
│  C++ Client    │                                   │ Python Server  │
└────────────────┘                                   └────────────────┘
         │                                                   │
         │  1. Registration Request (Code 1025)              │
         │  Payload: username (255 bytes)                    │
         ├──────────────────────────────────────────────────>│
         │                                                   │
         │                   2. Generate RSA Pair            │
         │                      Store in SQLite              │
         │                                                   │
         │  3. Registration Success (Code 1600)              │
         │  Payload: UUID (16 bytes)                         │
         │<──────────────────────────────────────────────────┤
         │                                                   │
         │  4. Public Key Request (Code 1827)                │
         ├──────────────────────────────────────────────────>│
         │                                                   │
         │  5. Public Key Response (Code 1602)               │
         │  Payload: UUID, RSA public key (160 bytes)        │
         │<──────────────────────────────────────────────────┤
         │                                                   │
         │  6. Generate AES-256 key                          │
         │     Encrypt with server's RSA public key          │
         │                                                   │
         │  7. Send AES Key (Code 1026)                      │
         │  Payload: UUID, Encrypted AES key                 │
         ├──────────────────────────────────────────────────>│
         │                                                   │
         │                   8. Decrypt AES key with RSA      │
         │                      Store AES key in SQLite      │
         │                                                   │
         │  9. Read local file                               │
         │     Encrypt with AES-256-CBC (zero IV)            │
         │     Compute CRC32                                 │
         │                                                   │
         │  10. Send Encrypted File (Code 1028)              │
         │  Payload: content_size, filename, encrypted_data  │
         ├──────────────────────────────────────────────────>│
         │                                                   │
         │                   11. Decrypt file with AES        │
         │                       Save to received_files/     │
         │                       Log to database             │
         │                                                   │
         │  12. File Received OK (Code 1603)                 │
         │<──────────────────────────────────────────────────┤
         │                                                   │
         │  13. Send CRC (Code 1031)                         │
         │  Payload: filename, CRC32                         │
         ├──────────────────────────────────────────────────>│
         │                                                   │
         │                   14. Validate CRC                 │
         │                                                   │
         │  15. CRC Valid (Code 1604)                        │
         │<──────────────────────────────────────────────────┤
         │                                                   │
```

## Protocol Specification

**Version**: 3
**Endianness**: Little-endian throughout
**Header Size**: 23 bytes
**Header Format**:
- client_id (16 bytes, UUID)
- version (1 byte)
- code (2 bytes, request/response code)
- payload_size (4 bytes)

**Request Codes**:
- 1025: Register
- 1026: Send AES Key
- 1027: Reconnect
- 1028: Send File
- 1029-1030: Reserved
- 1031: Send CRC

**Response Codes**:
- 1600: Registration Success
- 1601: Registration Failed
- 1602: Public Key Response
- 1603: File Received OK
- 1604: CRC Valid
- 1605: CRC Invalid
- 1606: Reconnection Success
- 1607: Reconnection Failed

## Security Model

**Encryption**:
- RSA-1024 (hybrid: 512-bit primary + XOR fallback)
- AES-256-CBC (with static zero IV - **not production-ready**)

**Key Management**:
- Client: Generates RSA pair on first registration, stores private key in `me.info` (Base64)
- Server: Generates RSA pair per client, stores public key in SQLite

**Integrity**:
- CRC32 checksum (custom implementation matching Linux `cksum`)

**Known Limitations** (see Security Notes in root README.md):
- Static IV for AES (predictable, vulnerable to attacks)
- No HMAC or message authentication
- Keys stored in plaintext
- No authentication beyond RSA key validation

## File Storage

**Client**:
- Config: `transfer.info` (server:port, username, file_path)
- Credentials: `me.info` (username, UUID, RSA private key)

**Server**:
- Config: `server/port.info` (default port: 1256)
- Database: `server/defensive.db` (SQLite3)
- Received Files: `server/data/received_files/` (gitignored)
- Logs: `server/data/logs/` (gitignored)

## Build & Deployment

**Client**:
- Windows: MSVC 19.44+ via `client\build.bat`
- Linux: g++ with C++17 (experimental support)
- Dependencies: Crypto++ (bundled), Boost headers

**Server**:
- Python 3.11+
- Dependencies: PyCryptodome (see `server/requirements.txt`)
- Deployment: Direct execution or Docker (see `server/Dockerfile`)

---

## Future Enhancements

- [ ] Add TLS/SSL for transport encryption
- [ ] Implement HMAC-SHA256 for message authentication
- [ ] Use random IV per AES encryption
- [ ] Add user authentication (OAuth2/JWT)
- [ ] Implement key rotation mechanism
- [ ] Add file chunking for large files (>100MB)
- [ ] Web-based GUI for server monitoring
- [ ] Cross-platform client builds (Linux, macOS)
EOF
```

#### MED: Testing Guide

```bash
cat > docs/development/testing.md << 'EOF'
# Testing Guide

## Test Structure

### Client Tests (C++)
Located in `client/tests/`:
- **unit/**: RSA, crypto, protocol unit tests
- **integration/**: Full workflow and performance tests

### Server Tests (Python)
Located in `server/tests/`:
- `test_server.py`: Server logic unit tests
- `test_gui.py`: GUI component tests
- `test_connection.py`: Connection handling

### Integration Tests
Located in `tests/integration/`:
- `test_system.py`: Full end-to-end backup workflow
- `test_client.py`: Client protocol simulation
- `binary_test_client.py`: Binary protocol validation

## Running Tests

### Quick Test (Smoke Test)
```bash
./scripts/smoke_test.sh
```

### Client Tests
```cmd
cd scripts\build
.\build_rsa_final_test.bat
.\build_rsa_wrapper_final_test.bat

cd ..\..\client\build
test_rsa_final.exe
test_rsa_wrapper_final.exe
```

### Server Tests
```bash
cd server
pytest tests/ -v
```

### Integration Tests
```bash
# Start server:
cd server && python server.py &
SERVER_PID=$!

# Run tests:
cd tests/integration
python test_system.py
python test_client.py
python binary_test_client.py

# Stop server:
kill $SERVER_PID
```

## Test Development

### Adding C++ Tests
1. Create test file in `client/tests/unit/` or `client/tests/integration/`
2. Add corresponding build script in `scripts/build/`
3. Update `client/tests/README.md` with test description
4. Run test to verify

### Adding Python Tests
1. Create test file in `server/tests/` with `test_` prefix
2. Use pytest fixtures for common setup
3. Add assertions with clear failure messages
4. Run with `pytest server/tests/test_yourtest.py -v`

## Continuous Integration

Tests run automatically on:
- Every push to `main` or `develop` branches
- Every pull request to `main`

See `.github/workflows/` for CI configuration.

## Troubleshooting Test Failures

### Client Test Failures
- **Linker errors**: Check Crypto++ paths in build.bat
- **RSA failures**: Verify Crypto++ version and PRNG initialization
- **CRC mismatches**: Endianness issue, verify little-endian throughout

### Server Test Failures
- **Import errors**: `pip install -r requirements.txt`
- **Connection refused**: Check port 1256 is available
- **Database locked**: Close other server instances

### Integration Test Failures
- **Server not responding**: Verify server started (check logs)
- **Protocol mismatch**: Ensure client and server on same protocol version
- **File not received**: Check `server/data/received_files/` permissions
EOF
```

### Documentation Templates

#### Template: Feature Documentation

```markdown
# [Feature Name]

## Overview
Brief description of what this feature does.

## Usage
How to use this feature (code examples, commands).

## Configuration
What settings/config files affect this feature.

## Implementation Details
Technical details for maintainers.

## Known Issues
Current limitations or bugs.

## Future Work
Planned improvements.
```

#### Template: Troubleshooting Guide

```markdown
# [Problem Category] Troubleshooting

## Symptoms
What the user observes when the problem occurs.

## Diagnosis
How to confirm this is the actual problem.

## Solutions

### Solution 1: [Most Common Fix]
Step-by-step instructions.

### Solution 2: [Alternative Fix]
When to use this approach.

## Prevention
How to avoid this problem in the future.

## Related Issues
Links to GitHub issues or other docs.
```

---

## Implementation Plan

### Overview

This section provides a **safe, step-by-step implementation sequence** for executing the cleanup plan. The plan is designed to be executed in phases, with validation checkpoints after each phase to ensure nothing breaks.

### Prerequisites

Before starting ANY cleanup operations:

1. **Full backup**: Ensure you have a complete backup of the repository
2. **Clean working tree**: Commit or stash all changes (`git status` should be clean)
3. **Branch protection**: Ensure you're NOT on the main branch
4. **Testing baseline**: Run full test suite and record results
5. **Documentation review**: Read this entire document thoroughly

### Implementation Sequence

The cleanup is divided into **5 phases**, each building on the previous:

```
Phase 1: Critical Security & Build Fixes (MUST DO FIRST)
    ↓
Phase 2: Root-Level Organization (High Priority)
    ↓
Phase 3: Source Code Reorganization (Medium Priority)
    ↓
Phase 4: Documentation & Configuration (Medium Priority)
    ↓
Phase 5: Final Polish & Validation (Low Priority)
```

---

### Phase 1: Critical Security & Build Fixes

**Duration:** 30-60 minutes
**Risk Level:** LOW (mostly additions to .gitignore and dependency documentation)
**Rollback:** Easy (single git reset)

#### Steps

```bash
# 1.1: Create feature branch
git checkout -b cleanup/phase1-critical
git push -u origin cleanup/phase1-critical

# 1.2: Execute CRIT-1 (Remove binary)
git rm tests/test_rsa_crypto_plus_plus
git commit -m "chore(cleanup): Remove committed test binary"

# 1.3: Execute CRIT-2 (Update .gitignore)
# Copy commands from CRIT-2 in Action Checklist
# ... (add comprehensive .gitignore rules)
git add .gitignore
git commit -m "fix(config): Comprehensive .gitignore to prevent binary commits"

# 1.4: Execute CRIT-3 (Handle temp_complete_server.py)
diff -q server/server.py temp_complete_server.py
# Follow decision tree in CRIT-3
# ... (either delete or move to legacy)

# 1.5: Execute CRIT-4 (Create requirements.txt)
# Copy commands from CRIT-4
# ... (create server/requirements.txt)
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "from Crypto.Cipher import AES; print('✓ OK')"
deactivate
cd ..
git add server/requirements.txt
git commit -m "feat(server): Add requirements.txt for dependency management"

# 1.6: Execute CRIT-5 (Remove duplicate port.info)
grep -rn "port\.info" --include="*.py" --include="*.bat" .
git rm port.info
git commit -m "chore(config): Remove duplicate root port.info"

# 1.7: Validation checkpoint
echo "=== Phase 1 Validation ==="
git log --oneline -5
git status
cd server && python -c "import server" && cd ..
echo "✓ Phase 1 complete"

# 1.8: Push and create PR (optional)
git push origin cleanup/phase1-critical
# Create PR, get review, merge to main
```

#### Validation Criteria for Phase 1

- [ ] `git status` shows clean tree
- [ ] `pip install -r server/requirements.txt` succeeds
- [ ] Server imports without errors: `python -c "import server"`
- [ ] `.gitignore` prevents committing of `*.exe`, `*.db`, `me.info`, `transfer.info`
- [ ] No binaries in git: `git ls-files | grep -E "\.exe$|\.o$"` returns nothing

---

### Phase 2: Root-Level Organization

**Duration:** 1-2 hours
**Risk Level:** MEDIUM (moves files, but preserves everything in legacy/)
**Rollback:** Moderate (can revert individual commits)

#### Steps

```bash
# 2.1: Create phase 2 branch
git checkout main
git pull origin main
git checkout -b cleanup/phase2-root-organization

# 2.2: Create legacy structure
mkdir -p legacy/{old_tests,build_variants,temp_files}

# 2.3: Execute HIGH-1 (Create README.md)
# Copy commands from HIGH-1
# ... (create comprehensive README.md)
git add README.md
git commit -m "docs: Add comprehensive root README with quick start"

# 2.4: Execute HIGH-2 (Consolidate build scripts)
# IMPORTANT: First verify build.bat works!
.\build.bat
# If successful, proceed:
git mv build_fixed.bat legacy/build_variants/
git mv build_safe.bat legacy/build_variants/
git mv build.bat.backup legacy/build_variants/
# ... (add README to legacy/build_variants)
git add legacy/build_variants/README.md
git commit -m "chore(legacy): Archive old build script variants"

# 2.5: Execute HIGH-3 (Move root test files)
mkdir -p legacy/old_tests
git mv simple_test.cpp simple_console_test.cpp test_minimal.cpp test_simple.cpp legacy/old_tests/
git mv simple_test.py minimal_test.py legacy/old_tests/
# ... (add README)
git add legacy/old_tests/README.md
git commit -m "chore(legacy): Archive early test experiments"

# 2.6: Execute HIGH-4 (Move integration tests)
mkdir -p tests/integration
git mv test_client.py test_system.py binary_test_client.py tests/integration/
# ... (add README)
git add tests/integration/README.md
git commit -m "test(integration): Organize integration tests"

# 2.7: Execute HIGH-5 (Delete empty files)
grep -rn "diff_output\.txt\|test_file\.txt" --include="*.cpp" --include="*.py" .
# If no references:
git rm diff_output.txt test_file.txt client/test_file.txt
git commit -m "chore(cleanup): Remove temporary files"

# 2.8: Validation checkpoint
echo "=== Phase 2 Validation ==="
tree -L 2 legacy/  # Should show organized legacy structure
ls tests/integration/*.py  # Should show 3 files
.\build.bat  # CRITICAL: Must still work
git log --oneline -7
echo "✓ Phase 2 complete"

# 2.9: Push and merge
git push origin cleanup/phase2-root-organization
# Create PR, test, merge
```

#### Validation Criteria for Phase 2

- [ ] Root directory has <10 files (not counting .git, legacy/, etc.)
- [ ] `build.bat` still builds successfully
- [ ] Legacy directories have README.md explaining contents
- [ ] `tests/integration/` contains 3 Python test files
- [ ] No broken references: `grep -r "simple_test\.cpp" .` returns nothing

---

### Phase 3: Source Code Reorganization

**Duration:** 2-3 hours
**Risk Level:** HIGH (moves source files, updates build paths)
**Rollback:** Difficult (requires careful git revert)

#### Steps

```bash
# 3.1: Create phase 3 branch
git checkout main
git pull origin main
git checkout -b cleanup/phase3-source-reorganization

# 3.2: Execute MED-1 (Reorganize client source tree)
# CAREFUL: This moves /src/ and /include/ to /client/
mkdir -p client/{include,src/stubs}

# Move headers:
git mv include/client client/include/
git mv include/wrappers client/include/

# Move source:
git mv src/client client/src/
git mv src/wrappers client/src/

# Move stubs:
git mv src/*.cpp client/src/stubs/

# Move build scripts:
git mv build.bat client/
git mv clean.bat client/
git mv start_client.bat client/
git mv run_client_debug.bat debug_client.bat check_client_process.bat client/

# 3.3: CRITICAL: Update build.bat paths
# Manual edit client/build.bat:
# - Verify all paths are relative and still correct
# - Paths like "include\client" should already work

# 3.4: Test build IMMEDIATELY
cd client
.\build.bat
# If build fails, STOP and fix paths before proceeding
cd ..

# 3.5: Commit source reorganization
git add client/
git commit -m "refactor(client): Consolidate client code in /client/ directory"

# 3.6: Execute MED-2 (Reorganize client tests)
mkdir -p client/tests/{unit,integration,fixtures}
mkdir -p scripts/build

# Move tests:
git mv tests/test_rsa_final.cpp client/tests/unit/
git mv tests/test_rsa_wrapper_final.cpp client/tests/unit/
# ... (move all test files per MED-2)

# Move test build scripts:
git mv scripts/build_*.bat scripts/build/

# 3.7: Update test build scripts
# Manual edit: Update paths in scripts/build/*.bat to reference client/tests/
# Example: Change "tests\test_rsa_final.cpp" to "client\tests\unit\test_rsa_final.cpp"

# 3.8: Test build scripts
cd scripts/build
.\build_rsa_final_test.bat
cd ../..
client\build\test_rsa_final.exe  # Must pass

# 3.9: Commit test reorganization
git add client/tests/ scripts/build/
git commit -m "test(client): Organize tests into unit/integration subdirectories"

# 3.10: Execute MED-3 (Organize scripts)
mkdir -p scripts/utils
git mv scripts/fix_emojis.py scripts/generate_valid_rsa_key.py scripts/utils/
# ... (add README)
git add scripts/README.md
git commit -m "chore(scripts): Organize build and utility scripts"

# 3.11: Execute MED-4 (Consolidate server tests)
mkdir -p server/tests
git mv server/test_server.py server/test_gui.py server/tests/
git mv tests/test_connection.py server/tests/
# ... (add test runner)
git add server/tests/
git commit -m "test(server): Organize server tests"

# 3.12: Validation checkpoint
echo "=== Phase 3 Validation ==="
cd client && .\build.bat && cd ..
cd scripts/build && .\build_rsa_final_test.bat && cd ../..
client\build\test_rsa_final.exe
python -m pytest server/tests/ -v
echo "✓ Phase 3 complete"

# 3.13: Push and merge
git push origin cleanup/phase3-source-reorganization
```

#### Validation Criteria for Phase 3

- [ ] Client builds from `client/` directory: `cd client && .\build.bat`
- [ ] Tests build and pass: `client\build\test_rsa_final.exe`
- [ ] Server tests pass: `pytest server/tests/`
- [ ] Integration tests still work: `python tests/integration/test_system.py`
- [ ] No orphaned `/src/` or `/include/` directories
- [ ] All test build scripts work from `scripts/build/`

---

### Phase 4: Documentation & Configuration

**Duration:** 1-2 hours
**Risk Level:** LOW (mostly documentation, low risk of breakage)
**Rollback:** Easy (git revert)

#### Steps

```bash
# 4.1: Create phase 4 branch
git checkout main
git pull origin main
git checkout -b cleanup/phase4-documentation

# 4.2: Execute MED-5 (Organize documentation)
mkdir -p docs/{architecture,development,deployment,troubleshooting,archive}

# Move and rename docs:
git mv "docs/NEW detailed spesification for the project.md" docs/architecture/specification-detailed.md
git mv docs/specification.md docs/architecture/protocol-specification.md
# ... (move all docs per MED-5)

# Delete build outputs:
git rm docs/build_client_output.txt
git rm docs/CLAUDE.md  # Keep root copy

# 4.3: Create docs index
# ... (copy from MED-5)
git add docs/README.md
git commit -m "docs: Reorganize into architecture/development/deployment hierarchy"

# 4.4: Execute LOW-1 (Add .editorconfig)
# ... (copy from LOW-1)
git add .editorconfig
git commit -m "chore(config): Add EditorConfig"

# 4.5: Execute LOW-2 (Add .gitattributes)
# ... (copy from LOW-2)
git add .gitattributes
git commit -m "chore(config): Add .gitattributes"

# 4.6: Execute LOW-4 (Create config examples)
mkdir -p client/config server/config
# ... (create *.example files)
git add client/config/*.example server/config/*.example
git commit -m "docs: Add configuration file examples"

# 4.7: Execute LOW-5 (Create CONTRIBUTING.md)
# ... (copy from LOW-5)
git add docs/development/contributing.md
git commit -m "docs: Add contributing guidelines"

# 4.8: Create system-overview.md (HIGH priority doc)
# ... (copy from Documentation section)
git add docs/architecture/system-overview.md
git commit -m "docs: Add comprehensive system architecture overview"

# 4.9: Create testing.md
# ... (copy from Documentation section)
git add docs/development/testing.md
git commit -m "docs: Add testing guide"

# 4.10: Validation checkpoint
echo "=== Phase 4 Validation ==="
tree docs/ -L 2
cat README.md | head -20
cat docs/README.md
echo "✓ Phase 4 complete"

# 4.11: Push and merge
git push origin cleanup/phase4-documentation
```

#### Validation Criteria for Phase 4

- [ ] Documentation organized into subdirectories
- [ ] `docs/README.md` provides clear index
- [ ] Root `README.md` exists and is comprehensive
- [ ] `.editorconfig` and `.gitattributes` present
- [ ] Configuration examples exist in `client/config/` and `server/config/`

---

### Phase 5: Final Polish & Validation

**Duration:** 30-60 minutes
**Risk Level:** VERY LOW (optional improvements)
**Rollback:** Easy

#### Steps

```bash
# 5.1: Create phase 5 branch
git checkout main
git pull origin main
git checkout -b cleanup/phase5-final-polish

# 5.2: Execute LOW-3 (Add LICENSE) - if applicable
# ... (select and add appropriate license)
git add LICENSE
git commit -m "docs: Add MIT License"

# 5.3: Create environment setup scripts (from Dependencies section)
# ... (server/setup_env.sh and server/setup_env.bat)
git add server/setup_env.*
git commit -m "feat(server): Add environment setup scripts"

# 5.4: Create smoke test script (from Tests section)
# ... (scripts/smoke_test.sh)
chmod +x scripts/smoke_test.sh
git add scripts/smoke_test.sh
git commit -m "test: Add smoke test script for quick validation"

# 5.5: Add CI/CD workflows (from Tests section)
# ... (create .github/workflows/*.yml)
git add .github/workflows/
git commit -m "ci: Add GitHub Actions workflows for build and test"

# 5.6: Create Dockerfile (from Dependencies section)
# ... (server/Dockerfile)
git add server/Dockerfile
git commit -m "feat(server): Add Dockerfile for containerized deployment"

# 5.7: Final validation - run ALL tests
echo "=== Final Validation ==="
./scripts/smoke_test.sh
cd client && .\build.bat && cd ..
cd scripts/build && .\build_rsa_final_test.bat && .\build_rsa_wrapper_final_test.bat && cd ../..
client\build\test_rsa_final.exe
client\build\test_rsa_wrapper_final.exe
pytest server/tests/ -v
# Start server and run integration tests
cd server && python server.py &
SERVER_PID=$!
sleep 3
cd ../tests/integration
python test_system.py
python test_client.py
kill $SERVER_PID

echo "✓ All tests passed! Cleanup complete!"

# 5.8: Push and merge
git push origin cleanup/phase5-final-polish
```

#### Validation Criteria for Phase 5

- [ ] Smoke test passes: `./scripts/smoke_test.sh`
- [ ] All client tests pass
- [ ] All server tests pass
- [ ] All integration tests pass
- [ ] CI/CD workflows defined
- [ ] Environment setup scripts work
- [ ] LICENSE file added (if applicable)

---

### Post-Implementation: Final Checklist

After all phases are merged to main:

- [ ] **Tag release**: `git tag -a v1.0-cleaned -m "Repository cleanup complete" && git push --tags`
- [ ] **Update CLAUDE.md**: Reflect new directory structure
- [ ] **Archive PROJECT_CLEANUP.md**: Move to `docs/archive/` as reference
- [ ] **Announce**: Notify team of new structure in README
- [ ] **Monitor**: Watch for issues over next 7 days
- [ ] **Cleanup branches**: Delete cleanup/* branches after 30 days

---

### Rollback Procedures

#### If Phase 1-2 Fails (Critical/High Priority)

```bash
# Rollback entire phase:
git checkout main
git branch -D cleanup/phase<N>-*

# Start over:
git checkout -b cleanup/phase<N>-retry
# Re-attempt with fixes
```

#### If Phase 3 Fails (Source Reorganization)

```bash
# This is the riskiest phase. If build breaks:

# Option 1: Fix paths and continue
cd client
# Edit build.bat to fix paths
.\build.bat  # Test
git add client/build.bat
git commit -m "fix: Correct build paths after reorganization"

# Option 2: Rollback entire reorganization
git checkout main
git branch -D cleanup/phase3-source-reorganization
# Investigate issue, plan retry
```

#### If Phase 4-5 Fails (Documentation)

```bash
# Low risk - usually just revert specific commits:
git revert <commit-hash>
git push origin cleanup/phase<N>-*
```

---

### Emergency Rollback (Nuclear Option)

If everything breaks and you need to restore pre-cleanup state:

```bash
# Find the commit BEFORE Phase 1 started:
git log --oneline --all | grep -B 1 "cleanup/phase1"
# Note the commit hash before phase1

# Create recovery branch:
git checkout -b recovery-pre-cleanup <commit-hash>
git push origin recovery-pre-cleanup

# Verify this state works:
.\build.bat
pytest server/tests/

# If working, make this the new main (DANGER - coordinate with team):
git checkout main
git reset --hard <commit-hash>
git push origin main --force

# All developers must re-clone after this!
```

**IMPORTANT:** Only use emergency rollback if absolutely necessary. It rewrites history and requires full team coordination.

---

## Pre-Implementation Checklist

Before starting Phase 1, complete this checklist:

### Preparation

- [ ] **Read entire PROJECT_CLEANUP.md document** (this file)
- [ ] **Understand the risk levels** for each phase (LOW/MEDIUM/HIGH)
- [ ] **Schedule 4-6 hours** of uninterrupted time (or break into multiple sessions by phase)
- [ ] **Notify team members** that cleanup is happening (if collaborative repo)

### Environment Setup

- [ ] **Clean working directory**: `git status` shows no uncommitted changes
- [ ] **Up-to-date main branch**: `git checkout main && git pull origin main`
- [ ] **Backup current state**:
  ```bash
  git branch backup-pre-cleanup-$(date +%Y%m%d)
  git push origin backup-pre-cleanup-$(date +%Y%m%d)
  ```
- [ ] **Verify build works**:
  ```bash
  .\build.bat  # Should complete successfully
  ```
- [ ] **Verify tests work**:
  ```bash
  # Run at least 1-2 primary tests:
  .\build\test_rsa_final.exe  # If exists
  python server/test_server.py  # If exists
  ```

### Tools & Dependencies

- [ ] **Git version**: `git --version` (should be 2.25+)
- [ ] **Python 3.11+**: `python --version`
- [ ] **MSVC available**: `cl.exe` accessible (Windows only)
- [ ] **Tree command**: `tree --version` or `find` (for validation)
- [ ] **Diff tool**: `diff --version` (for file comparisons)
- [ ] **Text editor**: VS Code, Vim, or preferred editor for manual edits

### Testing Baseline

- [ ] **Record current test results**:
  ```bash
  # Create baseline log:
  echo "=== Pre-Cleanup Baseline ===" > cleanup_baseline.log
  date >> cleanup_baseline.log
  echo "Git commit: $(git rev-parse HEAD)" >> cleanup_baseline.log
  echo "Build test:" >> cleanup_baseline.log
  .\build.bat >> cleanup_baseline.log 2>&1
  echo "Test run:" >> cleanup_baseline.log
  .\build\test_rsa_final.exe >> cleanup_baseline.log 2>&1 || echo "Test not available"
  cat cleanup_baseline.log
  ```

### Key File Verification

- [ ] **Identify critical files** that MUST NOT break:
  ```bash
  # List files that are actively used:
  ls -lh build.bat
  ls -lh server/server.py
  ls -lh src/client/client.cpp
  ls -lh include/wrappers/*.h
  ```
- [ ] **Verify third_party/** is intact:
  ```bash
  ls -la third_party/crypto++/ | head -20
  # Should show Crypto++ library files
  ```

### Access & Permissions

- [ ] **Write access to repository**: Can you push to origin?
  ```bash
  git push origin --dry-run
  ```
- [ ] **Branch protection rules**: Are you allowed to create branches and PRs?
- [ ] **No uncommitted secrets**: Check for `me.info`, `transfer.info`, private keys
  ```bash
  git status --ignored
  ls -la | grep -E "me\.info|transfer\.info|\.key$"
  ```

### Communication

- [ ] **Notify team**: "Starting repository cleanup, branches cleanup/* will be created"
- [ ] **Set status**: Mark yourself as busy / in focus mode (if applicable)
- [ ] **Prepare for questions**: Have this document open and ready to reference

### Mental Preparation

- [ ] **Understand**: Each phase has validation checkpoints - use them!
- [ ] **Remember**: Nothing is deleted permanently (moved to legacy/ or git history)
- [ ] **Know when to stop**: If a phase fails validation, STOP and fix before continuing
- [ ] **Have recovery plan**: You can always git revert or rollback to backup branch

### Final Go/No-Go Decision

**Answer these questions:**

1. Do I have a backup branch? **YES / NO**
2. Does the current build work? **YES / NO**
3. Do I have 1+ hours available? **YES / NO**
4. Do I understand the rollback procedures? **YES / NO**
5. Is my git working directory clean? **YES / NO**

**If all answers are YES, you are ready to begin.**

**If any answer is NO, address that issue before starting.**

---

## Success Metrics

After completing all phases, you should observe:

### Quantitative Improvements

- **Root directory files**: Reduced from ~28 to <10 files
- **Documentation organization**: 26 flat files → ~15 files in 5 categories
- **Test organization**: 14 scattered tests → Organized in unit/integration/fixtures
- **Build script clarity**: 3 duplicate scripts → 1 canonical + 2 archived
- **Gitignore coverage**: +40 patterns to prevent future mistakes

### Qualitative Improvements

- **New developer onboarding**: ~15 minute setup with README vs. ~2 hour exploration
- **Build clarity**: Single `cd client && .\build.bat` vs. ambiguous root scripts
- **Test execution**: Clear test commands in READMEs vs. scattered test files
- **Security posture**: All secrets in .gitignore, documented patterns
- **Documentation discoverability**: Hierarchical docs/ vs. flat 26-file directory

### Maintenance Benefits

- **Reduced confusion**: Clear separation of client/server/tests/docs
- **Better CI/CD**: Automated testing with GitHub Actions
- **Easier refactoring**: Organized code structure enables confident changes
- **Professional impression**: Clean repo structure signals quality to collaborators
- **Future-proof**: Blueprint supports scaling (web GUI, mobile client, etc.)

---

**END OF PROJECT_CLEANUP.MD**

---

**Document prepared by:** Claude (Anthropic)
**Date:** 2025-11-13
**Repository:** client-server-encrypted-backup-framework-clean
**Status:** Ready for review and approval

**Next steps:**
1. Review this document with project stakeholders
2. Approve or request modifications
3. Execute Phase 1 when ready
4. Iterate through phases with validation checkpoints
5. Celebrate a clean, professional repository! 🎉

