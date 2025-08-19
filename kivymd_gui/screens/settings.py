"""
Settings screen for the KivyMD GUI
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout

class SettingsScreen(MDScreen):
    """Screen for application settings"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        
    def on_enter(self):
        """Called when the screen is entered"""
        pass