#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic script to test database functionality step by step
"""

# Import UTF-8 solution first to fix encoding issues
import Shared.utils.utf8_solution

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from python_server.server.database import DatabaseManager

def diagnose_database_issues():
    """Diagnose database functionality step by step"""
    
    print("Database Functionality Diagnostic")
    print("=" * 40)
    
    try:
        # Test 1: Initialize database manager
        print("1. Testing DatabaseManager initialization...")
        db_manager = DatabaseManager("MockaBase.db")
        print("   PASS: DatabaseManager initialized successfully")
        
        # Test 2: Test table names
        print("2. Testing table names retrieval...")
        tables = db_manager.get_table_names()
        print(f"   PASS: Tables found: {tables}")
        
        # Test 3: Test table content for each table
        for table_name in tables:
            print(f"3. Testing content retrieval for '{table_name}'...")
            try:
                columns, rows = db_manager.get_table_content(table_name)
                print(f"   PASS: Table '{table_name}': {len(columns)} columns, {len(rows)} rows")
                if columns:
                    print(f"     Columns: {columns}")
                if rows and len(rows) > 0:
                    print(f"     Sample row: {dict(list(rows[0].items())[:3])}")
            except Exception as e:
                print(f"   FAIL: Error retrieving content for '{table_name}': {e}")
        
        # Test 4: Test specific database methods
        print("4. Testing specific database methods...")
        
        # Test get_database_stats
        try:
            stats = db_manager.get_database_stats()
            print(f"   PASS: get_database_stats: {stats}")
        except Exception as e:
            print(f"   FAIL: Error in get_database_stats: {e}")
        
        # Test get_all_clients
        try:
            clients = db_manager.get_all_clients()
            print(f"   PASS: get_all_clients: {len(clients)} clients")
            if clients:
                print(f"     Sample client: {clients[0] if len(clients) > 0 else 'None'}")
        except Exception as e:
            print(f"   FAIL: Error in get_all_clients: {e}")
        
        # Test get_all_files
        try:
            files = db_manager.get_all_files()
            print(f"   PASS: get_all_files: {len(files)} files")
            if files:
                print(f"     Sample file: {files[0] if len(files) > 0 else 'None'}")
        except Exception as e:
            print(f"   FAIL: Error in get_all_files: {e}")
        
        print("\nDiagnostic completed successfully!")
        return True
        
    except Exception as e:
        print(f"FAIL: Diagnostic failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    diagnose_database_issues()