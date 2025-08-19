"""
Client management screen for the KivyMD GUI
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout

class ClientsScreen(MDScreen):
    """Screen for managing connected clients"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "clients"
        
    def on_enter(self):
        """Called when the screen is entered"""
        pass