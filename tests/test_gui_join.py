import sqlite3

conn = sqlite3.connect('server/defensive.db')
cursor = conn.cursor()

print("=== TESTING SERVER-GUI JOIN QUERY ===")

# Test the exact query from get_all_files()
cursor.execute("""
    SELECT f.FileName, f.PathName, f.Verified, c.Name, f.FileSize, f.ModificationDate
    FROM files f JOIN clients c ON f.ClientID = c.ID
""")

files = cursor.fetchall()
print(f"Found {len(files)} files with client information:")

for file in files:
    print(f"  📁 {file[0]} (Client: {file[3]}, Verified: {file[2]}, Size: {file[4]})")

conn.close()
print("\n✅ JOIN query works perfectly!")
