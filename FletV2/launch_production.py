#!/usr/bin/env python3
"""
FletV2 Production Launcher

Simple script to launch FletV2 with your real server integration.
Handles environment setup and provides clear feedback about the connection status.
"""

import os
import sys
import logging
from pathlib import Path

def setup_environment():
    """Set up the environment for FletV2."""
    # Ensure we're in the FletV2 directory
    fletv2_dir = Path(__file__).parent
    os.chdir(fletv2_dir)

    # Add project root to Python path
    project_root = fletv2_dir.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

def check_integration_status():
    """Check and report integration status."""
    print("🔍 Checking FletV2 integration status...")

    try:
        from server_adapter import create_fletv2_server
        print("✅ Server adapter available")

        # Test server connection
        server = create_fletv2_server()
        if server.is_connected():
            print("✅ Real server connected successfully")

            # Get quick stats
            status = server.get_server_status()
            clients = server.get_clients()
            files = server.get_files()

            print(f"📊 Server Status:")
            print(f"   • Running: {status.get('running', False)}")
            print(f"   • Clients: {len(clients)}")
            print(f"   • Files: {len(files)}")
            print(f"   • Storage: {status.get('storage_used_gb', 0)} GB")

            return True
        else:
            print("⚠️ Server adapter available but not connected")
            return False

    except ImportError as e:
        print(f"⚠️ Server adapter not available: {e}")
        print("📝 Will run in mock mode for development")
        return False
    except Exception as e:
        print(f"❌ Server connection error: {e}")
        print("📝 Will fall back to mock mode")
        return False

def launch_fletv2():
    """Launch FletV2 application."""
    print("\n🚀 Launching FletV2...")

    try:
        # Import and run FletV2
        import flet as ft
        from main import FletV2App
        from theme import setup_modern_theme

        def main(page: ft.Page):
            # Set up page
            page.title = "Encrypted Backup Framework - Production"
            page.window.width = 1400
            page.window.height = 900
            page.window.min_width = 1000
            page.window.min_height = 600
            page.window.center()

            # Setup theme
            setup_modern_theme(page)

            # Create and add app
            app = FletV2App(page)
            page.add(app)

            print("✨ FletV2 launched successfully!")
            print("🌐 Access your backup server management interface in the browser")

        # Launch in browser for better development experience
        ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)

    except Exception as e:
        print(f"❌ Failed to launch FletV2: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

def main():
    """Main launcher function."""
    print("=" * 60)
    print("🎯 FletV2 Production Launcher")
    print("   Encrypted Backup Framework GUI")
    print("=" * 60)

    # Setup environment
    setup_environment()

    # Check integration status
    has_real_server = check_integration_status()

    if has_real_server:
        print("\n🎉 PRODUCTION MODE: Using real server data")
        print("⚠️  All operations will affect your actual database")
    else:
        print("\n🧪 DEVELOPMENT MODE: Using mock data")
        print("✅ Safe for UI development and testing")

    print("\n" + "=" * 60)

    # Launch FletV2
    if launch_fletv2():
        print("\n🎊 FletV2 session completed successfully!")
    else:
        print("\n❌ FletV2 launch failed!")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())