#!/usr/bin/env python3
"""
ONE-CLICK BUILD AND RUN - CyberBackup 3.0 (Python Version)
===========================================================

This Python script does exactly what the .bat file does, but runs in an 
interactive terminal where you can actually press keys when prompted.

Author: Auto-generated for CyberBackup 3.0
Usage: python one_click_build_and_run.py
===========================================================
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_phase(phase_num, total_phases, title):
    """Print phase header"""
    print()
    print(f"[PHASE {phase_num}/{total_phases}] {title}...")
    print("-" * 40)

def run_command(command, shell=True, check_exit=True):
    """Run a command and handle errors"""
    print(f"Running: {command}")
    print()
    
    result = subprocess.run(command, shell=shell)
    
    if check_exit and result.returncode != 0:
        print()
        print(f"[ERROR] Command failed with exit code: {result.returncode}")
        try:
            input("Press Enter to exit...")
        except EOFError:
            pass
        sys.exit(1)
    
    return result.returncode == 0

def check_command_exists(command):
    """Check if a command exists"""
    # Special case for Python - if we're running this script, Python exists
    if command == "python":
        return True, f"Python {sys.version.split()[0]}"
    
    try:
        result = subprocess.run(f"{command} --version", shell=True, 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        print(f"[DEBUG] Command check failed for {command}: {e}")
        return False, ""

def main():
    # Set UTF-8 encoding for emoji support
    try:
        os.system("chcp 65001 > nul")
    except:
        pass
    
    print()
    print("=" * 72)
    try:
        print("   🚀 ONE-CLICK BUILD AND RUN - CyberBackup 3.0")
    except UnicodeEncodeError:
        print("   ONE-CLICK BUILD AND RUN - CyberBackup 3.0")
    print("=" * 72)
    print()
    print("Starting complete build and deployment process...")
    print("This will configure, build, and launch the entire backup framework.")
    print()
    
    # Change to project root directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")
    print()
    
    # ========================================================================
    # PHASE 1: PREREQUISITES CHECK
    # ========================================================================
    print_phase(1, 6, "Checking Prerequisites")
    
    # Check Python
    exists, version = check_command_exists("python")
    if not exists:
        print("[ERROR] Python is not installed or not in PATH")
        print("Please install Python 3.x and add it to your PATH")
        try:
            input("Press Enter to exit...")
        except EOFError:
            pass
        sys.exit(1)
    print(f"[OK] Python found: {version.split()[1] if version else 'Unknown version'}")
    
    # Check CMake
    exists, version = check_command_exists("cmake")
    if not exists:
        print("[ERROR] CMake is not installed or not in PATH")
        print("Please install CMake 3.15+ and add it to your PATH")
        try:
            input("Press Enter to exit...")
        except EOFError:
            pass
        sys.exit(1)
    print(f"[OK] CMake found: {version.split()[2] if 'version' in version else version}")
    
    # Check Git (optional)
    exists, version = check_command_exists("git")
    if exists:
        print("[OK] Git found")
    else:
        print("[WARNING] Git not found (optional but recommended)")
    
    print()
    print("Prerequisites check completed successfully!")
    print()
    
    # ========================================================================
    # PHASE 2: CMAKE CONFIGURATION AND VCPKG SETUP
    # ========================================================================
    print_phase(2, 6, "Configuring Build System")
    
    print("Calling scripts\\build\\configure_cmake.bat for CMake + vcpkg setup...")
    print()
    
    if not run_command("call scripts\\build\\configure_cmake.bat"):
        print()
        print("[ERROR] CMake configuration failed!")
        print("Check the output above for details.")
        try:
            input("Press Enter to exit...")
        except EOFError:
            pass
        sys.exit(1)
    
    print()
    print("[OK] CMake configuration completed successfully!")
    print()
    
    # ========================================================================
    # PHASE 3: BUILD C++ CLIENT
    # ========================================================================
    print_phase(3, 6, "Building C++ Client")
    
    print("Building EncryptedBackupClient.exe with CMake...")
    print("Command: cmake --build build --config Release")
    print()
    
    if not run_command("cmake --build build --config Release"):
        print()
        print("[ERROR] C++ client build failed!")
        print("Check the compiler output above for details.")
        try:
            input("Press Enter to exit...")
        except EOFError:
            pass
        sys.exit(1)
    
    # Verify the executable was created
    exe_path = Path("build/Release/EncryptedBackupClient.exe")
    if not exe_path.exists():
        print("[ERROR] EncryptedBackupClient.exe was not created!")
        print(f"Expected location: {exe_path}")
        try:
            input("Press Enter to exit...")
        except EOFError:
            pass
        sys.exit(1)
    
    print()
    print("[OK] C++ client built successfully!")
    print(f"   Location: {exe_path}")
    print()
    
    # ========================================================================
    # PHASE 4: PYTHON ENVIRONMENT SETUP
    # ========================================================================
    print_phase(4, 6, "Setting up Python Environment")
    
    print("Installing Python dependencies from requirements.txt...")
    print()
    
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        result = run_command("pip install -r requirements.txt", check_exit=False)
        if not result:
            print("[WARNING] Some Python dependencies failed to install")
            print("This may cause issues with the API server or GUI")
            print()
        else:
            print("[OK] Python dependencies installed successfully!")
    else:
        print("[WARNING] requirements.txt not found")
        print("Installing basic dependencies manually...")
        run_command("pip install cryptography pycryptodome psutil flask", check_exit=False)
    
    print()
    
    # ========================================================================
    # PHASE 5: CONFIGURATION VERIFICATION
    # ========================================================================
    print_phase(5, 6, "Verifying Configuration")
    
    # Check if RSA keys exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    private_key = data_dir / "valid_private_key.der"
    if private_key.exists():
        print("[OK] RSA private key found")
    else:
        print("[WARNING] RSA private key missing - generating keys...")
        run_command("python scripts\\create_working_keys.py", check_exit=False)
    
    public_key = data_dir / "valid_public_key.der"
    if public_key.exists():
        print("[OK] RSA public key found")
    else:
        print("[WARNING] RSA public key missing - generating keys...")
        run_command("python scripts\\create_working_keys.py", check_exit=False)
    
    # Check if transfer.info exists
    transfer_info = data_dir / "transfer.info"
    if transfer_info.exists():
        print("[OK] transfer.info configuration found")
    else:
        print("[WARNING] Creating default transfer.info...")
        with open(transfer_info, 'w') as f:
            f.write("127.0.0.1:1256\n")
            f.write("testuser\n")
            f.write("test_file.txt\n")
    
    print()
    print("[OK] Configuration verification completed!")
    print()
    
    # ========================================================================
    # PHASE 6: LAUNCH SERVICES
    # ========================================================================
    print_phase(6, 6, "Launching Services")
    
    print("Starting the complete CyberBackup 3.0 system...")
    print()
    print("Services that will be started:")
    print("   - Backup Server (Port 1256)")
    print("   - API Bridge Server (Port 9090)")
    print("   - Web GUI (Browser interface)")
    print()
    
    print("Starting Python Backup Server (src.server.server module)...")
    server_path = Path("src/server/server.py")
    if server_path.exists():
        # Start backup server as a module from project root in new console window
        server_process = subprocess.Popen(
            [sys.executable, "-m", "src.server.server"],
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        print(f"Python Backup Server started with PID: {server_process.pid}")
        time.sleep(3)  # Give server time to start
    else:
        print(f"[WARNING] Server file not found: {server_path}")
    
    print("Starting API Bridge Server (cyberbackup_api_server.py)...")
    api_server_path = Path("cyberbackup_api_server.py") 
    if api_server_path.exists():
        # Start API server in new console window
        api_process = subprocess.Popen(
            [sys.executable, str(api_server_path)],
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        print(f"API Bridge Server started with PID: {api_process.pid}")
        time.sleep(3)  # Give API server time to start
    else:
        print(f"[WARNING] API server file not found: {api_server_path}")
    
    # Open Web GUI in browser
    import webbrowser
    gui_url = "http://127.0.0.1:9090/"
    print(f"Opening Web GUI in browser: {gui_url}")
    webbrowser.open(gui_url)
    
    # Success message
    print()
    print("=" * 72)
    try:
        print("   ✅ ONE-CLICK BUILD AND RUN COMPLETED SUCCESSFULLY!")
    except UnicodeEncodeError:
        print("   ONE-CLICK BUILD AND RUN COMPLETED SUCCESSFULLY!")
    print("=" * 72)
    print()
    print("Your CyberBackup 3.0 system should now be running with:")
    print()
    try:
        print("   📊 Web GUI:        http://localhost:9090")
        print("   🖥️  Server GUI:     Started automatically")
        print("   🔒 Backup Server:  Running on port 1256")
        print("   🌐 API Server:     Running on port 9090")
    except UnicodeEncodeError:
        print("   Web GUI:        http://localhost:9090")
        print("   Server GUI:     Started automatically")
        print("   Backup Server:  Running on port 1256")
        print("   API Server:     Running on port 9090")
    print()
    print("Next steps:")
    print("   1. The web interface should have opened automatically")
    print("   2. You can upload files through the web GUI")
    print("   3. Monitor transfers in the server GUI window")
    print("   4. Check logs in the console windows for debugging")
    print()
    print("To run tests: python scripts\\master_test_suite.py")
    print("To stop services: Close the console windows or press Ctrl+C")
    print()
    try:
        print("Have a great backup session! 🚀")
    except UnicodeEncodeError:
        print("Have a great backup session!")
    print("=" * 72)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Build process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] An unexpected error occurred: {e}")
        try:
            input("Press Enter to exit...")
        except EOFError:
            pass
        sys.exit(1)