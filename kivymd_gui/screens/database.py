"""
Database browser screen for the KivyMD GUI
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout

class DatabaseScreen(MDScreen):
    """Screen for browsing database contents"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "database"
        
    def on_enter(self):
        """Called when the screen is entered"""
        pass
