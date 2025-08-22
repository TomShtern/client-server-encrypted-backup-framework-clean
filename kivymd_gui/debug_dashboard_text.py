#!/usr/bin/env python3
"""
Debug Dashboard Text Rendering - Focused Test
============================================

Minimal test that replicates the exact dashboard card structure
to isolate the vertical text rendering issue.

The goal is to identify why text renders vertically (character-by-character)
in dashboard cards when it should render horizontally.
"""

import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import UTF-8 solution early
try:
    import Shared.utils.utf8_solution
    print("Imported UTF-8 solution")
except ImportError:
    print("UTF-8 solution not available")

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.metrics import dp

# Import our custom components
try:
    from kivymd_gui.components.md3_label import MD3Label
    print("Successfully imported MD3Label")
    HAS_MD3LABEL = True
except ImportError as e:
    print(f"Failed to import MD3Label: {e}")
    HAS_MD3LABEL = False

class DashboardTextDebugApp(MDApp):
    def build(self):
        # Set Material Design 3 theme
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        
        # Main container
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=dp(20)
        )
        
        # Add title
        title = MDLabel(
            text="Dashboard Text Debug - Find Vertical Rendering Issue",
            font_style="Title",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Primary"
        )
        main_layout.add_widget(title)
        
        # Test 1: Simple MD3Label vs MDLabel
        main_layout.add_widget(self.create_simple_comparison())
        
        # Test 2: Dashboard-style card (the problematic one)
        main_layout.add_widget(self.create_dashboard_card())
        
        # Test 3: Different container configurations
        main_layout.add_widget(self.create_container_test())
        
        return main_layout
    
    def create_simple_comparison(self):
        """Simple comparison between MD3Label and MDLabel"""
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(120),
            padding=dp(16),
            spacing=dp(8),
            elevation=2
        )
        
        # Card title
        card_title = MDLabel(
            text="Test 1: Simple Text Comparison",
            font_style="Headline",
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Primary"
        )
        card.add_widget(card_title)
        
        # Test layout
        test_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            spacing=dp(16)
        )
        
        # Left side: MDLabel
        left_box = MDBoxLayout(orientation="vertical", size_hint_x=0.5)
        left_box.add_widget(MDLabel(text="MDLabel:", font_style="Label", size_hint_y=None, height=dp(20)))
        mdlabel = MDLabel(
            text="Normal MDLabel Text",
            font_style="Body",
            theme_text_color="Primary"
        )
        left_box.add_widget(mdlabel)
        test_layout.add_widget(left_box)
        
        # Right side: MD3Label (if available)
        right_box = MDBoxLayout(orientation="vertical", size_hint_x=0.5)
        right_box.add_widget(MDLabel(text="MD3Label:", font_style="Label", size_hint_y=None, height=dp(20)))
        if HAS_MD3LABEL:
            md3label = MD3Label(
                text="Custom MD3Label Text",
                font_style="Body"
            )
        else:
            md3label = MDLabel(
                text="MD3Label not available",
                font_style="Body",
                theme_text_color="Error"
            )
        right_box.add_widget(md3label)
        test_layout.add_widget(right_box)
        
        card.add_widget(test_layout)
        return card
    
    def create_dashboard_card(self):
        """Replicate exact dashboard card structure"""
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(200),
            padding=dp(16),
            spacing=dp(12),
            elevation=2
        )
        
        # Card title
        card_title = MDLabel(
            text="Test 2: Dashboard Card Structure (PROBLEMATIC)",
            font_style="Headline",
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Primary"
        )
        card.add_widget(card_title)
        
        # This mimics the exact structure from dashboard.py
        if HAS_MD3LABEL:
            # Server Status Card structure (from line 620-670 in dashboard.py)
            title = MD3Label(
                text="Server Status",
                font_style="Title",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(32)
            )
            card.add_widget(title)
            
            # Status text (this often renders vertically)
            status_text = MD3Label(
                text="RUNNING",
                font_style="Headline",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(40)
            )
            card.add_widget(status_text)
            
            # Address label (this also renders vertically sometimes)
            address_label = MD3Label(
                text="127.0.0.1:1256",
                font_style="Body",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(24)
            )
            card.add_widget(address_label)
            
            # Uptime label
            uptime_label = MD3Label(
                text="Uptime: 2h 45m",
                font_style="Body",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(24)
            )
            card.add_widget(uptime_label)
            
        else:
            error_label = MDLabel(
                text="MD3Label not available - cannot test dashboard structure",
                theme_text_color="Error"
            )
            card.add_widget(error_label)
        
        return card
    
    def create_container_test(self):
        """Test different container configurations"""
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(150),
            padding=dp(16),
            spacing=dp(8),
            elevation=2
        )
        
        # Card title
        card_title = MDLabel(
            text="Test 3: Container Configurations",
            font_style="Headline",
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Primary"
        )
        card.add_widget(card_title)
        
        # Test different container types
        container_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(80),
            spacing=dp(16)
        )
        
        # Test 1: In MDBoxLayout
        box_test = MDBoxLayout(orientation="vertical", size_hint_x=0.33)
        box_test.add_widget(MDLabel(text="In MDBoxLayout:", font_style="Label", size_hint_y=None, height=dp(20)))
        if HAS_MD3LABEL:
            box_label = MD3Label(text="Box Text", font_style="Body")
        else:
            box_label = MDLabel(text="Box Text", font_style="Body")
        box_test.add_widget(box_label)
        container_layout.add_widget(box_test)
        
        # Test 2: In MDGridLayout
        grid_test = MDBoxLayout(orientation="vertical", size_hint_x=0.33)
        grid_test.add_widget(MDLabel(text="In MDGridLayout:", font_style="Label", size_hint_y=None, height=dp(20)))
        grid_container = MDGridLayout(cols=1, size_hint_y=None, height=dp(40))
        if HAS_MD3LABEL:
            grid_label = MD3Label(text="Grid Text", font_style="Body")
        else:
            grid_label = MDLabel(text="Grid Text", font_style="Body")
        grid_container.add_widget(grid_label)
        grid_test.add_widget(grid_container)
        container_layout.add_widget(grid_test)
        
        # Test 3: Direct in card
        direct_test = MDBoxLayout(orientation="vertical", size_hint_x=0.34)
        direct_test.add_widget(MDLabel(text="Direct in Card:", font_style="Label", size_hint_y=None, height=dp(20)))
        if HAS_MD3LABEL:
            direct_label = MD3Label(text="Direct Text", font_style="Body")
        else:
            direct_label = MDLabel(text="Direct Text", font_style="Body")
        direct_test.add_widget(direct_label)
        container_layout.add_widget(direct_test)
        
        card.add_widget(container_layout)
        return card

def main():
    """Main function to run the dashboard debug app"""
    print("Starting Dashboard Text Rendering Debug")
    print("=" * 50)
    
    # Print environment info
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        import kivymd
        print(f"KivyMD version: {kivymd.__version__}")
    except:
        print("KivyMD version: Unknown")
    
    print("=" * 50)
    print("\nFOCUSED TEST: Dashboard Card Text Rendering")
    print("Look for vertical text in 'Test 2: Dashboard Card Structure'")
    print("Compare with normal horizontal text in other tests")
    print("\nStarting app...")
    
    app = DashboardTextDebugApp()
    app.run()

if __name__ == "__main__":
    main()