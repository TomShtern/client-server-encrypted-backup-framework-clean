#!/usr/bin/env python3
"""
Fix vcpkg Issues - CyberBackup 3.0
==================================

This script fixes common vcpkg build issues by:
1. Updating vcpkg to latest version
2. Cleaning build cache
3. Reinstalling dependencies with proper configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command: str | list[str], cwd: str | None = None, timeout: int = 300):
    """Run a command and return success status"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd or os.getcwd(),
            timeout=timeout,
            text=True
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {command}")
        return False
    except Exception as e:
        print(f"Command failed: {e}")
        return False


def clean_vcpkg_cache():
    """Clean vcpkg cache and build directories"""
    print("Cleaning vcpkg cache...")
    
    # Directories to clean
    dirs_to_clean = [
        "vcpkg_installed",
        "build",
        "vcpkg/buildtrees",
        "vcpkg/packages",
        "vcpkg/downloads"
    ]
    
    for dir_path in dirs_to_clean:
        path = Path(dir_path)
        if path.exists():
            print(f"Removing {dir_path}...")
            try:
                shutil.rmtree(path)
                print(f"✅ Removed {dir_path}")
            except Exception as e:
                print(f"⚠️  Failed to remove {dir_path}: {e}")
        else:
            print(f"ℹ️  {dir_path} doesn't exist, skipping")


def update_vcpkg():
    """Update vcpkg to latest version"""
    print("Updating vcpkg...")
    
    # Change to vcpkg directory
    vcpkg_dir = Path("vcpkg")
    if not vcpkg_dir.exists():
        print("❌ vcpkg directory not found!")
        return False
    
    # Update vcpkg
    if not run_command("git pull", cwd=str(vcpkg_dir)):
        print("⚠️  Failed to update vcpkg via git pull")
    
    # Bootstrap vcpkg
    bootstrap_cmd = "bootstrap-vcpkg.bat" if os.name == 'nt' else "./bootstrap-vcpkg.sh"
    if not run_command(bootstrap_cmd, cwd=str(vcpkg_dir)):
        print("❌ Failed to bootstrap vcpkg")
        return False
    
    print("✅ vcpkg updated successfully")
    return True


def install_dependencies():
    """Install dependencies with proper configuration"""
    print("Installing vcpkg dependencies...")
    
    # Install dependencies
    install_cmd = "vcpkg\\vcpkg.exe install --triplet x64-windows --recurse"
    if not run_command(install_cmd, timeout=600):
        print("❌ Failed to install dependencies")
        return False
    
    print("✅ Dependencies installed successfully")
    return True


def main():
    """Main function"""
    print("🔧 vcpkg Issue Fixer for CyberBackup 3.0")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("vcpkg.json").exists():
        print("❌ vcpkg.json not found! Please run this from the project root.")
        return 1
    
    try:
        # Step 1: Clean cache
        print("\n📁 Step 1: Cleaning vcpkg cache...")
        clean_vcpkg_cache()
        
        # Step 2: Update vcpkg
        print("\n🔄 Step 2: Updating vcpkg...")
        if not update_vcpkg():
            print("❌ Failed to update vcpkg")
            return 1
        
        # Step 3: Install dependencies
        print("\n📦 Step 3: Installing dependencies...")
        if not install_dependencies():
            print("❌ Failed to install dependencies")
            return 1
        
        print("\n✅ vcpkg issues fixed successfully!")
        print("You can now run the one-click build script again.")
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
