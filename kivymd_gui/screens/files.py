# -*- coding: utf-8 -*-
"""
files.py - Files management screen with Material Design 3
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd_gui.components.md3_label import MD3Label, create_md3_label
from kivymd.uix.card import MDCard
from kivymd_gui.components.md3_button import create_md3_icon_button
from kivymd.uix.textfield import MDTextField, MDTextFieldLeadingIcon, MDTextFieldHintText
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemLeadingIcon
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty
import os

class FilesScreen(MDScreen):
    """Material Design 3 Files Management Screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "files"
        self._build_ui()
    
    def _build_ui(self):
        """Build the files UI with MD3 components"""
        layout = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(16))
        
        # Header with search
        header = MDBoxLayout(size_hint_y=None, height=dp(56))
        header.add_widget(MD3Label(
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
        
        # Files list container
        files_container = MDRelativeLayout()
        
        scroll = MDScrollView()
        self.files_list = MDList()
        scroll.add_widget(self.files_list)
        files_container.add_widget(scroll)
        
        # FAB for file operations (using M3 icon button adapter)
        fab = create_md3_icon_button(
            icon="upload",
            tone="primary",
            pos_hint={"right": 0.95, "bottom": 0.05},
            on_release=self.open_file_dialog
        )
        files_container.add_widget(fab)
        
        layout.add_widget(files_container)
        
        self.add_widget(layout)
        self._load_files_data()
    
    def _load_files_data(self):
        """Load files from received_files directory"""
        try:
            received_files_dir = os.path.join(os.getcwd(), "received_files")
            
            # Clear existing list items
            self.files_list.clear_widgets()
            
            if os.path.exists(received_files_dir):
                files = os.listdir(received_files_dir)
                if not files:
                    item = MDListItem(
                        MDListItemLeadingIcon(icon="file-outline"),
                        MDListItemHeadlineText(text="No files found"),
                        MDListItemSupportingText(text="No files have been received yet")
                    )
                    self.files_list.add_widget(item)
                    return
                
                for filename in files:
                    file_path = os.path.join(received_files_dir, filename)
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        size = self._format_file_size(stat.st_size)
                        mtime = self._format_date(stat.st_mtime)
                        
                        # Determine file type icon
                        ext = os.path.splitext(filename)[1].lower()
                        file_icon = self._get_file_icon(ext)
                        
                        item = MDListItem(
                            MDListItemLeadingIcon(icon=file_icon),
                            MDListItemHeadlineText(text=filename),
                            MDListItemSupportingText(text=f"{size} • {mtime} • Received")
                        )
                        self.files_list.add_widget(item)
            else:
                item = MDListItem(
                    MDListItemLeadingIcon(icon="alert-circle"),
                    MDListItemHeadlineText(text="Files directory not found"),
                    MDListItemSupportingText(text="The received_files directory does not exist")
                )
                self.files_list.add_widget(item)
                
        except Exception as e:
            print(f"Error loading files: {e}")
            self.files_list.clear_widgets()
            item = MDListItem(
                MDListItemLeadingIcon(icon="alert-circle"),
                MDListItemHeadlineText(text=f"Error loading files"),
                MDListItemSupportingText(text=str(e))
            )
            self.files_list.add_widget(item)
    
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
    
    def _get_file_icon(self, extension):
        """Get appropriate icon for file extension"""
        icon_map = {
            '.pdf': 'file-pdf-box',
            '.doc': 'file-word-box', '.docx': 'file-word-box',
            '.xls': 'file-excel-box', '.xlsx': 'file-excel-box',
            '.ppt': 'file-powerpoint-box', '.pptx': 'file-powerpoint-box',
            '.txt': 'file-document-outline',
            '.jpg': 'file-image', '.jpeg': 'file-image', '.png': 'file-image', 
            '.gif': 'file-image', '.bmp': 'file-image', '.svg': 'file-image',
            '.mp4': 'file-video', '.avi': 'file-video', '.mov': 'file-video', '.mkv': 'file-video',
            '.mp3': 'file-music', '.wav': 'file-music', '.flac': 'file-music',
            '.zip': 'folder-zip', '.rar': 'folder-zip', '.7z': 'folder-zip', '.tar': 'folder-zip', '.gz': 'folder-zip',
            '.py': 'language-python', '.js': 'language-javascript', '.html': 'language-html5',
            '.css': 'language-css3', '.json': 'code-json', '.xml': 'code-tags',
            '.exe': 'application', '.msi': 'application'
        }
        return icon_map.get(extension, 'file-outline')
    
    def open_file_dialog(self, *args):
        """Open platform file dialog for file operations"""
        try:
            # Use platform-specific file dialog
            import tkinter as tk
            from tkinter import filedialog
            
            # Hide tkinter root window
            root = tk.Tk()
            root.withdraw()
            
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title="Select File to Upload",
                filetypes=[
                    ("All files", "*.*"),
                    ("Text files", "*.txt"),
                    ("Images", "*.jpg *.jpeg *.png *.gif *.bmp"),
                    ("Documents", "*.pdf *.doc *.docx *.xls *.xlsx"),
                    ("Archives", "*.zip *.rar *.7z *.tar *.gz")
                ]
            )
            
            root.destroy()
            
            if file_path:
                self.handle_file_selection(file_path)
                
        except ImportError:
            # Fallback: Show info message if tkinter not available
            from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
            snackbar = MDSnackbar(
                MDSnackbarText(text="File manager not available - tkinter required"),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8
            )
            snackbar.open()
    
    def handle_file_selection(self, file_path):
        """Handle selected file"""
        try:
            # Show success message with file info
            filename = os.path.basename(file_path)
            file_size = self._format_file_size(os.path.getsize(file_path))
            
            from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
            snackbar = MDSnackbar(
                MDSnackbarText(text=f"Selected: {filename} ({file_size})"),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8
            )
            snackbar.open()
            
            # TODO: Integrate with actual file upload system
            print(f"File selected for upload: {file_path}")
            
        except Exception as e:
            print(f"Error handling file selection: {e}")
    
    def on_enter(self):
        """Called when the screen is entered"""
        self._load_files_data()