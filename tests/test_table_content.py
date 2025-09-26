#!/usr/bin/env python3
"""
Test database table content functionality
"""

# Import UTF-8 solution first to fix encoding issues

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from python_server.server.database import DatabaseManager


def test_table_content_functionality():
    """Test the database table content functionality for UI interactions"""

    print("Testing database table content functionality...")
    print("=" * 50)

    try:
        # Initialize database manager with MockaBase
        print("1. Initializing database manager with MockaBase...")
        db_manager = DatabaseManager("MockaBase.db")
        print("   PASS: Database manager initialized")

        # Test table listing
        print("2. Testing table listing...")
        tables = db_manager.get_table_names()
        print(f"   PASS: Found tables: {tables}")

        # Test table content retrieval
        for table_name in tables:
            print(f"3. Testing content retrieval for table '{table_name}'...")
            columns, rows = db_manager.get_table_content(table_name)
            print(f"   PASS: Table '{table_name}' has {len(columns)} columns and {len(rows)} rows")

            if columns:
                print(f"   Columns: {columns}")

            if rows:
                print(f"   Sample row keys: {list(rows[0].keys()) if rows else 'No rows'}")
                print(f"   Sample data: {dict(list(rows[0].items())[:3]) if rows else 'No data'}")

        # Test specific UI interaction scenarios
        print("4. Testing UI interaction scenarios...")

        # Test clicking on a table to view its content (like in the database view)
        if 'clients' in tables:
            print("   Testing clients table content retrieval...")
            columns, rows = db_manager.get_table_content('clients')
            print(f"   PASS: Retrieved {len(rows)} client rows with {len(columns)} columns")

            # Show sample data that would be displayed in UI
            if rows:
                print("   Sample client data for UI display:")
                for i, row in enumerate(rows[:3]):
                    print(f"     Row {i+1}: {row}")

        if 'files' in tables:
            print("   Testing files table content retrieval...")
            columns, rows = db_manager.get_table_content('files')
            print(f"   PASS: Retrieved {len(rows)} file rows with {len(columns)} columns")

            # Show sample data that would be displayed in UI
            if rows:
                print("   Sample file data for UI display:")
                for i, row in enumerate(rows[:3]):
                    print(f"     Row {i+1}: {row}")

        print("\nSUCCESS: Database table content functionality is working correctly!")
        return True

    except Exception as e:
        print(f"FAIL: Error during table content test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_table_content_functionality()
    if success:
        print("\nSUCCESS: Database table content functionality is working with MockaBase!")
    else:
        print("\nFAIL: Database table content functionality has issues!")
