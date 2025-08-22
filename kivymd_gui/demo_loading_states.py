#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script for testing enhanced loading states and empty state designs
in the KivyMD dashboard following Material Design 3 principles.

Run this script to see the sophisticated loading animations, skeleton screens,
empty states, and micro-interactions in action.
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Ensure UTF-8 solution is available
try:
    import Shared.utils.utf8_solution
except ImportError:
    pass

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp

try:
    from kivymd.app import MDApp
    from kivymd.uix.screen import MDScreen
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.button import MDButton, MDButtonText
    from kivymd.uix.label import MDLabel
    
    # Import our enhanced dashboard components
    from kivymd_gui.screens.dashboard import (
        MDSkeletonLoader, MDLoadingCard, MDEmptyState, 
        MDMicroInteractionMixin, MDProgressiveReveal
    )
    
    KIVYMD_AVAILABLE = True
except ImportError as e:
    print(f"[ERROR] KivyMD not available: {e}")
    KIVYMD_AVAILABLE = False


class LoadingStatesDemo(MDScreen):
    """Demo screen showing all loading and empty states"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_demo()
    
    def build_demo(self):
        """Build demo interface"""
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=[dp(16), dp(16), dp(16), dp(16)],
            adaptive_height=True
        )
        
        # Title
        title = MDLabel(
            text="Loading States & Empty State Demo",
            font_style="Display",
            role="small",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(48)
        )
        main_layout.add_widget(title)
        
        # Demo buttons
        self.create_demo_buttons(main_layout)
        
        # Demo area
        self.demo_area = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            adaptive_height=True,
            size_hint_y=None,
            minimum_height=dp(300)
        )
        main_layout.add_widget(self.demo_area)
        
        self.add_widget(main_layout)
    
    def create_demo_buttons(self, layout):
        """Create demo control buttons"""
        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(48),
            adaptive_height=True
        )
        
        # Skeleton loader demo
        skeleton_btn = MDButton(
            MDButtonText(text="Skeleton Loader"),
            style="filled",
            on_release=self.demo_skeleton_loader
        )
        buttons_layout.add_widget(skeleton_btn)
        
        # Loading card demo  
        loading_btn = MDButton(
            MDButtonText(text="Loading Card"),
            style="filled",
            on_release=self.demo_loading_card
        )
        buttons_layout.add_widget(loading_btn)
        
        # Empty state demo
        empty_btn = MDButton(
            MDButtonText(text="Empty State"),
            style="filled", 
            on_release=self.demo_empty_state
        )
        buttons_layout.add_widget(empty_btn)
        
        # Progressive reveal demo
        reveal_btn = MDButton(
            MDButtonText(text="Progressive Reveal"),
            style="outlined",
            on_release=self.demo_progressive_reveal
        )
        buttons_layout.add_widget(reveal_btn)
        
        layout.add_widget(buttons_layout)
    
    def clear_demo_area(self):
        """Clear the demo area"""
        self.demo_area.clear_widgets()
    
    def demo_skeleton_loader(self, *args):
        """Demonstrate skeleton loader with shimmer"""
        self.clear_demo_area()
        
        # Create multiple skeleton elements
        skeletons = []
        for i in range(5):
            skeleton = MDSkeletonLoader(
                skeleton_type="text",
                height=dp(24 + (i * 8)),
                size_hint_x=0.8 - (i * 0.1)
            )
            skeletons.append(skeleton)
            self.demo_area.add_widget(skeleton)
        
        # Stop shimmers after 3 seconds
        Clock.schedule_once(
            lambda dt: [s.stop_shimmer() for s in skeletons],
            3.0
        )
    
    def demo_loading_card(self, *args):
        """Demonstrate loading card with transition"""
        self.clear_demo_area()
        
        loading_card = MDLoadingCard(
            card_title="Loading Demo Data...",
            loading_type="spinner"
        )
        self.demo_area.add_widget(loading_card)
        
        # Simulate content loading
        def show_content(dt):
            content = MDLabel(
                text="Content loaded successfully!\\n\\nThis demonstrates the smooth transition from loading state to actual content.",
                theme_text_color="Primary",
                font_style="Body",
                role="large",
                halign="center"
            )
            loading_card.transition_to_content(content)
        
        Clock.schedule_once(show_content, 2.5)
    
    def demo_empty_state(self, *args):
        """Demonstrate empty state design"""
        self.clear_demo_area()
        
        empty_state = MDEmptyState(
            title="No Data Available",
            description="This is how empty states look with contextual guidance and clear call-to-action buttons.",
            icon="inbox-outline",
            action_text="Load Sample Data",
            action_callback=self.load_sample_data
        )
        self.demo_area.add_widget(empty_state)
    
    def load_sample_data(self):
        """Simulate loading sample data"""
        print("[INFO] Loading sample data...")
        # In a real app, this would fetch actual data
        
        # Show loading briefly, then content
        self.clear_demo_area()
        loading_card = MDLoadingCard(
            card_title="Loading Sample Data...",
            loading_type="skeleton"
        )
        self.demo_area.add_widget(loading_card)
        
        def show_data(dt):
            content = MDLabel(
                text="Sample data loaded!\\n\\n✓ 5 items loaded\\n✓ Data synchronized\\n✓ Ready for use",
                theme_text_color="Primary",
                font_style="Body",
                role="large",
                halign="center"
            )
            loading_card.transition_to_content(content)
        
        Clock.schedule_once(show_data, 1.5)
    
    def demo_progressive_reveal(self, *args):
        """Demonstrate progressive reveal animation"""
        self.clear_demo_area()
        
        # Create multiple cards for progressive reveal
        cards = []
        for i in range(6):
            card = MDLoadingCard(
                card_title=f"Card {i+1}",
                loading_type="skeleton",
                size_hint_y=None,
                height=dp(100)
            )
            cards.append(card)
            self.demo_area.add_widget(card)
        
        # Apply progressive reveal
        MDProgressiveReveal.reveal_sequence(cards, base_delay=0.1, stagger_delay=0.2)


class LoadingStatesDemoApp(MDApp):
    """Demo app for loading states"""
    
    def build(self):
        # Set Material Design 3 theme
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        
        return LoadingStatesDemo()


if __name__ == "__main__":
    if KIVYMD_AVAILABLE:
        print("[INFO] Starting Loading States Demo...")
        print("[INFO] This demo showcases:")
        print("  - Skeleton screens with shimmer effects")
        print("  - Loading cards with smooth transitions")
        print("  - Empty states with contextual guidance")
        print("  - Progressive reveal animations")
        print("  - Material Design 3 motion principles")
        print()
        LoadingStatesDemoApp().run()
    else:
        print("[ERROR] KivyMD is required to run this demo")
        print("Please install KivyMD 2.0.x to see the loading states in action")