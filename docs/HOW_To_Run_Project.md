🚀 HOW TO RUN THE PROJECT CORRECTLY

  Prerequisites & Setup

  1. Install Dependencies:
  # Install Python dependencies (including the Flask fix I 
  implemented)
  pip install -r requirements.txt

  # Ensure you have CMake and vcpkg set up
  # vcpkg should be in the project directory (already present)     

  2. Build the C++ Client:
  # From the project root directory
  mkdir -p build
  cd build

  # Configure with vcpkg
  cmake .. -DCMAKE_TOOLCHAIN_FILE=../vcpkg/scripts/buildsystem     
  s/vcpkg.cmake

  # Build the C++ client
  cmake --build . --config Release

  # The executable will be at:
  build/Release/EncryptedBackupClient.exe

  Running the 4-Layer System

  Step 1: Start the Python Server (Layer 4)
  # From project root
  cd server
  python server.py
  # Server will start on port 1256 (configurable in port.info)     

  Step 2: Start the Flask API Bridge (Layer 2)
  # From project root
  python cyberbackup_api_server.py
  # Flask API will start on port 9090

  Step 3: Open Web GUI (Layer 1)
  # Open in browser:
  # file:///C:/path/to/Client_Server_Encrypted_Backup_Framewor     
  k/src/client/NewGUIforClient.html
  # OR use the Flask API endpoint (if implemented)

  Step 4: Test File Transfer
  # Use the web interface to select a file and upload
  # OR test directly with the executor:
  python real_backup_executor.py testuser
  "test_backup_file.txt"

  Key Configuration Notes:

  - Ports: Server (1256), Flask API (9090) - ensure these are      
  free
  - Working Directory: Run from project root where
  transfer.info will be created
  - Batch Mode: C++ client uses --batch flag to prevent GUI        
  conflicts
  - File Verification: Check server/received_files/ for
  successful transfers

  Troubleshooting:

  - Port conflicts: Change ports in server/port.info and Flask     
   API
  - File not found: Ensure
  build/Release/EncryptedBackupClient.exe exists
  - Transfer.info errors: Fixed with my
  SynchronizedFileManager implementation
  - Version mismatches: Fixed with my flexible protocol
  compatibility
