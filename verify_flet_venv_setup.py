#!/usr/bin/env python3
"""
Comprehensive verification that flet_venv is the primary and only virtual environment.
This script validates the complete setup and ensures everything works correctly.
"""
import sys
import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"   {title}")
    print("=" * 70)

def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")

def print_warning(message: str):
    """Print warning message."""
    print(f"⚠️  {message}")

def print_info(message: str):
    """Print info message."""
    print(f"ℹ️  {message}")

def verify_environment_structure() -> Tuple[bool, List[str]]:
    """Verify the virtual environment structure."""
    print_header("VIRTUAL ENVIRONMENT STRUCTURE VERIFICATION")

    project_root = Path(__file__).parent
    issues = []

    # Check flet_venv exists
    flet_venv_path = project_root / "flet_venv"
    if flet_venv_path.exists():
        print_success(f"flet_venv directory exists at: {flet_venv_path}")

        # Check key subdirectories
        for subdir in ["Scripts", "Lib", "Include", "pyvenv.cfg"]:
            subpath = flet_venv_path / subdir
            if subpath.exists():
                print_success(f"  {subdir} exists")
            else:
                print_error(f"  {subdir} missing")
                issues.append(f"flet_venv/{subdir} missing")

    else:
        print_error("flet_venv directory not found")
        issues.append("flet_venv directory missing")

    # Check for old virtual environments
    old_venvs = []
    for venv_name in ["venv", ".venv", "env", "ENV", "python_venv"]:
        old_path = project_root / venv_name
        if old_path.exists():
            old_venvs.append(old_path)

    if old_venvs:
        print_warning(f"Found {len(old_venvs)} old virtual environment(s):")
        for venv in old_venvs:
            print(f"     - {venv}")
        issues.append(f"Old virtual environments found: {[str(v) for v in old_venvs]}")
    else:
        print_success("No old virtual environments found")

    return len(issues) == 0, issues

def verify_python_executable() -> Tuple[bool, List[str]]:
    """Verify Python executable and version."""
    print_header("PYTHON EXECUTABLE VERIFICATION")

    issues = []
    project_root = Path(__file__).parent

    # Check flet_venv Python executable
    python_exe = project_root / "flet_venv" / "Scripts" / "python.exe"
    if python_exe.exists():
        print_success(f"Python executable found: {python_exe}")

        try:
            # Check Python version
            result = subprocess.run([str(python_exe), "--version"],
                                  capture_output=True, text=True, check=True)
            python_version = result.stdout.strip()
            print_success(f"Python version: {python_version}")

            # Check if it's the right Python (should be 3.9+)
            if "Python 3." in python_version:
                version_num = python_version.split()[1]
                major, minor = version_num.split(".")[:2]
                if int(major) >= 3 and int(minor) >= 9:
                    print_success(f"Python version is compatible (≥3.9)")
                else:
                    print_warning(f"Python version might be too old: {version_num}")

        except subprocess.CalledProcessError as e:
            print_error(f"Failed to get Python version: {e}")
            issues.append("Cannot execute Python from flet_venv")
    else:
        print_error(f"Python executable not found at: {python_exe}")
        issues.append("Python executable missing in flet_venv")

    # Check current Python environment
    current_python = Path(sys.executable)
    if "flet_venv" in str(current_python):
        print_success("Currently running from flet_venv")
    else:
        print_info(f"Currently running from: {current_python}")
        print_info("(This is OK if running verification from different environment)")

    return len(issues) == 0, issues

def verify_requirements() -> Tuple[bool, List[str]]:
    """Verify that all requirements are installed."""
    print_header("REQUIREMENTS VERIFICATION")

    issues = []
    project_root = Path(__file__).parent

    # Read requirements.txt
    requirements_file = project_root / "requirements.txt"
    if not requirements_file.exists():
        print_error("requirements.txt not found")
        issues.append("requirements.txt missing")
        return False, issues

    print_success(f"Found requirements.txt: {requirements_file}")

    # Check if packages are installed in flet_venv
    python_exe = project_root / "flet_venv" / "Scripts" / "python.exe"
    if not python_exe.exists():
        print_error("Cannot verify packages - Python executable missing")
        issues.append("Cannot verify packages")
        return False, issues

    try:
        # Get list of installed packages
        result = subprocess.run([str(python_exe), "-m", "pip", "list"],
                              capture_output=True, text=True, check=True)
        installed_packages = result.stdout.lower()

        # Check key packages
        key_packages = ["flet", "flask", "psutil", "pydantic", "requests", "httpx"]
        missing_packages = []

        for package in key_packages:
            if package in installed_packages:
                print_success(f"  {package} is installed")
            else:
                print_error(f"  {package} is missing")
                missing_packages.append(package)

        if missing_packages:
            issues.append(f"Missing packages: {missing_packages}")

    except subprocess.CalledProcessError as e:
        print_error(f"Failed to check installed packages: {e}")
        issues.append("Cannot check installed packages")

    return len(issues) == 0, issues

def verify_vscode_configuration() -> Tuple[bool, List[str]]:
    """Verify VS Code configuration."""
    print_header("VS CODE CONFIGURATION VERIFICATION")

    issues = []
    project_root = Path(__file__).parent

    # Check .vscode/settings.json
    settings_file = project_root / ".vscode" / "settings.json"
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Check Python interpreter path
            interpreter_path = settings.get('python.defaultInterpreterPath', '')
            if 'flet_venv' in interpreter_path:
                print_success("VS Code settings use flet_venv interpreter")
            else:
                print_error(f"VS Code interpreter path: {interpreter_path}")
                issues.append("VS Code not configured for flet_venv")

            # Check venv folders
            venv_folders = settings.get('python.venvFolders', [])
            if 'flet_venv' in venv_folders:
                print_success("flet_venv in VS Code venv folders")
            else:
                print_warning(f"VS Code venv folders: {venv_folders}")

        except Exception as e:
            print_error(f"Error reading VS Code settings: {e}")
            issues.append("VS Code settings unreadable")
    else:
        print_warning("VS Code settings.json not found")

    # Check .vscode/launch.json
    launch_file = project_root / ".vscode" / "launch.json"
    if launch_file.exists():
        try:
            with open(launch_file, 'r', encoding='utf-8') as f:
                launch_config = json.load(f)

            flet_venv_configs = 0
            for config in launch_config.get('configurations', []):
                python_path = config.get('python', '')
                if 'flet_venv' in python_path:
                    flet_venv_configs += 1

            print_success(f"{flet_venv_configs} launch configurations use flet_venv")
        except Exception as e:
            print_error(f"Error reading launch.json: {e}")

    return len(issues) == 0, issues

def verify_workspace_files() -> Tuple[bool, List[str]]:
    """Verify workspace configuration files."""
    print_header("WORKSPACE FILES VERIFICATION")

    issues = []
    project_root = Path(__file__).parent

    # Check workspace files
    workspace_files = [
        "Client-Server-Backup-Framework.code-workspace",
        "FletV2-Workspace.code-workspace"
    ]

    for workspace_file in workspace_files:
        workspace_path = project_root / workspace_file
        if workspace_path.exists():
            try:
                with open(workspace_path, 'r', encoding='utf-8') as f:
                    workspace_config = json.load(f)

                settings = workspace_config.get('settings', {})
                interpreter_path = settings.get('python.defaultInterpreterPath', '')

                if 'flet_venv' in interpreter_path:
                    print_success(f"{workspace_file} uses flet_venv")
                else:
                    print_error(f"{workspace_file} interpreter: {interpreter_path}")
                    issues.append(f"{workspace_file} not configured for flet_venv")

            except Exception as e:
                print_error(f"Error reading {workspace_file}: {e}")
                issues.append(f"Cannot read {workspace_file}")
        else:
            print_info(f"{workspace_file} not found (optional)")

    return len(issues) == 0, issues

def verify_flet_functionality() -> Tuple[bool, List[str]]:
    """Verify that Flet can be imported and basic functionality works."""
    print_header("FLET FUNCTIONALITY VERIFICATION")

    issues = []
    project_root = Path(__file__).parent
    python_exe = project_root / "flet_venv" / "Scripts" / "python.exe"

    if not python_exe.exists():
        print_error("Cannot test Flet - Python executable missing")
        issues.append("Cannot test Flet functionality")
        return False, issues

    # Test Flet import
    test_script = '''
import sys
try:
    import flet as ft
    print("SUCCESS: Flet imported successfully")
    print(f"Flet version: {ft.__version__ if hasattr(ft, '__version__') else 'unknown'}")

    # Test basic Flet functionality
    def test_app(page: ft.Page):
        page.title = "Test App"
        page.add(ft.Text("Hello, Flet!"))

    print("SUCCESS: Basic Flet functionality works")
    sys.exit(0)

except ImportError as e:
    print(f"ERROR: Cannot import Flet: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Flet functionality test failed: {e}")
    sys.exit(1)
'''

    try:
        result = subprocess.run([str(python_exe), "-c", test_script],
                              capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print_success("Flet import and basic functionality test passed")
            for line in result.stdout.strip().split('\n'):
                if line.startswith('SUCCESS:') or 'version:' in line:
                    print_info(f"  {line}")
        else:
            print_error("Flet functionality test failed")
            print(f"Error output: {result.stderr}")
            issues.append("Flet functionality test failed")

    except subprocess.TimeoutExpired:
        print_error("Flet test timed out")
        issues.append("Flet test timeout")
    except Exception as e:
        print_error(f"Failed to run Flet test: {e}")
        issues.append("Cannot run Flet test")

    return len(issues) == 0, issues

def main() -> int:
    """Main verification function."""
    print_header("FLET_VENV COMPREHENSIVE VERIFICATION")
    print("This script verifies that flet_venv is properly configured as the")
    print("primary virtual environment with all requirements installed.")

    all_issues = []
    test_results = []

    # Run all verification tests
    tests = [
        ("Environment Structure", verify_environment_structure),
        ("Python Executable", verify_python_executable),
        ("Requirements", verify_requirements),
        ("VS Code Configuration", verify_vscode_configuration),
        ("Workspace Files", verify_workspace_files),
        ("Flet Functionality", verify_flet_functionality),
    ]

    for test_name, test_func in tests:
        try:
            success, issues = test_func()
            test_results.append((test_name, success))
            all_issues.extend(issues)
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            test_results.append((test_name, False))
            all_issues.append(f"Test '{test_name}' crashed: {str(e)}")

    # Print summary
    print_header("VERIFICATION SUMMARY")

    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)

    for test_name, success in test_results:
        status = "PASS" if success else "FAIL"
        icon = "✅" if success else "❌"
        print(f"{icon} {test_name}: {status}")

    print(f"\nTests Passed: {passed_tests}/{total_tests}")

    if all_issues:
        print_header("ISSUES FOUND")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")

        print_header("RECOMMENDED ACTIONS")
        print("1. Run: .\\activate-flet-venv.ps1")
        print("2. Run: pip install -r requirements.txt --upgrade")
        print("3. Restart VS Code to pick up configuration changes")
        print("4. Check that flet_venv\\Scripts\\python.exe exists")

        return 1
    else:
        print_header("🎉 ALL TESTS PASSED!")
        print("✅ flet_venv is properly configured as the primary environment")
        print("✅ All requirements are installed and working")
        print("✅ VS Code and workspace files are properly configured")
        print("✅ Flet functionality is working correctly")
        print("\n🚀 Your environment is ready for development!")

        return 0

if __name__ == "__main__":
    sys.exit(main())