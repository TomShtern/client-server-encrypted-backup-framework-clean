#!/usr/bin/env python3
"""
Comprehensive stress test to find all remaining errors in ServerGUI
"""

import sys
import os
import traceback

# Add the server directory to the path with better error handling
def setup_import_paths():
    """Setup import paths and validate ServerGUI availability"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try multiple potential locations for ServerGUI
    potential_paths = [
        os.path.join(base_dir, 'server'),  # server subdirectory
        os.path.join(base_dir, 'Server'),  # Server subdirectory (capital S)
        base_dir,  # same directory as this script
        os.path.join(base_dir, '..', 'server'),  # parent/server
        os.path.join(base_dir, 'src'),  # src subdirectory
    ]
    
    print("🔍 Searching for ServerGUI module...")
    for path in potential_paths:
        servergui_file = os.path.join(path, 'ServerGUI.py')
        print(f"   Checking: {servergui_file}")
        
        if os.path.exists(servergui_file):
            print(f"✅ Found ServerGUI.py at: {path}")
            if path not in sys.path:
                sys.path.insert(0, path)
            return True, path
        else:
            print(f"   ❌ Not found")
    
    # List all Python files in the base directory for debugging
    print(f"\n🔍 Python files in {base_dir}:")
    try:
        for file in os.listdir(base_dir):
            if file.endswith('.py'):
                print(f"   📄 {file}")
    except Exception as e:
        print(f"   ❌ Error listing files: {e}")
    
    return False, None

def test_all_gui_features():
    """Test all GUI features to find errors"""
    print("🔍 Comprehensive GUI Feature Test")
    print("=" * 50)
    
    errors_found = []
    
    # Setup import paths first
    servergui_found, servergui_path = setup_import_paths()
    
    if not servergui_found:
        error_msg = (
            "ServerGUI.py not found in any expected location. "
            "Please ensure ServerGUI.py exists in one of these locations:\n"
            "  - ./server/ServerGUI.py\n"
            "  - ./ServerGUI.py\n"
            "  - ../server/ServerGUI.py\n"
            "  - ./src/ServerGUI.py"
        )
        errors_found.append(error_msg)
        print(f"❌ {error_msg}")
        return errors_found
    
    try:
        # Import with better error handling - moved inside try block after path validation
        print(f"📦 Attempting import from: {servergui_path}")
        
        from server.ServerGUI import (
            ServerGUI, ModernCard, ModernProgressBar, ModernStatusIndicator,
            AdvancedProgressBar, ToastNotification, ModernTable, SettingsDialog,
            ModernChart, ModernTheme, CHARTS_AVAILABLE, SYSTEM_MONITOR_AVAILABLE,
            TRAY_AVAILABLE, initialize_server_gui, get_server_gui, shutdown_server_gui
        )
        print("✅ All imports successful")
    except ImportError as e:
        error_msg = f"Import error: {e}. ServerGUI.py found but import failed - check for syntax errors or missing dependencies."
        errors_found.append(error_msg)
        print(f"❌ {error_msg}")
        
        # Try to get more details about the import error
        try:
            import server.ServerGUI
            print("✅ Basic ServerGUI import works, specific imports may be missing")
        except Exception as basic_error:
            print(f"❌ Even basic ServerGUI import fails: {basic_error}")
            traceback.print_exc()
        
        return errors_found
    except Exception as e:
        error_msg = f"Unexpected import error: {e}"
        errors_found.append(error_msg)
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return errors_found
    
    # Test 1: Basic GUI creation and methods
    try:
        gui = ServerGUI()
        
        # Test all basic update methods
        gui.update_server_status(True, "127.0.0.1", 1256)
        gui.update_client_stats(connected=5, total=10, active_transfers=2)
        gui.update_transfer_stats(bytes_transferred=1024*1024, last_activity="now")
        gui.update_maintenance_stats({
            'files_cleaned': 5,
            'partial_files_cleaned': 2,
            'clients_cleaned': 1,
            'last_cleanup': '2025-06-15 10:00:00'
        })
        
        # Test notification methods
        gui.show_error("Test error")
        gui.show_success("Test success")
        gui.show_info("Test info")
        
        print("✅ Basic GUI methods work")
    except Exception as e:
        errors_found.append(f"Basic GUI methods error: {e}")
        print(f"❌ Basic GUI methods failed: {e}")
        traceback.print_exc()
    
    # Test 2: Widget creation
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        # Test all custom widgets
        card = ModernCard(root, title="Test Card")
        progress = ModernProgressBar(root)
        progress.set_progress(50)
        status = ModernStatusIndicator(root)
        status.set_status("online")
        
        # Test advanced progress bar
        adv_progress = AdvancedProgressBar(root)
        adv_progress.set_progress(75)
        
        # Test toast system
        toast = ToastNotification(root)
        
        # Test table
        columns = {'col1': {'text': 'Column 1', 'width': 100}}
        table = ModernTable(root, columns)
        table.set_data([{'col1': 'test'}])
        
        root.destroy()
        print("✅ All widgets create successfully")
    except Exception as e:
        errors_found.append(f"Widget creation error: {e}")
        print(f"❌ Widget creation failed: {e}")
        traceback.print_exc()
    
    # Test 3: Settings dialog
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        settings = {'port': 1256, 'storage_dir': 'test'}
        dialog = SettingsDialog(root, settings)
        # Don't actually show the dialog
        
        root.destroy()
        print("✅ Settings dialog creates successfully")
    except Exception as e:
        errors_found.append(f"Settings dialog error: {e}")
        print(f"❌ Settings dialog failed: {e}")
        traceback.print_exc()
    
    # Test 4: Chart functionality
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        chart = ModernChart(root, chart_type="line")
        if CHARTS_AVAILABLE:
            chart.update_data({'x': [1, 2, 3], 'y': [1, 4, 2]}, "Test Chart")
        
        root.destroy()
        print("✅ Chart functionality works")
    except Exception as e:
        errors_found.append(f"Chart error: {e}")
        print(f"❌ Chart functionality failed: {e}")
        traceback.print_exc()
    
    # Test 5: Global functions
    try:
        # Test global helper functions
        result = initialize_server_gui()
        if result:
            gui = get_server_gui()
            gui.show_info("Test from global functions")
            shutdown_server_gui()
        
        print("✅ Global functions work")
    except Exception as e:
        errors_found.append(f"Global functions error: {e}")
        print(f"❌ Global functions failed: {e}")
        traceback.print_exc()
    
    # Test 6: Theme validation
    try:
        # Test all theme constants exist and are valid
        theme_attrs = [attr for attr in dir(ModernTheme) if not attr.startswith('_')]
        for attr in theme_attrs:
            value = getattr(ModernTheme, attr)
            if isinstance(value, str) and value.startswith('#'):
                # Validate hex color
                if len(value) not in [4, 7] or not all(c in '0123456789ABCDEFabcdef' for c in value[1:]):
                    errors_found.append(f"Invalid color: {attr} = {value}")
        
        print("✅ Theme validation passed")
    except Exception as e:
        errors_found.append(f"Theme validation error: {e}")
        print(f"❌ Theme validation failed: {e}")
        traceback.print_exc()
    
    # Test 7: Method completeness
    try:
        gui = ServerGUI()
        
        # Check for essential methods
        essential_methods = [
            'initialize', 'shutdown', 'update_server_status', 
            'update_client_stats', 'update_transfer_stats',
            'show_error', 'show_success', 'show_info',
            '_create_main_window', '_create_menu_bar', '_create_header',
            '_create_tab_system', '_create_dashboard_tab'
        ]
        
        for method in essential_methods:
            if not hasattr(gui, method):
                errors_found.append(f"Missing method: {method}")
            elif not callable(getattr(gui, method)):
                errors_found.append(f"Method not callable: {method}")
        
        print("✅ Method completeness check passed")
    except Exception as e:
        errors_found.append(f"Method completeness error: {e}")
        print(f"❌ Method completeness failed: {e}")
        traceback.print_exc()
    
    # Test 8: Advanced features
    try:
        # Test availability flags
        print(f"📊 Charts available: {CHARTS_AVAILABLE}")
        print(f"🖥️ System monitoring available: {SYSTEM_MONITOR_AVAILABLE}")
        print(f"🔔 System tray available: {TRAY_AVAILABLE}")
        
        # Test chart data structures
        gui = ServerGUI()
        performance_data = gui.performance_data
        if not all(key in performance_data for key in ['cpu_usage', 'memory_usage', 'network_activity']):
            errors_found.append("Missing performance data keys")
        
        print("✅ Advanced features check passed")
    except Exception as e:
        errors_found.append(f"Advanced features error: {e}")
        print(f"❌ Advanced features failed: {e}")
        traceback.print_exc()
    
    return errors_found

def main():
    """Run comprehensive test"""
    print("🧪 COMPREHENSIVE ServerGUI ERROR DETECTION")
    print("=" * 60)
    
    errors = test_all_gui_features()
    
    print("\n" + "=" * 60)
    print("📋 FINAL RESULTS")
    print("=" * 60)
    
    if not errors:
        print("🎉 NO ERRORS FOUND!")
        print("✅ ServerGUI appears to be fully functional")
        print("🚀 All features tested successfully")
        return True
    else:
        print(f"❌ {len(errors)} ERRORS FOUND:")
        print("=" * 30)
        for i, error in enumerate(errors, 1):
            print(f"{i:2d}. {error}")
        
        print("\n🔧 These errors need to be fixed:")
        for error in errors:
            print(f"   • {error}")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
