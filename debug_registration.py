#!/usr/bin/env python3
"""
Debug registration issue by capturing server logs during registration attempt
"""

import socket
import struct
import subprocess
import sys
import time
import threading

def test_registration_with_logging():
    """Test registration while capturing server logs"""
    
    # Start server with output capture
    print("Starting server with log capture...")
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd="server",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1  # Line buffered
    )
    
    # Function to read server output
    server_output = []
    def read_server_output():
        try:
            for line in server_process.stdout:
                server_output.append(line.strip())
                print(f"SERVER: {line.strip()}")
                if "Server is now listening" in line:
                    break
        except:
            pass
    
    # Start output reader thread
    output_thread = threading.Thread(target=read_server_output, daemon=True)
    output_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    # Check if server is running
    if server_process.poll() is not None:
        print("Server failed to start!")
        stdout, stderr = server_process.communicate()
        print(f"Server output: {stdout}")
        return False
    
    print("\nAttempting registration...")
    
    try:
        # Connect and send registration
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect(('127.0.0.1', 1256))
        print("Connected to server")
        
        # Create registration payload (255 bytes with client name)
        client_name = "testuser"
        payload = bytearray(255)  # 255 bytes total
        name_bytes = client_name.encode('utf-8')
        payload[:len(name_bytes)] = name_bytes
        # payload is already zero-padded by initialization
        
        # Create registration header
        header = bytearray()
        header.extend(b'\x00' * 16)  # client_id (all zeros)
        header.append(3)  # version
        header.extend(struct.pack('<H', 1025))  # REQ_REGISTER
        header.extend(struct.pack('<I', len(payload)))  # payload_size
        
        print(f"Sending registration header: {header.hex()}")
        sock.send(header)
        
        print(f"Sending registration payload (255 bytes): {payload[:20].hex()}... (truncated)")
        sock.send(payload)
        
        # Receive response
        response = sock.recv(7)
        if len(response) == 7:
            version, code, payload_size = struct.unpack('<BHI', response)
            print(f"Received response: version={version}, code={code}, payload_size={payload_size}")
            
            # Map response codes
            response_names = {
                1600: "RESP_REGISTER_SUCCESS",
                1603: "RESP_GENERIC_SERVER_ERROR", 
                1607: "RESP_GENERIC_SERVER_ERROR_ALT"
            }
            response_name = response_names.get(code, f"UNKNOWN_CODE_{code}")
            print(f"Response meaning: {response_name}")
            
        else:
            print(f"Invalid response length: {len(response)}")
            
        sock.close()
        
    except Exception as e:
        print(f"Registration test failed: {e}")
    
    # Give server time to log the request processing
    time.sleep(1)
    
    # Continue reading any remaining server output
    try:
        # Read a few more lines
        for _ in range(10):
            line = server_process.stdout.readline()
            if line:
                server_output.append(line.strip())
                print(f"SERVER: {line.strip()}")
            else:
                break
    except:
        pass
    
    # Stop server
    print("\nStopping server...")
    try:
        server_process.terminate()
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
        server_process.wait()
    
    print("\nComplete server output:")
    print("-" * 50)
    for line in server_output:
        print(line)
    print("-" * 50)
    
    return True

if __name__ == "__main__":
    test_registration_with_logging()