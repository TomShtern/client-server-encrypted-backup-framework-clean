#!/usr/bin/env python3
# Debug script to test client-server communication step by step

import socket
import struct


def test_raw_connection():
    # Test a raw connection to the server to see what happens
    print("=== Raw Connection Test ===")

    try:
        # Connect to server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10 second timeout
        print("Connecting to 127.0.0.1:1256...")
        sock.connect(('127.0.0.1', 1256))
        print("[OK] Connected to server")

        # Send a simple registration request
        # Header: client_id (16 bytes all zeros), version (1 byte), code (2 bytes), payload_size (4 bytes)
        # Payload: username (255 bytes)

        client_id = b'\x00' * 16  # All zeros for registration
        version = 3  # Client version
        code = 1025  # REQ_REGISTER
        username = b"debug_test_user" + b'\x00' * (255 - len(b"debug_test_user"))  # Padded to 255 bytes
        payload_size = len(username)

        # Pack header with little-endian format (as expected by server)
        header = client_id + struct.pack('<BHI', version, code, payload_size)

        print("Sending registration request:")
        print(f"  Client ID: {client_id.hex()}")
        print(f"  Version: {version}")
        print(f"  Code: {code}")
        print(f"  Payload size: {payload_size}")

        # Send header
        sock.sendall(header)
        print("[OK] Header sent")

        # Send payload
        sock.sendall(username)
        print("[OK] Payload sent")

        # Try to receive response
        print("Waiting for server response...")
        try:
            # Try to read response header (7 bytes: version(1) + code(2) + payload_size(4))
            response_header = sock.recv(7)
            if len(response_header) == 7:
                resp_version, resp_code, resp_payload_size = struct.unpack('<BHI', response_header)
                print("Received response header:")
                print(f"  Version: {resp_version}")
                print(f"  Code: {resp_code}")
                print(f"  Payload size: {resp_payload_size}")

                # Try to read payload if any
                if resp_payload_size > 0:
                    payload = sock.recv(resp_payload_size)
                    print(f"Received payload ({len(payload)} bytes): {payload.hex()}")
                else:
                    print("No payload in response")
            else:
                print(f"Received incomplete header: {response_header.hex()}")
        except TimeoutError:
            print("[ERROR] Timeout waiting for server response")
        except Exception as e:
            print(f"[ERROR] Failed to receive response: {e}")

    except Exception as e:
        print(f"[ERROR] Connection test failed: {e}")
    finally:
        try:
            sock.close()
        except:
            pass

def check_transfer_info():
    # Check the transfer.info file content
    print("\n=== Transfer Info Check ===")
    try:
        with open("transfer.info", encoding='utf-8') as f:
            content = f.read()
            print("transfer.info content:")
            print(content)
    except Exception as e:
        print(f"[ERROR] Failed to read transfer.info: {e}")

def check_client_executable():
    # Check if the client executable exists
    print("\n=== Client Executable Check ===")
    import os
    client_path = "build/Release/EncryptedBackupClient.exe"
    if os.path.exists(client_path):
        print(f"[OK] Client executable found: {client_path}")
        # Get file size
        size = os.path.getsize(client_path)
        print(f"  File size: {size} bytes")
    else:
        print(f"[ERROR] Client executable not found: {client_path}")

def main():
    print("Debugging Client-Server Communication")
    print("====================================")

    check_transfer_info()
    check_client_executable()
    test_raw_connection()

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
