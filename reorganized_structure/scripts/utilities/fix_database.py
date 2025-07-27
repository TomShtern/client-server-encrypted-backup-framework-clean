#!/usr/bin/env python3
"""
Database repair script for the Encrypted Backup Server
"""

import sys
import os
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_database():
    """Fix the database by ensuring all tables exist"""
    
    # Change to server directory
    os.chdir('server')
    
    # Add server directory to path
    sys.path.insert(0, '.')
    
    try:
        print("🔧 Starting database repair...")
        
        # Import database manager
        from database import DatabaseManager
        
        print("✅ DatabaseManager imported successfully")
        
        # Create database manager instance
        db_manager = DatabaseManager()
        print(f"✅ Database manager created for: {db_manager.db_name}")
        
        # Check if database file exists
        if os.path.exists(db_manager.db_name):
            print(f"📁 Database file exists: {db_manager.db_name}")
        else:
            print(f"❌ Database file missing: {db_manager.db_name}")
        
        # Initialize database schema
        print("🔨 Initializing database schema...")
        db_manager.init_database()
        print("✅ Database schema initialized successfully!")
        
        # Verify tables exist
        print("🔍 Verifying tables...")
        with sqlite3.connect(db_manager.db_name) as conn:
            cursor = conn.cursor()
            
            # Check for clients table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
            if cursor.fetchone():
                print("✅ 'clients' table exists")
            else:
                print("❌ 'clients' table missing")
            
            # Check for files table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")
            if cursor.fetchone():
                print("✅ 'files' table exists")
            else:
                print("❌ 'files' table missing")
            
            # Show all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"📋 All tables in database: {[table[0] for table in tables]}")
        
        print("🎉 Database repair completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during database repair: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_database()
    if success:
        print("\n✅ Database is now ready for server startup!")
    else:
        print("\n❌ Database repair failed!")
    input("Press Enter to exit...")
