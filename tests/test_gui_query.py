import os
import sqlite3


def test_gui_queries():
    """Test the exact queries that the server-gui uses"""
    try:
        # Add server directory to path
        from Shared.path_utils import setup_imports
        setup_imports()

        # Test database connection
        db_path = "server/defensive.db"
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("=== TESTING SERVER-GUI QUERIES ===")

        # Test 1: Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in database: {[t[0] for t in tables]}")

        # Test 2: Check clients table
        print("\n=== CLIENTS TABLE ===")
        cursor.execute("SELECT * FROM clients")
        clients = cursor.fetchall()
        print(f"Clients count: {len(clients)}")
        for client in clients:
            print(f"Client: ID={client[0]}, Name={client[1]}")

        # Test 3: Check files table
        print("\n=== FILES TABLE ===")
        cursor.execute("SELECT * FROM files")
        files = cursor.fetchall()
        print(f"Files count: {len(files)}")
        for file in files:
            print(f"File: ID={file[0]}, Name={file[1]}, ClientID={file[5] if len(file) > 5 else 'N/A'}")

        # Test 4: The exact JOIN query from server-gui
        print("\n=== SERVER-GUI JOIN QUERY ===")
        try:
            # This is the exact query from database.py get_all_files()
            cursor.execute("""
                SELECT f.ID, f.FileName, f.PathName, f.Verified, f.FileSize, c.Name as ClientName
                FROM files f
                JOIN clients c ON f.ID = c.ID
            """)
            joined_files = cursor.fetchall()
            print(f"JOIN result count: {len(joined_files)}")
            for file in joined_files:
                print(f"Joined: FileID={file[0]}, FileName={file[1]}, ClientName={file[5]}")
        except Exception as e:
            print(f"JOIN query failed: {e}")

            # Try alternative JOIN on ClientID
            print("\nTrying alternative JOIN on ClientID...")
            try:
                cursor.execute("""
                    SELECT f.ID, f.FileName, f.PathName, f.Verified, f.FileSize, c.Name as ClientName
                    FROM files f
                    JOIN clients c ON f.ClientID = c.ID
                """)
                joined_files = cursor.fetchall()
                print(f"Alternative JOIN result count: {len(joined_files)}")
                for file in joined_files:
                    print(f"Alt Joined: FileID={file[0]}, FileName={file[1]}, ClientName={file[5]}")
            except Exception as e2:
                print(f"Alternative JOIN also failed: {e2}")

        # Test 5: Check file table schema
        print("\n=== FILES TABLE SCHEMA ===")
        cursor.execute("PRAGMA table_info(files)")
        file_schema = cursor.fetchall()
        for col in file_schema:
            print(f"Column: {col[1]} ({col[2]})")

        # Test 6: Check clients table schema
        print("\n=== CLIENTS TABLE SCHEMA ===")
        cursor.execute("PRAGMA table_info(clients)")
        client_schema = cursor.fetchall()
        for col in client_schema:
            print(f"Column: {col[1]} ({col[2]})")

        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gui_queries()
