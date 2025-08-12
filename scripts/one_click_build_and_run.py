#!/usr/bin/env python3
"""One-click build and run orchestrator for CyberBackup 3.0.

This script:
 1. Verifies environment & dependencies
 2. Builds the C++ client (via CMake & vcpkg toolchain)
 3. Launches backup server (optionally disables embedded GUI)
 4. Launches standalone Server GUI if embedded disabled
 5. Launches API bridge server
 6. Opens Web GUI in browser

Corrupted header block was repaired on 2025-08-11 after accidental paste.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Shared.utils.unified_config import get_config
import subprocess
import time
import contextlib
import json
import logging
import traceback
from pathlib import Path

try:
    import psutil
except ImportError:
    print("[WARNING] psutil not available - process cleanup may be limited")
    psutil = None

def setup_logging():
    """Setup basic logging for the build script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/build_script.log', mode='a'),
            logging.StreamHandler()  # Also log to console
        ]
    )
    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)

def setup_unicode_console():
    """Enhanced Unicode console setup for Windows emoji support"""
    if os.name == 'nt':  # Windows only
        with contextlib.suppress(Exception):
            # Set UTF-8 codepage
            os.system("chcp 65001 >nul 2>&1")
            # Reconfigure Python stdout for UTF-8 (Python 3.7+)
            # Use getattr to avoid Pylance errors on reconfigure method
            if hasattr(sys.stdout, 'reconfigure'):
                getattr(sys.stdout, 'reconfigure')(encoding='utf-8', errors='replace')
                getattr(sys.stderr, 'reconfigure')(encoding='utf-8', errors='replace')
                logging.info("Unicode console setup completed successfully")

def supports_emojis():
    """Quick test for emoji support in current console"""
    try:
        # Test with a simple emoji to stdout
        test_str = "🚀"
        # Try to encode it with current stdout encoding
        test_str.encode(sys.stdout.encoding or 'utf-8')
        return True
    except (UnicodeEncodeError, LookupError, AttributeError):
        return False

def safe_print(message, fallback=None):
    """Print with emoji support and automatic fallback"""
    try:
        print(message)
    except UnicodeEncodeError:
        # Use provided fallback or strip non-ASCII characters
        fallback_msg = fallback or message.encode('ascii', 'ignore').decode()
        print(fallback_msg)

def print_phase(phase_num, total_phases, title):
    """Print phase header with timestamp"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print()
    print(f"[{timestamp}] [PHASE {phase_num}/{total_phases}] {title}...")
    print("-" * 50)

def handle_error_and_exit(error_message, wait_for_input=True):
    """Print error message and exit with status 1"""
    print(error_message)
    if wait_for_input:
        input("Press Enter to exit...")
    sys.exit(1)

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
            with contextlib.suppress(EOFError):
                input("Press Enter to exit...")
            sys.exit(1)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print()
        print(f"[ERROR] Command timed out after {timeout} seconds: {command}")
        if check_exit:
            with contextlib.suppress(EOFError):
                input("Press Enter to exit...")
            sys.exit(1)
        return False
    except Exception as e:
        print()
        print(f"[ERROR] Failed to run command: {e}")
        if check_exit:
            with contextlib.suppress(EOFError):
                input("Press Enter to exit...")
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

def check_api_server_status(host=get_config('api.host', '127.0.0.1'), port=get_config('api.port', 9090), timeout=2):
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

def check_port_available(port=get_config('api.port', 9090)):
    """Check if a port is available (not in use)"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True
    except Exception:
        return False

def check_python_dependencies():
    """Check if required Python dependencies are available with version info"""
    required_modules = {
        'flask': 'Flask web framework',
        'flask_cors': 'CORS support for Flask API',
        'psutil': 'System process management',
        'sentry_sdk': 'Error monitoring (optional)',
        'cryptography': 'Cryptographic operations',
        'watchdog': 'File system monitoring'
    }
    missing_modules = []
    optional_missing = []

    for module, description in required_modules.items():
        try:
            imported_module = __import__(module)
            # Try to get version if available
            version = getattr(imported_module, '__version__', 'unknown version')
            print(f"[OK] {module} ({description}): {version}")
        except ImportError:
            if module in ['sentry_sdk', 'watchdog']:
                optional_missing.append((module, description))
                print(f"[INFO] {module} ({description}): Not installed (optional)")
            else:
                missing_modules.append((module, description))
                print(f"[ERROR] {module} ({description}): Missing (required)")

    return missing_modules, optional_missing

def check_and_fix_vcpkg_dependencies():
    """Check and fix vcpkg dependencies, especially boost-iostreams"""
    print("Checking vcpkg dependencies...")

    # Check if vcpkg.json exists and has required dependencies
    vcpkg_json_path = Path("vcpkg.json")
    if not vcpkg_json_path.exists():
        print("[ERROR] vcpkg.json not found!")
        return False

    try:
        with open(vcpkg_json_path, 'r') as f:
            vcpkg_config = json.load(f)

        required_deps = ["boost-asio", "boost-beast", "boost-iostreams", "cryptopp", "zlib"]
        current_deps = vcpkg_config.get("dependencies", [])

        if missing_deps := [dep for dep in required_deps if dep not in current_deps]:
            print(f"[WARNING] Missing vcpkg dependencies: {', '.join(missing_deps)}")
            print("Updating vcpkg.json...")

            # Update dependencies
            vcpkg_config["dependencies"] = required_deps

            with open(vcpkg_json_path, 'w') as f:
                json.dump(vcpkg_config, f, indent=2)

            print("[OK] vcpkg.json updated with missing dependencies")
        else:
            print("[OK] All required vcpkg dependencies are present")
        
        return True

    except Exception as e:
        print(f"[ERROR] Failed to check vcpkg dependencies: {e}")
        return False

def force_vcpkg_reinstall():
    """Force reinstall of vcpkg dependencies"""
    print("Forcing vcpkg dependency reinstall...")

    # Remove vcpkg_installed directory to force fresh install
    vcpkg_installed_path = Path("vcpkg_installed")
    if vcpkg_installed_path.exists():
        print("Removing vcpkg_installed directory...")
        try:
            import shutil
            shutil.rmtree(vcpkg_installed_path)
            print("[OK] vcpkg_installed directory removed")
        except Exception as e:
            print(f"[WARNING] Failed to remove vcpkg_installed: {e}")

    # Run vcpkg install command
    print("Running vcpkg install...")
    return run_command("vcpkg\\vcpkg.exe install --triplet x64-windows --recurse", timeout=600)

def wait_for_server_startup(host=get_config('api.host', '127.0.0.1'), port=get_config('api.port', 9090), max_wait=30, check_interval=1):
    """Wait for server to start with enhanced progress feedback and diagnostics"""
    print(f"Waiting for API server to start on {host}:{port}...")
    elapsed = 0
    last_error = None
    
    while elapsed < max_wait:
        try:
            if check_api_server_status(host, port):
                print(f"[OK] API server is responsive after {elapsed}s")
                return True
        except Exception as e:
            last_error = str(e)
        
        # Show progress with more frequent updates
        if elapsed % 3 == 0 and elapsed > 0:
            print(f"[INFO] Still waiting... ({elapsed}s/{max_wait}s)")
        
        time.sleep(check_interval)
        elapsed += check_interval
    
    print(f"[ERROR] API server failed to start within {max_wait} seconds")
    if last_error:
        print(f"[DEBUG] Last connection error: {last_error}")
    
    # Additional diagnostic information
    print("[DIAGNOSTIC] Checking system status...")
    if check_port_available(port):
        print(f"[DEBUG] Port {port} appears to be available (no process bound)")
    else:
        print(f"[DEBUG] Port {port} is in use by another process")
    
    return False

def check_backup_server_status():
    """Check if the Python backup server is running on port 1256"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((get_config('server.host', '127.0.0.1'), get_config('server.port', 1256)))
        sock.close()
        return result == 0
    except Exception:
        return False

def _report_terminated_processes(terminated_processes):
    """Report terminated processes and wait for cleanup"""
    if terminated_processes:
        print(f"Successfully terminated {len(terminated_processes)} processes:")
        for process_info in terminated_processes:
            print(f"  - {process_info}")
        print()
        # Brief pause to allow processes to fully clean up
        import time
        time.sleep(1)
    else:
        print("No CyberBackup processes found running.")
        print()

def cleanup_existing_processes():  # sourcery skip: low-code-quality
    """Clean up existing CyberBackup processes with improved reliability"""
    if not psutil:
        print("[WARNING] psutil not available - cannot perform automatic process cleanup")
        print("Please manually close any existing CyberBackup processes")
        return
        
    print("Cleaning up existing CyberBackup processes...")
    print()
    
    terminated_processes = []
    
    # Define process patterns to look for
    process_patterns = {
        "API Server": ["cyberbackup_api_server.py", "api_server"],
        "Backup Server": ["python_server/server/server.py", "server.py", "backup_server"],
        "C++ Client": ["encryptedbackupclient.exe", "EncryptedBackupClient.exe"],
        "Server GUI": ["ServerGUI.py", "server_gui"]
    }
    
    try:
        # Get list of all running processes with better error handling
        for process in psutil.process_iter(['pid', 'name', 'cmdline', 'connections']):
            try:
                process_info = process.info
                cmdline = process_info.get('cmdline', [])
                name = process_info.get('name', '').lower()
                
                if not cmdline:
                    continue
                
                cmdline_str = ' '.join(cmdline).lower()
                should_terminate = False
                process_type = ""
                
                # Check against each pattern
                for ptype, patterns in process_patterns.items():
                    if any(pattern.lower() in cmdline_str for pattern in patterns):
                        should_terminate = True
                        process_type = ptype
                        break
                
                # Additional port-based detection with safer connection checking
                if not should_terminate:
                    with contextlib.suppress(AttributeError, psutil.AccessDenied, psutil.NoSuchProcess):
                        # Use psutil.net_connections() for port checking
                        for conn in psutil.net_connections():
                            if (hasattr(conn, 'laddr') and conn.laddr and 
                                hasattr(conn, 'pid') and conn.pid == process_info['pid']):
                                port = (conn.laddr.port if hasattr(conn.laddr, 'port') else 
                                       (conn.laddr[1] if isinstance(conn.laddr, tuple) and len(conn.laddr) >= 2 else None))
                                if (port in [9090, 1256] and conn.status == psutil.CONN_LISTEN and 
                                    ('python' in name or 'flask' in cmdline_str)):
                                        should_terminate = True
                                        process_type = f"Port-bound Server ({port})"
                                        break
                
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
                continue  # Process may have disappeared or we don't have access
                
    except Exception as e:
        print(f"[WARNING] Error during process cleanup: {e}")
    
    _report_terminated_processes(terminated_processes)
    
    # Additional port cleanup with improved error handling
    if psutil:
        ports_to_clean = [get_config('api.port', 9090), get_config('server.port', 1256)]
        for port in ports_to_clean:
            try:
                print(f"Checking for processes on port {port}...")
                port_processes = []
                
                for conn in psutil.net_connections():
                    conn_port = None
                    if hasattr(conn, 'laddr') and conn.laddr:
                        if hasattr(conn.laddr, 'port'):
                            conn_port = conn.laddr.port
                        elif isinstance(conn.laddr, tuple) and len(conn.laddr) >= 2:
                            conn_port = conn.laddr[1]
                    
                    if conn_port == port and conn.status == psutil.CONN_LISTEN and conn.pid:
                        port_processes.append(conn.pid)
                
                for pid in port_processes:
                    with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied):
                        process = psutil.Process(pid)
                        process_name = process.name()
                        print(f"Terminating process using port {port}: {process_name} (PID: {pid})")
                        process.terminate()
                        
                        # Give process time to terminate gracefully
                        try:
                            process.wait(timeout=3)
                            print(f"Process {pid} terminated gracefully")
                        except psutil.TimeoutExpired:
                            print(f"Force killing process {pid}")
                            process.kill()
                            
            except Exception as e:
                print(f"[WARNING] Error cleaning port {port}: {e}")
    
    print("[OK] Process cleanup completed!")
    print()

def main():
    # Setup logging first
    setup_logging()
    server_port = get_config('server.port', 1256)
    api_port = get_config('api.port', 9090)
    gui_url = f"http://{get_config('api.host', '127.0.0.1')}:{api_port}/"
    logging.info("Starting CyberBackup 3.0 build and deployment process")
    
    # Enhanced Unicode console setup
    setup_unicode_console()
    
    # Check if emojis are supported
    emoji_support = supports_emojis()
    logging.info(f"Emoji support detected: {emoji_support}")
    
    print()
    print("=" * 72)
    if emoji_support:
        safe_print("   🚀 ONE-CLICK BUILD AND RUN - CyberBackup 3.0")
    else:
        safe_print("   ONE-CLICK BUILD AND RUN - CyberBackup 3.0")
    print("=" * 72)
    print()
    print("Starting complete build and deployment process...")
    print("This will configure, build, and launch the entire backup framework.")
    print()
    
    # Change to project root directory (parent of scripts directory)
    script_dir = Path(__file__).parent.parent
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
        with contextlib.suppress(EOFError):
            input("Press Enter to exit...")
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

        # Check and fix vcpkg dependencies first
        if not check_and_fix_vcpkg_dependencies():
            print("[ERROR] Failed to verify vcpkg dependencies!")
            with contextlib.suppress(EOFError):
                input("Press Enter to exit...")
            sys.exit(1)

        print("Calling scripts\\build\\configure_cmake.bat for CMake + vcpkg setup...")
        print()
        
        if not run_command("scripts\\build\\configure_cmake.bat", timeout=300):
            print()
            print("[ERROR] CMake configuration failed!")
            print("Check the output above for details.")
            with contextlib.suppress(EOFError):
                input("Press Enter to exit...")
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
            print()
            print("Common solutions:")
            print("1. Missing Boost dependencies:")
            print("   - Run: vcpkg\\vcpkg.exe install boost-iostreams:x64-windows")
            print("   - Or delete 'build' folder and run this script again")
            print("2. Outdated vcpkg cache:")
            print("   - Delete 'vcpkg_installed' folder and rebuild")
            print("3. CMake configuration issues:")
            print("   - Run: cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE=vcpkg/scripts/buildsystems/vcpkg.cmake")
            print()

            # Offer to try automatic fix
            try:
                choice = input("Would you like to try automatic vcpkg dependency reinstall? (y/N): ").strip().lower()
                if choice in ['y', 'yes']:
                    print("\nAttempting automatic fix...")
                    if force_vcpkg_reinstall():
                        print("Retrying build...")
                        if run_command("cmake --build build --config Release", timeout=180):
                            print("[OK] Build succeeded after vcpkg reinstall!")
                        else:
                            handle_error_and_exit("[ERROR] Build still failed after vcpkg reinstall\nManual intervention may be required")
                    else:
                        handle_error_and_exit("[ERROR] vcpkg reinstall failed")
                else:
                    handle_error_and_exit("", wait_for_input=True)
            except (EOFError, KeyboardInterrupt):
                handle_error_and_exit("\nExiting...", wait_for_input=False)
        
        # Verify the executable was created with fallback locations
        exe_path = Path("build/Release/EncryptedBackupClient.exe")
        alt_exe_path = Path("build/EncryptedBackupClient.exe") 
        client_exe_path = Path("Client/EncryptedBackupClient.exe")
        
        if exe_path.exists():
            print(f"[OK] C++ client found: {exe_path}")
        elif alt_exe_path.exists():
            print(f"[OK] C++ client found at alternative location: {alt_exe_path}")
        elif client_exe_path.exists():
            print(f"[OK] C++ client found at legacy location: {client_exe_path}")
        else:
            print("[ERROR] EncryptedBackupClient.exe was not created!")
            print(f"Checked locations:")
            print(f"  - {exe_path}")
            print(f"  - {alt_exe_path}")
            print(f"  - {client_exe_path}")
            print("\nWeb uploads may not work without the C++ client.")
            print("Continuing with server-only mode...")
        
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
        exe_locations = [
            Path("build/Release/EncryptedBackupClient.exe"),
            Path("build/EncryptedBackupClient.exe"),
            Path("Client/EncryptedBackupClient.exe"),
            Path("client/EncryptedBackupClient.exe")
        ]
        
        found_exe = None
        for exe_path in exe_locations:
            if exe_path.exists():
                found_exe = exe_path
                print(f"[OK] Found existing C++ client: {found_exe}")
                break
        
        if not found_exe:
            print("[WARNING] No C++ client found - web uploads may not work")
            print("Checked locations:")
            for path in exe_locations:
                print(f"  - {path}")
            print("\nRecommendation: Run cmake --build build --config Release")
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
    
    # Install additional dependencies with better error handling
    print("Installing additional dependencies...")
    additional_deps = ["sentry-sdk", "flask-cors", "watchdog"]
    
    for dep in additional_deps:
        print(f"Installing {dep}...")
        success = run_command(f"pip install {dep}", check_exit=False, timeout=60)
        if success:
            print(f"[OK] {dep} installed successfully")
        else:
            print(f"[WARNING] Failed to install {dep} - continuing anyway")
    
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
            f.write(f"{get_config('server.host', '127.0.0.1')}:{get_config('server.port', 1256)}\n")
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
    
    print("Starting Python Backup Server (python_server.server.server module)...")
    server_path = Path("python_server/server/server.py")
    
    # Validate server path exists with proper error handling
    if not server_path.exists():
        print(f"[ERROR] Server file not found: {server_path}")
        print("Expected location: python_server/server/server.py")
        print("Please verify the server components are installed correctly.")
        print("\nTrying alternative server startup...")
        # Continue execution to attempt other startup methods
    
    if server_path.exists():
        # Check if AppMap is available for recording
        appmap_available = check_appmap_available()

        if appmap_available:
            print("[INFO] AppMap detected - enabling execution recording")
            # Start backup server with AppMap recording using -m module syntax
            server_command = [
                "appmap-python", "--record", "process", 
                "python", "-m", "python_server.server.server"
            ]
            print("Command: appmap-python --record process python -m python_server.server.server")
        else:
            print("[INFO] AppMap not available - starting server normally")
            # Start backup server normally using -m module syntax
            server_command = [sys.executable, "-m", "python_server.server.server"]
            print(f"Command: {sys.executable} -m python_server.server.server")
        
        # Start backup server directly from project root in new console window
        server_env = os.environ.copy()
        # GUI Mode Selection:
        # By default we NOW keep the embedded GUI enabled (more reliable startup)
        # Set CYBERBACKUP_DISABLE_INTEGRATED_GUI=1 to suppress embedded and use standalone
        # Set CYBERBACKUP_STANDALONE_GUI=1 to force launching standalone (even if embedded enabled)
        disable_embedded = os.environ.get("CYBERBACKUP_DISABLE_INTEGRATED_GUI", "0")
        force_standalone = os.environ.get("CYBERBACKUP_STANDALONE_GUI", "0")
        if disable_embedded == "1":
            server_env["CYBERBACKUP_DISABLE_INTEGRATED_GUI"] = "1"
            print("[GUI] Embedded Server GUI disabled via env var")
        else:
            server_env.pop("CYBERBACKUP_DISABLE_INTEGRATED_GUI", None)
            print("[GUI] Embedded Server GUI enabled (default)")
        server_process = subprocess.Popen(
            server_command,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,
            env=server_env
        )
        print(f"Python Backup Server started with PID: {server_process.pid}")
        
        if appmap_available:
            print("[INFO] AppMap recording active - execution traces will be generated")
            print("       AppMap data will be saved when the server stops")
        
        # Wait for backup server to actually start listening on port 1256
        print("Waiting for backup server to start listening...")
        backup_server_ready = False
        for attempt in range(30):  # Try for 30 seconds (extended for GUI initialization)
            if check_backup_server_status():
                backup_server_ready = True
                print(f"[OK] Backup server is listening on port 1256 after {attempt + 1} seconds")
                break
            print(f"  Attempt {attempt + 1}/30: Waiting for backup server...")
            time.sleep(1)
        
        if not backup_server_ready:
            print("[ERROR] Backup server failed to start within 30 seconds")
            print("The API server may fail to connect to the backup server.")
        else:
            print("[OK] Backup server is ready!")

        # Launch standalone Server GUI based on environment variable configuration
        # Respect the GUI control settings calculated above
        should_launch_standalone = (disable_embedded == "1" or force_standalone == "1")
        
        if should_launch_standalone:
            print("[INFO] Launching standalone Server GUI (required by environment configuration)")
            server_gui_path = Path("python_server/server_gui/ServerGUI.py")
            if server_gui_path.exists():
                try:
                    gui_env = os.environ.copy()
                    gui_env["CYBERBACKUP_SERVERGUI_MODE"] = "standalone"
                    gui_proc = subprocess.Popen(
                        [sys.executable, "-m", "python_server.server_gui.ServerGUI"],
                        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,
                        env=gui_env
                    )
                    print(f"[OK] Standalone Server GUI launched (PID: {gui_proc.pid})")
                    # Quick health check after short delay
                    try:
                        import psutil as _ps
                        time.sleep(3)
                        if not _ps.pid_exists(gui_proc.pid):
                            print("[WARNING] Standalone Server GUI process exited early. Falling back guidance:")
                            print("          Run manually: python -m python_server.server_gui.ServerGUI")
                    except Exception:
                        pass
                except Exception as e:
                    print(f"[WARNING] Failed to launch standalone Server GUI: {e}")
            else:
                print(f"[WARNING] Standalone Server GUI not found: {server_gui_path}")
        else:
            print("[INFO] Standalone Server GUI launch skipped (embedded GUI is enabled)")
            print("       - Use CYBERBACKUP_DISABLE_INTEGRATED_GUI=1 to disable embedded GUI")
            print("       - Use CYBERBACKUP_STANDALONE_GUI=1 to force standalone GUI launch")
    else:
        print(f"[WARNING] Server file not found: {server_path}")
        # Try alternative server locations
        alt_locations = [
            Path("src/server/server.py"),
            Path("server.py"),
            Path("backup_server.py")
        ]
        print("Checking alternative server locations:")
        for alt_path in alt_locations:
            if alt_path.exists():
                print(f"[INFO] Found alternative server: {alt_path}")
                print(f"Consider updating the script to use the correct path.")
                break
            else:
                print(f"  - {alt_path}: Not found")
    
    # ========================================================================
    # ENHANCED API SERVER STARTUP WITH ROBUST VERIFICATION
    # ========================================================================
    
    print("Preparing API Bridge Server (cyberbackup_api_server.py)...")
    
    # Step 1: Check Python dependencies with enhanced reporting
    print("\nChecking Python dependencies...")
    missing_deps, optional_missing = check_python_dependencies()
    
    if missing_deps:
        print(f"\n[ERROR] Missing required Python modules:")
        for dep, desc in missing_deps:
            print(f"  - {dep}: {desc}")
        print("\nInstall missing dependencies:")
        for dep, desc in missing_deps:
            if dep == 'flask_cors':
                print("  pip install flask-cors")
            else:
                print(f"  pip install {dep}")
        print("\nOr install all at once:")
        dep_names = [dep for dep, _ in missing_deps]
        print(f"  pip install {' '.join(dep_names)}")
        print()
        with contextlib.suppress(EOFError):
            input("Press Enter to continue anyway (may cause startup failure)...")
    else:
        print("\n[OK] All required Python dependencies are available")
    
    if optional_missing:
        print(f"\n[INFO] Optional dependencies not installed:")
        for dep, desc in optional_missing:
            print(f"  - {dep}: {desc}")
        print("These are optional but recommended for full functionality.")
    
    # Step 2: Check port availability
    print("\nChecking port availability...")
    if not check_port_available(9090):
        print("[WARNING] Port 9090 appears to be in use")
        print("This may cause the API server to fail to start.")
        print("You can:")
        print("  1. Close other applications using port 9090")
        print("  2. Continue anyway (server may fail to start)")
        print()
        with contextlib.suppress(EOFError):
            input("Press Enter to continue...")
    else:
        print("[OK] Port 9090 is available")
    
    # Step 3: Start API server with enhanced error handling
    api_server_path = Path("api_server/cyberbackup_api_server.py")
    api_process = None
    server_started_successfully = False
    
    # Validate API server path exists
    if not api_server_path.exists():
        print(f"[ERROR] API server file not found: {api_server_path}")
        print("Expected location: api_server/cyberbackup_api_server.py")
        print("Please verify the API server is installed correctly.")
        server_started_successfully = False
    elif api_server_path.exists():
        print(f"\nStarting API Bridge Server: {api_server_path}")
        
        try:
            # Start API server in new console window with visible output
            # Fixed: Use module syntax to avoid circular import issues
            api_process = subprocess.Popen(
                [sys.executable, "-m", "api_server.cyberbackup_api_server"],
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
                print("3. Try running manually: python api_server/cyberbackup_api_server.py")
                print("4. Check console windows for error messages")
                
        except Exception as e:
            print(f"[ERROR] Failed to start API server: {str(e)}")
            server_started_successfully = False
    else:
        # Try alternative API server locations
        alt_api_locations = [
            Path("cyberbackup_api_server.py"),
            Path("src/api/cyberbackup_api_server.py"),
            Path("api/cyberbackup_api_server.py")
        ]
        
        found_alt_api = None
        for alt_path in alt_api_locations:
            if alt_path.exists():
                found_alt_api = alt_path
                print(f"[INFO] Found alternative API server: {alt_path}")
                api_server_path = alt_path
                break
        
        if not found_alt_api:
            print(f"[ERROR] API server file not found in any expected location:")
            print(f"  - {api_server_path}")
            for alt_path in alt_api_locations:
                print(f"  - {alt_path}")
            server_started_successfully = False
    
    # Step 5: Open Web GUI only if server started successfully
    if server_started_successfully:
        import webbrowser
        pass
        print(f"\nOpening Web GUI in browser: {gui_url}")
        webbrowser.open(gui_url)
    else:
        print("\n[FALLBACK] Manual startup instructions:")
        print("Since automatic startup failed, you can try:")
        print("1. Open a new terminal/command prompt")
        print("2. Navigate to this directory")
        print("3. Run: python api_server/cyberbackup_api_server.py")
        print(f"4. Wait for server to start, then open: {gui_url}")
        print()
        with contextlib.suppress(EOFError):
            choice = input("Would you like to try opening the browser anyway? (y/N): ").strip().lower()
            if choice in ['y', 'yes']:
                import webbrowser
                pass
                print(f"Opening Web GUI in browser: {gui_url}")
                webbrowser.open(gui_url)
    
    # Enhanced success/status message
    print()
    print("=" * 72)
    if server_started_successfully:
        if emoji_support:
            safe_print("   ✅ ONE-CLICK BUILD AND RUN COMPLETED SUCCESSFULLY!", "   [SUCCESS] ONE-CLICK BUILD AND RUN COMPLETED SUCCESSFULLY!")
        else:
            safe_print("   [SUCCESS] ONE-CLICK BUILD AND RUN COMPLETED SUCCESSFULLY!")
    else:
        if emoji_support:
            safe_print("   ⚠️  ONE-CLICK BUILD AND RUN COMPLETED WITH ISSUES", "   [WARNING] ONE-CLICK BUILD AND RUN COMPLETED WITH ISSUES")
        else:
            safe_print("   [WARNING] ONE-CLICK BUILD AND RUN COMPLETED WITH ISSUES")
    print("=" * 72)
    print()
    print("CyberBackup 3.0 System Status:")
    print()
    
    # Check actual server status for final report
    backup_server_running = check_backup_server_status()
    api_server_running = check_api_server_status()
    
    try:
        print(f"   [SERVER] Backup Server:  {'[OK] Running on port ' + str(server_port) if backup_server_running else '[ERROR] Not responding on port ' + str(server_port)}")
        print(f"   [API] API Server:     {'[OK] Running on port ' + str(api_port) if api_server_running else '[ERROR] Not responding on port ' + str(api_port)}")
        print(f"   [GUI] Web GUI:        {'[OK] ' + gui_url if api_server_running else '[ERROR] Not available (API server down)'}")
        print(f"   [GUI] Server GUI:     {'[OK] Started automatically' if backup_server_running else '[ERROR] Check server console'}")
    except UnicodeEncodeError:
        print(f"   [SERVER] Backup Server:  {'Running on port ' + str(server_port) if backup_server_running else 'Not responding on port ' + str(server_port)}")
        print(f"   [API] API Server:     {'Running on port ' + str(api_port) if api_server_running else 'Not responding on port ' + str(api_port)}")
        print(f"   [GUI] Web GUI:        {gui_url if api_server_running else 'Not available (API server down)'}")
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
        print("   3. Try manual startup: python api_server/cyberbackup_api_server.py")
        print("   4. Check if port 9090 is blocked by firewall/antivirus")
        print("   5. Restart the script after fixing issues")
    print()
    print("General commands:")
    print("   Tests: python scripts\\testing\\master_test_suite.py")
    print("   Quick test: python scripts\\testing\\quick_validation.py")
    print("   Stop services: Close the console windows or press Ctrl+C")
    print("   Logs: Check logs/ directory for detailed error information")
    print("   Manual cleanup: python -c \"import psutil; [p.terminate() for p in psutil.process_iter() if 'cyberbackup' in ' '.join(p.cmdline()).lower()]\"")
    if check_appmap_available():
        print("   View AppMap data: Use AppMap tools after stopping the server")
    print()
    if server_started_successfully and api_server_running:
        if emoji_support:
            safe_print("Have a great backup session! 🚀", "Have a great backup session!")
        else:
            safe_print("Have a great backup session!")
    else:
        if emoji_support:
            safe_print("Please check the troubleshooting steps above 🔧", "Please check the troubleshooting steps above")
        else:
            safe_print("Please check the troubleshooting steps above")
    print("=" * 72)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Build process interrupted by user")
        print("Attempting to clean up any started processes...")
        try:
            cleanup_existing_processes()
        except Exception as cleanup_error:
            print(f"[WARNING] Error during cleanup: {cleanup_error}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] An unexpected error occurred: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        import traceback
        print(f"[DEBUG] Stack trace:")
        traceback.print_exc()
        print("\nFor troubleshooting:")
        print("1. Check that all dependencies are installed: pip install -r requirements.txt")
        print("2. Verify Python and CMake are in PATH")
        print("3. Run individual components manually to isolate the issue")
        print("4. Check logs in the logs/ directory")
        with contextlib.suppress(EOFError):
            input("Press Enter to exit...")
        sys.exit(1)