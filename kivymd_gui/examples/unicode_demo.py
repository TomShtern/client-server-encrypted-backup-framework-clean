# -*- coding: utf-8 -*-
"""
Unicode Demo - Demonstrate Hebrew and emoji rendering in KivyMD
Shows how the new Unicode font system works with different content types
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# UTF-8 solution import - MUST be imported early
import Shared.utils.utf8_solution

# CRITICAL: Initialize Unicode font support before KivyMD imports
from kivymd_gui.utils.font_config import initialize_unicode_fonts
initialize_unicode_fonts()

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivy.clock import Clock

# Import our Unicode-aware MD3Label
from kivymd_gui.components.md3_label import (
    create_md3_label, create_unicode_label, 
    create_emoji_label, create_hebrew_label
)


class UnicodeDemo(MDApp):
    """Demo app showing Unicode font rendering"""
    
    def build(self):
        self.title = "Unicode Font Demo"
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        
        # Create main layout
        screen = MDScreen()
        scroll = MDScrollView()
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing="16dp",
            padding="24dp",
            size_hint_y=None
        )
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Demo content with different Unicode text types
        demo_content = [
            ("English Text", "Hello World! This is standard English text."),
            ("Hebrew Text", "שלום עולם! זהו טקסט עברי בסיסי."),
            ("Mixed Hebrew-English", "Hello שלום World עולם!"),
            ("Emoji Text", "🎉 ✅ ❌ 🔧 🚀 ⚡ 📁 💾 🌟"),
            ("Mixed All", "Hello שלום 🎉 World עולם ✅ Test!"),
            ("Filename Example", "קובץ_עברי_🎉_test.txt"),
            ("Status Messages", "✅ Server connected | שרת מחובר 🎉"),
            ("Error Messages", "❌ Connection failed | החיבור נכשל ⚠️"),
        ]
        
        # Add title
        title_label = create_md3_label(
            "Unicode Font Rendering Demo",
            font_style="Title",
            theme_text_color="Primary",
            halign="center",
            size_hint_y=None,
            height="48dp"
        )
        main_layout.add_widget(title_label)
        
        # Add demo labels
        for title, text in demo_content:
            # Section title
            section_title = create_md3_label(
                f"{title}:",
                font_style="Label",
                role="medium", 
                theme_text_color="Secondary",
                size_hint_y=None,
                height="32dp"
            )
            main_layout.add_widget(section_title)
            
            # Content label (auto-selects best font)
            content_label = create_md3_label(
                text,
                font_style="Body",
                role="large",
                theme_text_color="Primary", 
                size_hint_y=None,
                height="40dp"
            )
            main_layout.add_widget(content_label)
        
        # Add font information
        font_info_label = create_md3_label(
            "Fonts are automatically selected based on content:\n" +
            "• SegoeUI for Hebrew and general Unicode\n" +
            "• SegoeUIEmoji for emoji characters\n" +
            "• Arial as fallback Unicode font",
            font_style="Label",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="80dp"
        )
        main_layout.add_widget(font_info_label)
        
        scroll.add_widget(main_layout)
        screen.add_widget(scroll)
        return screen
    
    def on_start(self):
        """Called when app starts"""
        # Show a status message after 1 second
        Clock.schedule_once(self.show_status_message, 1)
    
    def show_status_message(self, dt):
        """Show a status message with Unicode content"""
        print("Unicode demo started successfully!")
        print("Check the GUI to see Hebrew and emoji rendering.")


def main():
    """Run the Unicode demo"""
    print("Starting Unicode Font Demo...")
    print("This demo will show Hebrew text and emojis rendered properly.")
    
    try:
        app = UnicodeDemo()
        app.run()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()