# -*- coding: utf-8 -*-
"""
files.py - Files management screen with Material Design 3
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFabButton
from kivymd.uix.textfield import MDTextField, MDTextFieldLeadingIcon, MDTextFieldHintText
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.filemanager import MDFileManager
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty
import os

class FilesScreen(MDScreen):
    """Material Design 3 Files Management Screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "files"
        self.file_manager = None
        self._build_ui()
    
    def _build_ui(self):
        """Build the files UI with MD3 components"""
        layout = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(16))
        
        # Header with search
        header = MDBoxLayout(size_hint_y=None, height=dp(56))
        header.add_widget(MDLabel(
            text="File Management",
            font_style="Display",
            theme_text_color="Primary"
        ))
        
        self.search_field = MDTextField(
            MDTextFieldLeadingIcon(icon="magnify"),
            MDTextFieldHintText(text="Search files..."),
            mode="outlined",
            size_hint_x=0.3
        )
        header.add_widget(self.search_field)
        layout.add_widget(header)
        
        # Files data table
        self.files_table = MDDataTable(
            size_hint=(1, 1),
            use_pagination=True,
            rows_num=15,
            column_data=[
                ("", dp(10)),  # Checkbox
                ("Icon", dp(10)),
                ("File Name", dp(50)),
                ("Client", dp(30)),
                ("Size", dp(20)),
                ("Date", dp(30)),
                ("Status", dp(20)),
            ],
            row_data=[],
            check=True,
            elevation=2
        )
        
        layout.add_widget(self.files_table)
        
        # FAB for file upload
        fab = MDFabButton(
            icon="upload",
            pos_hint={"right": 0.95, "bottom": 0.05},
            on_release=self.open_file_manager
        )
        layout.add_widget(fab)
        
        self.add_widget(layout)
        self._load_files_data()
    
    def _load_files_data(self):
        """Load files from received_files directory"""
        try:
            received_files_dir = os.path.join(os.getcwd(), "received_files")
            if os.path.exists(received_files_dir):
                files = []
                for filename in os.listdir(received_files_dir):
                    file_path = os.path.join(received_files_dir, filename)
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        size = self._format_file_size(stat.st_size)
                        mtime = self._format_date(stat.st_mtime)
                        files.append((
                            "",  # Checkbox
                            "file",  # Icon
                            filename,
                            "Unknown",  # Client
                            size,
                            mtime,
                            "Received"
                        ))
                self.files_table.row_data = files
        except Exception as e:
            print(f"Error loading files: {e}")
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def _format_date(self, timestamp):
        """Format timestamp to readable date"""
        import datetime
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
    
    def open_file_manager(self, *args):
        """Open file manager for upload"""
        if not self.file_manager:
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager,
                select_path=self.select_path,
                preview=True
            )
        self.file_manager.show("/")
    
    def select_path(self, path):
        """Handle file selection"""
        self.exit_manager()
        # Process selected file
        print(f"Selected: {path}")
    
    def exit_manager(self, *args):
        """Close file manager"""
        if self.file_manager:
            self.file_manager.close()
    
    def on_enter(self):
        """Called when the screen is entered"""
        self._load_files_data()