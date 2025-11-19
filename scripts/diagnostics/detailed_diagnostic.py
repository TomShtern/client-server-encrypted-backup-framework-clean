#!/usr/bin/env python3
"""
Detailed diagnostic to check data format for GUI
"""

# Import UTF-8 solution first to fix encoding issues

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from python_server.server.database import DatabaseManager


def detailed_diagnostic():
    """Detailed diagnostic of data format for GUI"""

    print("Detailed Database Data Format Diagnostic")
    print("=" * 50)

    try:
        # Initialize database manager
        print("1. Initializing DatabaseManager...")
        db_manager = DatabaseManager("MockaBase.db")
        print("   PASS: DatabaseManager initialized")

        # Test table content format
        print("2. Testing table content format...")
        tables = db_manager.get_table_names()
        print(f"   Tables found: {tables}")

        for table_name in tables:
            print(f"\n   Table: {table_name}")
            columns, rows = db_manager.get_table_content(table_name)
            print(f"   Columns: {columns}")
            print(f"   Rows count: {len(rows)}")

            if rows:
                print("   First row data:")
                first_row = rows[0]
                print(f"     Type: {type(first_row)}")
                print(f"     Keys: {list(first_row.keys())}")
                print(f"     Values: {list(first_row.values())}")

                # Check if all values are strings or can be converted to strings
                for key, value in first_row.items():
                    print(f"     {key}: {type(value)} = {repr(value)[:100]}")

        # Test get_all_files format
        print("\n3. Testing get_all_files format...")
        files = db_manager.get_all_files()
        print(f"   Files count: {len(files)}")

        if files:
            first_file = files[0]
            print(f"   First file type: {type(first_file)}")
            print(f"   First file keys: {list(first_file.keys())}")
            for key, value in first_file.items():
                print(f"     {key}: {type(value)} = {repr(value)[:100]}")

        # Test get_all_clients format
        print("\n4. Testing get_all_clients format...")
        clients = db_manager.get_all_clients()
        print(f"   Clients count: {len(clients)}")

        if clients:
            first_client = clients[0]
            print(f"   First client type: {type(first_client)}")
            print(f"   First client keys: {list(first_client.keys()) if hasattr(first_client, 'keys') else 'No keys method'}")
            if hasattr(first_client, '__dict__'):
                print(f"   First client dict: {first_client.__dict__}")

        print("\nDiagnostic completed successfully!")
        return True

    except Exception as e:
        print(f"FAIL: Diagnostic failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    detailed_diagnostic()
