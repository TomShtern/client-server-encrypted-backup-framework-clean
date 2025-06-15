import socket
import time

print("Quick connection test...")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    result = s.connect_ex(('127.0.0.1', 1256))
    s.close()
    
    if result == 0:
        print("✅ Server is running and accepting connections!")
    else:
        print(f"❌ Connection failed with error code: {result}")
except Exception as e:
    print(f"❌ Error: {e}")
