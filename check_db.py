import sqlite3
import sys

def check_database():
    try:
        conn = sqlite3.connect('server/defensive.db')
        cursor = conn.cursor()

        print("=== CLIENTS ===")
        cursor.execute('SELECT * FROM clients')
        clients = cursor.fetchall()
        if not clients:
            print("No clients found in database")
        else:
            for client in clients:
                print(f"ID: {client[0]}")
                print(f"Name: {client[1]}")
                if len(client) > 3:
                    print(f"LastSeen: {client[3]}")
                print("---")

        print("\n=== FILES ===")
        cursor.execute('SELECT * FROM files')
        files = cursor.fetchall()
        if not files:
            print("No files found in database")
        else:
            for file in files:
                print(f"ID: {file[0]}")
                print(f"FileName: {file[1]}")
                print(f"PathName: {file[2]}")
                print(f"Verified: {file[3]}")
                if len(file) > 4:
                    print(f"FileSize: {file[4]}")
                print("---")

        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
    sys.stdout.flush()
