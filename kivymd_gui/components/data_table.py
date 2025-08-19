"""
Enhanced data table component for the KivyMD GUI
"""

from kivymd.uix.datatables import MDDataTable
from kivymd.uix.boxlayout import MDBoxLayout

class EnhancedDataTable(MDBoxLayout):
    """Enhanced data table with search and pagination"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        
    def setup_table(self, column_data, row_data):
        """Setup the data table with columns and rows"""
        self.data_table = MDDataTable(
            column_data=column_data,
            row_data=row_data,
            use_pagination=True,
            rows_num=10,
            elevation=2
        )
        self.add_widget(self.data_table)