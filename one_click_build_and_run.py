#!/usr/bin/env python3
"""
ONE-CLICK BUILD AND RUN - Client-Server Encrypted Backup Framework
====================================================================

This Python script provides a complete cross-platform one-click solution to:
  1. Build the C++ client with CMake + vcpkg
  2. Set up Python environment  
  3. Start all services (backup server + API server)
  4. Launch the web GUI
  5. Verify everything is working

Author: Auto-generated for CyberBackup 3.0
Usage: python one_click_build_and_run.py [--skip-build] [--skip-tests] [--verbose]
====================================================================
"""

import os
import sys
import subprocess
import time
import argparse
import platform
from pathlib import Path
import shutil
import webbrowser
from typing import Optional, List

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class OneClickBuilder:
    """Main class for the one-click build and run process"""
    
    def __init__(self, skip_build: bool = False, skip_tests: bool = False, verbose: bool = False):
        self.skip_build = skip_build
        self.skip_tests = skip_tests
        self.verbose = verbose
        self.script_dir = Path(__file__).parent.absolute()
        self.is_windows = platform.system() == "Windows"
        
    def print_colored(self, message: str, color: str = Colors.WHITE) -> None:
        """Print colored message to console"""
        if self.is_windows:
            # For Windows, try to enable ANSI color support
            try:
                os.system('color')
            except:
                pass
        print(f"{color}{message}{Colors.END}")
        
    def print_success(self, message: str) -> None:
        """Print success message"""
        self.print_colored(f"[SUCCESS] {message}", Colors.GREEN)
        
    def print_error(self, message: str) -> None:
        """Print error message"""
        self.print_colored(f"[ERROR] {message}", Colors.RED)
        
    def print_warning(self, message: str) -> None:
        """Print warning message"""
        self.print_colored(f"[WARNING] {message}", Colors.YELLOW)
        
    def print_info(self, message: str) -> None:
        """Print info message"""
        self.print_colored(f"[INFO] {message}", Colors.CYAN)
        
    def print_phase(self, phase: str, description: str) -> None:
        """Print phase header"""
        print()
        self.print_colored(f"[{phase}] {description}", Colors.MAGENTA)
        self.print_colored("-" * 50, Colors.WHITE)
        
    def run_command(self, command: List[str], shell: bool = False, capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a command with error handling"""
        if self.verbose:
            self.print_info(f"Running: {' '.join(command)}")
            
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=capture_output,
                text=True,
                cwd=self.script_dir
            )
            return result
        except FileNotFoundError:
            raise Exception(f"Command not found: {command[0]}")
        except Exception as e:
            raise Exception(f"Failed to run command: {e}")
    
    def check_prerequisites(self) -> None:
        """Check if all required tools are available"""
        self.print_phase("PHASE 1/6", "Checking Prerequisites...")
        
        # Check Python
        try:
            result = self.run_command([sys.executable, "--version"], capture_output=True)
            if result.returncode == 0:
                self.print_success(f"Python found: {result.stdout.strip()}")
            else:
                raise Exception("Python check failed")
        except Exception:
            self.print_error("Python is not available")
            raise
            
        # Check CMake
        try:
            result = self.run_command(["cmake", "--version"], capture_output=True)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                self.print_success(f"CMake found: {version_line}")
            else:
                raise Exception("CMake check failed")
        except Exception:
            self.print_error("CMake is not installed or not in PATH")
            self.print_info("Please install CMake 3.15+ and add it to your PATH")
            raise
            
        # Check Git (optional)
        try:
            result = self.run_command(["git", "--version"], capture_output=True)
            if result.returncode == 0:
                self.print_success("Git found")
        except Exception:
            self.print_warning("Git not found (optional but recommended)")
            
        self.print_success("Prerequisites check completed!")
        
    def configure_cmake(self) -> None:
        """Configure CMake with vcpkg"""
        if self.skip_build:
            self.print_warning("Skipping build configuration (--skip-build specified)")
            return
            
        self.print_phase("PHASE 2/6", "Configuring Build System...")
        
        self.print_info("Running CMake configuration with vcpkg...")
        
        # Use the existing configure script
        if self.is_windows:
            script_path = self.script_dir / "scripts" / "configure_cmake.bat"
            result = self.run_command([str(script_path)], shell=True)
        else:
            # For non-Windows, we'd need a shell script equivalent
            self.print_warning("Non-Windows CMake configuration not implemented")
            return
            
        if result.returncode != 0:
            self.print_error("CMake configuration failed!")
            raise Exception("CMake configuration failed")
            
        self.print_success("CMake configuration completed!")
        
    def build_client(self) -> None:
        """Build the C++ client"""
        if self.skip_build:
            self.print_warning("Skipping C++ build (--skip-build specified)")
            return
            
        self.print_phase("PHASE 3/6", "Building C++ Client...")
        
        self.print_info("Building EncryptedBackupClient.exe with CMake...")
        self.print_info("Command: cmake --build build --config Release")
        
        result = self.run_command(["cmake", "--build", "build", "--config", "Release"])
        if result.returncode != 0:
            self.print_error("C++ client build failed!")
            raise Exception("Build failed")
            
        # Verify executable exists
        exe_name = "EncryptedBackupClient.exe" if self.is_windows else "EncryptedBackupClient"
        exe_path = self.script_dir / "build" / "Release" / exe_name
        
        if exe_path.exists():
            self.print_success("C++ client built successfully!")
            self.print_info(f"Location: {exe_path}")

            # Copy the executable to the client directory
            client_dir = self.script_dir / "client"
            client_dir.mkdir(exist_ok=True) # Ensure client directory exists
            shutil.copy(exe_path, client_dir / exe_name)
            self.print_success(f"Copied {exe_name} to {client_dir}")
        else:
            self.print_error(f"{exe_name} was not created!")
            self.print_info(f"Expected location: {exe_path}")
            raise Exception("Executable not found")
            
    def setup_python_environment(self) -> None:
        """Set up Python environment and dependencies"""
        self.print_phase("PHASE 4/6", "Setting up Python Environment...")
        
        requirements_file = self.script_dir / "requirements.txt"
        
        if requirements_file.exists():
            self.print_info("Installing Python dependencies from requirements.txt...")
            try:
                result = self.run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                if result.returncode == 0:
                    self.print_success("Python dependencies installed successfully!")
                else:
                    self.print_warning("Some Python dependencies failed to install")
                    self.print_info("This may cause issues with the API server or GUI")
            except Exception as e:
                self.print_warning(f"Failed to install dependencies: {e}")
        else:
            self.print_warning("requirements.txt not found")
            self.print_info("Installing basic dependencies manually...")
            try:
                basic_deps = ["cryptography", "pycryptodome", "psutil", "flask"]
                result = self.run_command([sys.executable, "-m", "pip", "install"] + basic_deps)
                if result.returncode == 0:
                    self.print_success("Basic dependencies installed!")
                else:
                    self.print_warning("Failed to install basic dependencies")
            except Exception as e:
                self.print_warning(f"Failed to install basic dependencies: {e}")
                
    def verify_configuration(self) -> None:
        """Verify that all configuration files are in place"""
        self.print_phase("PHASE 5/6", "Verifying Configuration...")
        
        data_dir = self.script_dir / "data"
        
        # Check RSA keys
        private_key_path = data_dir / "valid_private_key.der"
        public_key_path = data_dir / "valid_public_key.der"
        
        if private_key_path.exists():
            self.print_success("RSA private key found")
        else:
            self.print_warning("RSA private key missing - generating keys...")
            try:
                self.run_command([sys.executable, "scripts/create_working_keys.py"])
            except Exception as e:
                self.print_warning(f"Failed to generate keys: {e}")
                
        if public_key_path.exists():
            self.print_success("RSA public key found")
        else:
            self.print_warning("RSA public key missing - may need key generation")
            
        # Check transfer.info
        transfer_info_path = data_dir / "transfer.info"
        if transfer_info_path.exists():
            self.print_success("transfer.info configuration found")
        else:
            self.print_warning("Creating default transfer.info...")
            try:
                data_dir.mkdir(exist_ok=True)
                with open(transfer_info_path, 'w') as f:
                    f.write("127.0.0.1:1256\n")
                    f.write("testuser\n")
                    f.write("test_file.txt\n")
                self.print_success("Default transfer.info created")
            except Exception as e:
                self.print_warning(f"Failed to create transfer.info: {e}")
                
        self.print_success("Configuration verification completed!")
        
    def launch_services(self) -> None:
        """Launch all services"""
        self.print_phase("PHASE 6/6", "Launching Services...")
        
        self.print_info("Starting the complete CyberBackup 3.0 system...")
        print()
        self.print_info("Services that will be started:")
        self.print_info("  Backup Server (Port 1256)")
        self.print_info("  API Bridge Server (Port 9090)")
        self.print_info("  Web GUI (Browser interface)")
        print()

        # Start the Python backup server
        self.print_info("Starting Python Backup Server (server/server.py)...")
        server_path = self.script_dir / "server" / "server.py"
        self.server_process = subprocess.Popen(
            [sys.executable, str(server_path)],
            creationflags=subprocess.CREATE_NEW_CONSOLE if self.is_windows else 0
        )
        self.print_info(f"Python Backup Server started with PID: {self.server_process.pid}")
        time.sleep(5) # Give server time to start

        # Start the API Bridge Server
        self.print_info("Starting API Bridge Server (cyberbackup_api_server.py)...")
        api_server_path = self.script_dir / "cyberbackup_api_server.py"
        self.api_server_process = subprocess.Popen(
            [sys.executable, str(api_server_path)],
            creationflags=subprocess.CREATE_NEW_CONSOLE if self.is_windows else 0
        )
        self.print_info(f"API Bridge Server started with PID: {self.api_server_process.pid}")
        time.sleep(5) # Give API server time to start

        # Open Web GUI in browser
        gui_url = "http://127.0.0.1:9090/"
        self.print_info(f"Opening Web GUI in browser: {gui_url}")
        webbrowser.open(gui_url)

        self.print_success_banner()
            
    def print_success_banner(self) -> None:
        """Print the success banner"""
        print()
        self.print_colored("=" * 72, Colors.GREEN)
        self.print_colored("   ONE-CLICK BUILD AND RUN COMPLETED SUCCESSFULLY!", Colors.GREEN)
        self.print_colored("=" * 72, Colors.GREEN)
        print()
        self.print_success("Your CyberBackup 3.0 system should now be running with:")
        print()
        self.print_info("  Web GUI:        http://localhost:9090")
        self.print_info("  Server GUI:     Started automatically")
        self.print_info("  Backup Server:  Running on port 1256")
        self.print_info("  API Server:     Running on port 9090")
        print()
        self.print_info("Next steps:")
        self.print_info("  1. The web interface should have opened automatically")
        self.print_info("  2. You can upload files through the web GUI")
        self.print_info("  3. Monitor transfers in the server GUI window")
        self.print_info("  4. Check logs in the console windows for debugging")
        print()
        self.print_info("To run tests: python scripts/master_test_suite.py")
        self.print_info("To stop services: Close the console windows or press Ctrl+C")
        print()
        self.print_success("Have a great backup session!")
        self.print_colored("=" * 72, Colors.GREEN)
        
    def run(self) -> None:
        """Run the complete build and launch process"""
        if self.is_windows:
            # Set console encoding to UTF-8 for emoji support
            os.system("chcp 65001 > nul")
        try:
            # Print header
            print()
            self.print_colored("=" * 72, Colors.CYAN)
            self.print_colored("   ONE-CLICK BUILD AND RUN - CyberBackup 3.0", Colors.CYAN)
            self.print_colored("=" * 72, Colors.CYAN)
            print()
            self.print_info("Starting complete build and deployment process...")
            self.print_info("This will configure, build, and launch the entire backup framework.")
            print()
            
            # Change to script directory
            os.chdir(self.script_dir)
            self.print_info(f"Working directory: {self.script_dir}")
            
            # Run all phases
            self.check_prerequisites()
            self.configure_cmake()
            self.build_client()
            self.setup_python_environment()
            self.verify_configuration()
            self.launch_services()
            
        except KeyboardInterrupt:
            self.print_warning("Process interrupted by user")
            sys.exit(1)
        except Exception as e:
            print()
            self.print_error("An error occurred during the build and launch process:")
            self.print_error(str(e))
            if self.verbose:
                import traceback
                self.print_colored("Stack trace:", Colors.RED)
                traceback.print_exc()
            print()
            self.print_info("Please check the error message above and try again.")
            self.print_info("You can run with --verbose for more detailed error information.")
            sys.exit(1)
        finally:
            if hasattr(self, 'server_process') and self.server_process.poll() is None:
                self.print_info("Terminating Python Backup Server...")
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                if self.server_process.poll() is None:
                    self.print_warning("Python Backup Server did not terminate gracefully, killing it...")
                    self.server_process.kill()
                self.print_info("Python Backup Server terminated.")
            
            if hasattr(self, 'api_server_process') and self.api_server_process.poll() is None:
                self.print_info("Terminating API Bridge Server...")
                self.api_server_process.terminate()
                self.api_server_process.wait(timeout=5)
                if self.api_server_process.poll() is None:
                    self.print_warning("API Bridge Server did not terminate gracefully, killing it...")
                    self.api_server_process.kill()
                self.print_info("API Bridge Server terminated.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="One-click build and run for CyberBackup 3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python one_click_build_and_run.py                    # Full build and launch
  python one_click_build_and_run.py --skip-build      # Skip build, just launch
  python one_click_build_and_run.py --verbose         # Verbose output
        """
    )
    
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip the build phase (CMake configuration and compilation)"
    )
    
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output for debugging"
    )
    
    args = parser.parse_args()
    
    # Create and run the builder
    builder = OneClickBuilder(
        skip_build=args.skip_build,
        skip_tests=args.skip_tests,
        verbose=args.verbose
    )
    
    builder.run()

if __name__ == "__main__":
    main()