

# Plan: Improve Python Server Robustness

**Objective:** Enhance the Python server's error handling and resource management to make it more resilient, stable, and secure against unexpected client behavior and network issues.

**Strategy:** This plan focuses on adding comprehensive `try...except` blocks around network and file I/O operations, implementing stricter validation of client-provided data, and ensuring resources like sockets and file handles are always properly closed, even when errors occur.

**Pre-computation/Analysis:**

*   **File to Modify:** `server/server.py`
*   **Tool to Use:** `replace`
*   **Key Areas for Improvement:**
    *   The main `_handle_client_connection` loop.
    *   Socket read/write operations (`_read_exact`, `_send_response`).
    *   File handling logic within `_handle_send_file`.
    *   Database interactions in `_db_execute`.

**Step-by-Step Plan:**

1.  **Fortify Socket Operations:**
    *   **Action:** Wrap all `socket.sendall()` and `socket.recv()` calls within `try...except` blocks that specifically catch `socket.timeout`, `ConnectionResetError`, and other `OSError` exceptions.
    *   **Verification:** The server should log a clear warning when a client disconnects abruptly instead of crashing the client handler thread.

2.  **Implement Graceful Resource Cleanup:**
    *   **Action:** Use `try...finally` blocks in the `_handle_client_connection` method to ensure that the client socket is always closed and the connection semaphore is always released, regardless of whether an error occurred.
    *   **Verification:** The server's active connection count should reliably decrease even when clients disconnect improperly.

3.  **Add Stricter Payload Validation:**
    *   **Action:** Before processing any payload, add checks to ensure its size and content are plausible. For example, in `_handle_send_file`, validate that the `original_size` is not excessively large and that `packet_number` is within the expected range.
    *   **Verification:** The server should reject malformed requests with a specific error log instead of attempting to process them, preventing potential crashes or resource exhaustion.

4.  **Secure File Path Handling:**
    *   **Action:** Before saving a file in `_handle_send_file`, sanitize the `filename` received from the client to prevent path traversal attacks. This involves removing any directory separators (`/`, `\`) or parent directory references (`..`).
    *   **Verification:** A request to save a file with a name like `../../secret.txt` should be rejected, and the file should not be written outside the designated storage directory.

5.  **Improve Database Transaction Safety:**
    *   **Action:** Enhance the `_db_execute` function to handle `sqlite3.OperationalError` (e.g., 'database is locked') with a retry mechanism or a graceful failure message.
    *   **Verification:** The server should be more resilient to temporary database contention issues.

