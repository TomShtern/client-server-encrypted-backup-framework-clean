
import flet as ft
import asyncio
from FletV2.views.settings import create_settings_view

async def main(page: ft.Page):
    page.title = "Settings Test"
    
    # Mock dependencies
    server_bridge = None
    state_manager = None
    global_search = None
    
    try:
        content, dispose, setup = create_settings_view(server_bridge, page, state_manager, global_search)
        page.add(content)
        await setup()
        print("Settings view created and setup successfully")
    except Exception as e:
        print(f"Error creating settings view: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ft.app(target=main)
