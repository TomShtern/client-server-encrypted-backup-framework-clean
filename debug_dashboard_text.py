#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug dashboard text rendering - isolate the exact issue
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# UTF-8 solution
try:
    import Shared.utils.utf8_solution
    print("[INFO] UTF-8 solution enabled")
except ImportError:
    print("[WARNING] UTF-8 solution not available")

# Kivy configuration
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
os.environ['KIVY_TEXT'] = 'sdl2'
os.environ['KIVY_WINDOW'] = 'sdl2'

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd_gui.components.md3_label import MD3Label

class DebugTextApp(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        
        layout = MDBoxLayout(orientation="vertical", spacing="20dp", padding="20dp")
        
        # Test 1: Original MDLabel 
        layout.add_widget(MDLabel(text="TEST 1: Original MDLabel", font_style="Title"))
        layout.add_widget(MDLabel(text="Server Overview", font_style="Headline"))
        layout.add_widget(MDLabel(text="System Statistics", font_style="Body"))
        
        # Test 2: MD3Label
        layout.add_widget(MD3Label(text="TEST 2: MD3Label", font_style="Title"))
        layout.add_widget(MD3Label(text="Server Overview", font_style="Headline"))
        layout.add_widget(MD3Label(text="System Statistics", font_style="Body"))
        
        # Test 3: Labels with specific properties that might be in dashboard
        bad_label = MD3Label(
            text="TEST 3: Dashboard-style label",
            font_style="Body",
            theme_text_color="Primary",
            adaptive_height=True
        )
        layout.add_widget(bad_label)
        
        # Test 4: Check exact dashboard text that appears vertical
        dashboard_texts = [
            "Server Overview",
            "System Statistics", 
            "Live Monitoring",
            "Activity Log",
            "Performance Metrics"
        ]
        
        for text in dashboard_texts:
            label = MD3Label(text=f"Dashboard: {text}", font_style="Body")
            layout.add_widget(label)
        
        return layout

if __name__ == "__main__":
    print("[INFO] Starting dashboard text debug...")
    
    try:
        app = DebugTextApp()
        app.run()
    except Exception as e:
        print(f"[ERROR] Debug failed: {e}")
        import traceback
        traceback.print_exc()