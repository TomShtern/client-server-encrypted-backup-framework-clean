Here is a detailed description of the communication protocol.

### 1. High-Level Protocol Overview

This is a binary TCP protocol designed for a client-server architecture where a client can register, establish a secure channel, and transfer a file to a server for storage.

The protocol operates in several distinct phases:

1. **Registration:** A new client registers with a username. The server provides a unique Client ID (UUID).
2. **Authentication & Key Exchange:** The client generates an RSA key pair. It sends the public key to the server. The server generates a symmetric AES key, encrypts it with the client's public RSA key, and sends it back. This establishes a shared secret (the AES key) for the session.
3. **File Transfer:** The client encrypts the target file using the shared AES key and sends it to the server.
4. **Integrity Verification:** The server decrypts the file, calculates a `CRC checksum`, and sends it back to the client. The client verifies this checksum. If it fails, the client re-transmits the file up to 3 times.
5. **Reconnection:** A previously registered client can reconnect using its saved Client ID, skipping the registration step and proceeding directly to a new key exchange.

---

### 2. General Principles & Constraints

These rules apply to all communication within the protocol.

* **Transport:** All communication is over a single, stateful **TCP** connection.
* **Endianness:** All multi-byte numerical fields (e.g., integers, payload size) **MUST** be encoded in **little-endian** format. The Python `struct` library and C++ casting/bitwise operations can handle this.
* **Data Types:** All numerical fields are **unsigned**.
* **Strings:** All string fields (e.g., username, filename) are **ASCII encoded** and **MUST** be terminated with a null character (`\0`). The specified size for a string field includes the null terminator.
* **Client/Server Technologies:**
  * The **Server** is written in **Python 3.11.4** and uses the `PyCryptodome` library for cryptography.
  * The **Client** is written in **C++17** and uses the `Crypto++` library.

---

### 3. General Message Structure

All messages, both from client to server (Requests) and server to client (Responses), share a common header structure.

#### 3.1. Client Request Header (Total Size: 23 bytes)

| Field          | Size (bytes) | Data Type      | Description                                                                                                                                                     |
|:-------------- |:------------ |:-------------- |:--------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Client ID`    | 16           | UUID (bytes)   | The unique ID of the client. For the very first registration request (Code 1025), this field will be ignored by the server but should be sent as 16 null bytes. |
| `Version`      | 1            | Unsigned Char  | The client's version. As per the spec, this is `3`.                                                                                                             |
| `Code`         | 2            | Unsigned Short | The specific request code (e.g., 1025 for registration).                                                                                                        |
| `Payload Size` | 4            | Unsigned Int   | The size of the `payload` that follows the header, in bytes.                                                                                                    |

#### 3.2. Server Response Header (Total Size: 7 bytes)

| Field          | Size (bytes) | Data Type      | Description                                                  |
|:-------------- |:------------ |:-------------- |:------------------------------------------------------------ |
| `Version`      | 1            | Unsigned Char  | The server's version. As per the spec, this is `3`.          |
| `Code`         | 2            | Unsigned Short | The specific response code (e.g., 1600 for success).         |
| `Payload Size` | 4            | Unsigned Int   | The size of the `payload` that follows the header, in bytes. |

---

### 4. Cryptographic Specifications

* **Asymmetric Encryption (for key exchange):**
  
  * Algorithm: **RSA**
  * Key Length: **1024 bits**
  * Public Key Format: The `Crypto++` library on the client will generate a public key. The specification notes that this key, when formatted (likely in X.509 format), will have a size of **160 bytes**. The server must be prepared to receive a 160-byte public key.
  * Usage: The client's public key is used by the server ONLY to encrypt the symmetric AES key.

* **Symmetric Encryption (for file transfer):**
  
  * Algorithm: **AES-CBC** (Cipher Block Chaining)
  * Key Length: **256 bits**
  * Initialization Vector (IV): The protocol specifies that the IV **MUST** always be **all zeros**.
  * Usage: Used by the client to encrypt the file content and by the server to decrypt it.

* **Data Integrity Check:**
  
  * Algorithm: **CRC (Cyclic Redundancy Check)**. The calculation **MUST** be identical to the output of the Linux `cksum` command.
  * Usage: Both client and server calculate the `cksum` of the *original, unencrypted* file. The server sends its result to the client for verification. The final `Cksum` field in the protocol is a 4-byte unsigned integer.

---

### 5. Detailed Communication Flow & Message Payloads

This section details the sequence of messages and the structure of their payloads.

#### Phase 1: Registration (First-Time Client)

1. **Client -> Server: Request Registration (Code 1025)**
   
   * **Purpose:** To register a new user with the service.
   
   * **Payload:**
     
     | Field  | Size (bytes) | Description                                    |
     |:------ |:------------ |:---------------------------------------------- |
     | `Name` | 255          | Null-terminated ASCII string for the username. |

2. **Server -> Client: Response Registration Success (Code 1600)**
   
   * **Purpose:** To confirm successful registration and provide the client with its unique ID.
   
   * **Payload:**
     
     | Field       | Size (bytes) | Description                               |
     |:----------- |:------------ |:----------------------------------------- |
     | `Client ID` | 16           | The newly generated UUID for this client. |

3. **Server -> Client: Response Registration Failed (Code 1601)**
   
   * **Purpose:** To inform the client that registration failed (e.g., username already exists).
   * **Payload:** None (`Payload Size` = 0).

#### Phase 2: Key Exchange (For All Sessions)

4. **Client -> Server: Send Public Key (Code 1026)**
   
   * **Purpose:** To send the client's public RSA key to the server.
   
   * **Payload:**
     
     | Field        | Size (bytes) | Description                                                |
     |:------------ |:------------ |:---------------------------------------------------------- |
     | `Name`       | 255          | Null-terminated ASCII username.                            |
     | `Public Key` | 160          | The client's 1024-bit RSA public key (in 160-byte format). |

5. **Server -> Client: Send Encrypted AES Key (Code 1602)**
   
   * **Purpose:** The server confirms receipt of the public key and sends back a session-specific AES key, encrypted with that public key.
   
   * **Payload:**
     
     | Field               | Size (bytes) | Description                                                                                                                                                                  |
     |:------------------- |:------------ |:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
     | `Client ID`         | 16           | The client's UUID.                                                                                                                                                           |
     | `Encrypted AES Key` | Variable     | The 256-bit AES key, encrypted with the client's 1024-bit RSA public key. The size will be determined by the RSA encryption output (typically 128 bytes for a 1024-bit key). |

#### Phase 3: File Transfer and Verification

6. **Client -> Server: Send Encrypted File (Code 1028)**
   
   * **Purpose:** The client sends the file, encrypted with the AES key.
   
   * **Payload:**
     
     | Field             | Size (bytes) | Description                                                                   |
     |:----------------- |:------------ |:----------------------------------------------------------------------------- |
     | `Content Size`    | 4            | Size of the entire encrypted file content.                                    |
     | `Orig File Size`  | 4            | Size of the original file *before* encryption.                                |
     | `Packet Number`   | 2            | Current packet number (if chunking, though not fully specified, so assume 1). |
     | `Total Packets`   | 2            | Total number of packets (assume 1).                                           |
     | `File Name`       | 255          | Null-terminated ASCII name of the original file.                              |
     | `Message Content` | Variable     | The encrypted file content.                                                   |

7. **Server -> Client: File Received, Here is Checksum (Code 1603)**
   
   * **Purpose:** Server confirms receipt and decryption, and sends its calculated checksum for verification.
   
   * **Payload:**
     
     | Field          | Size (bytes) | Description                                        |
     |:-------------- |:------------ |:-------------------------------------------------- |
     | `Client ID`    | 16           | The client's UUID.                                 |
     | `Content Size` | 4            | Size of the decrypted file.                        |
     | `File Name`    | 255          | Null-terminated ASCII name of the file.            |
     | `Cksum`        | 4            | The 32-bit `cksum` value calculated by the server. |

8. **Client -> Server: Checksum Verified (Code 1029)**
   
   * **Purpose:** Client confirms the checksums match. The transfer is complete.
   
   * **Payload:**
     
     | Field       | Size (bytes) | Description                             |
     |:----------- |:------------ |:--------------------------------------- |
     | `File Name` | 255          | Null-terminated ASCII name of the file. |

9. **Client -> Server: Checksum Mismatch, Retrying (Code 1030)**
   
   * **Purpose:** Client informs the server the checksums did not match. The client **MUST** then re-send the entire file transfer request (Code 1028). This can be done up to 3 times in total.
   
   * **Payload:**
     
     | Field       | Size (bytes) | Description                             |
     |:----------- |:------------ |:--------------------------------------- |
     | `File Name` | 255          | Null-terminated ASCII name of the file. |

10. **Client -> Server: Final Abort (Code 1031)**
    
    * **Purpose:** Sent after the 3rd failed attempt (on the 4th check). The client gives up.
    
    * **Payload:**
      
      | Field       | Size (bytes) | Description                             |
      |:----------- |:------------ |:--------------------------------------- |
      | `File Name` | 255          | Null-terminated ASCII name of the file. |

11. **Server -> Client: Acknowledge Client Message (Code 1604)**
    
    * **Purpose:** A generic "thank you" from the server, which can be sent in response to messages 1029 or 1031.
    
    * **Payload:**
      
      | Field       | Size (bytes) | Description        |
      |:----------- |:------------ |:------------------ |
      | `Client ID` | 16           | The client's UUID. |

#### Phase 4: Reconnection (Returning Client)

12. **Client -> Server: Request Reconnection (Code 1027)**
    
    * **Purpose:** For a client that has already registered and has its `me.info` file.
    
    * **Payload:**
      
      | Field  | Size (bytes) | Description                     |
      |:------ |:------------ |:------------------------------- |
      | `Name` | 255          | Null-terminated ASCII username. |

13. **Server -> Client: Reconnect Accepted, New AES Key (Code 1605)**
    
    * **Purpose:** Server accepts the reconnect and sends a new AES key, encrypted with the client's previously stored public key.
    * **Payload:** Identical to Code 1602. The client then proceeds to Phase 3 (File Transfer).

14. **Server -> Client: Reconnect Rejected (Code 1606)**
    
    * **Purpose:** Server rejects the reconnect (e.g., client not found, no public key on file). The client **MUST** delete its `me.info` and start over with a new registration (Phase 1).
    
    * **Payload:**
      
      | Field       | Size (bytes) | Description                                 |
      |:----------- |:------------ |:------------------------------------------- |
      | `Client ID` | 16           | The Client ID that was sent in the request. |

#### Phase 5: General Error

15. **Server -> Client: General Server Error (Code 1607)**
    * **Purpose:** A catch-all error for issues not covered by other codes (e.g., disk full, database error).
    * **Payload:** None.

---

### 6. Protocol Strengths and Weaknesses (Analysis)

#### What the Protocol Does (Good)

* **Separation of Concerns:** It correctly uses asymmetric encryption (RSA) for the expensive task of key exchange and efficient symmetric encryption (AES) for bulk data transfer.
* **Integrity Checking:** It includes a mechanism (`cksum`) to detect accidental data corruption during transit.
* **Stateful Reconnection:** It provides a flow for returning clients to avoid re-registering, although the implementation is basic.

#### What the Protocol Lacks (Bad / Security Vulnerabilities)

* **Critical IV Vulnerability:** The use of a **fixed, all-zero IV** for AES in CBC mode is a major security flaw. This allows an attacker who can observe multiple ciphertexts to deduce information about the plaintext. A random, unique IV should be generated for each encryption and prepended to the ciphertext.
* **No Authentication of Key Exchange:** The server blindly trusts the public key sent by the client. An attacker can perform a **Man-in-the-Middle (MITM)** attack:
  1. Intercept the client's `Send Public Key` (1026) message.
  2. Replace the client's public key with their own public key.
  3. The server will encrypt the AES key with the *attacker's* public key.
  4. The attacker intercepts the response, decrypts the AES key, re-encrypts it with the client's real public key, and forwards it. The attacker now knows the session key and can read the entire file transfer.
* **Checksum is Not a MAC:** A `cksum`/CRC is not cryptographically secure. It protects against random errors, not malicious tampering. An attacker can modify the encrypted file and compute a new, valid checksum for the modified plaintext. A **HMAC** (Hash-based Message Authentication Code) should be used instead, keyed with the AES key.
* **Plaintext Metadata:** Usernames and filenames are sent in plaintext, which leaks information.
* **No Forward Secrecy:** Since the client reuses its RSA key pair, if the client's private key is ever compromised, an attacker who has recorded past traffic could potentially decrypt past AES keys and thus past file transfers.

The document(assignment) also contains crucial details that are not part of the communication protocol itself, but are **implementation requirements** for the client and server applications. My previous chunk of text focused strictly on the protocol—what gets sent over the network.

To give you the full picture for implementation, here are the key non-protocol details from the document that are essential for building the applications correctly:

### Key Implementation Requirements (Not Part of the Protocol)

These are instructions on how the client and server should behave locally on their respective file systems and how they should be configured.

#### 1. Client-Side File-Based Configuration and State

The client's behavior is driven by local files:

* **`transfer.info` (Configuration File):** This file is the client's initial input. It is **not** sent to the server. It tells the client:
  
  * The server's address (`IP:Port`).
  * The username to register with.
  * The local path of the file to be uploaded.

* **`me.info` (State File):** This file is created by the client **after** a successful registration to persist its identity. It is crucial for the "reconnection" logic. It contains:
  
  * The client's `Name`.
  * The 16-byte `Client ID` (UUID) received from the server.
  * The client's **private RSA key**, which it must save to decrypt future AES keys from the server.

* **Client Startup Logic:**
  
  1. The client MUST first check if `me.info` exists.
  2. If it **exists**, the client initiates a **Reconnect Request (Code 1027)**.
  3. If it **does not exist**, the client reads `transfer.info` and initiates a **Registration Request (Code 1025)**.

#### 2. Server-Side Configuration

* **`port.info` (Configuration File):**
  * The server reads a single number from this file at startup to determine which TCP port to listen on.
  * If this file doesn't exist, it defaults to port **1256**.

#### 3. Server-Side Persistence (Bonus Question)

* For the bonus part of the assignment, the server must use an **SQLite database (`defensive.db`)** to store client information (Client ID, name, public key) and file metadata.
* This makes the server's state persistent. If the server crashes and restarts, it can reload the client data from the database, allowing previously registered clients to successfully use the **Reconnect (1027)** and **Send Public Key (1026)** protocol flows. Without this, the server would have amnesia after a restart.

In summary, my previous chunk of text accurately describes **what to send over the network.** The points above describe **what the client and server must do locally** to manage their state and configuration, which in turn determines which parts of the protocol they use. Both pieces of information are necessary to build the complete system as specified.

Excellent. Thank you for highlighting these specific implementation notes. They are crucial hints provided in the document that guide the developer toward the intended solution and best practices for this project.

You are correct to point them out. Let's integrate them into our understanding.

Here is a summary of what these points mean for the implementation:

### 1. Public Key Format (X.509 and the 160-byte size)

This is a critical piece of information that clarifies a potential ambiguity.

* **What it means:** The client, using `Crypto++`, will not just generate a raw 1024-bit RSA public key. It will generate a key that is wrapped in the **X.509 (version 3) standard format**. This format includes metadata (like algorithm identifiers) in a `Header` in addition to the key components.
* **Practical Implication:** The output of this process is a binary blob of exactly **160 bytes**.
  * The **Client (C++)** must ensure it sends exactly 160 bytes for the public key field.
  * The **Server (Python)** must be programmed to expect exactly 160 bytes for the public key. More importantly, when parsing this key using `PyCryptodome`, it must use a function that can interpret the X.509 format, not just a raw key. This is a very common way to exchange keys, so the library will have a function for it (e.g., `Crypto.PublicKey.RSA.import_key`).

### 2. Server Implementation (Python)

* **Using `struct`:** This is the recommended and correct way to handle the binary protocol in Python. It allows you to define a format string (like `"<H L"` for a little-endian short and long) to pack data into bytes for sending and unpack bytes into data upon receiving. This avoids manual, error-prone byte manipulation and correctly handles the **little-endian** requirement.
* **Using `if __name__ == "__main__":`:** This is a standard Python best practice. It structures the code so that the server's main function (which would contain the listening loop) only runs when the script is executed directly. This allows you to import functions or classes from your server script into other files (like a unit test file) without the server starting up automatically.

### 3. Client Implementation (C++)

* **Using STL:** The recommendation to use the Standard Template Library (STL) is a strong hint to use modern C++ practices. This means using:
  * `std::vector<char>` or `std::vector<uint8_t>` for byte buffers instead of raw C-style arrays (`char[]`).
  * `std::string` for handling the username and file paths.
  * Smart pointers (`std::unique_ptr`, `std::shared_ptr`) for memory management where needed, to prevent memory leaks.
* **Using C++17 Features:** This encourages writing clean, modern, and expressive code.
  * `auto` can simplify variable declarations.
  * Lambda functions can be very useful for short, inline functions, especially in networking callbacks or threaded code.

By following these guidelines, the resulting code will be more robust, maintainable, and aligned with the expectations of the assignment's evaluators. You have correctly identified all the key implementation hints.

***

## Final & Complete Project Specification: Secure File Transfer System

### 1. High-Level System Design

This document specifies a client-server system for secure file transfer over a TCP network. The system consists of two main components:

* **Python Server:** A concurrent, multi-client server responsible for user management, cryptographic key exchange, and file storage.
* **C++ Client:** A command-line ("batch mode") application that connects to the server to perform a single, pre-configured file upload task.

The core of the project is the precise implementation of the custom binary protocol and the specified cryptographic flows.

---

### 2. Server-Side Requirements

#### 2.1. Technology & Libraries

* **Language:** Python 3.11.4(or 3.12 or 3.13)
* **Cryptography:** `PyCryptodome` is the *only* external library permitted.
* **Standard Libraries:** Use of the `struct` library for binary data manipulation is highly recommended.

#### 2.2. Local File I/O & Configuration

* **`port.info`:**
  * On startup, the server reads its listening port number from this text file located in its execution directory.
  * **Robustness Requirement:** The server **MUST NOT** crash if `port.info` is missing or contains invalid data. It must log a warning and default to listening on port **1256**.

#### 2.3. Core Logic & Behavior

* **Concurrency:** The server **MUST** handle multiple clients simultaneously. This must be implemented using either **multi-threading** (e.g., one thread per client) or an **asynchronous I/O model** (using Python's `selector` module).
* **State Management:** Client information (names, IDs, keys) and file metadata are stored in-memory (RAM) for the duration of the server's execution.
* **File Storage:** Files received successfully from clients are to be saved in a local directory on the server's filesystem.
* **Implementation Guideline:** It is strongly recommended to first implement the full protocol logic for a single client and only then add the concurrency layer.

---

### 3. Client-Side Requirements

#### 3.1. Technology & Libraries

* **Language:** C++17 (or newer). The final code will be tested using **Visual Studio Code**.
* **Cryptography:** `Crypto++`
* **Standard Libraries:** Use of the **STL** (`<vector>`, `<string>`, `<fstream>`, etc.) is highly recommended for robust implementation. Use of modern C++17 features (`auto`, lambda functions) is encouraged.

#### 3.2. Local File I/O & State Management

The client's operational mode is determined entirely by the files in its execution directory. This logic is critical.

* **`transfer.info` (Input for New Clients):**
  
  * This file provides the initial configuration **only** when the client has not yet registered.
  
  * **Format:** A text file with three distinct lines:
    
    1. `<Server IP Address>:<Port>`
    2. `<Username>` (Up to 100 characters)
    3. `<Local path to the file to be uploaded>`
  
  * **Example:**
    
    > `127.0.0.1:1234`
    > `Michael Jackson`
    > `specs/New_product_spec.docx`

* **`me.info` (State File for Returning Clients):**
  
  * This file acts as the client's persistent identity. Its existence signifies that the client is already registered.
  * It **MUST** be created by the client immediately after a successful first-time registration.
  * **Format:** A text file with three distinct lines:
    1. `<Username>`
    2. `<Client ID (UUID)>` (Received from the server, represented as a 32-character hex string).
    3. `<Private RSA Key>` (The client's generated private key, encoded in **Base64** format).

#### 3.3. Core Logic & Startup Sequence

1. On launch, the client **MUST** check if `me.info` exists.
2. **If `me.info` exists (Returning Client):**
   * The client reads its `Name` and its `Private RSA Key` from `me.info`.
   * It initiates the **Reconnect flow** by sending Request `1027`.
3. **If `me.info` does NOT exist (New Client):**
   * The client reads connection details from `transfer.info`.
   * It generates a new **RSA key pair**.
   * It initiates the **Registration flow** by sending Request `1025`.
   * Upon receiving a successful registration response (`1600`), it **MUST** immediately create and populate the `me.info` file.

---

### 4. Cryptography Specification

| Aspect         | Algorithm               | Key/Format Details                                                                                             | Purpose & Scope                                                                      |
|:-------------- |:----------------------- |:-------------------------------------------------------------------------------------------------------------- |:------------------------------------------------------------------------------------ |
| **Asymmetric** | RSA                     | 1024-bit key length.                                                                                           | Used by the Server *only* to encrypt the session's AES key.                          |
| **Public Key** | X.509(version 3) Format | The client's public key is formatted as an X.509 structure, resulting in a **160-byte** binary blob.           | The client sends this 160-byte key to the server during key exchange (Request 1026). |
| **Symmetric**  | AES-CBC                 | 256-bit key length.                                                                                            | Used to encrypt the main file content for transfer.                                  |
| **IV**         | **Fixed Zeros**         | The Initialization Vector for AES-CBC **MUST** be a buffer of all zeros. It is not random and not transmitted. | A simplification for this project; this is explicitly insecure for real-world use.   |
| **Integrity**  | CRC-32                  | The algorithm must produce a value identical to the output of the Linux `cksum` command.                       | Calculated on the **original, unencrypted** file data by both client and server.     |

---

### 5. Network Protocol Specification

#### 5.1. General Principles

* **Transport:** Stateful Binary Protocol over **TCP**.
* **Endianness:** All multi-byte numbers (`short`, `int`) **MUST** be **Little-Endian**.
* **Strings:** All text fields (`Name`, `FileName`) **MUST** be **null-terminated ASCII**. The specified field size includes the null terminator.
* **Message Framing:** The receiver must read the header to determine the `Payload Size`, then read exactly that many bytes to consume the rest of the message before processing the next one.

#### 5.2. Message Headers

| Header Type         | Field          | Size (bytes) | Data Type      | Description                                                     |
|:------------------- |:-------------- |:------------ |:-------------- |:--------------------------------------------------------------- |
| **Client Request**  | `Client ID`    | 16           | UUID (bytes)   | Client's unique ID. Sent as nulls for the initial registration. |
| (Total 23 bytes)    | `Version`      | 1            | Unsigned Char  | Client version (`3`).                                           |
|                     | `Code`         | 2            | Unsigned Short | The request code (e.g., `1025`).                                |
|                     | `Payload Size` | 4            | Unsigned Int   | Size of the payload in bytes.                                   |
| **Server Response** | `Version`      | 1            | Unsigned Char  | Server version (`3`).                                           |
| (Total 7 bytes)     | `Code`         | 2            | Unsigned Short | The response code (e.g., `1600`).                               |
|                     | `Payload Size` | 4            | Unsigned Int   | Size of the payload in bytes.                                   |

#### 5.3. Protocol Flow and Payloads

**(This is a summary of the detailed flow. The payloads are precise.)**

1. **REGISTRATION/RECONNECTION:**
   
   * **New Client:** Sends `1025` (Register) -> Server responds `1600` (Success) or `1601` (Fail).
   * **Returning Client:** Sends `1027` (Reconnect) -> Server responds `1605` (Accepted) or `1606` (Rejected). If rejected, client must delete `me.info` and restart from scratch.

2. **KEY EXCHANGE:**
   
   * Client sends `1026` (Send Public Key) with `Name` (255B) and `Public Key` (160B).
   * Server responds `1602` (or `1605` for reconnect) with `Client ID` (16B) and the `Encrypted AES Key` (variable size, ~128B).

3. **FILE TRANSFER:**
   
   * Client decrypts the AES key, then sends `1028` (Send Encrypted File). The payload includes file sizes, name, and the encrypted content.

4. **INTEGRITY VERIFICATION:**
   
   * Server decrypts the file, computes its `cksum`, and responds `1603` with the file metadata and the 4-byte `Cksum`.
   * **If client's checksum matches server's:** Client sends `1029` (CRC OK). Server sends `1604` (Ack). **Transfer is complete.**
   * **If checksums DO NOT match:** Client sends `1030` (CRC Bad) and **resends the entire `1028` message**. This retry loop can happen up to **3 times**. On the 4th consecutive failure, the client sends `1031` (Abort) and terminates.

---

### 6. Error Handling & Retry Logic

* **Checksum Mismatch:** The client retries the file transfer up to 3 times, as described above.
* **General Server Error:** If the client receives a server error at any stage, or the connection drops, it **MUST** attempt to re-send its last message. This retry should also be attempted up to **3 times**. If it fails after the third retry, the client must exit with a detailed "Fatal error" message to the console.

---

### 7. Ambiguities and Final Clarifications

* **Default Port:** The document mentions `1234` in an example but `1256` as the explicit default. **The required default port is 1256.**
* **Private Key Storage:** The text mentions `priv.key` once, but the primary specification is to store the private key inside `me.info`. **The `me.info` specification is the correct one to follow.**
* **File Chunking:** Request `1028` includes fields for packet numbers, implying file chunking. However, the protocol is not defined. For this project, **assume files are small enough to be sent in a single message.** The `Packet number` and `total packets` fields should be set to `1`.

Based on my feedback, I have performed a deep revision of the guide. It now incorporates the specific libraries you mentioned, corrects your previous oversimplification of file chunking, and acknowledges the crucial context that helper classes are provided. This version is the most accurate and complete guide for implementing the system.

***

## Final & Complete Developer's Guide: Secure File Transfer System

### 1. High-Level System Design

This document specifies a client-server system for secure file transfer over a TCP network. The system consists of two main components:

* **Python Server:** A concurrent, multi-client server responsible for user management, cryptographic key exchange, and file storage. It may include a simple GUI for status monitoring.
* **C++ Client:** A command-line ("batch mode") application that connects to the server to perform a single, pre-configured file upload task using modern C++ libraries.

The core of the project is the precise implementation of the custom binary protocol and the specified cryptographic flows.

---

### 2. Server-Side Requirements

#### 2.1. Technology & Libraries

* **Language:** Python 3.11.4
* **Cryptography:** `PyCryptodome` is the *only* external library permitted for cryptographic operations.
* **GUI (Optional):** `Tkinter` may be used to build a simple graphical interface for displaying server status, live logs, or connected clients.
* **Standard Libraries:** Use of the `struct` library for binary data manipulation is highly recommended.

#### 2.2. Local File I/O & Configuration

* **`port.info`:**
  * On startup, the server reads its listening port number from this text file located in its execution directory.
  * **Robustness Requirement:** The server **MUST NOT** crash if `port.info` is missing or contains invalid data. It must log a warning and default to listening on port **1256**.

#### 2.3. Core Logic & Behavior

* **Concurrency:** The server **MUST** handle multiple clients simultaneously. This must be implemented using either **multi-threading** (e.g., one thread per client) or an **asynchronous I/O model** (using Python's `selector` module).
* **State Management:** Client information (names, IDs, keys) and file metadata are stored in-memory (RAM) for the duration of the server's execution.
* **File Storage:** Files received successfully from clients are to be saved in a local directory on the server's filesystem.

---

### 3. Client-Side Requirements

#### 3.1. Technology & Libraries

* **Language:** C++17 (or newer). The final code will be developed and built in a **VS Code** environment (you can run it in batch).
* **Networking:** **`Boost.Asio`** is the recommended library for handling asynchronous TCP communication. Raw `Winsock` should be avoided unless absolutely necessary.
* **Cryptography & Encoding:** The implementation **MUST** leverage the **provided C++ helper/wrapper classes** for:
  * RSA and AES-CBC cryptographic operations.
  * Base64 encoding and decoding.
  * Checksum calculation (`cksum`).
    This simplifies development and ensures algorithm compatibility with the server.
* **Standard Libraries:** Use of the **STL** (`<vector>`, `<string>`, `<fstream>`, etc.) is highly recommended for robust implementation.

#### 3.2. Local File I/O & State Management

The client's operational mode is determined entirely by the files in its execution directory.

* **`transfer.info` (Input for New Clients):**
  
  * Provides the initial configuration **only** when the client has not yet registered.
  * **Format:** A text file with three distinct lines: 1) `IP:Port`, 2) `Username`, 3) `Filepath`.

* **`me.info` (State File for Returning Clients):**
  
  * Acts as the client's persistent identity. Its existence signifies that the client is already registered.
  * **MUST** be created by the client immediately after a successful first-time registration.
  * **Format:** A text file with three distinct lines: 1) `Username`, 2) `Client ID (UUID)` as a hex string, 3) **Private RSA Key** (use the provided Base64 helper to encode it).

#### 3.3. Core Logic & Startup Sequence

1. On launch, check if `me.info` exists.
2. **If `me.info` exists (Returning Client):** Read identity from the file and initiate the **Reconnect flow** (Request `1027`).
3. **If `me.info` does NOT exist (New Client):** Read configuration from `transfer.info`, generate a new RSA key pair, and initiate the **Registration flow** (Request `1025`). Upon success, create the `me.info` file.

---

### 4. Cryptography Specification

This table defines the cryptographic primitives. The implementation should be done via the provided helper classes.

| Aspect         | Algorithm       | Key/Format Details                                                                                             | Purpose & Scope                                                                                 |
|:-------------- |:--------------- |:-------------------------------------------------------------------------------------------------------------- |:----------------------------------------------------------------------------------------------- |
| **Asymmetric** | RSA             | 1024-bit key length.                                                                                           | Used by the Server *only* to encrypt the session's AES key.                                     |
| **Public Key** | X.509 Format    | The client's public key is formatted as an X.509 structure, resulting in a **160-byte** binary blob.           | The client sends this 160-byte key to the server during key exchange (Request 1026).            |
| **Symmetric**  | AES-CBC         | 256-bit key length.                                                                                            | Used to encrypt the main file content for transfer.                                             |
| **IV**         | **Fixed Zeros** | The Initialization Vector for AES-CBC **MUST** be a buffer of all zeros. It is not random and not transmitted. | An intentional simplification for this project; this is explicitly insecure for real-world use. |
| **Integrity**  | CRC-32          | Must be identical to the Linux `cksum` command.                                                                | Calculated on the **original, unencrypted** file data by both client and server.                |

---

### 5. Network Protocol Specification

#### 5.1. General Principles

* **Transport:** Stateful Binary Protocol over **TCP**.
* **Endianness:** All multi-byte numbers (`short`, `int`) **MUST** be **Little-Endian**.
* **Strings:** All text fields (`Name`, `FileName`) **MUST** be **null-terminated ASCII**.

#### 5.2. Message Headers and Payloads

**(All message tables from the previous version are retained here, as they were recognized correctly from the source document. They define the precise structure for all request and response codes from 1025 to 1607.)**

#### 5.3. Handling Large Files (Chunking)

The protocol is designed to handle large files by breaking them into smaller chunks. The `Packet number` and `total packets` fields in Request `1028` are used for this purpose.

* **Client-Side Implementation:**
  
  1. After encrypting the *entire* file, the client should split the resulting ciphertext into manageable chunks (e.g., 1024 bytes each).
  2. The client then sends a sequence of `1028` messages, one for each chunk.
  3. The `total packets` field must be the same value in all messages for this sequence.
  4. The `Packet number` field must be incremented for each chunk, starting from 1 (e.g., 1 of N, 2 of N, ... N of N).

* **Server-Side Implementation:**
  
  1. The server must identify chunks belonging to the same file transfer (e.g., using a key of `Client ID` + `File Name`).
  2. It should buffer the received `Message Content` from each chunk in memory or a temporary file.
  3. The server must use the `Packet number` to reassemble the chunks in the correct order.
  4. Only after receiving the final chunk (where `Packet number == total packets`) should the server reassemble the full ciphertext, decrypt the file, and proceed with the checksum verification.

---

### 6. Extra Feature: Server Persistence with SQLite

This is an optional extension to make the server stateful across restarts.

* **Database File:** `defensive.db`

* **Table `clients` Schema:**
  
  | Column Name | Type            | Notes                               |
  | ----------- | --------------- | ----------------------------------- |
  | `ID`        | 16 bytes (UUID) | Primary Key, Index                  |
  | `Name`      | 255 chars       | User's name                         |
  | `PublicKey` | 160 bytes       | The client's public key             |
  | `LastSeen`  | Datetime        | Timestamp of the last request       |
  | `AESKey`    | 256 bits        | The last AES key sent to the client |

* **Table `files` Schema:**
  
  | Column Name | Type            | Notes                                                 |
  | ----------- | --------------- | ----------------------------------------------------- |
  | `ID`        | 16 bytes (UUID) | Foreign Key to `clients.ID`                           |
  | `FileName`  | 255 chars       | Original name of the uploaded file                    |
  | `PathName`  | 255 chars       | Path where the file is stored on the server           |
  | `Verified`  | Boolean         | True if the file's checksum was successfully verified |

***

### 
