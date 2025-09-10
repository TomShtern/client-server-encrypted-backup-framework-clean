# Development Commands for Client-Server Encrypted Backup Framework - CORRECTED

## Python Flask API Server Development
```bash
# Activate virtual environment (Windows)
flet_venv\Scripts\activate

# Install/update Python dependencies
pip install -r requirements.txt

# Start Flask API server
python server/main.py

# Start Flask API server with debug mode
python server/main.py --debug --host 0.0.0.0 --port 5000

# Run Flask API server with auto-reload
FLASK_ENV=development python server/main.py
```

## JavaScript/HTML Web GUI Development
```bash
# Navigate to GUI directory
cd gui

# Install JavaScript dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## C++ Client Development
```batch
# Build the C++ client
.\build.bat

# Clean build artifacts
.\clean.bat

# Run the C++ client
.\start_client.bat
```

## Flet Desktop GUI Development
```bash
# Run Flet desktop GUI
python FletV2/main.py

# Run Flet GUI with web browser view (development)
python -m flet run FletV2/main.py --web

# Run Flet GUI with specific window size
python FletV2/main.py --width 1730 --height 1425
```

## Full System Development
```batch
# Terminal 1: Start Flask API server
python server/main.py --debug

# Terminal 2: Start web GUI
cd gui && npm run dev

# Terminal 3: Start Flet desktop GUI
python FletV2/main.py

# Terminal 4: Start C++ client (after building)
.\start_client.bat
```

## Database Operations
```bash
# Access SQLite3 database directly
sqlite3 backup.db

# Run database migrations (if applicable)
python server/manage.py db upgrade

# Backup database
sqlite3 backup.db ".backup backup_backup.db"

# Check database integrity
sqlite3 backup.db "PRAGMA integrity_check;"
```

## Testing and Quality - CORRECTED
```bash
# Run consolidated test suite
python tests\consolidated_tests.py

# Run Flask API tests
python -m pytest tests/test_api.py -v

# Run C++ client tests
# (Add C++ test commands based on your test framework)

# Run JavaScript tests
cd gui && npm test

# Run end-to-end tests
python tests/test_e2e.py
```

## Configuration Files - CORRECTED
- `transfer.info`: C++ client configuration (server address, username, file path)
- `server/config.py`: Flask API server configuration
- `gui/package.json`: JavaScript dependencies and scripts
- `requirements.txt`: Python dependencies for Flask API and Flet GUI
- `flet_venv/`: Python virtual environment
- `backup.db`: SQLite3 database file

## Development Workflow - CORRECTED
1. **Backend Development**: Work in `server/` directory (Flask API)
2. **Frontend Development**: Work in `gui/` directory (JavaScript/HTML)
3. **Desktop GUI**: Work in `FletV2/` directory (Flet)
4. **Client Development**: Work in `src/client/` directory (C++)
5. **Shared Utilities**: Use `Shared/` for cross-project code
6. **Database**: SQLite3 file `backup.db` in project root

## Debugging - CORRECTED
- **Flask API**: Use `flask run --debug` or set `FLASK_ENV=development`
- **Web GUI**: Use browser dev tools, check network tab for API calls
- **Flet GUI**: Use `python -m flet run --web` for browser debugging
- **C++ Client**: Use Visual Studio debugger or logging
- **Database**: Use `sqlite3 backup.db` for direct database inspection
- **Cross-component**: Check `appmap.log` for unified logging

## Deployment Commands
```bash
# Build C++ client for release
.\build.bat --release

# Build web GUI for production
cd gui && npm run build

# Package Flask API server
python setup.py sdist bdist_wheel

# Create deployment package
# (Add deployment scripts as needed)
```