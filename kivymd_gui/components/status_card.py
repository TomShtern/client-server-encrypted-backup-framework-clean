"""
Reusable status card component for the KivyMD GUI
"""

from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout

class StatusCard(MDCard):
    """Reusable status card component"""
    
    def __init__(self, title="", value="", icon="", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.value = value
        self.icon = icon
        self.elevation = 2
        self.size_hint_y = None
        self.height = "120dp"