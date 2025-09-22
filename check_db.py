#!/usr/bin/env python3
"""Quick database inspection script"""

import sqlite3
import os

# Check if database exists
db_path = "defensive.db"
if os.path.exists(db_path):
    print(f"Database {db_path} exists")

    # Connect and inspect
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {[table[0] for table in tables]}")

    # Check each table
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"Table {table_name}: {count} rows")

        # Show sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
        sample_data = cursor.fetchall()
        if sample_data:
            print(f"Sample data from {table_name}:")
            for row in sample_data:
                print(f"  {row}")
        print()

    conn.close()
else:
    print(f"Database {db_path} not found")