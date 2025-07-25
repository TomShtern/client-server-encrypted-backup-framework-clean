import sqlite3
import uuid

def fix_database_schema():
    """Fix the database schema to add ClientID column and migrate data"""
    
    print("=== FIXING DATABASE SCHEMA ===")
    
    # Connect to database
    conn = sqlite3.connect('server/defensive.db')
    cursor = conn.cursor()
    
    try:
        # Check if ClientID column already exists
        cursor.execute("PRAGMA table_info(files)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'ClientID' in columns:
            print("✅ ClientID column already exists")
            return
        
        print("📝 Adding ClientID column to files table...")
        
        # Add ClientID column
        cursor.execute("ALTER TABLE files ADD COLUMN ClientID BLOB(16)")
        
        print("🔄 Migrating existing data...")
        
        # Update existing files to use ID as ClientID and generate new unique IDs
        cursor.execute("SELECT ID, FileName FROM files")
        existing_files = cursor.fetchall()
        
        for file_id, filename in existing_files:
            # The current ID is actually the client ID, so move it to ClientID
            new_file_id = uuid.uuid4().bytes  # Generate new unique file ID
            
            cursor.execute("""
                UPDATE files 
                SET ClientID = ?, ID = ? 
                WHERE ID = ? AND FileName = ?
            """, (file_id, new_file_id, file_id, filename))
        
        print(f"✅ Migrated {len(existing_files)} file records")
        
        # Commit changes
        conn.commit()
        
        print("✅ Database schema fixed successfully!")
        
        # Verify the fix
        print("\n=== VERIFICATION ===")
        cursor.execute("""
            SELECT f.FileName, c.Name 
            FROM files f 
            JOIN clients c ON f.ClientID = c.ID 
            LIMIT 5
        """)
        
        joined_files = cursor.fetchall()
        print(f"✅ JOIN query works! Found {len(joined_files)} files with client names:")
        for filename, client_name in joined_files:
            print(f"  - {filename} (Client: {client_name})")
            
    except Exception as e:
        print(f"❌ Error fixing database schema: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database_schema()
