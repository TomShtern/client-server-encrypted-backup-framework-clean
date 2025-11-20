#!/usr/bin/env python3
"""
Minimal dashboard test - exactly replicate the dashboard text rendering issue
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

# Kivy configuration - EXACTLY like main.py
from kivy.config import Config

Config.set('graphics', 'width', '1400')
Config.set('graphics', 'height', '900')
Config.set('graphics', 'minimum_width', '1000')
Config.set('graphics', 'minimum_height', '700')
Config.set('graphics', 'resizable', '1')
Config.set('kivy', 'window_icon', '')

# CRITICAL: Fix text rendering configuration
os.environ['KIVY_TEXT'] = 'sdl2'
os.environ['KIVY_WINDOW'] = 'sdl2'

# UTF-8 environment setup
from Shared.filesystem.utf8_solution import UTF8Support

utf8_env = UTF8Support.get_env()
for key, value in utf8_env.items():
    os.environ[key] = value

from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd_gui.components.md3_label import MD3Label


class MinimalDashboardTest(MDApp):
    def build(self):
        # EXACTLY like main.py
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        layout = MDBoxLayout(
            orientation="vertical",
            spacing="20dp",
            padding="20dp"
        )

        # Test 1: EXACT dashboard labels that are showing vertical text
        layout.add_widget(MDLabel(text="BROKEN: Regular MDLabel"))

        broken_label = MDLabel(
            text="Server Overview",
            font_style="Display",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(48)
        )
        layout.add_widget(broken_label)

        # Test 2: Our "fixed" MD3Label
        layout.add_widget(MDLabel(text="FIXED: MD3Label"))

        fixed_label = MD3Label(
            text="Server Overview",
            font_style="Display",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(48)
        )
        layout.add_widget(fixed_label)

        # Test 3: Basic test without any size constraints
        layout.add_widget(MDLabel(text="BASIC: No constraints"))
        basic_label = MD3Label(text="Server Overview")
        layout.add_widget(basic_label)

        # Test 4: Force specific text properties
        layout.add_widget(MDLabel(text="FORCE: Explicit text_size"))
        force_label = MDLabel(text="Server Overview")
        # Explicitly set what we want
        force_label.text_size = (None, None)
        force_label.markup = False
        force_label.shorten = False
        layout.add_widget(force_label)

        # Test 5: The other way
        layout.add_widget(MDLabel(text="FORCE2: No text_size"))
        force2_label = MDLabel(text="Server Overview")
        # Don't set text_size at all, let Kivy handle it
        force2_label.markup = False
        force2_label.shorten = False
        layout.add_widget(force2_label)

        return layout

if __name__ == "__main__":
    print("[INFO] Starting minimal dashboard test...")
    print("[INFO] This will show which configuration actually works")

    try:
        app = MinimalDashboardTest()
        app.run()
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
