"""
Server state management model for the KivyMD GUI
"""

from kivy.event import EventDispatcher
from kivy.properties import StringProperty, BooleanProperty, NumericProperty

class ServerModel(EventDispatcher):
    """Model for managing server state and data"""
    
    # Server status properties
    is_running = BooleanProperty(False)
    port = NumericProperty(1256)
    host = StringProperty("localhost")
    
    # Statistics properties
    total_files = NumericProperty(0)
    total_clients = NumericProperty(0)
    uptime = StringProperty("00:00:00")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def update_status(self, is_running):
        """Update server running status"""
        self.is_running = is_running
        
    def update_statistics(self, files=0, clients=0, uptime="00:00:00"):
        """Update server statistics"""
        self.total_files = files
        self.total_clients = clients
        self.uptime = uptime