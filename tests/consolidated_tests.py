#!/usr/bin/env python3
"""
Consolidated Test Suite for Encrypted Backup System
==================================================

This file consolidates all useful test cases from various test files
that were scattered throughout the project.
"""

import socket
import struct
import os
import sys
import time
import threading
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

# Constants from the protocol
CLIENT_VERSION = 3
SERVER_VERSION = 3
REQ_REGISTER = 1025
REQ_SEND_PUBLIC_KEY = 1026
REQ_RECONNECT = 1027
REQ_SEND_FILE = 1028
RESP_REGISTER_OK = 1600
RESP_REGISTER_FAIL = 1601
RESP_PUBKEY_AES_SENT = 1602

class BackupClientTest:
    """Test class for backup client functionality"""
    
    def __init__(self, server_host='127.0.0.1', server_port=1256):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.client_id = b'\x00' * 16
        
    def connect(self):
        """Test basic connection to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            print(f"✓ Connected to {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def test_registration(self, username="testuser"):
        """Test user registration"""
        try:
            # Prepare registration payload
            payload = username.encode().ljust(255, b'\x00')
            
            # Send registration request
            header = struct.pack('<16sBHI', self.client_id, CLIENT_VERSION, REQ_REGISTER, len(payload))
            self.socket.send(header + payload)
            
            # Receive response
            response_header = self.socket.recv(7)
            version, code, payload_size = struct.unpack('<BHI', response_header)
            
            if code == RESP_REGISTER_OK:
                self.client_id = self.socket.recv(16)
                print(f"✓ Registration successful, client ID: {self.client_id.hex()}")
                return True
            else:
                print(f"✗ Registration failed, code: {code}")
                return False
                
        except Exception as e:
            print(f"✗ Registration test failed: {e}")
            return False
    
    def test_connection_basic(self):
        """Basic connection test"""
        return self.connect()
    
    def test_protocol_compliance(self):
        """Test protocol compliance"""
        if not self.connect():
            return False
        
        return self.test_registration()
    
    def disconnect(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            self.socket = None

def run_all_tests():
    """Run all consolidated tests"""
    print("=" * 50)
    print("ENCRYPTED BACKUP SYSTEM - CONSOLIDATED TESTS")
    print("=" * 50)
    
    test_client = BackupClientTest()
    
    tests = [
        ("Basic Connection", test_client.test_connection_basic),
        ("Protocol Compliance", test_client.test_protocol_compliance),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        try:
            if test_func():
                print(f"✓ {test_name} PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
            failed += 1
        
        test_client.disconnect()
    
    print(f"\n" + "=" * 50)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
