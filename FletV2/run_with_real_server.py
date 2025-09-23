#!/usr/bin/env python3
"""
Integration script to run FletV2 with real BackupServer instance.

This script properly initializes the BackupServer and passes it to FletV2.
Usage:
    python run_with_real_server.py

External Integration:
    from run_with_real_server import launch_fletv2_with_server
    launch_fletv2_with_server(my_backup_server)
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fletv2_root = os.path.join(project_root, 'FletV2')

for path in [project_root, fletv2_root]:
    if path not in sys.path:
        sys.path.insert(0, path)

# ALWAYS import UTF-8 solution first
import Shared.utils.utf8_solution as _

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Flet
import flet as ft

def initialize_real_server():
    """Initialize and start BackupServer instance."""
    try:
        # Import BackupServer
        from python_server.server.server import BackupServer

        # Create BackupServer instance (uses defaults for database and port)
        backup_server = BackupServer()
        logger.info("✅ BackupServer initialized successfully")

        # Start the server to make is_connected() return True
        try:
            logger.info("🚀 Starting BackupServer...")
            backup_server.start()
            logger.info("✅ BackupServer started successfully")

            # Verify the server is now connected
            if backup_server.is_connected():
                logger.info("✅ Server is connected and operational")
            else:
                logger.warning("⚠️ Server started but not showing as connected")

        except Exception as start_e:
            logger.error(f"❌ Failed to start server: {start_e}")
            # Continue anyway - some functionality may still work

        # Test basic functionality
        try:
            # Test get_clients to ensure server is working
            clients_result = backup_server.get_clients()
            if isinstance(clients_result, dict) and clients_result.get('success'):
                client_count = len(clients_result.get('data', []))
                logger.info(f"✅ Server test successful - {client_count} clients found")
            else:
                logger.warning(f"⚠️ Server test returned: {clients_result}")
        except Exception as test_e:
            logger.warning(f"⚠️ Server test failed: {test_e}")

        return backup_server

    except Exception as e:
        logger.error(f"❌ Failed to initialize BackupServer: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def launch_fletv2_with_server(backup_server=None):
    """Launch FletV2 with the provided backup server."""
    try:
        # Import FletV2 main function
        from main import main as fletv2_main

        logger.info("🚀 Starting FletV2 GUI with real server integration...")

        # Wrap main function with server
        async def app_with_server(page: ft.Page):
            await fletv2_main(page, backup_server)

        # Launch FletV2
        asyncio.run(ft.app_async(
            target=app_with_server,
            view=ft.AppView.FLET_APP
        ))

    except Exception as e:
        logger.error(f"❌ Failed to launch FletV2: {e}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """Main function for standalone execution."""
    logger.info("🎯 FletV2 Real Server Integration Script")
    logger.info("=" * 50)

    # Initialize real server
    backup_server = initialize_real_server()

    if backup_server:
        logger.info("✅ Real server initialized successfully")
    else:
        logger.warning("⚠️ Running without real server - some features may be limited")

    # Start FletV2 with real server
    logger.info("🎨 Starting FletV2 GUI...")
    launch_fletv2_with_server(backup_server)

if __name__ == "__main__":
    main()