#!/usr/bin/env python3
"""
Integrated BackupServer + FletV2 GUI Startup Script

This script directly instantiates the production BackupServer and integrates it
with the FletV2 GUI, eliminating the need for the FletV2ServerAdapter layer.

Usage:
    python start_integrated_gui.py              # Production mode with real server
    python start_integrated_gui.py --dev        # Development mode (web browser)
    python start_integrated_gui.py --mock       # Force mock mode for testing
"""

import asyncio
import contextlib
import logging
import os
import sys
import signal
from pathlib import Path
from typing import Optional, Any

# Add project directories to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Essential UTF-8 support for subprocess operations
import Shared.utils.utf8_solution as _  # Import for side effects

# Third-party imports
import flet as ft

# Import the production BackupServer
try:
    from python_server.server.server import BackupServer
    BACKUP_SERVER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import BackupServer: {e}")
    print("Running in mock-only mode")
    BACKUP_SERVER_AVAILABLE = False
    BackupServer = None

# Import FletV2 components
from main import main as flet_main, FletV2App
from utils.server_bridge import create_server_bridge
from utils.debug_setup import setup_terminal_debugging

# Set up logging
logger = setup_terminal_debugging(logger_name="IntegratedStartup")

class IntegratedServerManager:
    """
    Manages the lifecycle of both BackupServer and FletV2 GUI components,
    ensuring proper startup, integration, and shutdown coordination.
    """

    def __init__(self, force_mock: bool = False):
        self.force_mock = force_mock
        self.backup_server: Optional[Any] = None
        self.server_bridge: Optional[Any] = None
        self.gui_task: Optional[asyncio.Task] = None
        self.shutdown_event = asyncio.Event()

    async def initialize_backup_server(self) -> Optional[Any]:
        """
        Initialize the production BackupServer with proper error handling and migration.

        Returns:
            BackupServer instance if successful, None if failed or forced mock mode
        """
        if self.force_mock or not BACKUP_SERVER_AVAILABLE or not BackupServer:
            logger.info("🧪 Running in mock mode (BackupServer not available or forced)")
            return None

        try:
            logger.info("🚀 Initializing production BackupServer...")

            # Run database migration if needed before starting server
            if await self._run_database_migration():
                logger.info("✅ Database migration completed or not needed")
            else:
                logger.warning("⚠️ Database migration failed, continuing anyway")

            # Initialize BackupServer with default configuration
            # The BackupServer class handles its own database and component initialization
            backup_server = BackupServer()

            # Wait for server initialization to complete
            await asyncio.sleep(0.1)  # Give server time to initialize

            # Verify server is ready
            if hasattr(backup_server, 'is_connected') and backup_server.is_connected():
                logger.info("✅ BackupServer initialized successfully")
                return backup_server
            else:
                logger.warning("⚠️ BackupServer not responding to health check")
                return None

        except Exception as e:
            logger.error(f"❌ Failed to initialize BackupServer: {e}")
            logger.info("🧪 Falling back to mock mode")
            return None

    async def _run_database_migration(self) -> bool:
        """Run database migration if needed."""
        try:
            # Import migration system
            from schema_migration import migrate_database_schema

            logger.info("🔄 Checking database migration requirements...")

            # Run migration in a separate thread to avoid blocking
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            with ThreadPoolExecutor() as executor:
                # Run migration in background thread
                migration_result = await asyncio.get_event_loop().run_in_executor(
                    executor, migrate_database_schema, None
                )

            if migration_result:
                logger.info("✅ Database migration successful")
                return True
            else:
                logger.warning("⚠️ Database migration failed or not needed")
                return False

        except ImportError:
            logger.warning("📝 Migration system not available, skipping migration")
            return True  # Not an error if migration system isn't available
        except Exception as e:
            logger.error(f"❌ Migration error: {e}")
            return False

    def create_integrated_server_bridge(self, backup_server: Optional[Any]) -> Any:
        """
        Create ServerBridge with either real BackupServer or mock fallback.

        Args:
            backup_server: Initialized BackupServer instance or None for mock mode

        Returns:
            ServerBridge instance ready for FletV2 integration
        """
        try:
            if backup_server:
                logger.info("🔗 Creating ServerBridge with production BackupServer")
                server_bridge = create_server_bridge(real_server=backup_server)

                # Verify integration is working
                if hasattr(server_bridge, 'is_connected') and server_bridge.is_connected():
                    logger.info("✅ ServerBridge integration successful")
                    return server_bridge
                else:
                    logger.warning("⚠️ ServerBridge integration failed, falling back to mock")

            # Fallback to mock mode
            logger.info("🧪 Creating ServerBridge in mock mode")
            return create_server_bridge(real_server=None)

        except Exception as e:
            logger.error(f"❌ ServerBridge creation failed: {e}")
            logger.info("🧪 Using emergency mock fallback")
            return create_server_bridge(real_server=None)

    async def start_integrated_gui(self, development_mode: bool = False) -> None:
        """
        Start the integrated GUI with coordinated server management.

        Args:
            development_mode: If True, run in web browser for development
        """
        try:
            # Step 1: Initialize BackupServer
            self.backup_server = await self.initialize_backup_server()

            # Step 2: Create integrated ServerBridge
            self.server_bridge = self.create_integrated_server_bridge(self.backup_server)

            # Step 3: Use the main function with direct server injection
            async def integrated_main(page: ft.Page) -> None:
                """Wrapper function that calls the main function with real server."""
                try:
                    # Set up shutdown handler
                    page.on_window_event = self._create_window_event_handler(page)

                    # Call the main function with our BackupServer instance
                    await flet_main(page, real_server=self.backup_server)

                    # Log integration status
                    if self.backup_server:
                        logger.info("🎉 FletV2 GUI running with production BackupServer")
                    else:
                        logger.info("🧪 FletV2 GUI running in mock development mode")

                except Exception as e:
                    logger.error(f"❌ GUI initialization failed: {e}")
                    # Simple error display
                    error_text = ft.Text(f"Failed to start: {e}", color=ft.Colors.ERROR)
                    page.add(error_text)

            # Step 4: Launch GUI with appropriate view
            if development_mode:
                logger.info("🌐 Starting in development mode (web browser)")
                await ft.app_async(target=integrated_main, view=ft.AppView.WEB_BROWSER, port=8000)
            else:
                logger.info("🖥️ Starting in desktop application mode")
                await ft.app_async(target=integrated_main, view=ft.AppView.FLET_APP)

        except Exception as e:
            logger.error(f"❌ Integrated GUI startup failed: {e}")
            raise

    def _create_window_event_handler(self, page: ft.Page):
        """Create window event handler for shutdown coordination."""
        def on_window_event(e: ft.ControlEvent) -> None:
            if hasattr(e, 'data') and e.data == "close":
                logger.info("🛑 Window close event received, initiating shutdown...")
                self.shutdown_event.set()
        return on_window_event

    async def shutdown(self) -> None:
        """
        Perform coordinated shutdown of both server and GUI components.
        """
        logger.info("🛑 Starting coordinated shutdown...")

        try:
            # Shutdown BackupServer if it was initialized
            if self.backup_server:
                logger.info("🔌 Shutting down BackupServer...")
                try:
                    if hasattr(self.backup_server, 'shutdown'):
                        await self.backup_server.shutdown()
                    elif hasattr(self.backup_server, 'stop'):
                        await self.backup_server.stop()
                    logger.info("✅ BackupServer shutdown complete")
                except Exception as e:
                    logger.warning(f"⚠️ BackupServer shutdown error: {e}")

            # Clean up ServerBridge
            if self.server_bridge:
                logger.info("🧹 Cleaning up ServerBridge...")
                try:
                    if hasattr(self.server_bridge, 'cleanup'):
                        self.server_bridge.cleanup()
                    logger.info("✅ ServerBridge cleanup complete")
                except Exception as e:
                    logger.warning(f"⚠️ ServerBridge cleanup error: {e}")

            logger.info("✅ Coordinated shutdown complete")

        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")

async def main_integrated(development_mode: bool = False, force_mock: bool = False) -> None:
    """
    Main entry point for integrated BackupServer + FletV2 GUI.

    Args:
        development_mode: Run in web browser for development
        force_mock: Force mock mode even if BackupServer is available
    """
    manager = IntegratedServerManager(force_mock=force_mock)

    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"🛑 Signal {signum} received, initiating shutdown...")
        asyncio.create_task(manager.shutdown())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await manager.start_integrated_gui(development_mode=development_mode)
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
    finally:
        await manager.shutdown()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Integrated BackupServer + FletV2 GUI")
    parser.add_argument("--dev", action="store_true", help="Run in development mode (web browser)")
    parser.add_argument("--mock", action="store_true", help="Force mock mode for testing")
    args = parser.parse_args()

    # Configure environment
    os.environ.setdefault("PYTHONUTF8", "1")

# Integration Architecture: This startup script implements a clean 3-layer integration model:
# BackupServer -> ServerBridge -> FletV2App. The IntegratedServerManager handles lifecycle
# coordination, ensuring both components start and stop together gracefully. The key
# innovation is direct server injection into the existing FletV2App constructor,
# eliminating the need for the 836-line adapter layer.
#
# Error Resilience: The system maintains full fallback capability - if BackupServer
# initialization fails for any reason, it automatically falls back to mock mode,
# ensuring the GUI remains functional for development and testing.

    print("🚀 Starting Integrated BackupServer + FletV2 GUI...")
    print(f"📊 Mode: {'Development (Web)' if args.dev else 'Production (Desktop)'}")
    print(f"🧪 Mock: {'Forced' if args.mock else 'Auto-detect'}")

    try:
        asyncio.run(main_integrated(development_mode=args.dev, force_mock=args.mock))
    except KeyboardInterrupt:
        print("\n🛑 Shutdown complete")
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        sys.exit(1)