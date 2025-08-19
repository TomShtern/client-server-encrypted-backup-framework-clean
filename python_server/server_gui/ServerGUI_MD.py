# -*- coding: utf-8 -*-
"""
KivyMD Server GUI Skeleton - Basic Material Design GUI for Encrypted Backup Server
Simple migration skeleton from Tkinter to KivyMD

This is a minimal skeleton version to establish basic structure and test functionality.
"""

from __future__ import annotations
import sys
import os

# --- UTF-8 Solution Import ---
try:
    import Shared.utils.utf8_solution
except ImportError:
    print("[WARNING] Could not enable UTF-8 solution.")

# --- KivyMD Basic Imports ---
try:
    from kivymd.app import MDApp
    from kivymd.uix.screen import MDScreen
    from kivymd.uix.label import MDLabel
    from kivymd.uix.button import MDRaisedButton
    from kivymd.uix.boxlayout import MDBoxLayout
    KIVYMD_AVAILABLE = True
except ImportError as e:
    print(f"[ERROR] KivyMD not available: {e}")
    print("Please install KivyMD: pip install kivymd")
    KIVYMD_AVAILABLE = False
    sys.exit(1)


class DashboardScreen(MDScreen):
    """Simple dashboard screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "dashboard"
        self.setup_ui()
    
    def setup_ui(self):
        """Setup basic dashboard UI"""
        layout = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20
        )
        
        # Title
        title = MDLabel(
            text="Encrypted Backup Server",
            font_style="H4",
            halign="center",
            size_hint_y=None,
            height="60dp"
        )
        
        # Status label
        self.status_label = MDLabel(
            text="Server Status: Stopped",
            font_style="H6", 
            halign="center",
            size_hint_y=None,
            height="40dp"
        )
        
        # Start button
        start_button = MDRaisedButton(
            text="START SERVER",
            size_hint=(None, None),
            size=("200dp", "50dp"),
            pos_hint={'center_x': 0.5},
            on_release=self.start_server
        )
        
        # Stop button
        stop_button = MDRaisedButton(
            text="STOP SERVER",
            size_hint=(None, None),
            size=("200dp", "50dp"),
            pos_hint={'center_x': 0.5},
            on_release=self.stop_server
        )
        
        layout.add_widget(title)
        layout.add_widget(self.status_label)
        layout.add_widget(start_button)
        layout.add_widget(stop_button)
        
        self.add_widget(layout)
    
    def start_server(self, *args):
        """Start server placeholder"""
        self.status_label.text = "Server Status: Running"
        print("[INFO] Server start requested")
    
    def stop_server(self, *args):
        """Stop server placeholder"""
        self.status_label.text = "Server Status: Stopped"
        print("[INFO] Server stop requested")


class ServerMDApp(MDApp):
    """Basic KivyMD application skeleton"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Server GUI - KivyMD Skeleton"
        
        # Set basic theme
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark"
    
    def build(self):
        """Build the basic app"""
        return DashboardScreen()


def main():
    """Main entry point"""
    if not KIVYMD_AVAILABLE:
        print("[ERROR] KivyMD is not available. Please install it with: pip install kivymd")
        return
    
    print("[INFO] Starting KivyMD Server GUI Skeleton...")
    app = ServerMDApp()
    app.run()


if __name__ == "__main__":
    main()