#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test get_table_names method directly
"""

# Import UTF-8 solution first to fix encoding issues
import Shared.utils.utf8_solution

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from python_server.server.database import DatabaseManager
import sqlite3

def test_get_table_names():
    """Test the get_table_names method directly"""
    
    print("Testing get_table_names method...")
    print("=" * 40)
    
    try:
        # Test 1: Check directly with SQLite
        print("1. Direct SQLite table query...")
        conn = sqlite3.connect("MockaBase.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        direct_result = cursor.fetchall()
        direct_tables = [row[0] for row in direct_result]
        print(f"   Direct query result: {direct_tables}")
        conn.close()
        
        # Test 2: Check with DatabaseManager
        print("2. DatabaseManager get_table_names method...")
        db_manager = DatabaseManager("MockaBase.db")
        manager_tables = db_manager.get_table_names()
        print(f"   DatabaseManager result: {manager_tables}")
        
        # Test 3: Check the exact query used by get_table_names
        print("3. Testing exact query used by get_table_names...")
        result = db_manager.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """, fetchall=True)
        print(f"   Exact query result: {result}")
        
        if set(direct_tables) == set(manager_tables):
            print("   PASS: Both methods return the same tables")
        else:
            print("   FAIL: Methods return different results")
            return False
            
        print("\nSUCCESS: get_table_names method is working correctly!")
        return True
        
    except Exception as e:
        print(f"FAIL: Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_get_table_names()
    if success:
        print("\nSUCCESS: Table names retrieval is working!")
    else:
        print("\nFAIL: Table names retrieval has issues!")
