
# Plan: Add Unit Tests

**Objective:** Create a suite of unit tests for both the C++ client and the Python server to ensure their correctness, prevent regressions, and facilitate future development.

**Strategy:** This plan will introduce the Google Test framework for the C++ client and the `unittest` module for the Python server. It will focus on creating targeted tests for individual components, such as the cryptographic functions, the protocol message parsers, and the business logic of the client and server.

**Pre-computation/Analysis:**

*   **Files to Create (C++):** `tests/test_client.cpp`, `tests/CMakeLists.txt`
*   **Files to Create (Python):** `tests/test_server.py`
*   **Tool to Use:** `write_file`

**Step-by-Step Plan:**

1.  **Set up Google Test for the C++ Client:**
    *   **Action:** Add Google Test as a dependency in the `vcpkg.json` file and update the `CMakeLists.txt` file to create a new test executable.
    *   **Verification:** The project should build a new `run_tests` executable in the `build/Debug` directory.

2.  **Write Unit Tests for the C++ Client:**
    *   **Action:** Create a new `tests/test_client.cpp` file and add unit tests for the following components:
        *   **`CryptoManager`:** Test RSA key generation, AES encryption/decryption, and error handling.
        *   **`NetworkManager`:** Test the parsing of request and response headers.
        *   **`Client`:** Test the client's state machine logic (e.g., the transition from registration to file transfer).

3.  **Set up `unittest` for the Python Server:**
    *   **Action:** Create a new `tests/test_server.py` file and import the `unittest` module.
    *   **Verification:** The `python -m unittest tests/test_server.py` command should run without errors.

4.  **Write Unit Tests for the Python Server:**
    *   **Action:** Add unit tests to `tests/test_server.py` for the following components:
        *   **`BackupServer`:** Test the parsing of request and response headers, the handling of different request codes, and the logic for managing client state.
        *   **`Client`:** Test the logic for creating and managing client objects.
        *   **Database Functions:** Test the functions for saving and loading client and file information from the database.

5.  **Integrate Testing into the Build Process:**
    *   **Action:** Create a new script, `run_all_tests.bat`, that builds the C++ tests and runs both the C++ and Python test suites.
    *   **Verification:** The `run_all_tests.bat` script should execute all unit tests and report any failures.
