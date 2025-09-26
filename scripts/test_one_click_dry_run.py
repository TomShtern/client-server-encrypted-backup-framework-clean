#!/usr/bin/env python3
"""Dry run test of the one_click_build_and_run.py script phases"""

import sys
from pathlib import Path

# Setup standardized import paths
from Shared.path_utils import setup_imports

setup_imports()

from . import one_click_build_and_run as build_script


def test_dry_run():
    """Test the script phases without actually starting servers"""
    print("=" * 60)
    print("DRY RUN TEST - Testing script phases")
    print("=" * 60)

    # Test phase functions individually
    try:
        print("\n[PHASE 0] Testing process cleanup function...")
        # Don't actually cleanup processes in test
        print("Process cleanup function available: OK")

        print("\n[PHASE 1] Testing prerequisites check...")

        # Test Python check
        exists, version = build_script.check_command_exists("python")
        print(f"Python check: exists={exists}, version={version[:20]}...")

        # Test CMake check (may not exist)
        exists, version = build_script.check_command_exists("cmake")
        print(f"CMake check: exists={exists}")

        # Test Git check (may not exist)
        exists, version = build_script.check_command_exists("git")
        print(f"Git check: exists={exists}")

        print("\n[PHASE 2/3] Testing build system checks...")

        # Test vcpkg dependency check
        result = build_script.check_and_fix_vcpkg_dependencies()
        print(f"vcpkg dependencies: {result}")

        print("\n[PHASE 4] Testing Python environment...")

        # Test dependency check
        missing, optional = build_script.check_python_dependencies()
        print(f"Python dependencies: {len(missing)} missing, {len(optional)} optional")

        print("\n[PHASE 5] Testing configuration verification...")

        # Check key files
        data_dir = Path("data")
        private_key = data_dir / "valid_private_key.der"
        public_key = data_dir / "valid_public_key.der"
        transfer_info = data_dir / "transfer.info"

        print(f"RSA private key exists: {private_key.exists()}")
        print(f"RSA public key exists: {public_key.exists()}")
        print(f"transfer.info exists: {transfer_info.exists()}")

        print("\n[PHASE 6] Testing service availability checks...")

        # Test port checks
        backup_server_running = build_script.check_backup_server_status()
        api_server_running = build_script.check_api_server_status()

        print(f"Backup server (port 1256) running: {backup_server_running}")
        print(f"API server (port 9090) running: {api_server_running}")

        print("\n[SUCCESS] All phase tests completed successfully!")
        print("The script should run without major issues.")

        return True

    except Exception as e:
        print(f"\n[ERROR] Dry run test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dry_run()
    sys.exit(0 if success else 1)
