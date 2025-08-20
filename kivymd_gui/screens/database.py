# -*- coding: utf-8 -*-
"""
database.py - Database browser screen
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton, MDButtonText, MDButtonIcon
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemLeadingIcon
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
import os
import json
import sqlite3

class DatabaseScreen(MDScreen):
    """Material Design 3 Database Browser Screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "database"
        self.current_table = None
        self.menu = None
        self._build_ui()
    
    def _build_ui(self):
        """Build database browser UI"""
        layout = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(16))
        
        # Header with table selector
        header = MDBoxLayout(size_hint_y=None, height=dp(56))
        header.add_widget(MDLabel(
            text="Database Browser",
            font_style="Display",
            theme_text_color="Primary"
        ))
        
        # Table selector button
        self.table_btn = MDButton(
            MDButtonText(text="Select Table"),
            MDButtonIcon(icon="menu-down"),
            style="outlined",
            on_release=self.show_table_menu
        )
        header.add_widget(self.table_btn)
        
        # Refresh button
        refresh_btn = MDIconButton(
            icon="refresh",
            on_release=self.refresh_data
        )
        header.add_widget(refresh_btn)
        
        layout.add_widget(header)
        
        # Data list container
        scroll = MDScrollView()
        self.data_list = MDList()
        scroll.add_widget(self.data_list)
        
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def show_table_menu(self, caller):
        """Show table selection menu"""
        # Available data sources
        tables = ["files", "config", "transfers", "logs", "system_info"]
        
        menu_items = [
            {
                "text": table.replace("_", " ").title(),
                "on_release": lambda x=table: self.select_table(x)
            }
            for table in tables
        ]
        
        if self.menu:
            self.menu.dismiss()
        
        self.menu = MDDropdownMenu(
            caller=caller,
            items=menu_items,
            width_mult=3
        )
        self.menu.open()
    
    def select_table(self, table_name):
        """Select and load a database table"""
        self.current_table = table_name
        # Update button text (KivyMD 2.0.x compatible)
        for child in self.table_btn.children:
            if hasattr(child, 'text') and 'Text' in child.__class__.__name__:
                child.text = f"Table: {table_name.replace('_', ' ').title()}"
                break
        
        if self.menu:
            self.menu.dismiss()
        
        self.load_table_data(table_name)
    
    def load_table_data(self, table_name):
        """Load data for the selected table"""
        if table_name == "files":
            self._load_files_data()
        elif table_name == "config":
            self._load_config_data()
        elif table_name == "transfers":
            self._load_transfers_data()
        elif table_name == "logs":
            self._load_logs_data()
        elif table_name == "system_info":
            self._load_system_info()
        
        # Update the data list
        try:
            # Data is automatically updated when we modify self.data_list
            pass
        except Exception as e:
            print(f"Error updating list: {e}")
    
    def _load_files_data(self):
        """Load files data from received_files directory"""
        try:
            received_files_dir = os.path.join(os.getcwd(), "received_files")
            
            # Clear existing list items
            self.data_list.clear_widgets()
            
            if not os.path.exists(received_files_dir):
                item = MDListItem(
                    MDListItemLeadingIcon(icon="alert-circle"),
                    MDListItemHeadlineText(text="No files directory found")
                )
                self.data_list.add_widget(item)
                return
            
            files = os.listdir(received_files_dir)
            if not files:
                item = MDListItem(
                    MDListItemLeadingIcon(icon="file-outline"),
                    MDListItemHeadlineText(text="No files found")
                )
                self.data_list.add_widget(item)
                return
            
            for filename in files:
                file_path = os.path.join(received_files_dir, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    size_bytes = stat.st_size
                    size_human = self._format_file_size(size_bytes)
                    mtime = self._format_date(stat.st_mtime)
                    
                    item = MDListItem(
                        MDListItemLeadingIcon(icon="file"),
                        MDListItemHeadlineText(text=filename),
                        MDListItemSupportingText(text=f"{size_human} • Modified: {mtime}")
                    )
                    self.data_list.add_widget(item)
            
        except Exception as e:
            self.data_list.clear_widgets()
            item = MDListItem(
                MDListItemLeadingIcon(icon="alert-circle"),
                MDListItemHeadlineText(text=f"Error: {e}")
            )
            self.data_list.add_widget(item)
    
    def _load_config_data(self):
        """Load configuration data"""
        try:
            config_files = ["kivymd_gui/config.json", "config.json", "settings.json"]
            
            # Clear existing list items
            self.data_list.clear_widgets()
            
            items_added = False
            for config_file in config_files:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            data = json.load(f)
                        
                        def flatten_dict(d, parent_key='', sep='.'):
                            items = []
                            for k, v in d.items():
                                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                                if isinstance(v, dict):
                                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                                else:
                                    items.append((new_key, v))
                            return dict(items)
                        
                        flat_data = flatten_dict(data)
                        for key, value in flat_data.items():
                            item = MDListItem(
                                MDListItemLeadingIcon(icon="cog"),
                                MDListItemHeadlineText(text=key),
                                MDListItemSupportingText(text=f"{str(value)[:50]}{'...' if len(str(value)) > 50 else ''} • {config_file}")
                            )
                            self.data_list.add_widget(item)
                            items_added = True
                    except Exception as e:
                        item = MDListItem(
                            MDListItemLeadingIcon(icon="alert-circle"),
                            MDListItemHeadlineText(text=f"Error reading {config_file}"),
                            MDListItemSupportingText(text=str(e))
                        )
                        self.data_list.add_widget(item)
                        items_added = True
            
            if not items_added:
                item = MDListItem(
                    MDListItemLeadingIcon(icon="file-outline"),
                    MDListItemHeadlineText(text="No config files found")
                )
                self.data_list.add_widget(item)
            
        except Exception as e:
            self.data_list.clear_widgets()
            item = MDListItem(
                MDListItemLeadingIcon(icon="alert-circle"),
                MDListItemHeadlineText(text=f"Error: {e}")
            )
            self.data_list.add_widget(item)
    
    def _load_transfers_data(self):
        """Load transfer history (simulated)"""
        # Clear existing list items
        self.data_list.clear_widgets()
        
        # This would typically come from a database or log files
        sample_data = [
            ("TXN001", "Client-192.168.1.100", "document.pdf", "Success", "2024-01-15 10:30"),
            ("TXN002", "Client-192.168.1.101", "image.jpg", "Success", "2024-01-15 10:25"),
            ("TXN003", "Client-192.168.1.102", "data.zip", "Failed", "2024-01-15 10:20"),
        ]
        
        for txn_id, client, filename, status, timestamp in sample_data:
            icon = "check-circle" if status == "Success" else "alert-circle"
            item = MDListItem(
                MDListItemLeadingIcon(icon=icon),
                MDListItemHeadlineText(text=f"{txn_id}: {filename}"),
                MDListItemSupportingText(text=f"{client} • {status} • {timestamp}")
            )
            self.data_list.add_widget(item)
    
    def _load_logs_data(self):
        """Load log data"""
        # Clear existing list items
        self.data_list.clear_widgets()
        
        # Try to read actual log files
        log_files = ["server.log", "app.log", "kivymd_gui.log"]
        items_added = False
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-50:]  # Last 50 lines
                    
                    for line in lines:
                        if line.strip():
                            # Simple log parsing - adjust based on your log format
                            parts = line.strip().split(' ', 3)
                            if len(parts) >= 4:
                                timestamp = f"{parts[0]} {parts[1]}"
                                level = parts[2]
                                message = parts[3]
                                
                                icon = {
                                    "ERROR": "alert-circle",
                                    "WARNING": "alert", 
                                    "INFO": "information",
                                    "DEBUG": "bug"
                                }.get(level, "text-box")
                                
                                item = MDListItem(
                                    MDListItemLeadingIcon(icon=icon),
                                    MDListItemHeadlineText(text=f"[{level}] {message[:60]}{'...' if len(message) > 60 else ''}"),
                                    MDListItemSupportingText(text=f"{timestamp} • {log_file}")
                                )
                                self.data_list.add_widget(item)
                                items_added = True
                except Exception as e:
                    item = MDListItem(
                        MDListItemLeadingIcon(icon="alert-circle"),
                        MDListItemHeadlineText(text=f"Error reading {log_file}"),
                        MDListItemSupportingText(text=str(e))
                    )
                    self.data_list.add_widget(item)
                    items_added = True
        
        if not items_added:
            item = MDListItem(
                MDListItemLeadingIcon(icon="file-outline"),
                MDListItemHeadlineText(text="No log files found")
            )
            self.data_list.add_widget(item)
    
    def _load_system_info(self):
        """Load system information"""
        import psutil
        import platform
        
        # Clear existing list items
        self.data_list.clear_widgets()
        
        try:
            system_info = [
                ("Platform", platform.platform(), "desktop"),
                ("Python Version", platform.python_version(), "language-python"),
                ("CPU Count", str(psutil.cpu_count()), "chip"),
                ("CPU Usage", f"{psutil.cpu_percent()}%", "speedometer"),
                ("Memory Total", self._format_file_size(psutil.virtual_memory().total), "memory"),
                ("Memory Used", f"{psutil.virtual_memory().percent}%", "memory"),
                ("Disk Usage", f"{psutil.disk_usage('/').percent}%", "harddisk"),
                ("Working Directory", os.getcwd(), "folder"),
                ("Process ID", str(os.getpid()), "identifier"),
            ]
            
            for prop, value, icon in system_info:
                item = MDListItem(
                    MDListItemLeadingIcon(icon=icon),
                    MDListItemHeadlineText(text=prop),
                    MDListItemSupportingText(text=value)
                )
                self.data_list.add_widget(item)
            
        except Exception as e:
            item = MDListItem(
                MDListItemLeadingIcon(icon="alert-circle"),
                MDListItemHeadlineText(text=f"Error: {e}")
            )
            self.data_list.add_widget(item)
    
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
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    def refresh_data(self, *args):
        """Refresh current table data"""
        if self.current_table:
            self.load_table_data(self.current_table)
    
    def on_enter(self):
        """Called when the screen is entered"""
        # Load default table if none selected
        if not self.current_table:
            self.select_table("files")