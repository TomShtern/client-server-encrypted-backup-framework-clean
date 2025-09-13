# MockaBase Database Implementation

THIS SOLUTION WAS CREATED IN THE NOW OBSOLETE `flet_server_gui` SYSTEM, WHICH IS BAD, OVER-ENGINEERED, FIGHTING THE FRAMEWORK, OUTDATED AND NOT USED ANYMORE CODE, BECAUSE WE MOVED TO A MORE CORRECT FLET WAY IN `FletV2`. 
BUT THIS MOCKABASE SOLUTION IS STILL RELEVANT AS IT PROVIDES A MOCK DATABASE FOR DEVELOPMENT AND TESTING PURPOSES.

## Overview

MockaBase is a SQLite3 database with an identical schema to the real backup server database. It serves as a drop-in replacement for development and testing purposes, allowing the Flet GUI to function without requiring a live server connection.

## Purpose

1. **Development Environment**: Enable Flet GUI development without running the full server
2. **Testing**: Provide consistent test data for UI components
3. **Standalone Operation**: Allow the GUI to run independently for demonstration purposes
4. **Seamless Integration**: Enable easy switching between MockaBase and real database

## Database Schema

MockaBase contains two tables that exactly match the real database schema:

### Clients Table
```sql
CREATE TABLE clients (
    ID BLOB(16) PRIMARY KEY,
    Name VARCHAR(255) UNIQUE NOT NULL,
    PublicKey BLOB(160),
    LastSeen TEXT NOT NULL, 
    AESKey BLOB(32) 
)
```

### Files Table
```sql
CREATE TABLE files (
    ID BLOB(16) PRIMARY KEY,
    FileName VARCHAR(255) NOT NULL,
    PathName VARCHAR(255) NOT NULL,
    Verified BOOLEAN DEFAULT 0,
    FileSize INTEGER,
    ModificationDate TEXT,
    CRC INTEGER,
    ClientID BLOB(16) NOT NULL,
    FOREIGN KEY (ClientID) REFERENCES clients(ID) ON DELETE CASCADE
)
```

## Implementation Details

### File Location
- **Database File**: `MockaBase.db` in the project root directory
- **Creation Script**: `data/create_mockabase.py`
- **Verification Script**: `data/verify_mockabase.py`

### Automatic Integration
The Flet GUI automatically detects and uses MockaBase when:
1. No live server connection is available
2. `MockaBase.db` exists in the project root
3. The GUI is running in standalone mode

### Switching to Real Database
To switch from MockaBase to the real database:
1. Delete or rename `MockaBase.db`
2. Start the full server system via `scripts/one_click_build_and_run.py`
3. The GUI will automatically connect to the real database

## Data Generation

MockaBase contains realistic placeholder data:
- **15 mock clients** with realistic names and attributes
- **100 mock files** with various extensions and sizes
- **Realistic timestamps** within the past year
- **Random verification status** for files
- **Valid file sizes** ranging from 1KB to 100MB

## Usage Examples

### Creating MockaBase
```bash
python data/create_mockabase.py
```

### Verifying MockaBase
```bash
python data/verify_mockabase.py
```

### Testing Integration
```bash
python test_mockabase_integration.py
```

### Running Flet GUI with MockaBase
```bash
python flet_server_gui/main.py
```

## Code Changes Summary

### Modified Files
1. **`flet_server_gui/utils/server_data_manager.py`**
   - Added `database_name` parameter to `ServerDataManager`
   - Automatic detection of MockaBase when running standalone

2. **`flet_server_gui/utils/server_bridge.py`**
   - Added `database_name` parameter to `ModularServerBridge`
   - Passes database name to data manager

3. **`flet_server_gui/main.py`**
   - Modified ServerBridge instantiation to use MockaBase when available
   - Automatic fallback to default database when MockaBase not found

### Database Creation Scripts
1. **`data/create_mockabase.py`** - Creates MockaBase with schema and mock data
2. **`data/verify_mockabase.py`** - Verifies MockaBase structure and data
3. **`test_mockabase_integration.py`** - Tests integration with Flet GUI

## Benefits

1. **Zero Configuration**: Works automatically when `MockaBase.db` is present
2. **Identical Interface**: Same database operations as real database
3. **Real Data**: Contains realistic mock data for testing
4. **Easy Switching**: Simple file replacement to switch between mock and real
5. **Development Friendly**: No need to run full server for UI development
6. **Consistent Testing**: Same data every time for predictable testing

## Future Considerations

1. **Data Refresh**: Scripts to refresh mock data periodically
2. **Custom Mock Data**: Ability to generate specific test scenarios
3. **Performance Testing**: Larger datasets for performance evaluation
4. **Schema Evolution**: Automatic updates when real database schema changes

## Troubleshooting

### Common Issues
1. **Database Not Found**: Ensure `MockaBase.db` exists in project root
2. **Schema Mismatch**: Regenerate MockaBase if real database schema changes
3. **Connection Errors**: Verify SQLite3 is available and file permissions are correct

### Regenerating MockaBase
If you need to regenerate the MockaBase database:
```bash
# Remove existing database
rm MockaBase.db

# Create new database with fresh mock data
python data/create_mockabase.py

# Verify the new database
python data/verify_mockabase.py
```