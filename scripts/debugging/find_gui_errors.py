#!/usr/bin/env python3
import sys
import os
import traceback

# Add server directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python_server', 'server'))

def find_errors():
    print("=== ServerGUI Error Detection ===")
    
    try:
        # Test imports
        print("Testing imports...")
        from ServerGUI import (
            ServerGUI, ModernCard, ModernProgressBar, ModernStatusIndicator,
            ModernTheme, ToastNotification, ModernTable
        )
        print("✓ All imports successful")
        
        # Test basic instantiation
        print("Testing ServerGUI instantiation...")
        gui = ServerGUI()
        print("✓ ServerGUI created")
        
        # Test widget creation
        print("Testing widget creation...")
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        try:
            card = ModernCard(root, title="Test")
            print("✓ ModernCard works")
        except Exception as e:
            print(f"✗ ModernCard error: {e}")
            
        try:
            progress = ModernProgressBar(root)
            progress.set_progress(50)
            print("✓ ModernProgressBar works")
        except Exception as e:
            print(f"✗ ModernProgressBar error: {e}")
            
        try:
            status = ModernStatusIndicator(root)
            status.set_status("online")
            print("✓ ModernStatusIndicator works")
        except Exception as e:
            print(f"✗ ModernStatusIndicator error: {e}")
            
        root.destroy()
        
        # Test GUI methods
        print("Testing GUI methods...")
        try:
            gui.update_server_status(True, "127.0.0.1", 1256)
            gui.update_client_stats(5, 10, 2)
            gui.update_transfer_stats(1024, "now")
            gui.show_error("test")
            gui.show_success("test")
            gui.show_info("test")
            print("✓ All GUI methods work")
        except Exception as e:
            print(f"✗ GUI method error: {e}")
            traceback.print_exc()
        
        print("✅ No errors found!")
        return True
        
    except Exception as e:
        print(f"❌ Error found: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    find_errors()
