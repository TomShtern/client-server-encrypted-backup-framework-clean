import os
import sys
import traceback

# Setup paths
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print(f"CWD: {current_dir}")
print(f"Path: {sys.path[:3]}")

try:
    print("Imported flet")

    # Try importing theme first to check attributes
    import FletV2.theme as theme

    print(f"Theme file: {theme.__file__}")
    if hasattr(theme, "create_neumorphic_metric_card"):
        print("SUCCESS: create_neumorphic_metric_card exists in theme")
    else:
        print("FAILURE: create_neumorphic_metric_card MISSING in theme")
        # List attributes to debug
        print(f"Available attributes: {[x for x in dir(theme) if 'create' in x]}")

    print("Importing database_pro...")
    from FletV2.views.database_pro import create_database_view

    print("Import successful. Trying to create view...")

    # Mock Page
    class MockPage:
        def __init__(self):
            self.platform = "windows"
            self.route = "/"
            self.controls = []
            self.overlay = []
            self.on_route_change = None
            self.on_view_pop = None
            self.appbar = None
            self.navigation_bar = None
            self.floating_action_button = None
            self.window_width = 800
            self.window_height = 600

    page = MockPage()

    # Try creating the view
    create_database_view(None, page)
    print("View created successfully")

except Exception as e:
    print(f"CRITICAL FAILURE: {e}")
    traceback.print_exc()
