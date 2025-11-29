# Data Flow & Protocol Specification

> Binary protocol v3 - Little-endian throughout

## Protocol Overview

```
+------------------------------------------------------------------+
|                      BINARY PROTOCOL v3                          |
+------------------------------------------------------------------+
| Transport: TCP/IP          | Port: 1256 (default)                |
| Byte Order: Little-Endian  | Header Size: 23 bytes (request)     |
|                            |              7 bytes (response)      |
+------------------------------------------------------------------+
```

## Packet Structures

### Request Header (23 bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                         Client ID                             +
|                       (16 bytes UUID)                         |
+                                                               +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Version     |          Code             |                   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                   +
|                      Payload Size                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

Offset  Size    Field           Description
------  ----    -----           -----------
0       16      client_id       UUID bytes (all zeros for registration)
16      1       version         Protocol version (3)
17      2       code            Request code (little-endian)
19      4       payload_size    Payload length (little-endian)
```

### Response Header (7 bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Version     |          Code             |                   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                   +
|                      Payload Size                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

Offset  Size    Field           Description
------  ----    -----           -----------
0       1       version         Server version (3)
1       2       code            Response code (little-endian)
3       4       payload_size    Payload length (little-endian)
```

## Request & Response Codes

### Request Codes (Client -> Server)

| Code | Name | Description |
|------|------|-------------|
| 1025 | `REQ_REGISTER` | New client registration |
| 1026 | `REQ_SEND_PUBLIC_KEY` | Send RSA public key |
| 1027 | `REQ_RECONNECT` | Reconnect existing client |
| 1028 | `REQ_SEND_FILE` | Transfer encrypted file |
| 1029 | `REQ_CRC_OK` | CRC verification passed |
| 1030 | `REQ_CRC_RETRY` | CRC failed, retry transfer |
| 1031 | `REQ_CRC_ABORT` | CRC failed, abort transfer |

### Response Codes (Server -> Client)

| Code | Name | Description |
|------|------|-------------|
| 1600 | `RESP_REGISTER_OK` | Registration successful |
| 1601 | `RESP_REGISTER_FAIL` | Registration failed |
| 1602 | `RESP_PUBKEY_AES_SENT` | AES key sent (encrypted) |
| 1603 | `RESP_FILE_CRC` | File received + CRC |
| 1604 | `RESP_ACK` | Acknowledgment |
| 1605 | `RESP_RECONNECT_AES_SENT` | Reconnect + AES key |
| 1606 | `RESP_RECONNECT_FAIL` | Reconnect failed |
| 1607 | `RESP_ERROR` | Generic server error |

## Complete Session Flow

```
    CLIENT                                              SERVER
      |                                                    |
      |  [1] REQ_REGISTER (1025)                          |
      |  +-- Username (255 bytes, null-padded)            |
      |--------------------------------------------------->|
      |                                                    |
      |  [2] RESP_REGISTER_OK (1600)                      |
      |  +-- Client UUID (16 bytes)                       |
      |<---------------------------------------------------|
      |                                                    |
      |  [3] REQ_SEND_PUBLIC_KEY (1026)                   |
      |  +-- Username (255 bytes)                         |
      |  +-- RSA Public Key (162 bytes DER)               |
      |--------------------------------------------------->|
      |                                                    |
      |                    +------------------------------+|
      |                    | Server generates AES-256 key ||
      |                    | Encrypts with client's RSA   ||
      |                    +------------------------------+|
      |                                                    |
      |  [4] RESP_PUBKEY_AES_SENT (1602)                  |
      |  +-- Client UUID (16 bytes)                       |
      |  +-- Encrypted AES Key (RSA-OAEP)                 |
      |<---------------------------------------------------|
      |                                                    |
      | +-------------------------------+                  |
      | | Client decrypts AES key       |                  |
      | | with RSA private key          |                  |
      | +-------------------------------+                  |
      |                                                    |
      |  [5] REQ_SEND_FILE (1028)                         |
      |  +-- Content Size (4 bytes)                       |
      |  +-- Original Size (4 bytes)                      |
      |  +-- Packet Number (2 bytes)                      |
      |  +-- Total Packets (2 bytes)                      |
      |  +-- Filename (255 bytes)                         |
      |  +-- Encrypted File Data (AES-256-CBC)            |
      |--------------------------------------------------->|
      |                                                    |
      |                    +------------------------------+|
      |                    | Server decrypts file         ||
      |                    | Calculates CRC-32            ||
      |                    | Stores in filesystem         ||
      |                    +------------------------------+|
      |                                                    |
      |  [6] RESP_FILE_CRC (1603)                         |
      |  +-- Client UUID (16 bytes)                       |
      |  +-- Content Size (4 bytes)                       |
      |  +-- Filename (255 bytes)                         |
      |  +-- CRC Checksum (4 bytes)                       |
      |<---------------------------------------------------|
      |                                                    |
      | +-------------------------------+                  |
      | | Client verifies CRC matches   |                  |
      | +-------------------------------+                  |
      |                                                    |
      |  [7] REQ_CRC_OK (1029)                            |
      |  +-- Filename (255 bytes)                         |
      |--------------------------------------------------->|
      |                                                    |
      |  [8] RESP_ACK (1604)                              |
      |  +-- Client UUID (16 bytes)                       |
      |<---------------------------------------------------|
      |                                                    |
```

## Reconnection Flow

```
    CLIENT                                              SERVER
      |                                                    |
      | +-------------------------------+                  |
      | | Client has stored:            |                  |
      | | - UUID (me.info)              |                  |
      | | - RSA Private Key (priv.key)  |                  |
      | +-------------------------------+                  |
      |                                                    |
      |  [1] REQ_RECONNECT (1027)                         |
      |  +-- Username (255 bytes)                         |
      |--------------------------------------------------->|
      |                                                    |
      |                    +------------------------------+|
      |                    | Server finds client by UUID  ||
      |                    | Retrieves stored public key  ||
      |                    | Generates new AES key        ||
      |                    +------------------------------+|
      |                                                    |
      |  [2] RESP_RECONNECT_AES_SENT (1605)               |
      |  +-- Client UUID (16 bytes)                       |
      |  +-- Encrypted AES Key                            |
      |<---------------------------------------------------|
      |                                                    |
      |  [continue with file transfer...]                  |
      |                                                    |
```

## Encryption Flow

```
                    KEY EXCHANGE (RSA-1024)
+------------------------------------------------------------------+
|                                                                  |
|   CLIENT                                SERVER                   |
|   +------------------+                  +------------------+     |
|   | Generate         |                  |                  |     |
|   | RSA Keypair      |                  |                  |     |
|   | (1024-bit)       |                  |                  |     |
|   +--------+---------+                  |                  |     |
|            |                            |                  |     |
|            | Public Key (162 bytes DER) |                  |     |
|            +--------------------------->| Store key        |     |
|            |                            | Generate AES-256 |     |
|            |                            +--------+---------+     |
|            |                                     |               |
|            |    Encrypted AES Key (RSA-OAEP)     |               |
|            |<------------------------------------+               |
|            |                                                     |
|   +--------+---------+                                           |
|   | Decrypt AES key  |                                           |
|   | with Private Key |                                           |
|   +------------------+                                           |
|                                                                  |
+------------------------------------------------------------------+

                    FILE ENCRYPTION (AES-256-CBC)
+------------------------------------------------------------------+
|                                                                  |
|   PLAINTEXT FILE                                                 |
|   +----------------------------------------------------------+   |
|   | Original file content (any size)                         |   |
|   +----------------------------------------------------------+   |
|                              |                                   |
|                              v                                   |
|   +----------------------------------------------------------+   |
|   | PKCS7 Padding (to 16-byte boundary)                      |   |
|   +----------------------------------------------------------+   |
|                              |                                   |
|                              v                                   |
|   +----------------------------------------------------------+   |
|   | AES-256-CBC Encryption                                   |   |
|   | Key: 32 bytes (from server)                              |   |
|   | IV: 16 bytes (static zero IV)                            |   |
|   +----------------------------------------------------------+   |
|                              |                                   |
|                              v                                   |
|   CIPHERTEXT                                                     |
|   +----------------------------------------------------------+   |
|   | Encrypted content (multiple of 16 bytes)                 |   |
|   +----------------------------------------------------------+   |
|                                                                  |
+------------------------------------------------------------------+
```

## CRC Verification Flow

```
    CLIENT                                              SERVER
      |                                                    |
      |            Encrypted File                          |
      |--------------------------------------------------->|
      |                                                    |
      |                    +------------------------------+|
      |                    | Decrypt with AES-256-CBC     ||
      |                    | Remove PKCS7 padding         ||
      |                    | Calculate CRC-32             ||
      |                    +------------------------------+|
      |                                                    |
      |         RESP_FILE_CRC + Server CRC                 |
      |<---------------------------------------------------|
      |                                                    |
      | +------------------------------+                   |
      | | Calculate local CRC-32       |                   |
      | | Compare with server CRC      |                   |
      | +------------------------------+                   |
      |                                                    |
      |     if CRC matches:                                |
      |         REQ_CRC_OK (1029)                          |
      |     else if retries < 3:                           |
      |         REQ_CRC_RETRY (1030)                       |
      |     else:                                          |
      |         REQ_CRC_ABORT (1031)                       |
      |--------------------------------------------------->|
      |                                                    |

CRC-32 Algorithm: Linux 'cksum' compatible
- Polynomial: 0x04C11DB7 (reflected)
- Initial value: 0xFFFFFFFF
- Final XOR: 0xFFFFFFFF
- Includes file length in calculation
```

## Payload Structures

### Registration Request (1025)

```
+----------------------------------+
| Username (255 bytes, null-padded)|
+----------------------------------+
```

### Public Key Request (1026)

```
+----------------------------------+
| Username (255 bytes, null-padded)|
+----------------------------------+
| RSA Public Key (162 bytes DER)   |
+----------------------------------+
```

### File Transfer Request (1028)

```
+----------------------------------+
| Content Size (4 bytes, LE)       |  <-- Encrypted size
+----------------------------------+
| Original Size (4 bytes, LE)      |  <-- Plaintext size
+----------------------------------+
| Packet Number (2 bytes, LE)      |
+----------------------------------+
| Total Packets (2 bytes, LE)      |
+----------------------------------+
| Filename (255 bytes, null-padded)|
+----------------------------------+
| Encrypted File Data (variable)   |
+----------------------------------+
```

### File CRC Response (1603)

```
+----------------------------------+
| Client UUID (16 bytes)           |
+----------------------------------+
| Content Size (4 bytes, LE)       |
+----------------------------------+
| Filename (255 bytes, null-padded)|
+----------------------------------+
| CRC Checksum (4 bytes, LE)       |
+----------------------------------+
```

## State Machine

```
                    +-------------+
                    |    INIT     |
                    +------+------+
                           |
              +------------+------------+
              |                         |
              v                         v
     +--------+--------+       +--------+--------+
     |   REGISTERING   |       |  RECONNECTING   |
     +--------+--------+       +--------+--------+
              |                         |
              v                         |
     +--------+--------+                |
     |  KEY_EXCHANGE   |                |
     +--------+--------+                |
              |                         |
              +------------+------------+
                           |
                           v
                  +--------+--------+
                  |    CONNECTED    |
                  +--------+--------+
                           |
                           v
                  +--------+--------+
                  |  TRANSFERRING   |<----+
                  +--------+--------+     |
                           |              |
                           v              |
                  +--------+--------+     |
                  |  CRC_VERIFYING  |-----+ (retry)
                  +--------+--------+
                           |
              +------------+------------+
              |                         |
              v                         v
     +--------+--------+       +--------+--------+
     |    COMPLETE     |       |    ABORTED      |
     +-----------------+       +-----------------+
```

## Error Handling

| Error Condition | Client Action | Server Response |
|-----------------|---------------|-----------------|
| Invalid UUID | Re-register | `RESP_RECONNECT_FAIL` (1606) |
| Username exists | Notify user | `RESP_REGISTER_FAIL` (1601) |
| Invalid public key | Retry key exchange | `RESP_ERROR` (1607) |
| Decryption failure | Log error | `RESP_ERROR` (1607) |
| CRC mismatch | Retry (max 3) | N/A |
| Connection timeout | Reconnect | Close socket |
