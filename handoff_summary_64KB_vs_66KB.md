# Handoff Summary: 64KB vs 66KB Transfer Failure

## Objective
Provide a compact, actionable summary of the 66KB transfer failure (web GUI → Flask API → C++ client → Python server) that does not occur at 64KB, preserving critical technical details and recent investigation results.

## System snapshot
- Path: Web UI → Flask API (9090) → EncryptedBackupClient.exe (subprocess, --batch) → Python backup server (1256)
- C++ client: RSA key exchange, AES-256-CBC (static zero IV), CRC32 (cksum-compatible). Packets sized around 64KB.
- Server: Custom TCP protocol v3. Reassembles multi-packet transfers then decrypts once, computes CRC, responds.

## Wire protocol (active path)
- Request header (23 bytes): client_id[16] + version[1] + code[2] + payload_size[4] (little-endian)
- File payload per REQ_SEND_FILE (1028):
  - encrypted_size[4] + original_size[4] + packet_number[2] + total_packets[2] + filename[255] + encrypted_content
- Server response (7 bytes + payload): version[1] + code[2] + payload_size[4]; file CRC response payload = client_id[16] + encrypted_size[4] + filename[255] + crc32[4]

## Observed behavior
- 64KB file: succeeds (single packet: total_packets=1)
- 66KB file: fails (multi-packet path, e.g., 64KB + ~2KB)
- Tests indicating boundary issue:
  - test_64kb_vs_66kb.py → expects 64KB ok, 66KB fail
  - test_66kb_debug.py → sizes 60/64/66/70KB; multi-packet cases fail
- Integration runs via GUI and scripts align with above.

## Recent inspections (files and key findings)
- Server core
  - src/server/network_server.py: Parses 23B header; reads exact payload_size; dispatches without per-packet ack.
  - src/server/file_transfer.py (FileTransferManager):
    - Parses per-packet metadata; enforces content length == encrypted_size per packet
    - Reassembles by (client, filename); on completion: concat → single decrypt → size check → CRC → RESP_FILE_CRC
  - src/server/request_handlers.py: Delegates REQ_SEND_FILE to FileTransferManager; only responds after completion
  - src/server/protocol.py: Response pack format <BHI> used by network_server
- Client core
  - src/client/client.cpp:
    - transferFileWithBuffer(): reads whole file, encrypts whole file once, splits encryptedData into fixed-size buffers (≈64KB), sends REQ_SEND_FILE for each chunk, then awaits single RESP_FILE_CRC
    - sendRequest(): writes header then payload in socket chunks (≤16–32KB); framing preserved by payload_size
  - include/client/client.h: OPTIMAL_BUFFER_SIZE = 64KB; 16-bit packet_number/total_packets
  - AESWrapper: AES-256-CBC with static zero IV; PKCS7 padding

## Working hypothesis (why 64KB works but 66KB fails)
- Single-packet path (64KB) succeeds consistently, confirming: header parse, AES/CRC alignment, filename handling, and RESP_FILE_CRC flow are correct when total_packets = 1.
- Multi-packet path (66KB+) likely fails at one of these points:
  1) Reassembly boundary bug: packet_number/total_packets handling, ordering, or missing chunk detection causes incomplete assembly
  2) Per-packet content length vs encrypted_size mismatch on non-final packet
  3) Filename field handling across packets (255-byte padded field duplicated per packet); state keyed by filename could collide or overwrite
  4) Off-by-one or endianness issue in 16-bit packet_number/total_packets when total_packets > 1
  5) Client-side segmentation of encryptedData vs server’s expectation (e.g., slicing not aligned with encrypted_size metadata)

Note: Socket chunking (16–32KB) is below the application framing and should not affect parsing, as the server reads exact payload_size. Header format mismatch is unlikely (would break 64KB too).

## What to instrument next (minimal, high-signal)
Add targeted DEBUG logs in server’s multi-packet path to confirm the exact failure point:
- In FileTransferManager.handle_send_file():
  - Log packet_number/total_packets, encrypted_size, actual len(encrypted_content), filename (trimmed), and client_id prefix (first 4 bytes hex)
  - On storing chunk: log stored range and total received size for filename
  - On completion: log reassembled total encrypted length, decrypt result length, and whether original_size validation passes
- Emit a single-line summary per file transfer outcome with reason code (OK, BAD_CONTENT_LEN, MISSING_CHUNK, DECRYPT_FAIL, SIZE_MISMATCH)

These logs will pinpoint whether the second packet is rejected early (content size mismatch), lost (reassembly never completes), or fails post-decrypt (size mismatch).

## Reproduction path (no commands; scripts to use)
- Start Python backup server (server/server.py) and Flask API (cyberbackup_api_server.py) or use launch_gui.py
- Use test_66kb_debug.py to generate and attempt transfers for 60/64/66/70KB
- Observe server.log and client_debug.log during the 66KB attempt

## Edge cases to consider
- total_packets just above 1 (2–4) with small final fragments (1–4096 bytes)
- Filenames at or near 255 bytes, unicode paths, and identical filename across successive transfers
- Large files where total_packets exceeds 65535 (if 16-bit field is used unguarded)
- Concurrent transfers from the same client_id and filename

## Likely fixes (after confirming logs)
- If per-packet metadata/content mismatch: ensure encrypted_size is the slice length for that packet, not the whole-file length; verify both client and server interpret it identically
- If filename-based key collisions: include packet stream ID (e.g., client_id + filename + session nonce) in server’s partial_files map
- If packet_number handling is off-by-one: normalize to 0- or 1-based consistently on both ends and assert ranges early
- If decrypt occurs too early or multiple times: ensure decrypt happens only after full reassembly and with exact concatenation order

## References
- Tests: test_64kb_vs_66kb.py, test_66kb_debug.py
- Orchestration: launch_gui.py, one_click_build_and_run.py
- Server: src/server/network_server.py, src/server/file_transfer.py, src/server/request_handlers.py, src/server/protocol.py
- Client: src/client/client.cpp, include/client/client.h, src/wrappers/AESWrapper.cpp

## Status
- 64KB (single packet): PASS
- 66KB (multi-packet): FAIL (root cause under investigation; high suspicion on multi-packet reassembly/metadata)

## Next steps (proposed)
1) Add the server-side logging described above and rerun test_66kb_debug.py to capture failure locus
2) If the second packet is dropped/rejected, align encrypted_size semantics and packet slicing between client and server
3) Add a focused unit/integration test for a two-packet file (e.g., 66KB) exercising the multi-packet path end-to-end
4) After fix, verify end-to-end via GUI and confirm file presence and SHA256 match in server/received_files/

---
Requirements coverage: Provide a compact but thorough handoff summary with critical technical details, recent inspections, observed outputs, and relation to the 64KB vs 66KB bug → Done.
