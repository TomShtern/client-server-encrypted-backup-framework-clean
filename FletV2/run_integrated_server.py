#!/usr/bin/env python3
"""
Clean Integrated Server Startup Script

This script properly configures Python paths and environment variables
before starting the integrated BackupServer + FletV2 GUI.
"""

import os
import sys
from pathlib import Path

# Essential UTF-8 support for console operations
os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Try to import UTF-8 solution if available
try:
    # First try from parent directory structure
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import Shared.utils.utf8_solution as _
except ImportError:
    try:
        # Try relative import from current location
        import os
        import sys
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        import Shared.utils.utf8_solution as _
    except ImportError:
        # Silent fallback - UTF-8 setup attempted through environment variables
        pass

def setup_environment():
    """Set up proper Python environment for integrated server."""
    # Get current directory
    current_dir = Path(__file__).parent.absolute()
    parent_dir = current_dir.parent

    # Add directories to Python path
    paths_to_add = [
        str(current_dir),      # FletV2 directory
        str(parent_dir),       # Parent directory for Shared imports
    ]

    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)

    # Set environment variables - crucial for subprocess imports
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    new_pythonpath = os.pathsep.join(paths_to_add + ([current_pythonpath] if current_pythonpath else []))
    os.environ['PYTHONPATH'] = new_pythonpath
    os.environ['PYTHONUTF8'] = '1'
    os.environ['PYTHONIOENCODING'] = 'utf-8'

    print("[OK] Python paths configured:")
    for path in paths_to_add:
        print(f"   - {path}")

def is_port_available(port):
    """Check if a port is available for use."""
    import socket
    try:
        # Try IPv4 first
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # On Windows, also set SO_EXCLUSIVEADDRUSE to avoid Error 10048
            if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            sock.bind(('127.0.0.1', port))
            sock.listen(1)  # Try to listen to ensure port is truly available
            return True
    except OSError:
        pass

    try:
        # Try IPv6
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # On Windows, also set SO_EXCLUSIVEADDRUSE to avoid Error 10048
            if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            sock.bind(('::1', port))
            sock.listen(1)  # Try to listen to ensure port is truly available
            return True
    except OSError:
        pass

    return False

def find_available_port(start_port=8000, max_port=8100):
    """Find an available port starting from start_port."""
    import random
    import socket

    # First try the start port
    if is_port_available(start_port):
        return start_port

    # Try a few ports in sequence
    for port in range(start_port + 1, min(start_port + 10, max_port)):
        if is_port_available(port):
            return port

    # If sequential ports don't work, try random ports in the range
    attempts = 0
    while attempts < 20 and start_port + attempts < max_port:
        port = random.randint(start_port + 1, max_port)
        if is_port_available(port):
            return port
        attempts += 1

    # Last resort: let the OS choose a port
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # On Windows, also set SO_EXCLUSIVEADDRUSE to avoid Error 10048
            if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
                s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            s.bind(('127.0.0.1', 0))  # 0 means let OS choose
            s.listen(1)
            return s.getsockname()[1]
    except OSError:
        raise RuntimeError(f"No available ports found between {start_port} and {max_port}")

def run_integrated_server(dev_mode=True, port=None):
    """Run the integrated server with proper configuration."""
    setup_environment()

    # Import after path setup
    try:
        import asyncio

        from start_integrated_gui import main_integrated

        # Find available port if not specified
        if dev_mode and port is None:
            try:
                port = find_available_port()
                print(f"🔍 Found available port: {port}")
            except RuntimeError as e:
                print(f"⚠️ Port detection failed: {e}, using default 8000")
                port = 8000
        elif dev_mode and port is not None:
            # If a specific port is requested, verify it's available
            if not is_port_available(port):
                print(f"⚠️ Requested port {port} is not available. Finding alternative...")
                try:
                    port = find_available_port(start_port=port+1)
                    print(f"🔍 Found alternative port: {port}")
                except RuntimeError:
                    print(f"⚠️ Port detection failed, using requested port {port}")

        print("🚀 Starting integrated server...")
        print(f"📊 Mode: {'Development (Web)' if dev_mode else 'Production (Desktop)'}")
        if dev_mode and port:
            print(f"🌐 Web URL: http://127.0.0.1:{port}")

        # Try to run the integrated server with port
        try:
            port_to_use = port if port is not None else 8000
            asyncio.run(main_integrated(development_mode=dev_mode, force_mock=False, port=port_to_use))
        except OSError as e:
            error_msg = str(e).lower()
            if "address already in use" in error_msg or "[errno 10048]" in error_msg or "only one usage of each socket address" in error_msg:
                print(f"⚠️ Port {port} is already in use. Finding alternative port...")
                try:
                    start_port = (port + 1) if port is not None else 8000
                    new_port = find_available_port(start_port=start_port)
                    print(f"🔍 Found alternative port: {new_port}")
                    print(f"🌐 Web URL: http://127.0.0.1:{new_port}")
                    asyncio.run(main_integrated(development_mode=dev_mode, force_mock=False, port=new_port))
                except Exception as fallback_error:
                    print(f"❌ Failed to start server on alternative port: {fallback_error}")
                    raise
            else:
                # Re-raise the exception if it's not a port conflict
                raise
        except Exception as e:
            # Handle any other exceptions that might occur
            print(f"❌ Error starting server: {e}")
            import traceback
            traceback.print_exc()
            raise

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure you're running from the FletV2 directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clean Integrated BackupServer + FletV2 GUI")
    parser.add_argument("--prod", action="store_true", help="Run in production mode (desktop)")
    parser.add_argument("--port", type=int, help="Specific port to use")
    args = parser.parse_args()

    dev_mode = not args.prod

    try:
        run_integrated_server(dev_mode=dev_mode, port=args.port)
    except KeyboardInterrupt:
        print("\n🛑 Shutdown complete")
    except SystemExit:
        # Re-raise SystemExit to properly exit the program
        raise
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
