#!/usr/bin/env python3
"""
Debug script to check actual window width and breakpoint calculations
"""


from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen


class WidthTestApp(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"

        screen = MDScreen()
        layout = MDBoxLayout(orientation="vertical", spacing=dp(16), padding=dp(24))

        # Window dimensions
        window_info = MDLabel(
            text=f"Window: {Window.width}x{Window.height}",
            font_style="Headline",
            theme_text_color="Primary"
        )
        layout.add_widget(window_info)

        # Available width calculation (same as dashboard)
        screen_width = Window.width
        available_width = screen_width - dp(48)

        available_info = MDLabel(
            text=f"Available width: {available_width}dp (screen: {screen_width}dp - padding: 48dp)",
            font_style="Body",
            theme_text_color="Primary"
        )
        layout.add_widget(available_info)

        # Breakpoint detection (same as dashboard)
        MOBILE_MAX = dp(768)
        TABLET_MAX = dp(1200)

        if available_width <= MOBILE_MAX:
            breakpoint = "mobile"
            expected_cols = 1
        elif available_width <= TABLET_MAX:
            breakpoint = "tablet"
            expected_cols = 2
        else:
            breakpoint = "desktop"
            expected_cols = 3

        breakpoint_info = MDLabel(
            text=f"Breakpoint: {breakpoint} ({expected_cols} columns)",
            font_style="Body",
            theme_text_color="Secondary"
        )
        layout.add_widget(breakpoint_info)

        # Test narrow label like in dashboard
        test_label = MDLabel(
            text="0",
            font_style="Display",
            theme_text_color="Primary",
            size_hint_x=None,
            width=dp(80)
        )
        layout.add_widget(MDLabel(text=f"Test label (80dp width): '{test_label.text}'", font_style="Body"))
        layout.add_widget(test_label)

        screen.add_widget(layout)
        return screen


WidthTestApp().run()
