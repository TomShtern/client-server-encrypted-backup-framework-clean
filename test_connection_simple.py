#!/usr/bin/env python3
"""
Simple connection test to diagnose client-server connectivity issues.
This script tests if the server is running and accepting connections.
"""

import socket
import sys
import time

def test_server_connection(host='127.0.0.1', port=1256):
    """Test if server is reachable and accepting connections."""
    print(f"🔍 Testing connection to {host}:{port}")
    print("-" * 50)
    
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)  # 5 second timeout
        
        print(f"📡 Attempting to connect to {host}:{port}...")
        
        # Try to connect
        result = sock.connect_ex((host, port))
        
        if result == 0:
            print("✅ SUCCESS: Server is reachable and accepting connections!")
            print(f"🔗 Connected to {sock.getpeername()}")
            
            # Try to send a simple test message
            try:
                test_msg = b"TEST_CONNECTION"
                sock.send(test_msg)
                print("📤 Sent test message successfully")
                
                # Try to receive response (with timeout)
                sock.settimeout(2.0)
                response = sock.recv(1024)
                if response:
                    print(f"📥 Received response: {response[:50]}...")
                else:
                    print("📥 No response received (this might be normal)")
                    
            except socket.timeout:
                print("⏱️ No response within timeout (server might not respond to test messages)")
            except Exception as e:
                print(f"⚠️ Error during message exchange: {e}")
            
            sock.close()
            return True
            
        else:
            print(f"❌ FAILED: Cannot connect to server (error code: {result})")
            print("💡 Possible causes:")
            print("   • Server is not running")
            print("   • Server is running on a different port")
            print("   • Firewall is blocking the connection")
            print("   • Server is bound to a different interface")
            return False
            
    except socket.gaierror as e:
        print(f"❌ DNS/Address error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    finally:
        try:
            sock.close()
        except:
            pass

def check_port_in_use(port=1256):
    """Check if the port is in use by any process."""
    print(f"\n🔍 Checking if port {port} is in use...")
    
    try:
        # Try to bind to the port
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        result = test_sock.bind(('127.0.0.1', port))
        test_sock.close()
        print(f"✅ Port {port} is available (not in use)")
        return False
    except OSError:
        print(f"🔒 Port {port} is in use by another process")
        return True

def main():
    print("🔧 Client-Server Connection Diagnostics")
    print("=" * 50)
    
    # Check if port is in use
    port_in_use = check_port_in_use()
    
    if not port_in_use:
        print("\n❌ Server doesn't appear to be running!")
        print("💡 To start the server:")
        print("   1. Navigate to the server directory")
        print("   2. Run: python server.py")
        print("   3. Wait for 'Server is now listening...' message")
        return False
    
    # Test connection
    print()
    success = test_server_connection()
    
    if success:
        print("\n🎉 Connection test PASSED!")
        print("💡 The client should be able to connect to the server.")
        print("   If the client still can't connect, check:")
        print("   • Client configuration (transfer.info)")
        print("   • Client logs for specific error messages")
    else:
        print("\n❌ Connection test FAILED!")
        print("💡 Troubleshooting steps:")
        print("   1. Make sure the server is running: python server.py")
        print("   2. Check server logs for errors")
        print("   3. Verify port 1256 is not blocked by firewall")
        print("   4. Try restarting both server and client")
    
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
