
# Plan: Secure the Communication Protocol

**Objective:** Remediate the critical security vulnerabilities identified in the project's communication protocol to protect against data corruption, tampering, and eavesdropping.

**Strategy:** The current protocol uses a fixed IV and a non-cryptographic checksum (CRC32), making it vulnerable to several attacks. This plan will replace these weak components with industry-standard cryptographic controls: a random IV for AES-CBC and an HMAC for message authentication. This will be a protocol-breaking change, requiring coordinated updates to both the client and server.

**Pre-computation/Analysis:**

*   **Files to Modify (Server):** `server/server.py`, `server/crypto_compat.py`
*   **Files to Modify (Client):** `src/client/client.cpp`, `include/wrappers/AESWrapper.h`, `src/wrappers/AESWrapper.cpp`
*   **Vulnerability 1: Fixed IV.** Using a zero-filled IV for AES-CBC is deterministic and allows attackers to infer relationships between plaintext blocks if they can observe multiple ciphertexts. This will be replaced with a randomly generated IV for each encryption.
*   **Vulnerability 2: No Authentication.** Using `cksum` only protects against accidental corruption, not malicious tampering. An attacker can modify the ciphertext and compute a new valid checksum. This will be replaced with HMAC-SHA256.

**Step-by-Step Plan:**

### Part 1: Implement Random IV for AES-CBC

1.  **Modify the `AESWrapper` (C++ Client):**
    *   **Action:** Update `AESWrapper::encrypt`. It must now:
        1.  Generate a random 16-byte IV using a cryptographically secure random number generator (e.g., `CryptoPP::AutoSeededRandomPool`).
        2.  Prepend this 16-byte IV to the beginning of the resulting ciphertext.
        3.  The final return value will be `IV + EncryptedData`.
    *   **Action:** Update `AESWrapper::decrypt`. It must now:
        1.  Expect the ciphertext to be at least 16 bytes long.
        2.  Extract the first 16 bytes as the IV.
        3.  Use the extracted IV for the AES-CBC decryption process on the *rest* of the ciphertext.

2.  **Modify the Server (Python):**
    *   **Action:** Update the server's decryption logic in `_handle_send_file`.
        1.  Before decrypting the `full_encrypted_data`, split it into the `iv` (first 16 bytes) and the `ciphertext` (the remainder).
        2.  Pass this extracted `iv` to the `AES.new()` call: `cipher_aes = AES.new(current_aes_key, AES.MODE_CBC, iv=iv)`.

### Part 2: Replace CRC32 with HMAC-SHA256

1.  **Update the Protocol (Conceptual):** The `RESP_FILE_CRC` (1603) message will be repurposed. The `Cksum` field will now carry a 32-byte HMAC-SHA256 hash instead of a 4-byte CRC32.

2.  **Modify the Server (Python):**
    *   **Action:** In `_handle_send_file`, after reassembling the *full encrypted data* (but before decryption), calculate an HMAC.
        1.  Import `HMAC` and `SHA256` from `crypto_compat`.
        2.  Create the HMAC object: `h = HMAC.new(client.get_aes_key(), digestmod=SHA256)`.
        3.  Update it with the full ciphertext: `h.update(full_encrypted_data)`.
        4.  Get the 32-byte digest: `calculated_hmac = h.digest()`.
    *   **Action:** In the `_send_response` call for `RESP_FILE_CRC`, pack the `calculated_hmac` into the payload instead of the CRC.
    *   **Action:** Remove the `_calculate_crc` method entirely.

3.  **Modify the Client (C++):**
    *   **Action:** In `transferFile`, after encrypting the file and before sending packets, calculate the HMAC of the *entire ciphertext*.
        1.  Use `Crypto++`'s `HMAC` and `SHA256` classes.
        2.  Store the resulting 32-byte HMAC locally.
    *   **Action:** In `verifyCRC` (which should be renamed to `verifyIntegrity`), when the `RESP_FILE_CRC` response is received:
        1.  Extract the 32-byte `server_hmac` from the payload.
        2.  Compare it byte-for-byte with the locally computed HMAC.
        3.  The logic for `REQ_CRC_OK` (1029), `REQ_CRC_INVALID_RETRY` (1030), and `REQ_CRC_FAILED_ABORT` (1031) remains the same, but is now based on the HMAC comparison.
    *   **Action:** Remove the `calculateCRC32` function.

4.  **Update Documentation:**
    *   **Action:** Create a new markdown file `docs/PROTOCOL_V2_SECURITY_UPGRADE.md` detailing the new, secure protocol flow, specifying the use of random IVs and HMAC-SHA256.
