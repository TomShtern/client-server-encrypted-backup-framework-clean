import sqlite3

conn = sqlite3.connect('server/defensive.db')
cursor = conn.cursor()

print("=== TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"Table: {table[0]}")

print("\n=== FILES SCHEMA ===")
cursor.execute("PRAGMA table_info(files)")
file_schema = cursor.fetchall()
for col in file_schema:
    print(f"  {col[1]} ({col[2]})")

print("\n=== CLIENTS SCHEMA ===")
cursor.execute("PRAGMA table_info(clients)")
client_schema = cursor.fetchall()
for col in client_schema:
    print(f"  {col[1]} ({col[2]})")

print("\n=== FILES DATA ===")
cursor.execute("SELECT ID, FileName, ClientID FROM files LIMIT 5")
files = cursor.fetchall()
for file in files:
    print(f"  File: ID={file[0]}, Name={file[1]}, ClientID={file[2] if len(file) > 2 else 'N/A'}")

print("\n=== CLIENTS DATA ===")
cursor.execute("SELECT ID, Name FROM clients LIMIT 5")
clients = cursor.fetchall()
for client in clients:
    print(f"  Client: ID={client[0]}, Name={client[1]}")

conn.close()
print("Done!")
