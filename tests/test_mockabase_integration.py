#!/usr/bin/env python3
"""
Test script to verify MockaBase database integration with Flet GUI
"""

import os
import sqlite3


def test_mockabase_integration():
    """Test that MockaBase database is properly integrated"""

    # Check if MockaBase exists
    if not os.path.exists("MockaBase.db"):
        print("FAIL: MockaBase.db not found!")
        return False

    print("PASS: MockaBase.db found")

    # Connect to database
    try:
        conn = sqlite3.connect("MockaBase.db")
        cursor = conn.cursor()
        print("PASS: Successfully connected to MockaBase")
    except Exception as e:
        print(f"FAIL: Failed to connect to MockaBase: {e}")
        return False

    # Check tables exist
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"PASS: Tables found: {tables}")

        if "clients" not in tables:
            print("FAIL: 'clients' table not found")
            return False

        if "files" not in tables:
            print("FAIL: 'files' table not found")
            return False

    except Exception as e:
        print(f"FAIL: Failed to query tables: {e}")
        return False

    # Check clients table schema
    try:
        cursor.execute("PRAGMA table_info(clients)")
        client_columns = [row[1] for row in cursor.fetchall()]
        required_columns = ["ID", "Name", "PublicKey", "LastSeen", "AESKey"]

        for col in required_columns:
            if col not in client_columns:
                print(f"FAIL: Required column '{col}' missing from clients table")
                return False

        print("PASS: Clients table schema verified")

    except Exception as e:
        print(f"FAIL: Failed to verify clients table schema: {e}")
        return False

    # Check files table schema
    try:
        cursor.execute("PRAGMA table_info(files)")
        file_columns = [row[1] for row in cursor.fetchall()]
        required_columns = ["ID", "FileName", "PathName", "Verified", "FileSize", "ModificationDate", "CRC", "ClientID"]

        for col in required_columns:
            if col not in file_columns:
                print(f"FAIL: Required column '{col}' missing from files table")
                return False

        print("PASS: Files table schema verified")

    except Exception as e:
        print(f"FAIL: Failed to verify files table schema: {e}")
        return False

    # Check data exists
    try:
        cursor.execute("SELECT COUNT(*) FROM clients")
        client_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM files")
        file_count = cursor.fetchone()[0]

        print(f"PASS: Data verification: {client_count} clients, {file_count} files")

        if client_count == 0:
            print("FAIL: No client data found")
            return False

        if file_count == 0:
            print("FAIL: No file data found")
            return False

    except Exception as e:
        print(f"FAIL: Failed to verify data: {e}")
        return False

    # Close connection
    conn.close()

    print("SUCCESS: All MockaBase integration tests passed!")
    return True

if __name__ == "__main__":
    print("Testing MockaBase database integration...")
    print("=" * 50)

    if test_mockabase_integration():
        print("\nSUCCESS: MockaBase database integration is working correctly!")
        print("The Flet GUI should now be able to use MockaBase for database operations.")
    else:
        print("\nFAIL: MockaBase database integration has issues!")
        print("Please check the errors above and fix the integration.")
