import os
import sys
from unittest.mock import MagicMock

import flet as ft

# Add project root to path
sys.path.insert(0, os.getcwd())
# Add FletV2 to path to mimic app environment
sys.path.insert(0, os.path.join(os.getcwd(), "FletV2"))

try:
    from FletV2.views.dashboard import create_dashboard_view

    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

try:
    page = MagicMock(spec=ft.Page)
    bridge = MagicMock()
    # Mock bridge responses
    bridge.get_server_status.return_value = {
        "clients_connected": 5,
        "total_transfers": 2,
        "total_files": 1500,
        "uptime_seconds": 3600,
    }
    bridge.get_logs.return_value = [
        {
            "timestamp": "2025-01-01T12:00:00",
            "level": "INFO",
            "message": "Test log",
            "source": "System",
        }
    ]

    content, cleanup, loader = create_dashboard_view(
        server_bridge=bridge, page=page, _state_manager=None, navigate_callback=None
    )
    print("✅ View creation successful")

    # Test data loading
    import asyncio

    async def test_load():
        await loader()
        print("✅ Data loading successful")

    asyncio.run(test_load())

except Exception as e:
    print(f"❌ Execution failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
