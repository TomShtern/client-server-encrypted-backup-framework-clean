#!/usr/bin/env python3
"""
CRITICAL DIAGNOSTIC: Connection Sequence Analysis
Comprehensive diagnostic tool to identify exact connection failure point
"""

import socket
import threading
import time
import subprocess
import sys
import os
from typing import Optional, Tuple

class ConnectionDiagnostic:
    def __init__(self):
        self.server_port = 1256
        self.server_ip = "127.0.0.1"
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log diagnostic test result"""
        status = "PASS" if success else "FAIL"
        result = f"[{status}] {test_name}: {details}"
        print(result)
        self.test_results.append((test_name, success, details))
        
    def test_port_availability(self) -> bool:
        """Test if port 1256 is available or in use"""
        print("\n=== PORT AVAILABILITY TEST ===")
        
        # Test if port is already bound
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_socket.bind(('0.0.0.0', self.server_port))
            test_socket.listen(1)
            test_socket.close()
            self.log_result("Port Availability", True, f"Port {self.server_port} is available")
            return True
        except OSError as e:
            self.log_result("Port Availability", False, f"Port {self.server_port} in use or blocked: {e}")
            return False
            
    def test_socket_connection(self) -> bool:
        """Test basic TCP socket connection without protocol"""
        print("\n=== BASIC SOCKET CONNECTION TEST ===")
        
        # Start minimal server
        server_socket = None
        server_thread = None
        connection_established = False
        
        def minimal_server():
            nonlocal connection_established
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind(('0.0.0.0', self.server_port))
                server_socket.listen(1)
                server_socket.settimeout(5.0)
                
                print(f"  Minimal server listening on port {self.server_port}")
                
                try:
                    conn, addr = server_socket.accept()
                    print(f"  Server accepted connection from {addr}")
                    connection_established = True
                    
                    # Send simple response
                    conn.send(b"TEST_RESPONSE")
                    conn.close()
                except socket.timeout:
                    print("  Server timeout - no client connection")
                except Exception as e:
                    print(f"  Server error: {e}")
                finally:
                    server_socket.close()
            except Exception as e:
                print(f"  Server setup failed: {e}")
        
        # Start server in thread
        server_thread = threading.Thread(target=minimal_server, daemon=True)
        server_thread.start()
        
        # Give server time to start
        time.sleep(0.5)
        
        # Try to connect as client
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(3.0)
            client_socket.connect((self.server_ip, self.server_port))
            
            # Receive response
            response = client_socket.recv(1024)
            client_socket.close()
            
            if response == b"TEST_RESPONSE":
                self.log_result("Basic Socket Connection", True, "TCP connection successful")
                return True
            else:
                self.log_result("Basic Socket Connection", False, f"Unexpected response: {response}")
                return False
                
        except Exception as e:
            self.log_result("Basic Socket Connection", False, f"Client connection failed: {e}")
            return False
        finally:
            # Wait for server thread
            if server_thread:
                server_thread.join(timeout=1.0)
                
    def test_server_startup(self) -> bool:
        """Test if Python server starts correctly"""
        print("\n=== SERVER STARTUP TEST ===")
        
        try:
            # Check if server.py exists
            server_path = os.path.join("server", "server.py")
            if not os.path.exists(server_path):
                self.log_result("Server File Check", False, f"server.py not found at {server_path}")
                return False
            
            self.log_result("Server File Check", True, "server.py found")
            
            # Try to import server modules (basic syntax check)
            sys.path.insert(0, "server")
            try:
                import server
                self.log_result("Server Import", True, "Server module imports successfully")
            except Exception as e:
                self.log_result("Server Import", False, f"Server import failed: {e}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Server Startup Test", False, f"Error: {e}")
            return False
            
    def test_client_build(self) -> bool:
        """Test if client builds successfully"""
        print("\n=== CLIENT BUILD TEST ===")
        
        try:
            # Check if build.bat exists
            if not os.path.exists("build.bat"):
                self.log_result("Build Script Check", False, "build.bat not found")
                return False
                
            self.log_result("Build Script Check", True, "build.bat found")
            
            # Check if client executable exists
            client_exe = os.path.join("client", "EncryptedBackupClient.exe")
            if os.path.exists(client_exe):
                self.log_result("Client Executable", True, f"Client executable found at {client_exe}")
                return True
            else:
                self.log_result("Client Executable", False, f"Client executable not found at {client_exe}")
                return False
                
        except Exception as e:
            self.log_result("Client Build Test", False, f"Error: {e}")
            return False
            
    def test_configuration_files(self) -> bool:
        """Test configuration file presence and format"""
        print("\n=== CONFIGURATION FILES TEST ===")
        
        results = []
        
        # Check port.info
        try:
            if os.path.exists("port.info"):
                with open("port.info", "r") as f:
                    port_content = f.read().strip()
                    if port_content == "1256":
                        self.log_result("port.info", True, f"Contains correct port: {port_content}")
                        results.append(True)
                    else:
                        self.log_result("port.info", False, f"Wrong port: {port_content}")
                        results.append(False)
            else:
                self.log_result("port.info", False, "File not found")
                results.append(False)
        except Exception as e:
            self.log_result("port.info", False, f"Error reading: {e}")
            results.append(False)
            
        # Check transfer.info
        if os.path.exists("transfer.info"):
            try:
                with open("transfer.info", "r") as f:
                    lines = f.readlines()
                    if len(lines) >= 3:
                        server_line = lines[0].strip()
                        username_line = lines[1].strip()
                        filepath_line = lines[2].strip()
                        
                        self.log_result("transfer.info format", True, 
                                      f"Server: {server_line}, User: {username_line}, File: {filepath_line}")
                        results.append(True)
                    else:
                        self.log_result("transfer.info format", False, f"Only {len(lines)} lines found, need 3")
                        results.append(False)
            except Exception as e:
                self.log_result("transfer.info", False, f"Error reading: {e}")
                results.append(False)
        else:
            self.log_result("transfer.info", False, "File not found - CLIENT WILL FAIL")
            results.append(False)
            
        # Check me.info
        if os.path.exists("me.info"):
            self.log_result("me.info", True, "Client credentials file exists")
            results.append(True)
        else:
            self.log_result("me.info", False, "File not found - client will need to register")
            results.append(True)  # This is OK for first run
            
        return all(results)
        
    def test_wsl_networking(self) -> bool:
        """Test WSL networking configuration"""
        print("\n=== WSL NETWORKING TEST ===")
        
        try:
            # Test localhost connectivity
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(2.0)
            
            # Try connecting to a known port that should fail (to test networking stack)
            try:
                test_socket.connect(('127.0.0.1', 9999))  # Should fail
                test_socket.close()
                self.log_result("WSL Networking", False, "Unexpected connection to port 9999")
                return False
            except socket.error:
                # This is expected - connection should fail
                self.log_result("WSL Networking", True, "Localhost networking stack operational")
                return True
                
        except Exception as e:
            self.log_result("WSL Networking", False, f"Networking test failed: {e}")
            return False
            
    def create_minimal_config(self):
        """Create minimal configuration files for testing"""
        print("\n=== CREATING MINIMAL CONFIG ===")
        
        if not os.path.exists("transfer.info"):
            with open("transfer.info", "w") as f:
                f.write("127.0.0.1:1256\n")
                f.write("testuser\n")
                f.write("tests/test_file.txt\n")
            print("  Created transfer.info with test configuration")
            
        # Ensure test file exists
        os.makedirs("tests", exist_ok=True)
        if not os.path.exists("tests/test_file.txt"):
            with open("tests/test_file.txt", "w") as f:
                f.write("This is a test file for connection diagnostics.\n")
            print("  Created tests/test_file.txt")
            
    def run_full_diagnostic(self):
        """Run complete diagnostic sequence"""
        print("CRITICAL DIAGNOSTIC: Connection Sequence Analysis")
        print("=" * 60)
        
        # Run all diagnostic tests
        tests = [
            ("Port Availability", self.test_port_availability),
            ("WSL Networking", self.test_wsl_networking),
            ("Configuration Files", self.test_configuration_files),
            ("Server Startup", self.test_server_startup),
            ("Client Build", self.test_client_build),
            ("Basic Socket Connection", self.test_socket_connection),
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            try:
                result = test_func()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"EXCEPTION in {test_name}: {e}")
                all_passed = False
                
        # Summary
        print("\n" + "=" * 60)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
        for test_name, success, details in self.test_results:
            status = "PASS" if success else "FAIL"
            print(f"[{status}] {test_name}")
            if details and not success:
                print(f"    -> {details}")
                
        if not all_passed:
            print(f"\nCRITICAL ISSUES DETECTED:")
            failed_tests = [name for name, success, _ in self.test_results if not success]
            for i, test in enumerate(failed_tests, 1):
                print(f"  {i}. {test}")
                
            print(f"\nNEXT STEPS:")
            if any("transfer.info" in test for test, success, _ in self.test_results if not success):
                print("  - Create transfer.info file with correct format")
            if any("Port" in test for test, success, _ in self.test_results if not success):
                print("  - Check if another process is using port 1256")
            if any("Socket" in test for test, success, _ in self.test_results if not success):
                print("  - Check Windows Firewall and WSL networking")
            if any("Build" in test for test, success, _ in self.test_results if not success):
                print("  - Run build.bat to compile client")
        else:
            print(f"\nALL DIAGNOSTIC TESTS PASSED")
            print(f"Connection should work - run actual client/server test")
            
        return all_passed

def main():
    diagnostic = ConnectionDiagnostic()
    
    # Create minimal config if needed
    diagnostic.create_minimal_config()
    
    # Run full diagnostic
    diagnostic.run_full_diagnostic()

if __name__ == "__main__":
    main()