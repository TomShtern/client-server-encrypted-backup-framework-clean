Full Review: C++ Client (Core + GUI)
References: “NEW detailed specification for the project.md”

1. Protocol Serialization & Endianness
Issue:
If your client currently packs structs with reinterpret_cast, or writes raw structs to the socket, this is non-compliant.
Spec Reference:
“All multi-byte numeric fields are unsigned little-endian”, “All string fields are fixed-size buffers, null-terminated, padded with zeros”

Fix:
Manually serialize every numeric field to a buffer in little-endian order. Use utility functions for uint16/uint32 and string fields.
Example:

C++
void write_le_uint16(std::vector<uint8_t>& buf, uint16_t val) {
    buf.push_back(val & 0xFF);
    buf.push_back((val >> 8) & 0xFF);
}
// Repeat for uint32_t
Agent Action:
Replace all direct struct writes with manual per-field serialization and deserialization.

2. Error Handling & Retry Logic
Issue:
Errors must trigger a precisely worded message and up to 3 retries.
Spec Reference:
“server responded with an error”, “Retry the last failed operation up to 2 more times”, “Fatal error: ... after 3 attempts.”

Fix:
Wrap all network, protocol, and file ops with a retry loop. Print the exact lowercase message on failure.
Agent Action:
Add a retry utility:

C++
for (int attempt = 1; attempt <= 3; ++attempt) {
    if (operation()) break;
    std::cerr << "server responded with an error" << std::endl;
    if (attempt == 3) {
        std::cerr << "Fatal error: <context> after 3 attempts." << std::endl;
        exit(1);
    }
}
3. AES & RSA Crypto Compliance
Issue:
Default AES key sizes or incorrect RSA padding will break interoperability.
Spec Reference:
“AES key MUST be 256 bits (32 bytes)”, “RSA encryption ... MUST use OAEP with SHA-256 padding”

Fix:

Always check AES key is 32 bytes.
Use all-zero 16-byte IV for AES-CBC.
Use CryptoPP::RSAES_OAEP_SHA256_Decryptor for decrypting AES key.
Agent Action:
Explicitly set AES key/IV and RSA padding in all crypto ops.

4. POSIX cksum (NOT CRC32)
Issue:
Crypto++ CRC32 is not the same as POSIX cksum.
Spec Reference:
"cksum Algorithm is NOT Standard CRC-32", see Appendix A.2.

Fix:
Implement cksum as described:

CRC32 over file bytes
Then CRC32 over 4 bytes of file length (little-endian)
Final CRC is bitwise NOT
Agent Action:
Implement and call a compliant posix_cksum() in file transfer logic.

5. Chunked File Transfer
Issue:
Files >1MB must be chunked and sent in order, each chunk as a new 1028 request.
Spec Reference:
“Large files MUST be split into multiple packets”, “Recommended chunk size: 1MB or less”

Fix:
Refactor file sending to split into <=1MB chunks, number each, and send with proper headers.
Agent Action:
Loop over file in 1MB chunks, set packet numbers, and send with 1028 code.

6. String Field Padding
Issue:
If you use std::string or dynamic char*, your protocol fields may be non-compliant.
Spec Reference:
“All string fields are fixed-size buffers, null-terminated, padded with zeros”

Fix:
For every string field (username, filename), pad to field size (e.g., 255 bytes), null-terminate, zero-pad the rest.
Agent Action:
When serializing, use:

C++
std::vector<uint8_t> buf(255, 0);
std::copy_n(str.c_str(), std::min<size_t>(str.size(), 254), buf.data());
7. me.info/transfer.info Robustness
Issue:
Client must not register if me.info exists; must fall back on defaults if config files are missing.
Spec Reference:
“Client MUST NOT send a registration request ... if a me.info file already exists.”

Fix:
Check for me.info at startup. If found, use reconnection flow.
If config files missing, print warning and use default (do not crash).
Agent Action:

On startup: if (me.info exists) use reconnection; else, register.
If config files missing, std::cerr << "Warning: ..."; use default values.
8. GUI: Error Reporting & State Feedback
Issue:
GUI must reflect protocol and error state.
Spec Reference:
Error handling, retry logic, fatal exit.

Fix:

Show “server responded with an error” (lowercase) to user on protocol/network errors.
After 3 failed attempts, show detailed fatal error and disable further actions.
Show file transfer progress, including retries and chunk numbers.
Agent Action:

Add error reporting widget/area.
Tie protocol error handler to GUI feedback.
Update progress bar per chunk sent/received.
9. GUI: File and Config Selection
Issue:
Manual editing of transfer.info/me.info is brittle.
Spec Reference:
Robustness and user experience (implicit).

Fix:

Allow file picker dialog for selecting file to send.
Allow entering/changing username and server IP/port in GUI fields, with validation.
Show parsed config summary before sending.
Agent Action:

Use QFileDialog/QFileChooser/etc. for file selection.
Show/editable fields for username/server.
Parse and display config file contents in GUI.
10. GUI: Progress, Retry, and Final State
Issue:
No user feedback on retries/status is confusing.
Spec Reference:
Testing checklist, error handling, chunking.

Fix:

Progress bar: shows file chunks sent/total.
Retry indicator: shows current attempt out of 3.
Status area: shows CRC checks, server response, final result (success/failure).
Agent Action:

Add progress bar, retry counter, and status label to main window.
Update in real time as protocol events occur.
11. Concurrency & Thread Safety
Issue:
GUI may freeze if protocol/network run on UI thread.
Spec Reference:
“Handle connection timeouts using deadline_timer”, “Use async_read...”

Fix:

Run all network/protocol operations in a worker thread.
Use signals/slots (Qt) or thread-safe event handlers to update GUI.
Agent Action:

Offload protocol to std::thread or QtConcurrent.
Post results back to GUI thread safely.
12. Configuration Robustness
Issue:
Config file missing/invalid should not crash client.
Spec Reference:
“Show warning, don’t crash.”

Fix:
On missing/invalid config, print warning and use default (e.g., port 1256).
Agent Action:
Check file existence/validity, fallback to default values.

13. Boost.asio Networking Best Practices
Issue:
Improper use of synchronous API will block GUI and cause poor UX.
Spec Reference:
“Use async_read with completion conditions ... catch boost::system::system_error”

Fix:

Use async_connect, async_read, async_write with completion handlers.
Handle timeouts (deadline_timer).
Catch exceptions, show error in GUI.
Agent Action:
Refactor network code to async, use handlers to trigger protocol state machine and GUI updates.

14. Security Improvements (For Later)
Issue:
Spec intentionally weak for assignment, but you should document real-world fixes.
Spec Reference:
Appendix A.5, Security Vulnerability Analysis

Fix:

Use random IVs and MAC in real deployment.
Hide username enumeration.
Add sequence numbers/nonces.
15. Code Style & Modern C++17
Issue:
Legacy C++ or non-idiomatic code (raw new/delete, manual memory, C casts, etc.).
Spec Reference:
“Use C++17 conventions”, “Optimize for success”

Fix:

Replace raw pointers with smart pointers.
Use std::vector, std::string, std::array, auto.
Prefer range-for, structured bindings, etc.
Agent Action:
Modernize codebase for clarity and safety.

Summary Table
Area	Issue/Problem	Spec Reference	Action/Fix
Protocol serialization	Struct write, wrong endianness	Header, binary rules	Manual per-field LE serialization
Error/retry	No/incorrect retry, wrong message	Error handling	Exact error msg, 3 tries, fatal exit
Crypto	Default key size, bad padding	Crypto section	AES-256, OAEP-SHA256, static IV
CRC	Wrong CRC function	Appendix A.2	Implement POSIX cksum
Chunking	No/incorrect chunking	File chunking	1MB chunks, numbered, 1028 req.
String fields	Not fixed-size, not null-padded	Binary rules	Pad all strings to spec size
me.info/transfer.info	Wrong flow if file exists/missing file crash	Flow 1/2, config	Use reconnection, warn+default on missing
GUI error reporting	No feedback on error/retry	Error handling	Show error/attempts/progress in GUI
GUI config selection	Manual edit only	Robustness	File picker, editable fields, config summary
GUI progress/CRC	No progress/CRC status	Testing checklist	Progress bar, status area, CRC display
Concurrency	UI freeze on network	Boost.asio	Worker/network thread, post to GUI
Config robustness	Crash on bad/missing config	Config files	Fallback/default, warning
Networking	Blocking API, no timeout	Boost.asio	Async API, deadline_timer, exception handling
Code style	Outdated C++	C++17 conventions	Smart pointers, STL, modern idioms
Final Notes
Follow each Agent Action step to bring the client (and client GUI) to full spec compliance and optimal user experience.
For every suggestion, reference the specific section in your NEW detailed specification for the project.md.
Every fix is actionable and can be directly implemented by your AI agent or yourself.
No changes to the specification were made—fixes are about code, not the spec.
