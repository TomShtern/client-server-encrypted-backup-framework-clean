#!/usr/bin/env python3
"""
Unicode and Hebrew/Emoji Rendering Test for KivyMD
Tests various Unicode characters, Hebrew text, and emojis
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# UTF-8 solution - CRITICAL: Import early for proper Unicode setup
try:
    import Shared.utils.utf8_solution
    from Shared.utils.utf8_solution import UTF8Support
    # Ensure UTF-8 environment is applied
    utf8_env = UTF8Support.get_env()
    for key, value in utf8_env.items():
        os.environ[key] = value
    print("[INFO] UTF-8 solution enabled with environment setup")
    print(f"[INFO] UTF-8 test result: {Shared.utils.utf8_solution.test_utf8()}")
except ImportError:
    print("[WARNING] UTF-8 solution not available")

# Kivy configuration for Unicode support
from kivy.config import Config

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')

# Unicode and font configuration
os.environ['KIVY_TEXT'] = 'sdl2'
os.environ['KIVY_WINDOW'] = 'sdl2'
os.environ['PYTHONIOENCODING'] = 'utf-8'

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd_gui.components.md3_label import MD3Label


class UnicodeRenderingTestApp(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"

        # Main scroll container
        scroll = MDScrollView()
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing="10dp",
            padding="20dp",
            adaptive_height=True
        )

        # Test cases for different Unicode scenarios
        test_cases = [
            ("English Text", "Hello World! This is regular English text."),
            ("Numbers & Symbols", "1234567890 !@#$%^&*()_+-=[]{}|;':\",./<>?"),
            ("Hebrew Text", "שלום עולם! זהו טקסט בעברית."),
            ("Hebrew + English", "Hello שלום World עולם!"),
            ("Basic Emojis", "😀 😃 😄 😁 😆 😅 😂 🤣 😊 😇"),
            ("Country Flags", "🇺🇸 🇮🇱 🇬🇧 🇫🇷 🇩🇪 🇯🇵 🇨🇳 🇮🇳"),
            ("Technical Emojis", "💻 ⚙️ 🔧 🔨 ⚡ 🔥 💾 📱 🖥️ ⌨️"),
            ("Mixed Unicode", "Café naïve résumé Москва 東京 العربية"),
            ("Unicode Symbols", "™ © ® ° ± × ÷ ≠ ≤ ≥ ∞ π α β γ δ"),
            ("RTL Test Hebrew", "כתובת: רחוב בן גוריון 123, תל אביב"),
        ]

        for title, text in test_cases:
            # Create card for each test case
            card = MDCard(
                size_hint_y=None,
                height="80dp",
                padding="15dp",
                spacing="5dp",
                orientation="vertical"
            )

            # Title label
            title_label = MD3Label(
                text=f"TEST: {title}",
                font_style="Label",
                theme_text_color="Secondary",
                size_hint_y=None,
                height="20dp"
            )

            # Test content label
            content_label = MD3Label(
                text=text,
                font_style="Body",
                theme_text_color="Primary",
                size_hint_y=None,
                height="40dp",
                # Allow text wrapping for longer content
                text_size=(None, None)
            )

            card.add_widget(title_label)
            card.add_widget(content_label)
            main_layout.add_widget(card)

        scroll.add_widget(main_layout)
        return scroll

if __name__ == "__main__":
    print("[INFO] Starting Unicode rendering test...")
    print(f"[INFO] System encoding: {sys.stdout.encoding}")
    print(f"[INFO] File system encoding: {sys.getfilesystemencoding()}")
    print(f"[INFO] Default locale: {os.environ.get('LANG', 'Not set')}")

    try:
        app = UnicodeRenderingTestApp()
        app.run()
    except Exception as e:
        print(f"[ERROR] Unicode test failed: {e}")
        import traceback
        traceback.print_exc()
