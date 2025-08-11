#!/usr/bin/env python3
"""
Test script to directly start the server GUI and verify it shows files
"""

import sys
import os

# Add server directory to path
from Shared.path_utils import setup_imports
setup_imports()

try:
    from ServerGUI import ServerGUI
    print("✅ ServerGUI imported successfully")
    
    # Create and initialize GUI
    gui = ServerGUI()
    print("✅ ServerGUI instance created")
    
    # Test database connection
    if hasattr(gui, 'server') and gui.server and hasattr(gui.server, 'db_manager'):
        files = gui.server.db_manager.get_all_files()
        print(f"✅ Found {len(files)} files in database:")
        for file in files:
            print(f"  📁 {file['filename']} (Client: {file['client']})")
    else:
        print("⚠️  GUI doesn't have server/db_manager, testing direct database access...")
        
        # Test direct database access
        import sqlite3
        conn = sqlite3.connect('server/defensive.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT f.FileName, f.PathName, f.Verified, c.Name, f.FileSize, f.ModificationDate
            FROM files f JOIN clients c ON f.ClientID = c.ID
        """)
        
        files = cursor.fetchall()
        print(f"✅ Direct database query found {len(files)} files:")
        for file in files:
            print(f"  📁 {file[0]} (Client: {file[3]})")
        
        conn.close()
    
    print("\n🚀 Starting GUI...")
    if gui.initialize():
        print("✅ GUI initialized successfully!")
        print("🎯 The server-gui should now be visible and showing the files!")
        print("📋 Files should be displayed in the GUI with their client names.")
    else:
        print("❌ GUI initialization failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
