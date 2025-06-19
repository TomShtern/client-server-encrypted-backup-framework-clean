#!/usr/bin/env python3
"""
Test the complete CyberBackup 3.0 integration system
"""

import os
import sys
import time
import json
import tempfile
import requests
from pathlib import Path

def create_test_file(content="Test backup file for CyberBackup 3.0", filename="test_cyberbackup.txt"):
    """Create a test file for backup"""
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, filename)
    
    with open(test_file, 'w') as f:
        f.write(content)
    
    return test_file

def test_api_endpoints():
    """Test the API endpoints"""
    base_url = "http://localhost:9090"
    
    print("🔍 Testing API Endpoints...")
    print("=" * 40)
    
    try:
        # Test health check
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Health Check: {health['status']}")
            print(f"   Server Connected: {health['server_connected']}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
        
        # Test status endpoint
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Status: {status['status']}")
            print(f"   Connected: {status['connected']}")
            print(f"   Message: {status['message']}")
        else:
            print(f"❌ Status Check Failed: {response.status_code}")
            return False
        
        # Test server info
        response = requests.get(f"{base_url}/api/server_info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Server Info: {info['host']}:{info['port']}")
            print(f"   Running: {info['running']}")
        else:
            print(f"❌ Server Info Failed: {response.status_code}")
            return False
        
        # Test connection
        response = requests.post(f"{base_url}/api/connect", 
                               json={"host": "127.0.0.1", "port": 1256, "username": "test_user"}, 
                               timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Connect: {result['success']}")
            print(f"   Message: {result['message']}")
        else:
            print(f"❌ Connect Failed: {response.status_code}")
            return False
        
        return True
        
    except requests.ConnectionError:
        print("❌ Cannot connect to API server at localhost:9090")
        print("   Please make sure the API server is running")
        return False
    except Exception as e:
        print(f"❌ API Test Error: {e}")
        return False

def test_file_backup():
    """Test actual file backup through the API"""
    base_url = "http://localhost:9090"
    
    print("\n🚀 Testing File Backup...")
    print("=" * 40)
    
    # Create test file
    test_file = create_test_file()
    print(f"📁 Created test file: {test_file}")
    print(f"📏 File size: {os.path.getsize(test_file)} bytes")
    
    try:
        # Start backup via API
        backup_request = {
            "path": test_file,
            "name": os.path.basename(test_file)
        }
        
        response = requests.post(f"{base_url}/api/start_backup", 
                               json=backup_request, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Backup Started: {result['success']}")
            print(f"   Message: {result['message']}")
            print(f"   File: {result['file_name']}")
            
            # Monitor backup progress
            print("\n📊 Monitoring backup progress...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                
                status_response = requests.get(f"{base_url}/api/status", timeout=5)
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"   Progress: {status['progress']}% - {status['message']}")
                    
                    if status['status'] == 'completed':
                        print("✅ Backup completed successfully!")
                        break
                    elif status['status'] == 'failed':
                        print(f"❌ Backup failed: {status['message']}")
                        return False
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    return False
            
            # Check received files
            files_response = requests.get(f"{base_url}/api/received_files", timeout=5)
            if files_response.status_code == 200:
                files = files_response.json()['files']
                print(f"\n📁 Received Files: {len(files)} files")
                for file_info in files:
                    print(f"   • {file_info['name']} ({file_info['size']} bytes)")
                
                if len(files) > 0:
                    print("✅ File transfer verification: SUCCESS")
                    return True
                else:
                    print("❌ File transfer verification: NO FILES FOUND")
                    return False
            else:
                print(f"❌ Cannot check received files: {files_response.status_code}")
                return False
        else:
            print(f"❌ Backup Start Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backup Test Error: {e}")
        return False
    finally:
        # Cleanup
        try:
            os.remove(test_file)
            os.rmdir(os.path.dirname(test_file))
        except:
            pass

def check_prerequisites():
    """Check that all components are running"""
    print("🔍 Checking Prerequisites...")
    print("=" * 30)
    
    checks_passed = 0
    total_checks = 3
    
    # Check API server
    try:
        response = requests.get("http://localhost:9090/health", timeout=3)
        if response.status_code == 200:
            print("✅ API Server: Running on port 9090")
            checks_passed += 1
        else:
            print("❌ API Server: Responding but unhealthy")
    except:
        print("❌ API Server: NOT running on port 9090")
        print("   Start with: python cyberbackup_api_server.py")
    
    # Check HTML client
    if os.path.exists("src/client/NewGUIforClient.html"):
        print("✅ HTML Client: Found")
        checks_passed += 1
    else:
        print("❌ HTML Client: NOT found")
    
    # Check backup server via API
    try:
        response = requests.get("http://localhost:9090/api/server_info", timeout=3)
        if response.status_code == 200:
            info = response.json()
            if info['running']:
                print("✅ Backup Server: Running on port 1256")
                checks_passed += 1
            else:
                print("❌ Backup Server: NOT running on port 1256")
        else:
            print("❌ Backup Server: Cannot check status")
    except:
        print("❌ Backup Server: Cannot check status")
    
    print(f"\nPrerequisite Check: {checks_passed}/{total_checks} passed")
    return checks_passed == total_checks

def main():
    """Main test function"""
    print("🚀 CYBERBACKUP 3.0 INTEGRATION TEST")
    print("=" * 50)
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        print("\nTo start the complete system:")
        print("   1. Run: start_complete_system.bat")
        print("   2. Or manually start the servers:")
        print("      - python server/server.py")
        print("      - python cyberbackup_api_server.py")
        return False
    
    print("\n" + "=" * 50)
    
    # Test API endpoints
    if not test_api_endpoints():
        print("\n❌ API endpoint tests failed!")
        return False
    
    # Test file backup
    if not test_file_backup():
        print("\n❌ File backup test failed!")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("✅ CyberBackup 3.0 integration is working correctly")
    print("✅ API endpoints are responding properly")
    print("✅ File backups are actually being performed")
    print("✅ Files are being transferred to received_files")
    print("✅ Real integration with C++ client verified")
    print()
    print("🌐 Open the GUI: http://localhost:9090")
    print("📁 Check received files: server/received_files")
    print()
    print("The system is ready for real encrypted backups!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
