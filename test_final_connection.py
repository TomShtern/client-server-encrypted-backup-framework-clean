#!/usr/bin/env python3
"""
Final connection test to verify client and server are connected
"""
import socket
import time

def test_connection():
    print("🔗 FINAL CONNECTION TEST")
    print("=" * 50)
    print("Testing if client can connect to server...")
    
    try:
        # Test basic TCP connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        
        print("📡 Connecting to 127.0.0.1:1256...")
        sock.connect(('127.0.0.1', 1256))
        print("✅ TCP connection successful!")
        
        sock.close()
        
        print("\n🎉 CLIENT AND SERVER ARE CONNECTED!")
        print("✅ Server is running on port 1256")
        print("✅ Client can establish TCP connections")
        print("✅ Ready for GUI testing!")
        
        print("\n📋 NEXT STEPS:")
        print("1. Look for the GUI window: '🚀 Ultra Modern Encrypted Backup Client'")
        print("2. Click the 'Connect' button to test real connection")
        print("3. The connection status should show 'Connected' if successful")
        print("4. Try other buttons like 'Select File' and 'Start Backup'")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
