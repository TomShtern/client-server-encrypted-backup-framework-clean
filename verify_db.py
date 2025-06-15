import sqlite3

conn = sqlite3.connect('defensive.db')
cursor = conn.cursor()

print('=== DATABASE VERIFICATION ===')

# Get tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print(f'Tables: {[t[0] for t in tables]}')

# Check clients
cursor.execute('SELECT * FROM clients LIMIT 3')
clients = cursor.fetchall()
print(f'Clients: {len(clients)}')
for client in clients:
    print(f'  Client: {client}')

# Check files
cursor.execute('SELECT * FROM files ORDER BY rowid DESC LIMIT 3')
files = cursor.fetchall()
print(f'Recent files: {len(files)}')
for file_info in files:
    print(f'  File: {file_info}')

conn.close()
