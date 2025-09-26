#!/usr/bin/env python3
"""
Visual test to verify KivyMD text rendering fix
Creates side-by-side comparison of old vs new label rendering
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
Config.set('graphics', 'height', '400')
os.environ['KIVY_TEXT'] = 'sdl2'
os.environ['KIVY_WINDOW'] = 'sdl2'

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd_gui.components.md3_label import MD3Label


class TextRenderingComparisonApp(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"

        main_layout = MDBoxLayout(orientation="horizontal", spacing="20dp", padding="20dp")

        # OLD (Broken) Label Card
        old_card = MDCard(
            size_hint=(0.5, 1),
            padding="20dp",
            md_bg_color=self.theme_cls.errorColor
        )
        old_layout = MDBoxLayout(orientation="vertical", spacing="10dp")

        old_title = MDLabel(
            text="OLD: Broken MDLabel",
            font_style="Title",
            theme_text_color="Primary",
            size_hint_y=None,
            height="40dp"
        )

        old_test_label = MDLabel(
            text="Server Dashboard Status System Statistics Live Monitoring",
            font_style="Body",
            theme_text_color="Primary",
            size_hint_y=None,
            height="200dp"
        )

        old_layout.add_widget(old_title)
        old_layout.add_widget(old_test_label)
        old_card.add_widget(old_layout)

        # NEW (Fixed) Label Card
        new_card = MDCard(
            size_hint=(0.5, 1),
            padding="20dp",
            md_bg_color=self.theme_cls.primaryColor
        )
        new_layout = MDBoxLayout(orientation="vertical", spacing="10dp")

        new_title = MD3Label(
            text="NEW: Fixed MD3Label",
            font_style="Title",
            theme_text_color="Primary",
            size_hint_y=None,
            height="40dp"
        )

        new_test_label = MD3Label(
            text="Server Dashboard Status System Statistics Live Monitoring",
            font_style="Body",
            theme_text_color="Primary",
            size_hint_y=None,
            height="200dp"
        )

        new_layout.add_widget(new_title)
        new_layout.add_widget(new_test_label)
        new_card.add_widget(new_layout)

        main_layout.add_widget(old_card)
        main_layout.add_widget(new_card)

        return main_layout

if __name__ == "__main__":
    print("[INFO] Starting text rendering comparison test...")
    print("[INFO] LEFT (RED): Old broken MDLabel")
    print("[INFO] RIGHT (BLUE): New fixed MD3Label")
    print("[INFO] Look for horizontal vs vertical text rendering")

    try:
        app = TextRenderingComparisonApp()
        app.run()
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
