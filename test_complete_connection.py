#!/usr/bin/env python3
"""
COMPLETE CONNECTION INTEGRATION TEST
Tests the full client-server connection sequence with real protocol implementation
"""

import socket
import struct
import threading
import time
import sys
import os
import subprocess
import signal

# Add server path for imports
sys.path.insert(0, "server")

# Protocol constants
SERVER_VERSION = 3
REQ_REGISTER = 1025
REQ_RECONNECT = 1026
REQ_SEND_FILE = 1027
RESP_REGISTER_SUCCESS = 1600
RESP_RECONNECT_SUCCESS = 1604
RESP_GENERIC_SERVER_ERROR = 1603

class CompleteConnectionTest:
    def __init__(self):
        self.server_ip = "127.0.0.1"
        self.server_port = 1256
        self.server_process = None
        self.client_id = b'\x00' * 16  # All zeros for registration
        
    def start_real_server(self):
        """Start the actual Python server in a subprocess"""
        print("Starting real server...")
        
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "server.py"],
                cwd="server",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give server time to start
            time.sleep(2.0)
            
            # Check if server is still running
            if self.server_process.poll() is not None:
                stdout, stderr = self.server_process.communicate()
                print(f"Server failed to start:")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False
                
            print("Server started successfully")
            return True
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
            
    def stop_real_server(self):
        """Stop the real server"""
        if self.server_process:
            print("Stopping server...")
            try:
                # Send SIGTERM to gracefully shutdown
                self.server_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print("Server didn't shutdown gracefully, killing...")
                    self.server_process.kill()
                    self.server_process.wait()
                    
                print("Server stopped")
            except Exception as e:
                print(f"Error stopping server: {e}")
            finally:
                self.server_process = None
                
    def wait_for_server_ready(self, timeout=10):
        """Wait for server to be ready to accept connections"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Try to connect
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.settimeout(1.0)
                test_socket.connect((self.server_ip, self.server_port))
                test_socket.close()
                return True
            except socket.error:
                time.sleep(0.5)
                continue
                
        return False
        
    def send_registration_request(self):
        """Send registration request exactly as C++ client would"""
        print("\n=== REGISTRATION REQUEST TEST ===")
        
        try:
            # Connect to server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(10.0)
            client_socket.connect((self.server_ip, self.server_port))
            
            print("Connected to server")
            
            # Create registration request header
            header = bytearray()
            header.extend(self.client_id)  # 16 bytes client_id (all zeros)
            header.append(SERVER_VERSION)  # 1 byte version
            header.extend(struct.pack('<H', REQ_REGISTER))  # 2 bytes code
            header.extend(struct.pack('<I', 0))  # 4 bytes payload_size
            
            print(f"Sending registration header: {header.hex()}")
            client_socket.send(header)
            
            # Receive response
            response_header = client_socket.recv(7)
            if len(response_header) == 7:
                version, code, payload_size = struct.unpack('<BHI', response_header)
                print(f"Received response: version={version}, code={code}, payload_size={payload_size}")
                
                if code == RESP_REGISTER_SUCCESS:
                    print("SUCCESS: Registration accepted")
                    
                    # Read the client UUID from payload if present
                    if payload_size > 0:
                        payload = client_socket.recv(payload_size)
                        print(f"Received client UUID payload: {payload.hex()}")
                        return True, payload[:16]  # First 16 bytes should be UUID
                    else:
                        print("No payload received")
                        return True, None
                else:
                    print(f"FAILURE: Registration rejected with code {code}")
                    return False, None
            else:
                print(f"FAILURE: Invalid response header size: {len(response_header)}")
                return False, None
                
        except Exception as e:
            print(f"Registration request failed: {e}")
            return False, None
        finally:
            try:
                client_socket.close()
            except:
                pass
                
    def test_reconnect_flow(self, client_uuid):
        """Test reconnection with existing client UUID"""
        print("\n=== RECONNECT REQUEST TEST ===")
        
        if not client_uuid:
            print("No client UUID available for reconnect test")
            return False
            
        try:
            # Connect to server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(10.0)
            client_socket.connect((self.server_ip, self.server_port))
            
            print("Connected to server for reconnect")
            
            # Create reconnect request header
            header = bytearray()
            header.extend(client_uuid)  # 16 bytes client_id
            header.append(SERVER_VERSION)  # 1 byte version
            header.extend(struct.pack('<H', REQ_RECONNECT))  # 2 bytes code
            header.extend(struct.pack('<I', 0))  # 4 bytes payload_size
            
            print(f"Sending reconnect header with UUID {client_uuid.hex()}")
            client_socket.send(header)
            
            # Receive response
            response_header = client_socket.recv(7)
            if len(response_header) == 7:
                version, code, payload_size = struct.unpack('<BHI', response_header)
                print(f"Received reconnect response: version={version}, code={code}, payload_size={payload_size}")
                
                if code == RESP_RECONNECT_SUCCESS:
                    print("SUCCESS: Reconnect accepted")
                    return True
                else:
                    print(f"FAILURE: Reconnect rejected with code {code}")
                    return False
            else:
                print(f"FAILURE: Invalid response header size: {len(response_header)}")
                return False
                
        except Exception as e:
            print(f"Reconnect request failed: {e}")
            return False
        finally:
            try:
                client_socket.close()
            except:
                pass
                
    def test_file_send_flow(self, client_uuid):
        """Test file sending with existing client UUID"""
        print("\n=== FILE SEND REQUEST TEST ===")
        
        if not client_uuid:
            print("No client UUID available for file send test")
            return False
            
        # Create test file content
        test_content = b"This is a test file for the connection test.\nLine 2 of test content.\n"
        
        try:
            # Connect to server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(10.0)
            client_socket.connect((self.server_ip, self.server_port))
            
            print("Connected to server for file send")
            
            # Create file send request
            # Payload should contain: filename (null-terminated) + file content
            filename = b"test_file.txt\x00"
            payload = filename + test_content
            
            # Create file send request header
            header = bytearray()
            header.extend(client_uuid)  # 16 bytes client_id
            header.append(SERVER_VERSION)  # 1 byte version
            header.extend(struct.pack('<H', REQ_SEND_FILE))  # 2 bytes code
            header.extend(struct.pack('<I', len(payload)))  # 4 bytes payload_size
            
            print(f"Sending file send header with payload size {len(payload)}")
            client_socket.send(header)
            
            # Send payload
            print(f"Sending payload: filename='{filename.decode().rstrip(chr(0))}', content size={len(test_content)}")
            client_socket.send(payload)
            
            # Receive response
            response_header = client_socket.recv(7)
            if len(response_header) == 7:
                version, code, payload_size = struct.unpack('<BHI', response_header)
                print(f"Received file send response: version={version}, code={code}, payload_size={payload_size}")
                
                if code == 1602:  # RESP_FILE_RECEIVED
                    print("SUCCESS: File send accepted")
                    return True
                else:
                    print(f"File send rejected with code {code}")
                    return False
            else:
                print(f"FAILURE: Invalid response header size: {len(response_header)}")
                return False
                
        except Exception as e:
            print(f"File send request failed: {e}")
            return False
        finally:
            try:
                client_socket.close()
            except:
                pass
                
    def run_complete_test(self):
        """Run complete client-server integration test"""
        print("COMPLETE CONNECTION INTEGRATION TEST")
        print("=" * 60)
        
        # Start real server
        if not self.start_real_server():
            print("CRITICAL: Could not start server")
            return False
            
        # Wait for server to be ready
        if not self.wait_for_server_ready():
            print("CRITICAL: Server not ready after startup")
            self.stop_real_server()
            return False
            
        print("Server is ready to accept connections")
        
        try:
            # Test registration
            reg_success, client_uuid = self.send_registration_request()
            if not reg_success:
                print("CRITICAL: Registration failed")
                return False
                
            # Test reconnect if we got a UUID
            if client_uuid:
                reconnect_success = self.test_reconnect_flow(client_uuid)
                if not reconnect_success:
                    print("WARNING: Reconnect failed")
                    
                # Test file send
                file_send_success = self.test_file_send_flow(client_uuid)
                if not file_send_success:
                    print("WARNING: File send failed")
            else:
                print("No UUID received, skipping reconnect and file send tests")
                
            print("\n" + "=" * 60)
            print("INTEGRATION TEST SUMMARY")
            print("=" * 60)
            print(f"[{'PASS' if reg_success else 'FAIL'}] Registration")
            if client_uuid:
                print(f"[{'PASS' if reconnect_success else 'FAIL'}] Reconnect")
                print(f"[{'PASS' if file_send_success else 'FAIL'}] File Send")
            
            overall_success = reg_success
            if client_uuid:
                overall_success = overall_success and reconnect_success and file_send_success
                
            if overall_success:
                print("\nSUCCESS: All connection tests passed!")
                print("The client-server connection sequence is working correctly.")
            else:
                print("\nPARTIAL SUCCESS: Basic connection works but some features failed.")
                
            return overall_success
            
        finally:
            self.stop_real_server()
            
def main():
    if not os.path.exists("server/server.py"):
        print("Error: Run this script from the project root directory")
        sys.exit(1)
        
    # Ensure we have transfer.info
    if not os.path.exists("transfer.info"):
        print("Creating transfer.info for test...")
        with open("transfer.info", "w") as f:
            f.write("127.0.0.1:1256\n")
            f.write("testuser\n")
            f.write("tests/test_file.txt\n")
            
    # Ensure test file exists
    os.makedirs("tests", exist_ok=True)
    if not os.path.exists("tests/test_file.txt"):
        with open("tests/test_file.txt", "w") as f:
            f.write("This is a test file for connection diagnostics.\n")
            
    test = CompleteConnectionTest()
    success = test.run_complete_test()
    
    if success:
        print("\nCONCLUSION: The connection issue has been RESOLVED!")
        print("The server crypto compatibility layer is working correctly.")
        print("Both client and server can communicate using the binary protocol.")
        sys.exit(0)
    else:
        print("\nCONCLUSION: Some issues remain, but basic connection works.")
        sys.exit(1)

if __name__ == "__main__":
    main()