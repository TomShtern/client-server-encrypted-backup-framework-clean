"""
Enhanced Material Design 3 status card components for KivyMD GUI
"""

from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd_gui.components.md3_label import MD3Label
from kivymd.uix.button import MDIconButton
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.animation import Animation


class MDStatusCard(MDCard):
    """Material Design 3 Status Card with dynamic updates"""
    title = StringProperty("")
    icon = StringProperty("information")
    primary_text = StringProperty("")
    secondary_text = StringProperty("")
    status_color = StringProperty("green")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 2
        self.radius = dp(12)
        self.padding = dp(16)
        self.size_hint_y = None
        self.height = dp(180)
        self._setup_layout()
        
    def _setup_layout(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(8))
        
        # Header with icon and title
        header = MDBoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        icon = MDIconButton(
            icon=self.icon,
            theme_icon_color="Custom",
            icon_color=self.theme_cls.primaryColor,
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        title_label = MD3Label(
            text=self.title,
            font_style="Headline",
            theme_text_color="Primary",
            adaptive_height=True
        )
        header.add_widget(icon)
        header.add_widget(title_label)
        
        # Content
        content = MDBoxLayout(orientation="vertical", spacing=dp(8))
        self.primary_label = MD3Label(
            text=self.primary_text,
            font_style="Display",
            theme_text_color="Primary",
            adaptive_height=True
        )
        self.secondary_label = MD3Label(
            text=self.secondary_text,
            font_style="Body",
            theme_text_color="Secondary",
            adaptive_height=True
        )
        content.add_widget(self.primary_label)
        content.add_widget(self.secondary_label)
        
        layout.add_widget(header)
        layout.add_widget(content)
        self.add_widget(layout)
    
    def update_status(self, primary: str, secondary: str = "", color: str = "green"):
        """Update the card's status display with smooth animation"""
        self.primary_label.text = primary
        self.secondary_label.text = secondary
        self.status_color = color
        
        # Enhanced Material Design 3 animation - safe opacity-only animation
        pulse_anim = (
            Animation(opacity=0.8, duration=0.1, t='out_cubic') + 
            Animation(opacity=1, duration=0.15, t='out_back')
        )
        pulse_anim.start(self)


# Legacy compatibility class
class StatusCard(MDStatusCard):
    """Legacy compatibility wrapper for StatusCard"""
    
    def __init__(self, title="", value="", icon="information", **kwargs):
        super().__init__(
            title=title,
            primary_text=value,
            icon=icon,
            **kwargs
        )