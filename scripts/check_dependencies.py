#!/usr/bin/env python3
"""Complete dependency verification for CyberBackup Framework"""

import importlib
import os
import socket
import subprocess
import sys
from pathlib import Path


def check_python_deps() -> list[str]:
    """Check Python dependencies."""
    print("\n📦 Python Dependencies:")
    print("-" * 30)

    required = [
        'psutil', 'cryptography', 'flask', 'requests', 'werkzeug',
        'Crypto', 'threading', 'json', 'hashlib', 'base64'
    ]
    missing: list[str] = []

    for dep in required:
        try:
            if dep in ['threading', 'json', 'hashlib', 'base64']:
                # Built-in modules
                __import__(dep)
                print(f"✓ {dep:<15} - OK (built-in)")
            else:
                importlib.import_module(dep)
                try:
                    version = importlib.import_module(dep).__version__
                    print(f"✓ {dep:<15} - OK (v{version})")
                except Exception:
                    print(f"✓ {dep:<15} - OK")
        except ImportError:
            print(f"✗ {dep:<15} - MISSING")
            missing.append(dep)

    return missing

def check_python_version():
    """Check Python version"""
    print("\n🐍 Python Environment:")
    print("-" * 30)

    version = sys.version_info
    print(f"✓ Python Version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 8:
        print("✓ Python version meets requirements (3.8+)")
    else:
        print("⚠ Python version should be 3.8+ for best compatibility")

    print(f"✓ Python Executable: {sys.executable}")

def check_cpp_deps():
    """Check C++ build environment"""
    print("\n🛠 C++ Build Environment:")
    print("-" * 30)

    # Check CMake
    try:
        result = subprocess.run(['cmake', '--version'], capture_output=True, text=True, encoding='utf-8', timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ CMake - {version_line}")
        else:
            print("✗ CMake - Command failed")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("✗ CMake - NOT FOUND")

    # Check vcpkg
    try:
        vcpkg_path = Path("vcpkg/vcpkg.exe")
        if vcpkg_path.exists():
            print("✓ vcpkg.exe - Found in project")

            # Check vcpkg list
            result = subprocess.run([str(vcpkg_path), 'list'], capture_output=True, text=True, encoding='utf-8', timeout=30)
            if result.returncode == 0:
                required_libs = ['boost-asio', 'boost-beast', 'cryptopp', 'zlib']
                installed_libs = result.stdout.lower()

                for lib in required_libs:
                    if lib in installed_libs:
                        print(f"✓ {lib:<15} - Installed")
                    else:
                        print(f"✗ {lib:<15} - NOT INSTALLED")
            else:
                print("⚠ vcpkg list command failed")
        else:
            print("✗ vcpkg.exe - NOT FOUND in project")
    except Exception as e:
        print(f"✗ vcpkg check failed: {e}")

def check_build_system():
    """Check build system status"""
    print("\n🏗 Build System:")
    print("-" * 30)

    # Check if CMake build directory exists
    build_dir = Path("build")
    if build_dir.exists():
        print("✓ Build directory exists")

        # Check for CMakeCache.txt
        cmake_cache = build_dir / "CMakeCache.txt"
        if cmake_cache.exists():
            print("✓ CMake cache found - Project configured")
        else:
            print("⚠ CMake cache missing - Project needs configuration")

        # Check for executable
        exe_path = build_dir / "Release" / "EncryptedBackupClient.exe"
        if exe_path.exists():
            print("✓ EncryptedBackupClient.exe - Built")
            size = exe_path.stat().st_size
            print(f"  File size: {size:,} bytes")
        else:
            print("✗ EncryptedBackupClient.exe - NOT BUILT")
    else:
        print("✗ Build directory missing")

def check_visual_studio():
    """Check Visual Studio/MSVC"""
    print("\n🏢 Visual Studio/MSVC:")
    print("-" * 30)

    # Check for cl.exe (MSVC compiler)
    try:
        result = subprocess.run(['where', 'cl'], capture_output=True, text=True, encoding='utf-8', shell=True, timeout=10)
        if result.returncode == 0:
            print("✓ MSVC Compiler (cl.exe) - Found")
            print(f"  Path: {result.stdout.strip()}")
        else:
            print("✗ MSVC Compiler - NOT FOUND")
    except Exception:
        print("✗ MSVC Compiler - Check failed")

    # Check for MSBuild
    try:
        result = subprocess.run(['where', 'msbuild'], capture_output=True, text=True, encoding='utf-8', shell=True, timeout=10)
        if result.returncode == 0:
            print("✓ MSBuild - Found")
        else:
            print("✗ MSBuild - NOT FOUND")
    except Exception:
        print("✗ MSBuild - Check failed")

def check_ports():
    """Check required ports are available"""
    print("\n🌐 Network Ports:")
    print("-" * 30)

    ports = [
        (9090, "Flask API Server"),
        (1256, "Python Backup Server")
    ]

    for port, description in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            if result == 0:
                print(f"⚠ Port {port:<4} ({description}) - IN USE")
            else:
                print(f"✓ Port {port:<4} ({description}) - AVAILABLE")
        except Exception as e:
            print(f"✗ Port {port:<4} ({description}) - ERROR: {e}")

def check_project_structure():
    """Check critical project files and directories"""
    print("\n📁 Project Structure:")
    print("-" * 30)

    critical_paths = [
        ("Client/cpp/client.cpp", "C++ Client Source"),
        ("python_server/server/server.py", "Python Server"),
        ("cyberbackup_api_server.py", "Flask API Server"),
        ("real_backup_executor.py", "Backup Executor"),
        ("requirements.txt", "Python Requirements"),
        ("CMakeLists.txt", "CMake Configuration"),
        ("vcpkg.json", "vcpkg Dependencies"),
    ]

    for path, description in critical_paths:
        if Path(path).exists():
            print(f"✓ {description:<25} - Found")
        else:
            print(f"✗ {description:<25} - MISSING: {path}")

def check_config_files():
    """Check configuration files"""
    print("\n⚙️ Configuration Files:")
    print("-" * 30)

    config_paths = [
        ("config/server/default.json", "Server Config"),
        ("data/keys/", "Key Directory"),
        ("server/received_files/", "Backup Storage"),
    ]

    for path, description in config_paths:
        path_obj = Path(path)
        if path_obj.exists():
            if path_obj.is_dir():
                count = len(list(path_obj.iterdir()))
                print(f"✓ {description:<20} - Found ({count} items)")
            else:
                print(f"✓ {description:<20} - Found")
        else:
            print(f"⚠ {description:<20} - Missing: {path}")

def main():
    """Run complete dependency check"""
    print("🔍 CyberBackup Framework - Complete Dependency Check")
    print("=" * 60)
    print(f"📍 Working Directory: {os.getcwd()}")

    # Run all checks
    check_python_version()
    missing_python = check_python_deps()
    check_cpp_deps()
    check_build_system()
    check_visual_studio()
    check_ports()
    check_project_structure()
    check_config_files()

    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    print("-" * 60)

    if missing_python:
        print(f"❌ Missing Python packages: {', '.join(missing_python)}")
        print(f"💡 Install with: pip install {' '.join(missing_python)}")
    else:
        print("✅ All Python dependencies found")

    # Check if build is ready
    if Path("build/Release/EncryptedBackupClient.exe").exists():
        print("✅ C++ Client built and ready")
    else:
        print("⚠️ C++ Client needs building")
        print("💡 Run: cmake -B build -DCMAKE_TOOLCHAIN_FILE=\"vcpkg\\scripts\\buildsystems\\vcpkg.cmake\"")
        print("💡 Then: cmake --build build --config Release")

    print("\n🚀 Next Steps:")
    if missing_python:
        print("1. Install missing Python packages")
    if not Path("build/Release/EncryptedBackupClient.exe").exists():
        print("2. Build C++ client executable")
    print("3. Run: python launch_gui.py (to start the complete system)")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
