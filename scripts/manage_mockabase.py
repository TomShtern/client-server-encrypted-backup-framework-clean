#!/usr/bin/env python3
"""
Regenerate MockaBase Database
Utility script to recreate the MockaBase database with fresh mock data
"""

import os
import sqlite3
import sys


def regenerate_mockabase():
    """Regenerate MockaBase database"""
    print("Regenerating MockaBase database...")

    # Remove existing database
    if os.path.exists("MockaBase.db"):
        try:
            os.remove("MockaBase.db")
            print("Removed existing MockaBase.db")
        except Exception as e:
            print(f"Failed to remove existing database: {e}")
            return False

    # Import and run the creation script
    try:
        sys.path.append("data")
        from create_mockabase import create_mockabase, generate_mock_clients, generate_mock_files

        # Create database with schema
        conn = create_mockabase()
        cursor = conn.cursor()

        # Generate mock data
        generate_mock_clients(cursor, 20)  # Generate 20 clients
        generate_mock_files(cursor, 150)   # Generate 150 files

        # Commit changes
        conn.commit()

        # Verify data
        cursor.execute("SELECT COUNT(*) FROM clients")
        client_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM files")
        file_count = cursor.fetchone()[0]

        print("MockaBase regenerated successfully!")
        print(f"- Clients: {client_count}")
        print(f"- Files: {file_count}")
        print(f"- Database file: {os.path.abspath('MockaBase.db')}")

        # Close connection
        conn.close()

        return True

    except Exception as e:
        print(f"Error regenerating MockaBase: {e}")
        return False

def verify_mockabase():
    """Verify MockaBase database"""
    print("Verifying MockaBase database...")

    if not os.path.exists("MockaBase.db"):
        print("MockaBase.db not found!")
        return False

    try:
        conn = sqlite3.connect("MockaBase.db")
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        if "clients" not in tables or "files" not in tables:
            print("Required tables not found!")
            return False

        # Check data
        cursor.execute("SELECT COUNT(*) FROM clients")
        client_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM files")
        file_count = cursor.fetchone()[0]

        print("Verification successful!")
        print(f"- Tables: {tables}")
        print(f"- Clients: {client_count}")
        print(f"- Files: {file_count}")

        conn.close()
        return True

    except Exception as e:
        print(f"Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("MockaBase Database Manager")
    print("=" * 30)

    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        success = verify_mockabase()
    else:
        success = regenerate_mockabase()
        if success:
            print("\nVerifying regenerated database...")
            success = verify_mockabase()

    if success:
        print("\nOperation completed successfully!")
        sys.exit(0)
    else:
        print("\nOperation failed!")
        sys.exit(1)
