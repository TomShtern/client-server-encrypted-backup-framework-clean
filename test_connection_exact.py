#!/usr/bin/env python3
"""
EXACT CONNECTION SEQUENCE TEST
Mimics the exact client connection behavior to identify failure point
"""

import socket
import struct
import threading
import time
import sys
import os

# Protocol constants from the C++ client
SERVER_VERSION = 3
REQ_REGISTER = 1025
RESP_REGISTER_SUCCESS = 1600
RESP_GENERIC_SERVER_ERROR = 1603

class ExactConnectionTest:
    def __init__(self):
        self.server_ip = "127.0.0.1"
        self.server_port = 1256
        self.client_id = b'\x00' * 16  # All zeros for registration
        
    def test_server_header_parsing(self):
        """Test if server can parse client headers correctly"""
        print("\n=== EXACT HEADER FORMAT TEST ===")
        
        # Create minimal server that logs exact bytes received
        def header_logging_server():
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind(('0.0.0.0', self.server_port))
                server_socket.listen(1)
                server_socket.settimeout(10.0)
                
                print(f"Header logging server listening on port {self.server_port}")
                
                conn, addr = server_socket.accept()
                print(f"Server accepted connection from {addr}")
                
                # Read exactly 23 bytes (client header size)
                header_bytes = conn.recv(23)
                print(f"Received {len(header_bytes)} bytes:")
                print(f"Raw bytes: {header_bytes.hex()}")
                
                if len(header_bytes) == 23:
                    # Parse according to client format
                    # struct RequestHeader {
                    #     uint8_t client_id[16];
                    #     uint8_t version;
                    #     uint16_t code;
                    #     uint32_t payload_size;
                    # };
                    
                    client_id = header_bytes[:16]
                    version = header_bytes[16]
                    code = struct.unpack('<H', header_bytes[17:19])[0]  # little-endian uint16
                    payload_size = struct.unpack('<I', header_bytes[19:23])[0]  # little-endian uint32
                    
                    print(f"Parsed header:")
                    print(f"  Client ID: {client_id.hex()}")
                    print(f"  Version: {version}")
                    print(f"  Code: {code}")
                    print(f"  Payload Size: {payload_size}")
                    
                    # Check if this matches registration request
                    if version == SERVER_VERSION and code == REQ_REGISTER:
                        print("  -> VALID REGISTRATION REQUEST")
                        
                        # Send success response
                        # ResponseHeader: version(1) + code(2) + payload_size(4) = 7 bytes
                        response_header = struct.pack('<BHI', SERVER_VERSION, RESP_REGISTER_SUCCESS, 0)
                        conn.send(response_header)
                        print("  -> Sent success response")
                    else:
                        print(f"  -> INVALID REQUEST (version={version}, code={code})")
                        
                        # Send error response
                        response_header = struct.pack('<BHI', SERVER_VERSION, RESP_GENERIC_SERVER_ERROR, 0)
                        conn.send(response_header)
                        print("  -> Sent error response")
                else:
                    print(f"  -> HEADER SIZE MISMATCH: expected 23, got {len(header_bytes)}")
                
                conn.close()
                server_socket.close()
                
            except Exception as e:
                print(f"Header logging server error: {e}")
        
        # Start server
        server_thread = threading.Thread(target=header_logging_server, daemon=True)
        server_thread.start()
        time.sleep(0.5)
        
        # Create client request exactly as C++ client does
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5.0)
            
            print(f"Client connecting to {self.server_ip}:{self.server_port}")
            client_socket.connect((self.server_ip, self.server_port))
            print("Client connected successfully")
            
            # Create registration request header (exactly as C++ client)
            # struct RequestHeader {
            #     uint8_t client_id[16];    // All zeros for registration
            #     uint8_t version;          // 3
            #     uint16_t code;            // 1025 (REQ_REGISTER)
            #     uint32_t payload_size;    // 0 for registration
            # };
            
            header = bytearray()
            header.extend(self.client_id)  # 16 bytes client_id
            header.append(SERVER_VERSION)  # 1 byte version
            header.extend(struct.pack('<H', REQ_REGISTER))  # 2 bytes code (little-endian)
            header.extend(struct.pack('<I', 0))  # 4 bytes payload_size (little-endian)
            
            print(f"Sending header ({len(header)} bytes): {header.hex()}")
            client_socket.send(header)
            
            # Try to receive response
            response_header = client_socket.recv(7)  # Server should send 7-byte response header
            if len(response_header) == 7:
                version, code, payload_size = struct.unpack('<BHI', response_header)
                print(f"Received response: version={version}, code={code}, payload_size={payload_size}")
                
                if code == RESP_REGISTER_SUCCESS:
                    print("SUCCESS: Server accepted registration request")
                    return True
                else:
                    print(f"FAILURE: Server rejected request with code {code}")
                    return False
            else:
                print(f"FAILURE: Invalid response header size: {len(response_header)}")
                return False
                
        except Exception as e:
            print(f"Client connection failed: {e}")
            return False
        finally:
            try:
                client_socket.close()
            except:
                pass
            
        # Wait for server thread
        server_thread.join(timeout=2.0)
        return False
        
    def test_boost_asio_simulation(self):
        """Test connection using similar patterns to Boost.Asio"""
        print("\n=== BOOST.ASIO SIMULATION TEST ===")
        
        try:
            # Simulate Boost.Asio resolver behavior
            print("Simulating Boost.Asio resolver...")
            
            # Get address info (similar to resolver.resolve())
            addr_info = socket.getaddrinfo(
                self.server_ip, 
                self.server_port, 
                socket.AF_INET, 
                socket.SOCK_STREAM
            )
            
            print(f"Resolved endpoints: {addr_info}")
            
            # Try each endpoint (Boost.Asio connect behavior)
            for family, socktype, proto, canonname, sockaddr in addr_info:
                try:
                    print(f"Trying endpoint: {sockaddr}")
                    
                    # Create socket
                    sock = socket.socket(family, socktype, proto)
                    sock.settimeout(5.0)
                    
                    # Set socket options (similar to C++ client)
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    
                    # Connect
                    sock.connect(sockaddr)
                    
                    # Verify connection
                    local_addr = sock.getsockname()
                    remote_addr = sock.getpeername()
                    
                    print(f"Connection established:")
                    print(f"  Local: {local_addr}")
                    print(f"  Remote: {remote_addr}")
                    
                    # Small delay (similar to C++ client)
                    time.sleep(0.1)
                    
                    sock.close()
                    print("SUCCESS: Boost.Asio-style connection works")
                    return True
                    
                except Exception as e:
                    print(f"  Endpoint failed: {e}")
                    continue
                    
            print("FAILURE: All endpoints failed")
            return False
            
        except Exception as e:
            print(f"Boost.Asio simulation failed: {e}")
            return False
            
    def test_client_executable_behavior(self):
        """Test by running actual client executable if available"""
        print("\n=== CLIENT EXECUTABLE TEST ===")
        
        client_exe = os.path.join("client", "EncryptedBackupClient.exe")
        if not os.path.exists(client_exe):
            print(f"Client executable not found at {client_exe}")
            return False
            
        # Ensure we have transfer.info
        if not os.path.exists("transfer.info"):
            print("transfer.info not found - creating minimal version")
            with open("transfer.info", "w") as f:
                f.write(f"{self.server_ip}:{self.server_port}\n")
                f.write("testuser\n")
                f.write("tests/test_file.txt\n")
                
        # Start minimal server
        def minimal_protocol_server():
            try:
                import sys
                sys.path.insert(0, "server")
                from server import EncryptedBackupServer
                
                server = EncryptedBackupServer()
                print("Starting actual server for client test...")
                server.start()
                
            except Exception as e:
                print(f"Could not start actual server: {e}")
                return
                
        server_thread = threading.Thread(target=minimal_protocol_server, daemon=True)
        server_thread.start()
        time.sleep(2.0)  # Give server time to start
        
        try:
            # Run client executable
            import subprocess
            result = subprocess.run([client_exe], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10,
                                  cwd=os.path.dirname(client_exe))
            
            print(f"Client exit code: {result.returncode}")
            print(f"Client stdout:\n{result.stdout}")
            print(f"Client stderr:\n{result.stderr}")
            
            if result.returncode == 0:
                print("SUCCESS: Client executable ran without errors")
                return True
            else:
                print(f"FAILURE: Client executable failed with code {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            print("Client executable timed out")
            return False
        except Exception as e:
            print(f"Could not run client executable: {e}")
            return False
            
    def run_exact_tests(self):
        """Run all exact connection tests"""
        print("EXACT CONNECTION SEQUENCE TEST")
        print("=" * 50)
        
        tests = [
            ("Boost.Asio Simulation", self.test_boost_asio_simulation),
            ("Exact Header Format", self.test_server_header_parsing),
            ("Client Executable", self.test_client_executable_behavior),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\nRunning {test_name}...")
            try:
                result = test_func()
                results.append((test_name, result))
                status = "PASS" if result else "FAIL"
                print(f"[{status}] {test_name}")
            except Exception as e:
                print(f"[ERROR] {test_name}: {e}")
                results.append((test_name, False))
                
        # Summary
        print("\n" + "=" * 50)
        print("EXACT TEST RESULTS")
        print("=" * 50)
        
        for test_name, success in results:
            status = "PASS" if success else "FAIL"
            print(f"[{status}] {test_name}")
            
        passed = sum(1 for _, success in results if success)
        total = len(results)
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed < total:
            print("\nFAILURE ANALYSIS:")
            print("The connection is failing at the TCP level, not the protocol level.")
            print("This suggests:")
            print("1. Port 1256 is not accessible")
            print("2. Firewall is blocking connections")
            print("3. Server is not binding correctly")
            print("4. WSL networking configuration issue")
        
        return passed == total

def main():
    # Ensure we're in the right directory
    if not os.path.exists("src"):
        print("Error: Run this script from the project root directory")
        sys.exit(1)
        
    test = ExactConnectionTest()
    test.run_exact_tests()

if __name__ == "__main__":
    main()