#!/usr/bin/env python3
"""
Minimal Backup Server for Testing
Just accepts connections and processes basic requests to test the 66KB issue
"""

import socket
import struct
import threading


def handle_client(client_socket, client_address):
    """Handle a client connection"""
    print(f"Client connected: {client_address}")

    try:
        client_socket.settimeout(60.0)

        while True:
            try:
                # Read 23-byte header
                header_data = b''
                while len(header_data) < 23:
                    chunk = client_socket.recv(23 - len(header_data))
                    if not chunk:
                        print(f"Client {client_address} disconnected")
                        return
                    header_data += chunk

                # Parse header
                client_id = header_data[:16]
                version = header_data[16]
                code = struct.unpack('<H', header_data[17:19])[0]
                payload_size = struct.unpack('<I', header_data[19:23])[0]

                print(f"Request from {client_address}: Version={version}, Code={code}, PayloadSize={payload_size}")

                # Read payload if any
                payload = b''
                if payload_size > 0:
                    while len(payload) < payload_size:
                        chunk = client_socket.recv(min(4096, payload_size - len(payload)))
                        if not chunk:
                            print(f"Client {client_address} disconnected during payload")
                            return
                        payload += chunk

                print(f"Received {len(payload)} bytes payload from {client_address}")

                # Send a simple response based on request code
                if code == 1025:  # REQ_REGISTER
                    # Registration response
                    response_code = 1600  # RESP_REG_OK
                    response_payload = b'1234567890123456'  # 16-byte client ID
                elif code == 1027:  # REQ_RECONNECT
                    # Reconnection response
                    response_code = 1605  # RESP_RECONNECT_AES_SENT
                    response_payload = b'1234567890123456' + b'A' * 32  # Client ID + AES key
                elif code == 1028:  # REQ_SEND_FILE
                    # File transfer response
                    response_code = 1603  # RESP_FILE_CRC
                    response_payload = b'A' * 279  # Dummy response
                else:
                    # Generic response
                    response_code = 1604  # RESP_ACK
                    response_payload = b''

                # Construct response: version(1) + code(2) + payload_size(4) + payload
                response_header = struct.pack('<BHI', 3, response_code, len(response_payload))
                response = response_header + response_payload

                client_socket.send(response)
                print(f"Sent response to {client_address}: Code={response_code}, PayloadSize={len(response_payload)}")

                # For file transfers, break after response
                if code == 1028:
                    print(f"File transfer completed for {client_address}")
                    break

            except TimeoutError:
                print(f"Timeout for client {client_address}")
                break
            except Exception as e:
                print(f"Error handling client {client_address}: {e}")
                break

    except Exception as e:
        print(f"Connection error with {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"Client {client_address} connection closed")

def main():
    """Start the minimal backup server"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind(('127.0.0.1', 1256))
        server_socket.listen(5)
        print("Minimal Backup Server started on port 1256")
        print("Press Ctrl+C to stop")

        while True:
            try:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Accept error: {e}")

    except Exception as e:
        print(f"Server error: {e}")
        return 1
    finally:
        server_socket.close()
        print("Server stopped")

    return 0

if __name__ == "__main__":  # pragma: no cover - manual run helper
    main()
