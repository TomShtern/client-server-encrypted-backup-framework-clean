"""
Analytics screen for the KivyMD GUI
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout

class AnalyticsScreen(MDScreen):
    """Screen for displaying analytics charts and statistics"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "analytics"
        
    def on_enter(self):
        """Called when the screen is entered"""
        pass