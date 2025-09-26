#!/usr/bin/env python3
"""
Test specific database methods that were mentioned in error messages
"""

# Import UTF-8 solution first to fix encoding issues

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from python_server.server.database import DatabaseManager


def test_database_methods():
    """Test the specific database methods that were causing errors"""

    print("Testing database methods that were mentioned in error messages...")
    print("=" * 60)

    try:
        # Test 1: Initialize database manager with MockaBase
        print("1. Testing DatabaseManager initialization with MockaBase...")
        db_manager = DatabaseManager("MockaBase.db")
        print("   PASS: DatabaseManager initialized successfully")

        # Test 2: Test get_database_stats method
        print("2. Testing get_database_stats method...")
        stats = db_manager.get_database_stats()
        print(f"   PASS: Database stats retrieved: {stats}")

        # Test 3: Test get_all_clients method
        print("3. Testing get_all_clients method...")
        clients = db_manager.get_all_clients()
        print(f"   PASS: All clients retrieved: {len(clients)} clients found")

        # Test 4: Test get_all_files method
        print("4. Testing get_all_files method...")
        files = db_manager.get_all_files()
        print(f"   PASS: All files retrieved: {len(files)} files found")

        # Test 5: Test table queries directly
        print("5. Testing direct table queries...")
        result = db_manager.execute("SELECT COUNT(*) FROM clients", fetchone=True)
        print(f"   PASS: Direct clients query: {result[0]} clients")

        result = db_manager.execute("SELECT COUNT(*) FROM files", fetchone=True)
        print(f"   PASS: Direct files query: {result[0]} files")

        # Test 6: Test specific error conditions
        print("6. Testing that tables exist...")
        tables = db_manager.execute("SELECT name FROM sqlite_master WHERE type='table'", fetchall=True)
        table_names = [row[0] for row in tables]
        print(f"   PASS: Tables found: {table_names}")

        if "clients" not in table_names:
            print("   FAIL: 'clients' table not found!")
            return False

        if "files" not in table_names:
            print("   FAIL: 'files' table not found!")
            return False

        print("   PASS: All required tables exist")

        print("\nSUCCESS: All database method tests passed!")
        print("The database issues you mentioned should now be resolved.")
        return True

    except Exception as e:
        print(f"FAIL: Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_methods()
    if success:
        print("\nSUCCESS: Database integration is working correctly!")
    else:
        print("\nFAIL: Database integration has issues that need to be addressed!")
