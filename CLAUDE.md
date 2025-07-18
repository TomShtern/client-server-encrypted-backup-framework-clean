# CodeViz Research Context

> **Note**: This file contains research context from CodeViz. Most recent contexts are at the bottom.

---

## Research Query

i want an exact map and visualization of this project, how it works, how data flows in it, what is connected to what and more improtant data to know and understand how this project is.

*Session: d794aadde0a4ddb80c15c20e07752b4c | Generated: 7/18/2025, 6:51:21 PM*

### Analysis Summary

# Project Map and Visualization

This report provides a comprehensive map and visualization of the Client Server Encrypted Backup Framework, detailing its architecture, data flow, and key components.

## High-Level Architecture

The project is structured around a **Client-Server model** designed for secure file transfer and backup. The core components are the **Server**, responsible for managing clients, handling file transfers, and storing data, and the **Client**, which initiates connections, encrypts/decrypts files, and performs backup operations. A **Graphical User Interface (GUI)** facilitates user interaction on both the client and server sides. Utility scripts and configuration files support the main functionalities.

-   **Server**: Manages connections, handles file transfers, and stores data. Implemented primarily in Python.
-   **Client**: Initiates connections, encrypts/decrypts data, and performs backup/restore operations. Implemented in C++ with a web-based GUI.
-   **GUI**: Provides user interfaces for both client and server operations.
-   **Shared Components/Utilities**: Cryptographic wrappers, configuration management, and various helper scripts.

### Core Communication Flow

The **Client** [src/client/client.cpp](src/client/client.cpp) establishes a connection with the **Server** [server/server.py](server/server.py). Data, primarily files, is encrypted on the client side using **AES** and **RSA** [include/wrappers/AESWrapper.h](include/wrappers/AESWrapper.h), [include/wrappers/RSAWrapper.h](include/wrappers/RSAWrapper.h) before being sent over the network. The server receives, decrypts (if necessary), and stores the data.

## Mid-Level Component Breakdown

### **Server Component**

The **Server** [server/server.py](server/server.py) is the central hub, managing client connections, file transfers, and data storage. It leverages several sub-components for specific tasks.

-   **Main Server Logic**: The entry point for the server application.
    -   [server/server.py](server/server.py): Orchestrates the server's operation, including starting the network listener and integrating with the GUI.
    -   [cyberbackup_api_server.py](cyberbackup_api_server.py): Likely handles API endpoints for external interactions, possibly for the server-side GUI.
-   **Network Communication**: Handles incoming client connections and data transmission.
    -   **Network Server** [server/network_server.py](server/network_server.py): Manages socket connections and listens for incoming data.
    -   **Protocol Handler** [server/protocol.py](server/protocol.py): Defines the communication protocol between client and server, including message formats and command handling.
-   **Client Management**: Keeps track of connected clients and their states.
    -   **Client Manager** [server/client_manager.py](server/client_manager.py): Manages active client sessions, authentication, and client-specific data.
-   **File Transfer & Storage**: Manages the actual file data.
    -   **File Transfer** [server/file_transfer.py](server/file_transfer.py): Handles the reception and storage of files from clients. Received files are typically stored in [server/received_files/](server/received_files/).
    -   **Server Backup** [server/server_backup.py](server/server_backup.py): Potentially handles server-side backup operations or data integrity checks.
-   **Cryptography & Compatibility**: Ensures secure communication and data handling.
    -   **Crypto Compatibility** [server/crypto_compat.py](server/crypto_compat.py): Provides cryptographic functions compatible with the client's encryption methods.
-   **Configuration & Database**: Manages server settings and persistent data.
    -   **Config** [server/config.py](server/config.py): Loads and manages server configuration settings.
    -   **Database** [server/database.py](server/database.py): Manages persistent storage for client information, file metadata, or other server-side data.
-   **GUI Integration**: Connects the server backend to its graphical interface.
    -   **GUI Integration** [server/gui_integration.py](server/gui_integration.py): Provides an interface for the server to communicate with and update the server GUI.
    -   **ServerGUI** [server/ServerGUI.py](server/ServerGUI.py): The Python-based GUI for the server, likely displaying status, logs, and client activity.
-   **Request Handlers**: Processes specific client requests.
    -   **Request Handlers** [server/request_handlers.py](server/request_handlers.py): Contains functions to process different types of requests received from clients (e.g., upload, download, authentication).
-   **Exceptions**: Defines custom exceptions for server-side error handling.
    -   **Exceptions** [server/exceptions.py](server/exceptions.py): Custom exception classes for robust error management.

### **Client Component**

The **Client** [src/client/client.cpp](src/client/client.cpp) is responsible for initiating connections, preparing files for transfer, and interacting with the user via a web-based GUI.

-   **Main Client Logic**:
    -   [src/client/main.cpp](src/client/main.cpp): The entry point for the C++ client application.
    -   [src/client/client.cpp](src/client/client.cpp): Implements the core client functionalities, including connection management, file operations, and interaction with cryptographic wrappers.
-   **Web Server Backend**: Serves the client-side GUI.
    -   **WebServerBackend** [include/client/WebServerBackend.h](include/client/WebServerBackend.h) and [src/client/WebServerBackend.cpp](src/client/WebServerBackend.cpp): Implements a local web server to serve the client's HTML/JavaScript GUI.
-   **Client GUI**: The user interface for the client.
    -   **NewGUIforClient.html** [src/client/NewGUIforClient.html](src/client/NewGUIforClient.html): The HTML file defining the client's web-based graphical user interface.
-   **Cryptography**: Handles encryption and decryption of data.
    -   **Crypto Compliance** [include/client/crypto_compliance.h](include/client/crypto_compliance.h): Ensures cryptographic operations adhere to specified standards.
    -   **AESWrapper** [include/wrappers/AESWrapper.h](include/wrappers/AESWrapper.h): Provides Advanced Encryption Standard (AES) functionalities.
    -   **RSAWrapper** [include/wrappers/RSAWrapper.h](include/wrappers/RSAWrapper.h): Provides RSA encryption/decryption and key management.
    -   **RSAWrapperCNG** [include/wrappers/RSAWrapperCNG.h](include/wrappers/RSAWrapperCNG.h): Likely an alternative RSA implementation using Windows Cryptography Next Generation (CNG).
    -   **Base64Wrapper** [include/wrappers/Base64Wrapper.h](include/wrappers/Base64Wrapper.h): Handles Base64 encoding/decoding, often used for binary data transmission.
-   **Error Handling**: Manages client-side errors.
    -   **Error Handling** [include/client/error_handling.h](include/client/error_handling.h): Defines mechanisms for error reporting and handling within the client.
-   **Compression**:
    -   **CompressionWrapper** [include/utils/CompressionWrapper.h](include/utils/CompressionWrapper.h): Provides data compression functionalities, potentially used before encryption and transfer.

### **GUI Components**

The project uses separate GUIs for the client and server, with a focus on web-based interfaces for the client.

-   **Client GUI**:
    -   **NewGUIforClient.html** [src/client/NewGUIforClient.html](src/client/NewGUIforClient.html): The primary HTML file for the client's web interface.
    -   **WebServerBackend** [src/client/WebServerBackend.cpp](src/client/WebServerBackend.cpp): The C++ component that serves this HTML and handles interactions with the client's core logic.
-   **Server GUI**:
    -   **ServerGUI.py** [server/ServerGUI.py](server/ServerGUI.py): The Python script for the server's graphical interface.
    -   **gui_phase.json** [gui_phase.json](gui_phase.json) and **gui_progress.json** [gui_progress.json](gui_progress.json): These JSON files likely store state or progress information for the GUI, enabling persistence or inter-process communication.
    -   **launch_gui.py** [launch_gui.py](launch_gui.py) and **launch_gui.bat** [launch_gui.bat](launch_gui.bat): Scripts to launch the server GUI.

### **Configuration and Utilities**

These components support the main client and server operations.

-   **Configuration Management**:
    -   **config_manager.py** [config_manager.py](config_manager.py): A Python script for managing application configurations.
    -   **config/** [config/](config/): Directory containing various configuration files (e.g., [config/default.json](config/default.json), [config/development.json](config/development.json), [config/production.json](config/production.json)) for different environments.
-   **Key Generation**:
    -   **generate_rsa_keys.py** [generate_rsa_keys.py](generate_rsa_keys.py): Python script to generate RSA key pairs for cryptographic operations.
    -   **scripts/generate_rsa_keys.py** [scripts/generate_rsa_keys.py](scripts/generate_rsa_keys.py) and **scripts/generate_valid_rsa_key.py** [scripts/generate_valid_rsa_key.py](scripts/generate_valid_rsa_key.py): Additional scripts for RSA key generation, possibly with specific validation or formatting.
    -   **scripts/create_working_keys.py** [scripts/create_working_keys.py](scripts/create_working_keys.py): Script to set up functional cryptographic keys.
-   **Build System**:
    -   **CMakeLists.txt** [CMakeLists.txt](CMakeLists.txt): The main CMake build script for the C++ client.
    -   **CMakeListsTest.txt** [CMakeListsTest.txt](CMakeListsTest.txt): CMake script specifically for building tests.
    -   **CMakePresets.json** [CMakePresets.json](CMakePresets.json): Defines common configure, build, and test presets for CMake.
    -   **vcpkg.json** [vcpkg.json](vcpkg.json): Configuration file for Vcpkg, a C++ package manager, used to manage external dependencies for the C++ client.
    -   **build/** [build/](build/): Directory for build artifacts.
-   **Scripts**: A collection of utility scripts for various tasks.
    -   **scripts/** [scripts/](scripts/): Contains a wide range of scripts for tasks like CMake configuration [scripts/configure_cmake.bat](scripts/configure_cmake.bat), error analysis [scripts/deep_error_analysis.py](scripts/deep_error_analysis.py), deployment [scripts/deploy_production.bat](scripts/deploy_production.bat), and testing [scripts/master_test_suite.py](scripts/master_test_suite.py).
-   **Documentation**:
    -   **docs/** [docs/](docs/): Contains various documentation files, including specifications, plans, and guides. Notable files include [docs/NEW detailed spesification for the project.md](docs/NEW detailed spesification for the project.md), [docs/SYSTEM_COMPLETION_PLAN.md](docs/SYSTEM_COMPLETION_PLAN.md), and [docs/AES_CRYPTO_INTEGRATION_GUIDE.md](docs/AES_CRYPTO_INTEGRATION_GUIDE.md).
    -   **README.md** [README.md](README.md): General project overview.
    -   **ARCHITECTURE.md** [ARCHITECTURE.md](ARCHITECTURE.md): High-level architectural description.
    -   **Final & Complete Project Specification Secure File Transfer System.md** [Final & Complete Project Specification Secure File Transfer System.md](Final & Complete Project Specification Secure File Transfer System.md): Detailed project specification.

## Data Flow

### Client to Server (Backup/Upload)

1.  **File Selection**: User selects files via the **Client GUI** [src/client/NewGUIforClient.html](src/client/NewGUIforClient.html).
2.  **File Reading**: The **Client** [src/client/client.cpp](src/client/client.cpp) reads the selected file content.
3.  **Compression (Optional)**: File data might be compressed using **CompressionWrapper** [include/utils/CompressionWrapper.h](include/utils/CompressionWrapper.h).
4.  **Encryption**:
    -   **Symmetric Encryption (AES)**: The file content is encrypted using **AESWrapper** [include/wrappers/AESWrapper.h](include/wrappers/AESWrapper.h) with a randomly generated session key.
    -   **Asymmetric Encryption (RSA)**: The AES session key is then encrypted using the server's public RSA key via **RSAWrapper** [include/wrappers/RSAWrapper.h](include/wrappers/RSAWrapper.h).
5.  **Encoding**: The encrypted file data and encrypted session key are typically Base64 encoded using **Base64Wrapper** [include/wrappers/Base64Wrapper.h](include/wrappers/Base64Wrapper.h) for safe transmission over text-based protocols.
6.  **Network Transmission**: The encrypted and encoded data, along with metadata (filename, size, etc.), is sent to the **Server** [server/network_server.py](server/network_server.py) following the defined **Protocol** [server/protocol.py](server/protocol.py).

### Server to Client (Restore/Download)

1.  **Request Reception**: The **Server** [server/network_server.py](server/network_server.py) receives a download request from the client.
2.  **File Retrieval**: The **Server** [server/file_transfer.py](server/file_transfer.py) retrieves the requested file from its storage ([server/received_files/](server/received_files/)).
3.  **Encryption (if stored encrypted)**: If files are stored encrypted on the server, they are retrieved in their encrypted form. The server would also retrieve the corresponding encrypted session key.
4.  **Decryption (on Server, if applicable)**: If the server needs to decrypt the file before sending (e.g., for integrity checks or specific server-side processing), it would use its private RSA key to decrypt the session key, then use the session key to decrypt the file data via **Crypto Compatibility** [server/crypto_compat.py](server/crypto_compat.py).
5.  **Network Transmission**: The (potentially re-encrypted or raw) file data is sent back to the **Client** [src/client/client.cpp](src/client/client.cpp) via the network protocol.
6.  **Reception & Decryption (on Client)**: The **Client** receives the data. If the file was sent encrypted, the client uses its private RSA key to decrypt the session key, then uses the session key to decrypt the file content.
7.  **Decompression (Optional)**: If the data was compressed, it is decompressed.
8.  **File Storage**: The client saves the restored file to the local filesystem.

## Important Data and Concepts

-   **Cryptographic Keys**: RSA public/private key pairs are fundamental for secure communication and key exchange. AES symmetric keys are used for bulk data encryption. Key generation is handled by scripts like [generate_rsa_keys.py](generate_rsa_keys.py).
-   **Configuration Files**: JSON files in the [config/](config/) directory ([config/default.json](config/default.json), [config/development.json](config/development.json), [config/production.json](config/production.json)) define critical parameters for both client and server, such as network ports, storage paths, and security settings.
-   **Protocol Definition**: The **Protocol** [server/protocol.py](server/protocol.py) module is crucial as it dictates how client and server communicate, including command structures, data formats, and error codes.
-   **GUI State Management**: The use of `gui_phase.json` [gui_phase.json](gui_phase.json) and `gui_progress.json` [gui_progress.json](gui_progress.json) suggests a mechanism for the GUI to store and retrieve its state or progress, potentially for inter-process communication or persistence across sessions.
-   **Build System (CMake & Vcpkg)**: The C++ client relies heavily on CMake [CMakeLists.txt](CMakeLists.txt) for its build process and Vcpkg [vcpkg.json](vcpkg.json) for managing external C++ libraries, ensuring cross-platform compilation and dependency resolution.
-   **Logging**: While not explicitly detailed in the file list, a robust system would include logging (likely in the [logs/](logs/) directory) for debugging, auditing, and monitoring server and client activities.
-   **Testing Framework**: The `tests/` directory ([tests/test_client.py](tests/test_client.py), [tests/test_upload.py](tests/test_upload.py), etc.) indicates the presence of unit and integration tests, which are vital for ensuring the correctness and reliability of the system.
-   **Documentation**: The extensive `docs/` directory provides critical insights into the project's design, requirements, and future plans. Reading files like [docs/NEW detailed spesification for the project.md](docs/NEW detailed spesification for the project.md) and [docs/SYSTEM_COMPLETION_PLAN.md](docs/SYSTEM_COMPLETION_PLAN.md) is essential for a deep understanding.

