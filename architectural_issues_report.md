# Architectural Issues Report

This document details the major architectural issues discovered during the code review.

## 1. Monolithic API Server (`cyberbackup_api_server.py`)

The `cyberbackup_api_server.py` file is a monolithic component that acts as a web server, a process manager for the C++ client, and a state manager for the backup jobs. This is a significant architectural concern because it violates the single-responsibility principle and makes the code difficult to maintain and test.

**Recommendations:**

*   **Separate the web server:** The Flask web server should be separated into its own module. Its only responsibility should be to handle HTTP requests and responses.
*   **Create a separate process manager:** The logic for managing the C++ client subprocess should be extracted into a separate module. This module would be responsible for starting, stopping, and monitoring the client process.
*   **Create a separate state manager:** The logic for managing the state of the backup jobs should be extracted into its own module. This module would be responsible for creating, updating, and deleting backup jobs.

## 2. Insecure File-Based Communication with the Client

The API server communicates with the C++ client by writing the backup configuration to a `transfer.info` file. The C++ client then reads this file to get its configuration. This is an insecure way to communicate with the client because the `transfer.info` file is stored in plain text on the file system, and it could be read or modified by an attacker.

**Recommendations:**

*   **Use a more secure communication channel:** The API server should use a more secure communication channel to send the backup configuration to the C++ client. One option would be to use a named pipe or a socket.
*   **Encrypt the configuration:** If file-based communication is still desired, the configuration should be encrypted before it is written to the `transfer.info` file.

## 3. Scattered Configuration

The configuration for the system is scattered across multiple files, including `transfer.info`, `progress_config.json`, and hard-coded values in the source code. This makes it difficult to manage the configuration and to understand how the system is configured.

**Recommendations:**

*   **Centralize the configuration:** All the configuration for the system should be centralized in a single configuration file. This file should be in a standard format, such as JSON or YAML.
*   **Use a configuration library:** A configuration library, such as `configparser` or `pyyaml`, should be used to read the configuration file. This will make it easier to manage the configuration and to avoid errors.

## 4. Unused C++ Web Server Component

The `src/client/WebServerBackend.cpp` file implements a simple HTTP server that was likely used in a previous version of the architecture. In the current system, the Python-based Flask server (`cyberbackup_api_server.py`) provides the web interface. This makes the C++ web server component obsolete.

**Recommendations:**

*   **Remove the C++ web server:** The `WebServerBackend.cpp` file and its corresponding header should be removed from the project to eliminate dead code and reduce confusion.

## 5. Brittle Crypto++ Integration

The `src/client/crypto_support` directory contains a collection of stub files and helper functions that were created to resolve linking errors with the Crypto++ library. This indicates that there were significant challenges in integrating the library. This approach is brittle and likely to break if the Crypto++ library or the compiler is updated.

**Recommendations:**

*   **Properly configure the build system:** The build system should be configured to correctly link against the Crypto++ library. This may involve updating the `CMakeLists.txt` file to correctly specify the include paths and library paths for Crypto++.
*   **Use a dependency manager:** A dependency manager, such as vcpkg or Conan, should be used to manage the Crypto++ dependency. This will make it easier to install and update the library.

## 6. Insecure Cryptographic Practices

The C++ code contains several insecure cryptographic practices:

*   **Static IV in AES:** The `AESWrapper.cpp` uses a static, all-zero initialization vector (IV) for AES-CBC encryption. This is a major security vulnerability because it makes the encryption deterministic, which means that the same plaintext will always produce the same ciphertext. This makes the encryption vulnerable to chosen-plaintext attacks.
*   **Inefficient RSA Key Generation:** The `RSAWrapper.cpp` uses a loop to generate an RSA key of a specific size. This is inefficient and may not always succeed.

**Recommendations:**

*   **Use a random IV for AES:** A random, unpredictable IV should be used for each encryption operation. The IV should be sent to the server along with the ciphertext.
*   **Use a proper key generation method for RSA:** The RSA key generation should be done using a proper method that allows you to specify the desired key size directly.

## 7. Positive Modularization within Python Server Components

While the overall architecture has significant issues, the Python server components within `src/server` (e.g., `client_manager.py`, `database.py`, `file_transfer.py`, `gui_integration.py`, `network_server.py`, `protocol.py`, `request_handlers.py`, `server_singleton.py`, `server.py`) demonstrate good modularization and separation of concerns. Each of these files encapsulates a specific responsibility, making the individual components more maintainable and testable. This is a positive aspect that should be leveraged in future refactoring efforts.

**Recommendations:**

*   **Continue this modular approach:** When refactoring the monolithic `cyberbackup_api_server.py`, ensure that the new components also adhere to this principle of single responsibility and clear separation.
*   **Promote consistency:** Extend this modularization to other parts of the Python codebase that may still be monolithic or have intertwined responsibilities.

## 8. Significant Improvements in Core Utilities

The review of `src/shared/utils` revealed several well-designed modules that directly address previously identified architectural weaknesses:

*   **Unified Configuration Management (`src/shared/config_manager.py`, `src/shared/utils/unified_config.py`):** These modules provide a robust, layered, and extensible system for managing configuration, including migration from legacy formats and environment variable support. This is a major step towards resolving the "Scattered Configuration" issue.
*   **Centralized Error Handling and Propagation (`src/shared/utils/error_handler.py`):** This module implements a comprehensive framework for structured error reporting, classification, and propagation across architectural layers. This directly addresses the need for better error visibility and debugging.
*   **Synchronized File Lifecycle Management (`src/shared/utils/file_lifecycle.py`):** This module provides a thread-safe mechanism to manage temporary files, preventing race conditions during subprocess interactions. This is crucial for the stability of the backup process.
*   **Enhanced Process Monitoring (`src/shared/utils/process_monitor.py`, `src/shared/utils/process_monitor_gui.py`):** These modules offer robust subprocess monitoring, including real-time metrics, health checks, and automated recovery. This improves the observability and resilience of the system.

**Recommendations:**

*   **Integrate and Utilize:** Ensure these new utility modules are fully integrated into all relevant parts of the system, replacing older, less robust implementations.
*   **Documentation:** Document the usage and benefits of these new utility modules for future development.

## 9. State of the Testing Suite

The `tests` directory contains a mix of basic integration tests and debugging scripts. While some tests are valuable for quick checks and debugging, the overall suite lacks comprehensive automated unit and integration tests.

**Observations:**

*   **Manual Verification:** Many tests rely on manual inspection of console output rather than automated assertions.
*   **Limited Scope:** Some tests only verify basic connectivity or file presence, without deep content or integrity checks.
*   **Lack of Framework:** Most tests do not leverage a formal testing framework (like `pytest` or `unittest.TestCase` consistently), which hinders automation, reporting, and test organization.
*   **Redundancy:** Some tests (`test_upload.py`, `test_larger_upload.py`, `test_upload_debug.py`) cover similar ground with varying levels of detail.
*   **Empty/Incomplete Tests:** `tests/test_client.py` is empty, indicating a gap in client-side testing.

**Recommendations:**

*   **Adopt a Formal Testing Framework:** Migrate existing tests to a framework like `pytest` for better organization, fixtures, and reporting.
*   **Increase Test Coverage:** Develop comprehensive unit tests for individual modules and functions, especially for critical components like cryptography, protocol handling, and database interactions.
*   **Robust Integration Tests:** Create more robust integration tests that cover end-to-end workflows with automated assertions for data integrity, error handling, and performance.
*   **Automate Cleanup:** Ensure all tests clean up any created files or resources to maintain a clean test environment.
*   **Continuous Integration:** Integrate the test suite into a CI/CD pipeline to run tests automatically on every code change.

## Files Reviewed for this Report

**C++ Files:**
*   `src/client/main.cpp`
*   `src/client/client.cpp`
*   `src/wrappers/RSAWrapper.cpp`
*   `src/wrappers/AESWrapper.cpp`
*   `src/wrappers/Base64Wrapper.cpp`
*   `src/client/WebServerBackend.cpp`
*   `src/utils/CompressionWrapper.cpp`
*   `src/client/crypto_support/algebra_implementations.cpp`
*   `src/client/crypto_support/cfb_stubs.cpp`
*   `src/client/crypto_support/crypto_helpers.cpp`
*   `src/client/crypto_support/crypto_stubs.cpp`
*   `src/client/crypto_support/cryptopp_helpers_clean.cpp`
*   `src/client/crypto_support/randpool_stub.cpp`

**Python Files:**
*   `cyberbackup_api_server.py`
*   `src/api/real_backup_executor.py`
*   `src/server/file_receipt_monitor.py`
*   `src/server/client_manager.py`
*   `src/server/config.py`
*   `one_click_build_and_run.py`
*   `src/server/ServerGUI.py`
*   `src/server/crypto_compat.py`
*   `src/server/database.py`
*   `src/server/exceptions.py`
*   `src/server/file_transfer.py`
*   `src/server/gui_integration.py`
*   `src/server/network_server.py`
*   `src/server/protocol.py`
*   `src/server/request_handlers.py`
*   `src/server/server_singleton.py`
*   `src/server/server.py`
*   `src/shared/config_manager.py`
*   `src/shared/utils/error_handler.py`
*   `src/shared/utils/file_lifecycle.py`
*   `src/shared/utils/process_monitor_gui.py`
*   `src/shared/utils/process_monitor.py`
*   `src/shared/utils/unified_config.py`
*   `tests/test_api.py`
*   `tests/test_client.py`
*   `tests/test_fixes_validation.py`
*   `tests/test_gui_join.py`
*   `tests/test_gui_query.py`
*   `tests/test_gui_upload.py`
*   `tests/test_larger_upload.py`
*   `tests/test_server_gui.py`
*   `tests/test_singleton.py`
*   `tests/test_upload_debug.py`
*   `tests/test_upload.py`

## Brief Overview of Reviewed Files

### C++ Files:

*   **`src/client/main.cpp`**
    *   **What it does:** The entry point for the C++ client application. It parses command-line arguments, initializes the `Client` object, and manages the main execution loop (batch mode or interactive GUI).
    *   **Is it necessary:** Yes, it's the executable's main function.
    *   **Dependencies:** `client/client.h`, standard C++ libraries (`iostream`, `thread`, `chrono`, `atomic`, `csignal`, `exception`, `string`). Windows-specific headers (`windows.h`, `conio.h`) for console setup.
    *   **Relations:** Directly uses the `Client` class from `client.cpp`.

*   **`src/client/client.cpp`**
    *   **What it does:** Implements the core logic of the C++ backup client, including configuration reading, server connection, RSA key management, AES encryption/decryption, file chunking, transfer, CRC calculation, and console UI updates.
    *   **Is it necessary:** Yes, it contains the primary client functionality.
    *   **Dependencies:** `client/client.h`, `wrappers/RSAWrapper.h`, `wrappers/AESWrapper.h`, `wrappers/Base64Wrapper.h`, `boost::asio`, standard C++ libraries (`fstream`, `vector`, `string`, `chrono`, `iomanip`).
    *   **Relations:** Interacts with `main.cpp` (called by), `RSAWrapper.cpp`, `AESWrapper.cpp`, `Base64Wrapper.cpp`. Reads `transfer.info` and `me.info`. Communicates with the Python server via a custom binary protocol.

*   **`src/wrappers/RSAWrapper.cpp`**
    *   **What it does:** Provides a C++ wrapper for RSA encryption/decryption and key generation using the Crypto++ library. Handles key loading from DER format and ensures public key size compliance.
    *   **Is it necessary:** Yes, for RSA cryptographic operations.
    *   **Dependencies:** Crypto++ library (`rsa.h`, `osrng.h`, `oaep.h`, `sha.h`, `files.h`), standard C++ libraries.
    *   **Relations:** Used by `client.cpp` for key exchange and AES key encryption/decryption.

*   **`src/wrappers/AESWrapper.cpp`**
    *   **What it does:** Provides a C++ wrapper for AES encryption/decryption using the Crypto++ library. Supports CBC mode with PKCS7 padding and uses a static zero IV (a security concern).
    *   **Is it necessary:** Yes, for AES cryptographic operations.
    *   **Dependencies:** Crypto++ library (`aes.h`, `modes.h`, `filters.h`, `osrng.h`), standard C++ libraries.
    *   **Relations:** Used by `client.cpp` for file encryption.

*   **`src/wrappers/Base64Wrapper.cpp`**
    *   **What it does:** Provides a C++ wrapper for Base64 encoding and decoding using the Crypto++ library. Removes newlines from encoded output.
    *   **Is it necessary:** Yes, for Base64 encoding/decoding, particularly for key storage.
    *   **Dependencies:** Crypto++ library (`base64.h`), standard C++ libraries.
    *   **Relations:** Used by `client.cpp` for saving/loading private keys in `me.info`.

*   **`src/client/WebServerBackend.cpp`**
    *   **What it does:** Implements a simple HTTP API server using Boost.Beast, providing REST endpoints for a web GUI. It manages application state and handles requests like status, connect, and backup initiation.
    *   **Is it necessary:** No, it's an **obsolete/unused** component in the current architecture, as the Python Flask server (`cyberbackup_api_server.py`) has taken over its role.
    *   **Dependencies:** Boost.Asio, Boost.Beast, standard C++ libraries.
    *   **Relations:** Historically intended to serve the web UI; now superseded by `cyberbackup_api_server.py`.

*   **`src/utils/CompressionWrapper.cpp`**
    *   **What it does:** Provides a C++ wrapper for zlib compression and decompression, including metric tracking.
    *   **Is it necessary:** No, it's **currently unused** in the project but could be integrated for file compression.
    *   **Dependencies:** zlib library, standard C++ libraries.
    *   **Relations:** None currently, but could be integrated into the file transfer process in `client.cpp`.

*   **`src/client/crypto_support/algebra_implementations.cpp`**
    *   **What it does:** Provides specific template implementations for abstract algebra classes within Crypto++ to resolve linker errors. Includes a precomputed prime table.
    *   **Is it necessary:** Yes, for successful compilation of the Crypto++-dependent code.
    *   **Dependencies:** Crypto++ internal headers (`integer.h`, `algebra.h`, `nbtheory.h`, `rsa.h`, `sha.h`).
    *   **Relations:** Directly supports the Crypto++ integration, particularly for RSA operations.

*   **`src/client/crypto_support/cfb_stubs.cpp`**
    *   **What it does:** Provides minimal stub implementations for CFB (Cipher Feedback) mode template methods in Crypto++ to resolve linker errors.
    *   **Is it necessary:** Yes, for successful compilation.
    *   **Dependencies:** Crypto++ internal headers (`cryptlib.h`, `modes.h`).
    *   **Relations:** Directly supports the Crypto++ integration.

*   **`src/client/crypto_support/crypto_helpers.cpp`**
    *   **What it does:** Provides helper functions like `IntToString` and a stub for `AssignIntToInteger` for Crypto++ compatibility, resolving linker errors.
    *   **Is it necessary:** Yes, for successful compilation.
    *   **Dependencies:** Standard C++ libraries (`string`, `sstream`, `typeinfo`).
    *   **Relations:** Directly supports the Crypto++ integration.

*   **`src/client/crypto_support/crypto_stubs.cpp`**
    *   **What it does:** Provides stub implementations for low-level, optimized cryptographic functions (AES, SHA) in Crypto++ to resolve linker errors.
    *   **Is it necessary:** Yes, for successful compilation.
    *   **Dependencies:** Standard C++ libraries (`cstdint`).
    *   **Relations:** Directly supports the Crypto++ integration.

*   **`src/client/crypto_support/cryptopp_helpers_clean.cpp`**
    *   **What it does:** A cleaned-up version of `crypto_helpers.cpp`, providing similar helper function implementations for Crypto++ compatibility.
    *   **Is it necessary:** Yes, for successful compilation.
    *   **Dependencies:** Standard C++ libraries.
    *   **Relations:** Directly supports the Crypto++ integration.

*   **`src/client/crypto_support/randpool_stub.cpp`**
    *   **What it does:** A stub file for `RandomPool` in Crypto++, primarily including `osrng.h` which provides `AutoSeededRandomPool`.
    *   **Is it necessary:** Yes, for successful compilation.
    *   **Dependencies:** Crypto++ `osrng.h`, Windows CryptoAPI headers (`windows.h`, `wincrypt.h`).
    *   **Relations:** Directly supports the Crypto++ integration for random number generation.

### Python Files:

*   **`cyberbackup_api_server.py`**
    *   **What it does:** The Flask web server that acts as the bridge between the web UI and the C++ client. It handles HTTP requests, manages the C++ client subprocess, and coordinates backup jobs.
    *   **Is it necessary:** Yes, it's the critical integration layer for the web UI.
    *   **Dependencies:** `flask`, `flask_cors`, `subprocess`, `threading`, `json`, `os`, `time`, `logging`, `src.api.real_backup_executor`.
    *   **Relations:** Orchestrates the C++ client via `real_backup_executor.py`. Communicates with the web UI.

*   **`src/api/real_backup_executor.py`**
    *   **What it does:** Manages the execution of the C++ client as a subprocess. It handles subprocess communication, progress monitoring, and file verification.
    *   **Is it necessary:** Yes, it's the core component for running the C++ client from Python.
    *   **Dependencies:** `subprocess`, `threading`, `time`, `os`, `json`, `logging`, `src.shared.utils.file_lifecycle`, `src.shared.utils.process_monitor`, `src.server.file_receipt_monitor`.
    *   **Relations:** Called by `cyberbackup_api_server.py`. Executes `EncryptedBackupClient.exe`. Uses `file_lifecycle.py` for temporary file management, `process_monitor.py` for subprocess health, and `file_receipt_monitor.py` for verification.

*   **`src/server/file_receipt_monitor.py`**
    *   **What it does:** Monitors the `received_files` directory for new files and performs multi-factor verification (size, stability, hash) to confirm successful transfers.
    *   **Is it necessary:** Yes, provides ground-truth verification of file transfers.
    *   **Dependencies:** `threading`, `time`, `os`, `logging`, `hashlib`, `src.server.database`.
    *   **Relations:** Used by `real_backup_executor.py` to verify transferred files. Updates the database via `src.server.database`.

*   **`src/server/client_manager.py`**
    *   **What it does:** Manages the in-memory state and lifecycle of connected clients on the server. Handles client registration, public/AES key management, session timeouts, and partial file reassembly data.
    *   **Is it necessary:** Yes, centralizes client state management for the Python server.
    *   **Dependencies:** `threading`, `time`, `logging`, `src.server.crypto_compat`, `src.server.exceptions`, `src.server.config`, `src.server.database`.
    *   **Relations:** Used by `src.server.server.py` and `src.server.request_handlers.py` to access and manage client data. Persists client data via `src.server.database`.

*   **`src/server/config.py`**
    *   **What it does:** Defines server-wide configuration constants, including port numbers, timeouts, file paths, and protocol version compatibility settings. Also sets up basic logging.
    *   **Is it necessary:** Yes, provides centralized configuration for the Python server.
    *   **Dependencies:** `logging`, `sys`.
    *   **Relations:** Imported by many server-side modules (`client_manager.py`, `file_transfer.py`, `network_server.py`, `protocol.py`, `request_handlers.py`, `server.py`).

*   **`one_click_build_and_run.py`**
    *   **What it does:** An orchestration script that automates the entire build and run process for the CyberBackup system, including C++ client compilation, Python dependency installation, service launching, and web UI opening.
    *   **Is it necessary:** Yes, it's the primary convenience script for setting up and starting the system.
    *   **Dependencies:** `os`, `sys`, `subprocess`, `time`, `psutil`, `pathlib`, `requests`, `webbrowser`.
    *   **Relations:** Executes `cmake`, `pip`, `python -m src.server.server`, `cyberbackup_api_server.py`.

*   **`src/server/ServerGUI.py`**
    *   **What it does:** Implements the graphical user interface (GUI) for the Python backup server using Tkinter. It displays server status, client statistics, file transfers, and performance metrics.
    *   **Is it necessary:** Yes, provides a visual dashboard for server monitoring.
    *   **Dependencies:** `tkinter`, `threading`, `queue`, `datetime`, `logging`, `os`, `sys`, `json`, `csv`, `sqlite3`, `collections`, `math`, `shutil`, `zlib`, `socket`, `pystray`, `PIL` (Pillow), `matplotlib`, `psutil`, `sentry_sdk`, `src.server.server`, `src.server.server_singleton`, `src.shared.utils.process_monitor_gui`.
    *   **Relations:** Interacts with the `BackupServer` instance (passed in `__init__`) to fetch data and update status.

*   **`src/server/crypto_compat.py`**
    *   **What it does:** A compatibility layer that provides a unified API for cryptographic operations (AES, RSA, padding, random bytes, SHA256) using either `pycryptodome` or `cryptography` library.
    *   **Is it necessary:** Yes, ensures flexibility and robustness in cryptographic backend.
    *   **Dependencies:** `Crypto` (from `pycryptodome`) or `cryptography` library, `os`, `sys`, `hashlib`.
    *   **Relations:** Imported by `client_manager.py`, `file_transfer.py`, `request_handlers.py`, `server.py` to perform crypto operations.

*   **`src/server/database.py`**
    *   **What it does:** Manages all SQLite database operations for the server, including schema initialization, client registration, file record management, and startup permission checks.
    *   **Is it necessary:** Yes, provides persistence for client and file data.
    *   **Dependencies:** `sqlite3`, `logging`, `os`, `datetime`, `uuid`, `src.server.config`, `src.server.exceptions`.
    *   **Relations:** Used by `client_manager.py`, `file_transfer.py`, `request_handlers.py`, `server.py` to interact with the database.

*   **`src/server/exceptions.py`**
    *   **What it does:** Defines custom exception classes (`ServerError`, `ProtocolError`, `ClientError`, `FileError`) for structured error handling within the server.
    *   **Is it necessary:** Yes, improves error categorization and debugging.
    *   **Dependencies:** None (standard Python `Exception`).
    *   **Relations:** Imported and raised by various server modules (`client_manager.py`, `file_transfer.py`, `network_server.py`, `request_handlers.py`, `server.py`).

*   **`src/server/file_transfer.py`**
    *   **What it does:** Manages the complex multi-packet file transfer process on the server side, including reassembly, AES decryption, CRC32 validation, and atomic file storage.
    *   **Is it necessary:** Yes, it's the core logic for receiving and processing client file uploads.
    *   **Dependencies:** `socket`, `struct`, `uuid`, `os`, `time`, `threading`, `logging`, `re`, `datetime`, `src.server.crypto_compat`, `src.server.exceptions`, `src.server.config`, `src.server.protocol`.
    *   **Relations:** Delegated to by `request_handlers.py`. Updates database via `src.server.database`.

*   **`src/server/gui_integration.py`**
    *   **What it does:** Manages the integration between the main server logic and the `ServerGUI`. It initializes the GUI in a separate thread, and provides methods for safely updating GUI elements from the server's main thread.
    *   **Is it necessary:** Yes, enables the server to have a graphical interface.
    *   **Dependencies:** `threading`, `logging`, `src.server.ServerGUI`.
    *   **Relations:** Used by `src.server.server.py` to manage the GUI.

*   **`src/server/network_server.py`**
    *   **What it does:** Handles the low-level network communication for the server, including socket creation, listening for connections, accepting clients, and managing client connection threads. It also handles protocol header parsing and response sending.
    *   **Is it necessary:** Yes, it's the foundation for all network communication.
    *   **Dependencies:** `socket`, `threading`, `signal`, `struct`, `logging`, `time`, `src.server.config`, `src.server.exceptions`, `src.server.protocol`.
    *   **Relations:** Instantiated and started by `src.server.server.py`. Calls `request_handler.process_request` for each incoming client request.

*   **`src/server/protocol.py`**
    *   **What it does:** Defines the binary protocol constants (request/response codes) and utility functions for parsing headers, constructing responses, and validating protocol versions.
    *   **Is it necessary:** Yes, defines the communication contract between client and server.
    *   **Dependencies:** `struct`, `logging`, `src.server.config`.
    *   **Relations:** Imported by `network_server.py`, `request_handlers.py`, `file_transfer.py` to ensure protocol compliance.

*   **`src/server/request_handlers.py`**
    *   **What it does:** Dispatches incoming client requests to appropriate handler methods (e.g., registration, public key, file transfer). It acts as a central router for client commands.
    *   **Is it necessary:** Yes, centralizes the business logic for handling client requests.
    *   **Dependencies:** `socket`, `struct`, `uuid`, `os`, `logging`, `re`, `datetime`, `src.server.crypto_compat`, `src.server.exceptions`, `src.server.config`, `src.server.file_transfer`.
    *   **Relations:** Called by `network_server.py`. Delegates file transfer to `file_transfer.py`. Interacts with `client_manager.py` and `database.py` via the `server` instance.

*   **`src/server/server_singleton.py`**
    *   **What it does:** Implements a singleton pattern to ensure only one instance of the Python server runs at a time. It uses PID files and port checks to detect and terminate existing instances.
    *   **Is it necessary:** Yes, prevents multiple server instances from conflicting.
    *   **Dependencies:** `os`, `sys`, `time`, `signal`, `socket`, `atexit`, `logging`, `pathlib`, `psutil` (optional).
    *   **Relations:** Used by `one_click_build_and_run.py` and `src.server.server.py` at startup.

*   **`src/server/server.py`**
    *   **What it does:** The main Python backup server application. It initializes and orchestrates all other server components (network, database, client manager, GUI, request handlers).
    *   **Is it necessary:** Yes, it's the central orchestrator for the Python server.
    *   **Dependencies:** All other `src/server` modules (`client_manager`, `config`, `crypto_compat`, `database`, `exceptions`, `file_transfer`, `gui_integration`, `network_server`, `protocol`, `request_handlers`, `server_singleton`), standard Python libraries.
    *   **Relations:** The top-level component that brings all server-side modules together.

*   **`src/shared/config_manager.py`**
    *   **What it does:** A base class for configuration management. It loads configuration from JSON files (default, environment-specific, local), supports deep merging, and provides methods for getting/setting values with dot notation.
    *   **Is it necessary:** Yes, provides a foundational, modular approach to configuration.
    *   **Dependencies:** `json`, `os`, `sys`, `pathlib`, `logging`.
    *   **Relations:** Extended by `src/shared/utils/unified_config.py`.

*   **`src/shared/utils/error_handler.py`**
    *   **What it does:** Implements a centralized error propagation framework. It defines structured error types (code, category, severity), allows errors to be created and propagated across architectural layers, and supports callbacks for real-time reporting.
    *   **Is it necessary:** Yes, crucial for robust error management and debugging in a multi-layered system.
    *   **Dependencies:** `logging`, `traceback`, `time`, `threading`, `enum`, `dataclasses`, `datetime`.
    *   **Relations:** Used by `src/api/real_backup_executor.py`, `src/shared/utils/process_monitor.py`, and other modules to report and propagate errors.

*   **`src/shared/utils/file_lifecycle.py`**
    *   **What it does:** Provides a `SynchronizedFileManager` for thread-safe management of temporary files, especially for subprocess interactions. It prevents premature deletion of files in use by using reference counting and cleanup events.
    *   **Is it necessary:** Yes, addresses critical race conditions and improves system stability.
    *   **Dependencies:** `os`, `time`, `threading`, `tempfile`, `logging`, `pathlib`, `shutil`.
    *   **Relations:** Used by `src/api/real_backup_executor.py` to manage temporary files used by the C++ client.

*   **`src/shared/utils/process_monitor_gui.py`**
    *   **What it does:** Provides Tkinter-based GUI widgets (`ProcessMonitorWidget`, `ProcessMetricsChart`) for visualizing process monitoring data.
    *   **Is it necessary:** Yes, provides the visual interface for process monitoring.
    *   **Dependencies:** `tkinter`, `threading`, `time`, `datetime`, `logging`, `src.shared.utils.process_monitor`.
    *   **Relations:** Integrates with `src/shared/utils/process_monitor.py` to fetch data. Used by `src/server/ServerGUI.py`.

*   **`src/shared/utils/process_monitor.py`**
    *   **What it does:** Implements a comprehensive subprocess monitoring system. It maintains a central registry of processes, collects real-time metrics (using `psutil`), detects health issues, and supports automated restarts.
    *   **Is it necessary:** Yes, crucial for managing and ensuring the health of subprocesses (like the C++ client).
    *   **Dependencies:** `os`, `time`, `threading`, `subprocess`, `psutil`, `datetime`, `collections`, `logging`, `src.shared.utils.error_handler`.
    *   **Relations:** Used by `src/api/real_backup_executor.py` to monitor the C++ client. Reports errors via `src.shared.utils.error_handler.py`.

*   **`src/shared/utils/unified_config.py`**
    *   **What it does:** Extends `config_manager.py` to create a unified configuration system. It loads and merges configurations from JSON files, legacy `.info` files, and environment variables, with defined precedence. It also includes tools for migrating legacy configurations.
    *   **Is it necessary:** Yes, provides a centralized and robust solution for configuration management, addressing a major architectural issue.
    *   **Dependencies:** `os`, `json`, `logging`, ``threading`, `pathlib`, `datetime`, `configparser`, `re`, `src.shared.config_manager`.
    *   **Relations:** Intended to be the single source of truth for all configuration across the system.

*   **`tests/test_api.py`**
    *   **What it does:** Provides basic integration tests for the Flask API server's endpoints (`/api/status`, `/api/connect`, `/api/start_backup`) using HTTP requests.
    *   **Is it necessary:** Yes, for quick verification of API responsiveness.
    *   **Dependencies:** `requests`, `json`, `os`.
    *   **Relations:** Tests `cyberbackup_api_server.py`.

*   **`tests/test_client.py`**
    *   **What it does:** This file is **empty**.
    *   **Is it necessary:** No, it's an empty placeholder.
    *   **Dependencies:** None.
    *   **Relations:** Represents a missing test suite for the C++ client's Python interactions.

*   **`tests/test_fixes_validation.py`**
    *   **What it does:** A comprehensive test suite validating critical fixes, including `SynchronizedFileManager` race conditions, protocol version flexibility, and error propagation framework functionality.
    *   **Is it necessary:** Yes, crucial for verifying the effectiveness of architectural fixes.
    *   **Dependencies:** `unittest`, `os`, `sys`, `threading`, `time`, `tempfile`, `subprocess`, `json`, `pathlib`, `unittest.mock`, `src.shared.utils.file_lifecycle`, `src.shared.utils.error_handler`, `src.shared.utils.unified_config`, `src.server.protocol`, `src.server.config`.
    *   **Relations:** Tests multiple core components and their interactions.

*   **`tests/test_gui_join.py`**
    *   **What it does:** A simple script to test a specific SQL JOIN query used by the server GUI to retrieve file and client information from the SQLite database.
    *   **Is it necessary:** Yes, for verifying a specific database query.
    *   **Dependencies:** `sqlite3`.
    *   **Relations:** Tests database interaction for the GUI.

*   **`tests/test_gui_query.py`**
    *   **What it does:** A more comprehensive script for testing various SQL queries used by the server GUI, including table existence, data retrieval, and JOIN queries.
    *   **Is it necessary:** Yes, for verifying database queries.
    *   **Dependencies:** `sqlite3`, `sys`, `os`.
    *   **Relations:** Tests database interaction for the GUI.

*   **`tests/test_gui_upload.py`**
    *   **What it does:** An integration test that simulates a file upload through the Flask API server (as initiated by the GUI) and verifies that the file is received and its content is intact.
    *   **Is it necessary:** Yes, for end-to-end testing of the GUI-driven upload flow.
    *   **Dependencies:** `requests`, `os`, `time`.
    *   **Relations:** Tests `cyberbackup_api_server.py` and the overall file transfer pipeline.

*   **`tests/test_larger_upload.py`**
    *   **What it does:** A basic test for uploading a larger file via the Flask API server.
    *   **Is it necessary:** Yes, for testing scalability with larger files.
    *   **Dependencies:** `requests`, `os`.
    *   **Relations:** Tests `cyberbackup_api_server.py` and the file transfer pipeline.

*   **`tests/test_server_gui.py`**
    *   **What it does:** A script to directly launch the `ServerGUI` and verify its ability to connect to the database and display file information.
    *   **Is it necessary:** Yes, for verifying GUI launch and basic data display.
    *   **Dependencies:** `sys`, `os`, `src.server.ServerGUI`, `sqlite3`.
    *   **Relations:** Tests `src.server.ServerGUI.py` and its database integration.

*   **`tests/test_singleton.py`**
    *   **What it does:** A test suite for the server's singleton functionality, ensuring only one instance runs, and performs a basic content analysis of received files.
    *   **Is it necessary:** Yes, for verifying the server's single-instance behavior and basic file integrity.
    *   **Dependencies:** `sys`, `os`, `time`, `subprocess`, `pathlib`, `src.server.server_singleton`.
    *   **Relations:** Tests `src.server.server_singleton.py`.

*   **`tests/test_upload_debug.py`**
    *   **What it does:** A debugging utility that performs a step-by-step execution of the API upload process, including status and connection checks, to help diagnose upload issues.
    *   **Is it necessary:** Yes, as a diagnostic tool for developers.
    *   **Dependencies:** `requests`, `tempfile`, `os`, `time`.
    *   **Relations:** Debugs `cyberbackup_api_server.py` and the upload pipeline.

*   **`tests/test_upload.py`**
    *   **What it does:** A basic end-to-end test for file upload functionality, verifying that a file uploaded via the API appears in the `received_files` directory.
    *   **Is it necessary:** Yes, as a quick smoke test for the upload pipeline.
    *   **Dependencies:** `requests`, `os`, `time`.
    *   **Relations:** Tests `cyberbackup_api_server.py` and the file transfer pipeline.
