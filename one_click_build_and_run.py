#!/usr/bin/env python3
"""
ONE-CLICK BUILD AND RUN - CyberBackup 3.0 (Python Version)
===========================================================

This Python script does exactly what the .bat file does, but runs in an 
interactive terminal where you can actually press keys when prompted.

Author: Auto-generated for CyberBackup 3.0
Usage: py    print()
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
        if check_appmap_available():
            print("   📈 AppMap:         Recording execution traces")
    except UnicodeEncodeError:
        print("   Web GUI:        http://localhost:9090")
        print("   Server GUI:     Started automatically")
        print("   Backup Server:  Running on port 1256")
        print("   API Server:     Running on port 9090")
        if check_appmap_available():
            print("   AppMap:         Recording execution traces")d_and_run.py
===========================================================
"""

import os
import sys
import subprocess
import time
import psutil
from pathlib import Path

def print_phase(phase_num, total_phases, title):
    """Print phase header"""
    print()
    print(f"[PHASE {phase_num}/{total_phases}] {title}...")
    print("-" * 40)

def run_command(command, shell=True, check_exit=True, cwd=None, timeout=60):
    """Run a command and handle errors with better timeout and path handling"""
    print(f"Running: {command}")
    print()
    
    try:
        # For Windows batch files, ensure proper execution
        if isinstance(command, str) and command.endswith('.bat'):
            # Use absolute path and proper shell execution for batch files
            command = os.path.abspath(command)
        
        result = subprocess.run(
            command, 
            shell=shell, 
            cwd=cwd or os.getcwd(),
            timeout=timeout,
            capture_output=False  # Show output in real-time
        )
        
        if check_exit and result.returncode != 0:
            print()
            print(f"[ERROR] Command failed with exit code: {result.returncode}")
            try:
                input("Press Enter to exit...")
            except EOFError:
                pass
            sys.exit(1)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print()
        print(f"[ERROR] Command timed out after {timeout} seconds: {command}")
        if check_exit:
            try:
                input("Press Enter to exit...")
            except EOFError:
                pass
            sys.exit(1)
        return False
    except Exception as e:
        print()
        print(f"[ERROR] Failed to run command: {e}")
        if check_exit:
            try:
                input("Press Enter to exit...")
            except EOFError:
                pass
            sys.exit(1)
        return False

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

def check_appmap_available():
    """Check if AppMap is available for recording"""
    try:
        result = subprocess.run("appmap-python --help", shell=True, 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False

def check_api_server_status(host='127.0.0.1', port=9090, timeout=2):
    """Check if the Flask API server is running and responsive"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def check_port_available(port=9090):
    """Check if a port is available (not in use)"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.bind(('127.0.0.1', port))
        sock.close()
        return True
    except Exception:
        return False

def check_python_dependencies():
    """Check if required Python dependencies are available"""
    required_modules = ['flask', 'flask_cors', 'psutil']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    return missing_modules

def wait_for_server_startup(host='127.0.0.1', port=9090, max_wait=30, check_interval=1):
    """Wait for server to start with progress feedback"""
    print(f"Waiting for API server to start on {host}:{port}...")
    elapsed = 0
    
    while elapsed < max_wait:
        if check_api_server_status(host, port):
            print(f"[OK] API server is responsive after {elapsed}s")
            return True
        
        # Show progress every 5 seconds
        if elapsed % 5 == 0 and elapsed > 0:
            print(f"[INFO] Still waiting... ({elapsed}s/{max_wait}s)")
        
        time.sleep(check_interval)
        elapsed += check_interval
    
    print(f"[ERROR] API server failed to start within {max_wait} seconds")
    return False

def check_backup_server_status():
    """Check if the Python backup server is running on port 1256"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 1256))
        sock.close()
        return result == 0
    except Exception:
        return False

def cleanup_existing_processes():
    """Clean up existing CyberBackup processes before starting new ones"""
    print("Cleaning up existing CyberBackup processes...")
    print()
    
    terminated_processes = []
    
    try:
        # Get list of all running processes
        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = process.info['cmdline']
                if not cmdline:
                    continue
                
                cmdline_str = ' '.join(cmdline).lower()
                should_terminate = False
                process_type = ""
                
                # Check for CyberBackup related processes
                if 'cyberbackup_api_server.py' in cmdline_str:
                    should_terminate = True
                    process_type = "API Server"
                elif 'src.server.server' in cmdline_str or 'src\\server\\server' in cmdline_str:
                    should_terminate = True
                    process_type = "Backup Server"
                elif 'encryptedbackupclient.exe' in cmdline_str:
                    should_terminate = True
                    process_type = "C++ Client"
                elif any(port_check in cmdline_str for port_check in ['port 9090', 'port 1256', ':9090', ':1256']):
                    # Additional check for processes using our ports
                    if 'python' in cmdline_str and ('flask' in cmdline_str or 'server' in cmdline_str):
                        should_terminate = True
                        process_type = "Port-bound Server"
                
                if should_terminate:
                    print(f"Terminating {process_type} (PID: {process.info['pid']})")
                    try:
                        # Try graceful termination first
                        process.terminate()
                        process.wait(timeout=3)
                        terminated_processes.append(f"{process_type} (PID: {process.info['pid']})")
                    except psutil.TimeoutExpired:
                        # Force kill if graceful termination fails
                        print(f"  Force killing PID {process.info['pid']} (timeout)")
                        process.kill()
                        terminated_processes.append(f"{process_type} (PID: {process.info['pid']}) - Force killed")
                    except psutil.NoSuchProcess:
                        # Process already terminated
                        terminated_processes.append(f"{process_type} (PID: {process.info['pid']}) - Already terminated")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process may have disappeared or we don't have access
                continue
                
    except Exception as e:
        print(f"[WARNING] Error during process cleanup: {e}")
    
    if terminated_processes:
        print()
        print("Terminated processes:")
        for proc in terminated_processes:
            print(f"  - {proc}")
        print()
        print("Waiting for processes to fully terminate...")
        time.sleep(2)  # Give processes time to clean up
    else:
        print("[INFO] No existing CyberBackup processes found")
        print()
    
    # Additional port cleanup - kill any processes still using our ports
    ports_to_clean = [9090, 1256]
    for port in ports_to_clean:
        try:
            for conn in psutil.net_connections():
                # Handle both tuple and named attribute formats for laddr
                conn_port = None
                if hasattr(conn, 'laddr') and conn.laddr:
                    if hasattr(conn.laddr, 'port'):
                        # Named attribute format (newer psutil versions)
                        conn_port = conn.laddr.port
                    elif isinstance(conn.laddr, tuple) and len(conn.laddr) >= 2:
                        # Tuple format (host, port) - older psutil versions
                        conn_port = conn.laddr[1]
                
                if conn_port == port and conn.status == psutil.CONN_LISTEN:
                    try:
                        process = psutil.Process(conn.pid)
                        print(f"Killing process using port {port}: {process.name()} (PID: {conn.pid})")
                        process.terminate()
                        time.sleep(1)
                        if process.is_running():
                            process.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        except Exception as e:
            print(f"[WARNING] Error cleaning port {port}: {e}")
    
    print("[OK] Process cleanup completed!")
    print()

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
    # PHASE 0: CLEANUP EXISTING PROCESSES
    # ========================================================================
    print_phase(0, 7, "Cleaning Up Existing Processes")
    cleanup_existing_processes()
    
    # ========================================================================
    # PHASE 1: PREREQUISITES CHECK
    # ========================================================================
    print_phase(1, 7, "Checking Prerequisites")
    
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
        print("[WARNING] CMake is not installed or not in PATH")
        print("Skipping C++ build phases - will run existing components only")
        skip_build = True
    else:
        print(f"[OK] CMake found: {version.split()[2] if 'version' in version else version}")
        skip_build = False
    
    # Check Git (optional)
    exists, version = check_command_exists("git")
    if exists:
        print("[OK] Git found")
    else:
        print("[WARNING] Git not found (optional but recommended)")
    
    print()
    print("Prerequisites check completed successfully!")
    print()
    
    if not skip_build:
        # ========================================================================
        # PHASE 2: CMAKE CONFIGURATION AND VCPKG SETUP
        # ========================================================================
        print_phase(2, 7, "Configuring Build System")
        
        print("Calling scripts\\build\\configure_cmake.bat for CMake + vcpkg setup...")
        print()
        
        if not run_command("scripts\\build\\configure_cmake.bat", timeout=300):
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
        print_phase(3, 7, "Building C++ Client")
        
        print("Building EncryptedBackupClient.exe with CMake...")
        print("Command: cmake --build build --config Release")
        print()
        
        if not run_command("cmake --build build --config Release", timeout=180):
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
    else:
        print()
        print_phase(2, 7, "Skipping Build System Configuration")
        print("[INFO] CMake not available - skipping build phases")
        print("Will use existing C++ client if available")
        print()
        
        print_phase(3, 7, "Checking Existing C++ Client")
        exe_path = Path("build/Release/EncryptedBackupClient.exe")
        if exe_path.exists():
            print(f"[OK] Found existing C++ client: {exe_path}")
        else:
            alt_path = Path("client/EncryptedBackupClient.exe")
            if alt_path.exists():
                print(f"[OK] Found existing C++ client: {alt_path}")
            else:
                print("[WARNING] No C++ client found - web uploads may not work")
                print("Available locations checked:")
                print(f"  - {exe_path}")
                print(f"  - {alt_path}")
        print()
    
    # ========================================================================
    # PHASE 4: PYTHON ENVIRONMENT SETUP
    # ========================================================================
    print_phase(4, 7, "Setting up Python Environment")
    
    print("Installing Python dependencies from requirements.txt...")
    print()
    
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        result = run_command("pip install -r requirements.txt", check_exit=False, timeout=180)
        if not result:
            print("[WARNING] Some Python dependencies failed to install")
            print("This may cause issues with the API server or GUI")
            print()
        else:
            print("[OK] Python dependencies installed successfully!")
    else:
        print("[WARNING] requirements.txt not found")
        print("Installing basic dependencies manually...")
        run_command("pip install cryptography pycryptodome psutil flask", check_exit=False, timeout=180)
    
    # Install additional GUI dependencies
    print("Installing GUI-specific dependencies...")
    run_command("pip install sentry-sdk flask-cors", check_exit=False, timeout=120)
    
    print()
    
    # ========================================================================
    # PHASE 5: CONFIGURATION VERIFICATION
    # ========================================================================
    print_phase(5, 7, "Verifying Configuration")
    
    # Check if RSA keys exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    private_key = data_dir / "valid_private_key.der"
    if private_key.exists():
        print("[OK] RSA private key found")
    else:
        print("[WARNING] RSA private key missing - generating keys...")
        run_command("python scripts\\security\\key-generation\\create_working_keys.py", check_exit=False, timeout=60)
    
    public_key = data_dir / "valid_public_key.der"
    if public_key.exists():
        print("[OK] RSA public key found")
    else:
        print("[WARNING] RSA public key missing - generating keys...")
        run_command("python scripts\\security\\key-generation\\create_working_keys.py", check_exit=False, timeout=60)
    
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
    print_phase(6, 7, "Launching Services")
    
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
        # Check if AppMap is available for recording
        appmap_available = check_appmap_available()
        
        if appmap_available:
            print("[INFO] AppMap detected - enabling execution recording")
            # Start backup server with AppMap recording
            server_command = [
                "appmap-python", "--record", "process", 
                "python", "-m", "src.server.server"
            ]
            print("Command: appmap-python --record process python -m src.server.server")
        else:
            print("[INFO] AppMap not available - starting server normally")
            # Start backup server normally
            server_command = [sys.executable, "-m", "src.server.server"]
            print(f"Command: {sys.executable} -m src.server.server")
        
        # Start backup server as a module from project root in new console window
        server_process = subprocess.Popen(
            server_command,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        print(f"Python Backup Server started with PID: {server_process.pid}")
        
        if appmap_available:
            print("[INFO] AppMap recording active - execution traces will be generated")
            print("       AppMap data will be saved when the server stops")
        
        # Wait for backup server to actually start listening on port 1256
        print("Waiting for backup server to start listening...")
        backup_server_ready = False
        for attempt in range(15):  # Try for 15 seconds
            if check_backup_server_status():
                backup_server_ready = True
                print(f"[OK] Backup server is listening on port 1256 after {attempt + 1} seconds")
                break
            print(f"  Attempt {attempt + 1}/15: Waiting for backup server...")
            time.sleep(1)
        
        if not backup_server_ready:
            print("[ERROR] Backup server failed to start within 15 seconds")
            print("The API server may fail to connect to the backup server.")
        else:
            print("[OK] Backup server is ready!")
    else:
        print(f"[WARNING] Server file not found: {server_path}")
    
    # ========================================================================
    # ENHANCED API SERVER STARTUP WITH ROBUST VERIFICATION
    # ========================================================================
    
    print("Preparing API Bridge Server (cyberbackup_api_server.py)...")
    
    # Step 1: Check Python dependencies
    print("\nChecking Python dependencies...")
    missing_deps = check_python_dependencies()
    if missing_deps:
        print(f"[ERROR] Missing required Python modules: {', '.join(missing_deps)}")
        print("Please install missing dependencies:")
        for dep in missing_deps:
            if dep == 'flask_cors':
                print(f"  pip install flask-cors")
            else:
                print(f"  pip install {dep}")
        print()
        try:
            input("Press Enter to continue anyway (may cause startup failure)...")
        except EOFError:
            pass
    else:
        print("[OK] All required Python dependencies are available")
    
    # Step 2: Check port availability
    print("\nChecking port availability...")
    if not check_port_available(9090):
        print("[WARNING] Port 9090 appears to be in use")
        print("This may cause the API server to fail to start.")
        print("You can:")
        print("  1. Close other applications using port 9090")
        print("  2. Continue anyway (server may fail to start)")
        print()
        try:
            input("Press Enter to continue...")
        except EOFError:
            pass
    else:
        print("[OK] Port 9090 is available")
    
    # Step 3: Start API server with enhanced error handling
    api_server_path = Path("cyberbackup_api_server.py")
    api_process = None
    server_started_successfully = False
    
    if api_server_path.exists():
        print(f"\nStarting API Bridge Server: {api_server_path}")
        
        try:
            # Start API server in new console window with visible output
            api_process = subprocess.Popen(
                [sys.executable, str(api_server_path)],
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            print(f"API Bridge Server started with PID: {api_process.pid}")
            
            # Step 4: Wait for server to become responsive
            server_started_successfully = wait_for_server_startup()
            
            if server_started_successfully:
                print("[OK] API Bridge Server is running and responsive!")
            else:
                print("[ERROR] API Bridge Server failed to start properly")
                print("\nTroubleshooting steps:")
                print("1. Check if port 9090 is being used by another application")
                print("2. Verify Flask and flask-cors are installed: pip install flask flask-cors")
                print("3. Try running manually: python cyberbackup_api_server.py")
                print("4. Check console windows for error messages")
                
        except Exception as e:
            print(f"[ERROR] Failed to start API server: {str(e)}")
            server_started_successfully = False
    else:
        print(f"[ERROR] API server file not found: {api_server_path}")
        server_started_successfully = False
    
    # Step 5: Open Web GUI only if server started successfully
    if server_started_successfully:
        import webbrowser
        gui_url = "http://127.0.0.1:9090/"
        print(f"\nOpening Web GUI in browser: {gui_url}")
        webbrowser.open(gui_url)
    else:
        print("\n[FALLBACK] Manual startup instructions:")
        print("Since automatic startup failed, you can try:")
        print("1. Open a new terminal/command prompt")
        print("2. Navigate to this directory")
        print("3. Run: python cyberbackup_api_server.py")
        print("4. Wait for server to start, then open: http://127.0.0.1:9090/")
        print()
        try:
            choice = input("Would you like to try opening the browser anyway? (y/N): ").strip().lower()
            if choice in ['y', 'yes']:
                import webbrowser
                gui_url = "http://127.0.0.1:9090/"
                print(f"Opening Web GUI in browser: {gui_url}")
                webbrowser.open(gui_url)
        except EOFError:
            pass
    
    # Enhanced success/status message
    print()
    print("=" * 72)
    if server_started_successfully:
        try:
            print("   ✅ ONE-CLICK BUILD AND RUN COMPLETED SUCCESSFULLY!")
        except UnicodeEncodeError:
            print("   ONE-CLICK BUILD AND RUN COMPLETED SUCCESSFULLY!")
    else:
        try:
            print("   ⚠️  ONE-CLICK BUILD AND RUN COMPLETED WITH ISSUES")
        except UnicodeEncodeError:
            print("   ONE-CLICK BUILD AND RUN COMPLETED WITH ISSUES")
    print("=" * 72)
    print()
    print("CyberBackup 3.0 System Status:")
    print()
    
    # Check actual server status for final report
    backup_server_running = check_backup_server_status()
    api_server_running = check_api_server_status()
    
    try:
        print(f"   [SERVER] Backup Server:  {'[OK] Running on port 1256' if backup_server_running else '[ERROR] Not responding on port 1256'}")
        print(f"   [API] API Server:     {'[OK] Running on port 9090' if api_server_running else '[ERROR] Not responding on port 9090'}")
        print(f"   [GUI] Web GUI:        {'[OK] http://localhost:9090' if api_server_running else '[ERROR] Not available (API server down)'}")
        print(f"   [GUI] Server GUI:     {'[OK] Started automatically' if backup_server_running else '[ERROR] Check server console'}")
    except UnicodeEncodeError:
        print(f"   [SERVER] Backup Server:  {'Running on port 1256' if backup_server_running else 'Not responding on port 1256'}")
        print(f"   [API] API Server:     {'Running on port 9090' if api_server_running else 'Not responding on port 9090'}")
        print(f"   [GUI] Web GUI:        {'http://localhost:9090' if api_server_running else 'Not available (API server down)'}")
        print(f"   [GUI] Server GUI:     {'Started automatically' if backup_server_running else 'Check server console'}")
    print()
    if server_started_successfully and api_server_running:
        print("Next steps:")
        print("   1. The web interface should have opened automatically")
        print("   2. You can upload files through the web GUI")
        print("   3. Monitor transfers in the server GUI window")
        print("   4. Check logs in the console windows for debugging")
        if check_appmap_available():
            print("   5. AppMap traces will be generated in appmap.json when server stops")
    else:
        print("Troubleshooting - If web GUI is not working:")
        print("   1. Check console windows for error messages")
        print("   2. Verify Flask is installed: pip install flask flask-cors")
        print("   3. Try manual startup: python cyberbackup_api_server.py")
        print("   4. Check if port 9090 is blocked by firewall/antivirus")
        print("   5. Restart the script after fixing issues")
    print()
    print("General commands:")
    print("   Tests: python scripts\\testing\\master_test_suite.py")
    print("   Stop services: Close the console windows or press Ctrl+C")
    if check_appmap_available():
        print("   View AppMap data: Use AppMap tools after stopping the server")
    print()
    if server_started_successfully and api_server_running:
        try:
            print("Have a great backup session! 🚀")
        except UnicodeEncodeError:
            print("Have a great backup session!")
    else:
        try:
            print("Please check the troubleshooting steps above 🔧")
        except UnicodeEncodeError:
            print("Please check the troubleshooting steps above")
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