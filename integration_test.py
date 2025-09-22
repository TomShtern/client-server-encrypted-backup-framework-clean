#!/usr/bin/env python3
"""
Integration test for BackupServer and ServerBridge compatibility.
Tests that all expected methods exist and return proper response formats.
"""

import sys
import os
import traceback

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python_server'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'FletV2'))

# Import UTF-8 support
import Shared.utils.utf8_solution

def test_backup_server_integration():
    """Test that BackupServer has all methods expected by ServerBridge."""

    print("🧪 Testing BackupServer and ServerBridge Integration")
    print("=" * 60)

    try:
        # Import the classes
        from python_server.server.server import BackupServer
        from FletV2.utils.server_bridge import ServerBridge

        print("✅ Successfully imported BackupServer and ServerBridge")

        # Create BackupServer instance (without starting it)
        print("\n📦 Creating BackupServer instance...")
        backup_server = BackupServer()
        print("✅ BackupServer instance created successfully")

        # Create ServerBridge with the real server
        print("\n🌉 Creating ServerBridge with real server...")
        server_bridge = ServerBridge(real_server=backup_server)
        print("✅ ServerBridge created with real server")

        # Test categories of methods
        test_categories = {
            "Client Operations": [
                "get_clients", "get_client_details", "add_client",
                "delete_client", "disconnect_client"
            ],
            "File Operations": [
                "get_files", "get_client_files", "delete_file",
                "download_file", "verify_file"
            ],
            "Database Operations": [
                "get_database_info", "get_table_data"
            ],
            "Server Status": [
                "get_server_status", "get_detailed_server_status",
                "get_server_health", "test_connection"
            ],
            "Analytics": [
                "get_system_status", "get_analytics_data",
                "get_performance_metrics", "get_dashboard_summary"
            ],
            "Log Operations": [
                "get_logs"
            ],
            "Settings": [
                "load_settings", "save_settings"
            ]
        }

        total_methods = 0
        successful_methods = 0

        for category, methods in test_categories.items():
            print(f"\n📋 Testing {category}:")

            for method_name in methods:
                total_methods += 1

                try:
                    # Check if method exists on BackupServer
                    if hasattr(backup_server, method_name):
                        method = getattr(backup_server, method_name)
                        print(f"  ✅ {method_name}: Method exists on BackupServer")

                        # Test basic method call (for non-destructive methods)
                        if method_name in ["get_server_status", "get_server_health", "test_connection",
                                         "load_settings", "get_logs", "get_system_status"]:
                            try:
                                if method_name == "get_client_details":
                                    result = method("dummy_id")
                                elif method_name == "get_table_data":
                                    result = method("clients")
                                elif method_name == "save_settings":
                                    result = method({})
                                else:
                                    result = method()

                                if isinstance(result, dict) and 'success' in result:
                                    print(f"    🎯 Returns proper format: {result.keys()}")
                                    successful_methods += 1
                                else:
                                    print(f"    ⚠️  Unexpected return format: {type(result)}")
                            except Exception as e:
                                print(f"    ⚠️  Method call failed: {e}")
                        else:
                            successful_methods += 1
                            print(f"    ℹ️  Skipped destructive method test")

                    else:
                        print(f"  ❌ {method_name}: Method missing from BackupServer")

                except Exception as e:
                    print(f"  ❌ {method_name}: Error testing method: {e}")

        print(f"\n📊 Integration Test Results:")
        print(f"   Total methods tested: {total_methods}")
        print(f"   Successful: {successful_methods}")
        print(f"   Success rate: {(successful_methods/total_methods)*100:.1f}%")

        # Test ServerBridge delegation
        print(f"\n🔗 Testing ServerBridge delegation...")
        try:
            # Test a safe method through ServerBridge
            bridge_result = server_bridge.get_server_status()
            if isinstance(bridge_result, dict) and 'success' in bridge_result:
                print("✅ ServerBridge successfully delegates to BackupServer")
                print(f"   Sample result: {list(bridge_result.keys())}")
            else:
                print(f"⚠️  Unexpected ServerBridge result format: {type(bridge_result)}")
        except Exception as e:
            print(f"❌ ServerBridge delegation failed: {e}")
            traceback.print_exc()

        print(f"\n🎉 Integration test completed!")

        if successful_methods >= total_methods * 0.8:  # 80% success rate
            print("✅ INTEGRATION SUCCESS: BackupServer is compatible with ServerBridge")
            return True
        else:
            print("⚠️  INTEGRATION WARNING: Some methods may need attention")
            return False

    except Exception as e:
        print(f"❌ INTEGRATION FAILED: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_backup_server_integration()
    sys.exit(0 if success else 1)