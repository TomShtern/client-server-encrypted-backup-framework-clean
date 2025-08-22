#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to diagnose KivyMD text rendering issues
This creates a minimal test case to identify the problem
"""

import os
import sys

# Add UTF-8 solution
sys.path.insert(0, '.')
try:
    import Shared.utils.utf8_solution
    print("[INFO] UTF-8 solution enabled")
except ImportError:
    print("[WARNING] UTF-8 solution not available")

# Kivy configuration - must be set before importing kivy
from kivy.config import Config

# Text rendering configuration
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')

# Force specific text renderer (try different options)
Config.set('graphics', 'resizable', False)

# Try different text providers
print("[INFO] Available text providers:", Config.get('kivy', 'text'))

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton

class TextRenderingTest(MDApp):
    def build(self):
        # Set Material Design 3 theme
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        
        # Main layout
        layout = MDBoxLayout(
            orientation="vertical",
            spacing="20dp",
            padding="20dp"
        )
        
        # Test different text elements
        test_texts = [
            "Simple text test",
            "Server Dashboard",
            "System Statistics", 
            "Live Monitoring",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "1234567890",
            "Special chars: !@#$%^&*()"
        ]
        
        for i, text in enumerate(test_texts):
            label = MDLabel(
                text=f"Test {i+1}: {text}",
                font_style="Body",
                theme_text_color="Primary",
                size_hint_y=None,
                height="40dp"
            )
            layout.add_widget(label)
        
        # Test button text
        button = MDRaisedButton(
            text="Test Button",
            size_hint=(None, None),
            size=("200dp", "40dp"),
            pos_hint={"center_x": 0.5}
        )
        layout.add_widget(button)
        
        return layout

if __name__ == "__main__":
    print("[INFO] Starting text rendering test...")
    print(f"[INFO] Python encoding: {sys.stdout.encoding}")
    print(f"[INFO] File system encoding: {sys.getfilesystemencoding()}")
    
    try:
        app = TextRenderingTest()
        app.run()
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()