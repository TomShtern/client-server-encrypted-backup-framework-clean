"""
Log viewer screen for the KivyMD GUI
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout

class LogsScreen(MDScreen):
    """Screen for viewing server logs"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "logs"
        
    def on_enter(self):
        """Called when the screen is entered"""
        pass