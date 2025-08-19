"""
File management screen for the KivyMD GUI
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout

class FilesScreen(MDScreen):
    """Screen for managing received files"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "files"
        
    def on_enter(self):
        """Called when the screen is entered"""
        pass