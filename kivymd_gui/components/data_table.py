"""
Enhanced data table component for the KivyMD GUI
KivyMD 2.0.x compatible implementation using MDList
"""

from kivymd.uix.list import MDList, MDListItem, MDListItemLeadingIcon
from kivymd.uix.list import MDListItemHeadlineText, MDListItemSupportingText, MDListItemTrailingSupportingText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivy.metrics import dp

class EnhancedDataTable(MDBoxLayout):
    """Enhanced data table with search and pagination - KivyMD 2.0.x compatible"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.column_data = []
        self.row_data = []
        self.data_list = None
        
    def setup_table(self, column_data, row_data):
        """Setup the data table with columns and rows"""
        self.column_data = column_data
        self.row_data = row_data
        
        # Clear existing widgets
        self.clear_widgets()
        
        # Add header if needed
        if column_data:
            header_text = " | ".join([col[0] if isinstance(col, tuple) else str(col) for col in column_data])
            header = MDLabel(
                text=header_text,
                font_style="Label",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(32),
                padding=[dp(16), dp(8)]
            )
            self.add_widget(header)
        
        # Create scrollable list
        scroll = MDScrollView()
        self.data_list = MDList()
        scroll.add_widget(self.data_list)
        self.add_widget(scroll)
        
        # Populate data
        self.update_data(row_data)
    
    def update_data(self, row_data):
        """Update the table data"""
        if not self.data_list:
            return
            
        self.data_list.clear_widgets()
        
        for row in row_data:
            if isinstance(row, (list, tuple)) and len(row) > 0:
                # Create list item from row data
                headline = str(row[0]) if len(row) > 0 else ""
                supporting = " | ".join([str(cell) for cell in row[1:3]]) if len(row) > 1 else ""
                trailing = str(row[-1]) if len(row) > 3 else ""
                
                item = MDListItem(
                    MDListItemLeadingIcon(icon="table-row"),
                    MDListItemHeadlineText(text=headline),
                    MDListItemSupportingText(text=supporting) if supporting else None,
                    MDListItemTrailingSupportingText(text=trailing) if trailing else None
                )
                # Filter out None components
                item_components = [comp for comp in [
                    MDListItemLeadingIcon(icon="table-row"),
                    MDListItemHeadlineText(text=headline),
                    MDListItemSupportingText(text=supporting) if supporting else None,
                    MDListItemTrailingSupportingText(text=trailing) if trailing else None
                ] if comp is not None]
                
                item = MDListItem(*item_components)
                self.data_list.add_widget(item)