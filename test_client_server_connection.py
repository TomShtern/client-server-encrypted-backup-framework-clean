#!/usr/bin/env python3
"""
Test client-server connection to verify they can communicate
"""
import socket
import struct
import time

def test_client_server_connection():
    print("🔗 Testing Client-Server Connection")
    print("=" * 50)
    
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        # Connect to server
        print("📡 Connecting to server at 127.0.0.1:1256...")
        sock.connect(('127.0.0.1', 1256))
        print("✅ Successfully connected to server!")
        
        # Send a simple test message (simulating client protocol)
        print("📤 Sending test message...")
        
        # Create a simple test packet (version + request code)
        version = 3
        request_code = 1025  # REQ_REGISTER
        client_id = b'\x00' * 16  # Dummy client ID
        name_size = 8
        name = b'testuser'
        
        # Pack the message
        message = struct.pack('<BH16sB', version, request_code, client_id, name_size) + name
        
        sock.send(message)
        print("✅ Test message sent successfully!")
        
        # Try to receive response
        print("📥 Waiting for server response...")
        response = sock.recv(1024)
        
        if response:
            print(f"✅ Received response from server: {len(response)} bytes")
            # Parse response
            if len(response) >= 7:
                resp_version, resp_code, resp_payload_size = struct.unpack('<BHI', response[:7])
                print(f"   Response version: {resp_version}")
                print(f"   Response code: {resp_code}")
                print(f"   Payload size: {resp_payload_size}")
        else:
            print("⚠️  No response received from server")
        
        # Close connection
        sock.close()
        print("✅ Connection test completed successfully!")
        print("\n🎉 Client and Server can communicate!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_client_server_connection()
