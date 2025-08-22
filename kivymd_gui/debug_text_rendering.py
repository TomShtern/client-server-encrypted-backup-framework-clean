#!/usr/bin/env python3
"""
Debug Text Rendering - Isolate Vertical Text Issue
=================================================

This script tests MD3Label vs MDLabel to identify what causes
vertical character-by-character text rendering in KivyMD.

Tests:
1. MD3Label vs MDLabel with identical configurations
2. Different font styles and text_size settings
3. Various container types and layouts
4. Theme and styling conflicts
5. Text length and content variations
"""

import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDButton, MDButtonText

# Import our custom components
try:
    from kivymd_gui.components.md3_label import MD3Label, create_md3_label
    print("Successfully imported MD3Label")
except ImportError as e:
    print(f"Failed to import MD3Label: {e}")
    MD3Label = None
    create_md3_label = None

class TextRenderingDebugApp(MDApp):
    def build(self):
        # Set Material Design 3 theme
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        
        # Main container
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing="10dp",
            padding="20dp"
        )
        
        # Add title
        title = MDLabel(
            text="Text Rendering Debug - Vertical vs Horizontal",
            font_style="Title",
            size_hint_y=None,
            height="40dp",
            theme_text_color="Primary"
        )
        main_layout.add_widget(title)
        
        # Create scrollable content
        scroll = MDScrollView()
        content_layout = MDBoxLayout(
            orientation="vertical",
            spacing="20dp",
            size_hint_y=None,
            padding="10dp"
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Test 1: Basic MDLabel vs MD3Label comparison
        content_layout.add_widget(self.create_test_section(
            "Test 1: Basic MDLabel vs MD3Label",
            [
                ("MDLabel (Default)", self.create_mdlabel_default),
                ("MD3Label (Default)", self.create_md3label_default),
            ]
        ))
        
        # Test 2: Font styles comparison
        content_layout.add_widget(self.create_test_section(
            "Test 2: Font Styles",
            [
                ("MDLabel Title", lambda: self.create_mdlabel("MDLabel Title Style", font_style="Title")),
                ("MD3Label Title", lambda: self.create_md3label("MD3Label Title Style", font_style="Title")),
                ("MDLabel Body", lambda: self.create_mdlabel("MDLabel Body Style", font_style="Body")),
                ("MD3Label Body", lambda: self.create_md3label("MD3Label Body Style", font_style="Body")),
            ]
        ))
        
        # Test 3: Text size configurations
        content_layout.add_widget(self.create_test_section(
            "Test 3: Text Size Configurations",
            [
                ("MDLabel text_size=None", lambda: self.create_mdlabel_with_text_size("MDLabel with text_size=None", None)),
                ("MDLabel text_size=(None,None)", lambda: self.create_mdlabel_with_text_size("MDLabel with text_size=(None,None)", (None, None))),
                ("MDLabel no text_size", lambda: self.create_mdlabel_no_text_size("MDLabel without text_size")),
                ("MD3Label equivalent", lambda: self.create_md3label("MD3Label equivalent", font_style="Body")),
            ]
        ))
        
        # Test 4: Container types
        content_layout.add_widget(self.create_test_section(
            "Test 4: Container Types",
            [
                ("In MDCard", self.create_card_container_test),
                ("In MDBoxLayout", self.create_boxlayout_container_test),
                ("In MDGridLayout", self.create_gridlayout_container_test),
            ]
        ))
        
        # Test 5: Text content variations
        content_layout.add_widget(self.create_test_section(
            "Test 5: Text Content Variations",
            [
                ("Short text", lambda: self.create_md3label("Short", font_style="Body")),
                ("Medium text", lambda: self.create_md3label("This is medium length text", font_style="Body")),
                ("Long text", lambda: self.create_md3label("This is a very long text that should definitely wrap and test how the label handles longer content", font_style="Body")),
                ("Unicode text", lambda: self.create_md3label("Unicode: hello world", font_style="Body")),
            ]
        ))
        
        # Test 6: Role properties (the suspected culprit)
        content_layout.add_widget(self.create_test_section(
            "Test 6: Role Properties (SUSPECTED ISSUE)",
            [
                ("MDLabel with role='small'", lambda: self.create_mdlabel_with_role("MDLabel with role='small'", "small")),
                ("MDLabel with role='medium'", lambda: self.create_mdlabel_with_role("MDLabel with role='medium'", "medium")),
                ("MDLabel with role='large'", lambda: self.create_mdlabel_with_role("MDLabel with role='large'", "large")),
                ("MDLabel without role", lambda: self.create_mdlabel("MDLabel without role", font_style="Body")),
            ]
        ))
        
        # Add refresh button
        refresh_btn = MDButton(
            MDButtonText(text="Refresh Test"),
            style="elevated",
            size_hint=(None, None),
            size=("200dp", "40dp"),
            pos_hint={"center_x": 0.5}
        )
        refresh_btn.bind(on_release=lambda x: self.refresh_app())
        content_layout.add_widget(refresh_btn)
        
        scroll.add_widget(content_layout)
        main_layout.add_widget(scroll)
        
        return main_layout
    
    def create_test_section(self, title, tests):
        """Create a test section with multiple test items"""
        section_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height="200dp",
            padding="10dp",
            spacing="5dp",
            elevation=2
        )
        
        # Section title
        section_title = MDLabel(
            text=title,
            font_style="Headline",
            size_hint_y=None,
            height="30dp",
            theme_text_color="Primary"
        )
        section_card.add_widget(section_title)
        
        # Test items
        for test_name, test_func in tests:
            try:
                test_widget = test_func()
                
                # Wrap in container with label
                test_container = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height="30dp",
                    spacing="10dp"
                )
                
                # Test name label
                name_label = MDLabel(
                    text=f"{test_name}:",
                    size_hint_x=None,
                    width="150dp",
                    font_style="Label"
                )
                test_container.add_widget(name_label)
                
                # Test widget
                test_container.add_widget(test_widget)
                
                section_card.add_widget(test_container)
                
            except Exception as e:
                error_label = MDLabel(
                    text=f"{test_name}: ERROR - {str(e)}",
                    theme_text_color="Error",
                    size_hint_y=None,
                    height="30dp"
                )
                section_card.add_widget(error_label)
        
        return section_card
    
    def create_mdlabel_default(self):
        """Create default MDLabel"""
        return MDLabel(
            text="Default MDLabel",
            theme_text_color="Primary"
        )
    
    def create_md3label_default(self):
        """Create default MD3Label"""
        if MD3Label:
            return MD3Label(
                text="Default MD3Label",
                font_style="Body"
            )
        else:
            return MDLabel(text="MD3Label not available", theme_text_color="Error")
    
    def create_mdlabel(self, text, font_style="Body"):
        """Create MDLabel with specified parameters"""
        return MDLabel(
            text=text,
            font_style=font_style,
            theme_text_color="Primary"
        )
    
    def create_md3label(self, text, font_style="Body"):
        """Create MD3Label with specified parameters"""
        if MD3Label:
            return MD3Label(
                text=text,
                font_style=font_style
            )
        else:
            return MDLabel(text="MD3Label not available", theme_text_color="Error")
    
    def create_mdlabel_with_text_size(self, text, text_size):
        """Create MDLabel with specific text_size setting"""
        return MDLabel(
            text=text,
            font_style="Body",
            text_size=text_size,
            theme_text_color="Primary"
        )
    
    def create_mdlabel_no_text_size(self, text):
        """Create MDLabel without text_size property"""
        label = MDLabel(
            text=text,
            font_style="Body",
            theme_text_color="Primary"
        )
        # Explicitly remove text_size if it exists
        if hasattr(label, 'text_size'):
            delattr(label, 'text_size')
        return label
    
    def create_mdlabel_with_role(self, text, role):
        """Create MDLabel with role property (this should cause vertical rendering)"""
        try:
            return MDLabel(
                text=text,
                font_style="Body",
                role=role,  # This is the suspected cause of vertical rendering
                theme_text_color="Primary"
            )
        except Exception as e:
            return MDLabel(
                text=f"Role error: {str(e)}",
                theme_text_color="Error"
            )
    
    def create_card_container_test(self):
        """Test label in card container"""
        card = MDCard(
            size_hint=(None, None),
            size=("200dp", "40dp"),
            padding="5dp"
        )
        if MD3Label:
            label = MD3Label(text="In MDCard", font_style="Body")
        else:
            label = MDLabel(text="In MDCard", font_style="Body")
        card.add_widget(label)
        return card
    
    def create_boxlayout_container_test(self):
        """Test label in box layout container"""
        box = MDBoxLayout(
            size_hint=(None, None),
            size=("200dp", "40dp"),
            padding="5dp"
        )
        if MD3Label:
            label = MD3Label(text="In MDBoxLayout", font_style="Body")
        else:
            label = MDLabel(text="In MDBoxLayout", font_style="Body")
        box.add_widget(label)
        return box
    
    def create_gridlayout_container_test(self):
        """Test label in grid layout container"""
        grid = MDGridLayout(
            cols=1,
            size_hint=(None, None),
            size=("200dp", "40dp"),
            padding="5dp"
        )
        if MD3Label:
            label = MD3Label(text="In MDGridLayout", font_style="Body")
        else:
            label = MDLabel(text="In MDGridLayout", font_style="Body")
        grid.add_widget(label)
        return grid
    
    def refresh_app(self):
        """Refresh the app to re-run tests"""
        print("Refreshing app...")
        self.stop()

def main():
    """Main function to run the debug app"""
    print("Starting Text Rendering Debug")
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
    print("\nWHAT TO LOOK FOR:")
    print("1. Vertical text = characters stacked vertically (BAD)")
    print("2. Horizontal text = normal left-to-right reading (GOOD)")
    print("3. Pay special attention to 'Role Properties' section")
    print("4. Compare MD3Label vs MDLabel behavior")
    print("\nStarting app...")
    
    app = TextRenderingDebugApp()
    app.run()

if __name__ == "__main__":
    main()