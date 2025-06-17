# ServerGUI.py - Cross-platform GUI for Encrypted Backup Server
# Implements Option 4 (Simple Popup + System Tray) using tkinter (cross-platform)

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import queue
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import logging
import os
import sys

# Import system tray functionality based on platform
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("Warning: pystray not available - system tray disabled")

# Custom logging handler that puts messages into a queue
class QueueLoggingHandler(logging.Handler):
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))

class ServerGUIStatus:
    """Server status information structure"""
    def __init__(self):
        self.running = False
        self.server_address = ""
        self.port = 0
        self.clients_connected = 0
        self.total_clients = 0
        self.active_transfers = 0
        self.bytes_transferred = 0
        self.uptime_seconds = 0
        self.last_activity = ""
        self.error_message = ""
        self.maintenance_stats = {
            'files_cleaned': 0,
            'partial_files_cleaned': 0,
            'clients_cleaned': 0,
            'last_cleanup': 'Never'
        }

class ServerGUI:
    """Main GUI class for the server dashboard"""
    
    def __init__(self):
        self.status = ServerGUIStatus()
        self.gui_enabled = False
        self.root = None
        self.status_window = None
        self.tray_icon = None
        self.update_queue = queue.Queue()
        self.running = False
        self.gui_thread = None
        self.start_time = time.time()
        self.shutdown_callback = None # For graceful server shutdown
        self.refresh_callback = None # For manually refreshing stats
        self.log_queue = queue.Queue() # Queue for log messages
        self.log_text_widget = None # Reference to the log Text widget
        
        # GUI update lock
        self.lock = threading.Lock()
        
        # Status widgets references
        self.status_labels = {}
        self.progress_vars = {}

    def set_shutdown_callback(self, callback):
        """Sets the callback function to be called when the server is exiting."""
        self.shutdown_callback = callback

    def set_refresh_callback(self, callback):
        """Sets the callback function for refreshing stats."""
        self.refresh_callback = callback

    def get_log_queue(self) -> queue.Queue:
        """Returns the log queue for the GUI."""
        return self.log_queue
        
    def initialize(self) -> bool:
        """Initialize GUI system"""
        try:
            self.running = True
            self.gui_thread = threading.Thread(target=self._gui_main_loop, daemon=True)
            self.gui_thread.start()
            
            # Wait a moment for GUI to initialize
            time.sleep(0.5)
            return self.gui_enabled
            
        except Exception as e:
            print(f"GUI initialization failed: {e}")
            return False
    
    def shutdown(self):
        """Shutdown GUI system"""
        self.running = False
        
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
        
        if self.root:
            try:
                self.root.quit()
            except:
                pass
        
        if self.gui_thread and self.gui_thread.is_alive():
            self.gui_thread.join(timeout=2.0)
    
    def _gui_main_loop(self):
        """Main GUI thread loop"""
        try:
            # Initialize tkinter
            self.root = tk.Tk()
            self.root.title("Encrypted Backup Server")
            self.root.geometry("600x500")
            self.root.protocol("WM_DELETE_WINDOW", self._on_status_window_close)
              # Create GUI components first
            self._create_status_window()
            self._create_system_tray()
            
            self.gui_enabled = True
            
            # Start update timer
            self._schedule_updates()
            
            # Run GUI main loop
            self.root.mainloop()
            
        except Exception as e:
            print(f"GUI main loop error: {e}")
        finally:
            self.gui_enabled = False
    
    def _create_status_window(self):
        """Create the main status window"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1) # Allow main_frame to expand
        main_frame.columnconfigure(1, weight=1)
        # Allow sections to expand width-wise
        main_frame.rowconfigure(5, weight=1) # Allow Error Display (and future Log) to expand height-wise


        # Title
        title_label = ttk.Label(main_frame, text="Encrypted Backup Server Status", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10)) # Reduced pady
        
        # Server Information Section
        server_frame = ttk.LabelFrame(main_frame, text="Server Information", padding="10")
        server_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 5)) # Reduced pady
        server_frame.columnconfigure(1, weight=1)
        
        row = 0
        # Server Status
        ttk.Label(server_frame, text="Status:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.status_labels['status'] = ttk.Label(server_frame, text="Stopped", foreground='red')
        self.status_labels['status'].grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Server Address
        ttk.Label(server_frame, text="Address:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.status_labels['address'] = ttk.Label(server_frame, text="Not configured")
        self.status_labels['address'].grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Uptime
        ttk.Label(server_frame, text="Uptime:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.status_labels['uptime'] = ttk.Label(server_frame, text="00:00:00")
        self.status_labels['uptime'].grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Client Statistics Section
        client_frame = ttk.LabelFrame(main_frame, text="Client Statistics", padding="10")
        client_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        client_frame.columnconfigure(1, weight=1)
        
        row = 0
        # Connected Clients
        ttk.Label(client_frame, text="Connected:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.status_labels['connected'] = ttk.Label(client_frame, text="0")
        self.status_labels['connected'].grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Total Clients
        ttk.Label(client_frame, text="Total Registered:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.status_labels['total_clients'] = ttk.Label(client_frame, text="0")
        self.status_labels['total_clients'].grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Active Transfers
        ttk.Label(client_frame, text="Active Transfers:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.status_labels['transfers'] = ttk.Label(client_frame, text="0")
        self.status_labels['transfers'].grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Transfer Statistics Section
        transfer_frame = ttk.LabelFrame(main_frame, text="Transfer Statistics", padding="10")
        transfer_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        transfer_frame.columnconfigure(1, weight=1)
        
        row = 0
        # Bytes Transferred
        ttk.Label(transfer_frame, text="Bytes Transferred:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.status_labels['bytes'] = ttk.Label(transfer_frame, text="0 B")
        self.status_labels['bytes'].grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Last Activity
        ttk.Label(transfer_frame, text="Last Activity:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.status_labels['activity'] = ttk.Label(transfer_frame, text="None")
        self.status_labels['activity'].grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Maintenance Section
        maintenance_frame = ttk.LabelFrame(main_frame, text="Maintenance Statistics", padding="10")
        maintenance_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        maintenance_frame.columnconfigure(1, weight=1)
        
        row = 0
        # Files Cleaned
        ttk.Label(maintenance_frame, text="Files Cleaned:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.status_labels['files_cleaned'] = ttk.Label(maintenance_frame, text="0")
        self.status_labels['files_cleaned'].grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Partial Files Cleaned
        ttk.Label(maintenance_frame, text="Partial Files Cleaned:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.status_labels['partial_cleaned'] = ttk.Label(maintenance_frame, text="0")
        self.status_labels['partial_cleaned'].grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Clients Cleaned
        ttk.Label(maintenance_frame, text="Stale Clients Cleaned:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.status_labels['clients_cleaned'] = ttk.Label(maintenance_frame, text="0")
        self.status_labels['clients_cleaned'].grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Last Cleanup
        ttk.Label(maintenance_frame, text="Last Cleanup:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.status_labels['last_cleanup'] = ttk.Label(maintenance_frame, text="Never")
        self.status_labels['last_cleanup'].grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Error Display
        error_frame = ttk.LabelFrame(main_frame, text="Status Messages", padding="10")
        error_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 5)) # Reduced pady
        error_frame.columnconfigure(0, weight=1)
        
        self.status_labels['error'] = ttk.Label(error_frame, text="Ready", foreground='green')
        self.status_labels['error'].grid(row=0, column=0, sticky=tk.W)

        # Activity Log Section
        log_display_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_display_frame.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=(0, 5)) # Reduced pady
        log_display_frame.columnconfigure(0, weight=1)
        log_display_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=2) # Give log display more weight

        self.log_text_widget = tk.Text(log_display_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text_widget.grid(row=0, column=0, sticky="nsew")

        log_scrollbar = ttk.Scrollbar(log_display_frame, orient=tk.VERTICAL, command=self.log_text_widget.yview)
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text_widget.config(yscrollcommand=log_scrollbar.set)
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(5, 0)) # Reduced pady
        
        ttk.Button(button_frame, text="Hide Window", 
                  command=self._hide_status_window).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="View Logs",
                  command=self._view_logs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Refresh Stats",
                  command=self._on_refresh_stats_clicked).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(button_frame, text="Exit Server", 
                  command=self._exit_server).pack(side=tk.LEFT)
    
    def _create_system_tray(self):
        """Create system tray icon"""
        if not TRAY_AVAILABLE:
            return
        
        try:
            # Create a simple icon
            image = Image.new('RGB', (64, 64), color='blue')
            draw = ImageDraw.Draw(image)
            draw.rectangle([16, 16, 48, 48], fill='white')
            draw.text((24, 28), 'SRV', fill='black')
            
            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem("Show Status", self._show_status_window),
                pystray.MenuItem("View Logs", self._view_logs),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self._exit_server)
            )
            
            # Create and start tray icon
            self.tray_icon = pystray.Icon("BackupServer", image, 
                                        "Encrypted Backup Server", menu)
            
            # Start tray in separate thread
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()
            
        except Exception as e:
            print(f"System tray creation failed: {e}")
    
    def _schedule_updates(self):
        """Schedule periodic GUI updates"""
        if self.running and self.gui_enabled:
            self._process_updates()
            self._update_uptime()
            self.root.after(1000, self._schedule_updates)  # Update every second
    
    def _process_updates(self):
        """Process queued status updates"""
        try:
            while True:
                update = self.update_queue.get_nowait()
                self._apply_update(update)
        except queue.Empty:
            pass

        # Process log queue
        try:
            while True:
                log_message = self.log_queue.get_nowait()
                self._add_log_message_to_widget(log_message)
        except queue.Empty:
            pass

    def _add_log_message_to_widget(self, message: str):
        """Adds a log message to the Text widget and manages line limit."""
        if not self.log_text_widget:
            return

        self.log_text_widget.config(state=tk.NORMAL)
        self.log_text_widget.insert(tk.END, message + "\n")

        # Limit lines in the text widget (e.g., 200 lines)
        max_lines = 200
        num_lines = int(self.log_text_widget.index('end-1c').split('.')[0])
        if num_lines > max_lines:
            self.log_text_widget.delete('1.0', f'{num_lines - max_lines}.0')

        self.log_text_widget.see(tk.END) # Auto-scroll
        self.log_text_widget.config(state=tk.DISABLED)

    def _apply_update(self, update: Dict[str, Any]):
        """Apply a status update to the GUI"""
        if not self.gui_enabled:
            return
        
        try:
            update_type = update.get('type')
            
            if update_type == 'server_status':
                self._update_server_status(update)
            elif update_type == 'client_stats':
                self._update_client_stats(update)
            elif update_type == 'transfer_stats':
                self._update_transfer_stats(update)
            elif update_type == 'maintenance_stats':
                self._update_maintenance_stats(update)
            elif update_type == 'error':
                self._update_error(update)
            elif update_type == 'notification':
                self._show_notification(update)
                
        except Exception as e:
            print(f"GUI update error: {e}")
    
    def _update_server_status(self, update: Dict[str, Any]):
        """Update server status information"""
        if 'running' in update:
            self.status.running = update['running']
            status_text = "Running" if self.status.running else "Stopped"
            color = 'green' if self.status.running else 'red'
            self.status_labels['status'].config(text=status_text, foreground=color)
        
        if 'address' in update:
            self.status.server_address = update['address']
            self.status_labels['address'].config(text=self.status.server_address)
        
        if 'port' in update:
            self.status.port = update['port']
            address_text = f"{self.status.server_address}:{self.status.port}"
            self.status_labels['address'].config(text=address_text)
    
    def _update_client_stats(self, update: Dict[str, Any]):
        """Update client statistics"""
        if 'connected' in update:
            self.status.clients_connected = update['connected']
            self.status_labels['connected'].config(text=str(self.status.clients_connected))
        
        if 'total' in update:
            self.status.total_clients = update['total']
            self.status_labels['total_clients'].config(text=str(self.status.total_clients))
        
        if 'active_transfers' in update:
            self.status.active_transfers = update['active_transfers']
            self.status_labels['transfers'].config(text=str(self.status.active_transfers))
    
    def _update_transfer_stats(self, update: Dict[str, Any]):
        """Update transfer statistics"""
        if 'bytes_transferred' in update:
            self.status.bytes_transferred = update['bytes_transferred']
            formatted_bytes = self._format_bytes(self.status.bytes_transferred)
            self.status_labels['bytes'].config(text=formatted_bytes)
        
        if 'last_activity' in update:
            self.status.last_activity = update['last_activity']
            self.status_labels['activity'].config(text=self.status.last_activity)
    
    def _update_maintenance_stats(self, update: Dict[str, Any]):
        """Update maintenance statistics"""
        stats = update.get('stats', {})

        if 'files_cleaned' in stats:
            self.status.maintenance_stats['files_cleaned'] = stats['files_cleaned']
            self.status_labels['files_cleaned'].config(
                text=str(self.status.maintenance_stats['files_cleaned']))

        if 'partial_files_cleaned' in stats:
            self.status.maintenance_stats['partial_files_cleaned'] = stats['partial_files_cleaned']
            self.status_labels['partial_cleaned'].config(
                text=str(self.status.maintenance_stats['partial_files_cleaned']))

        if 'clients_cleaned' in stats:
            self.status.maintenance_stats['clients_cleaned'] = stats['clients_cleaned']
            self.status_labels['clients_cleaned'].config(
                text=str(self.status.maintenance_stats['clients_cleaned']))

        if 'last_cleanup' in stats:
            self.status.maintenance_stats['last_cleanup'] = stats['last_cleanup']
            self.status_labels['last_cleanup'].config(
                text=self.status.maintenance_stats['last_cleanup'])
    
    def _update_error(self, update: Dict[str, Any]):
        """Update error/status message"""
        message = update.get('message', '')
        error_type = update.get('error_type', 'info')
        
        color = 'red' if error_type == 'error' else 'green' if error_type == 'success' else 'black'
        self.status_labels['error'].config(text=message, foreground=color)
    
    def _update_uptime(self):
        """Update server uptime display"""
        if self.status.running:
            uptime_seconds = int(time.time() - self.start_time)
            uptime_str = self._format_duration(uptime_seconds)
            self.status_labels['uptime'].config(text=uptime_str)
    
    def _show_notification(self, update: Dict[str, Any]):
        """Show notification popup"""
        title = update.get('title', 'Server Notification')
        message = update.get('message', '')
        
        if self.gui_enabled:
            messagebox.showinfo(title, message)
    
    def _format_bytes(self, bytes_count: Union[int, float]) -> str:
        """Format byte count as human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} PB"
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds as HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Event handlers
    def _on_status_window_close(self):
        """Handle status window close event"""
        self._hide_status_window()
    
    def _show_status_window(self, widget=None):
        """Show status window"""
        if self.root:
            self.root.deiconify()
            self.root.lift()
    
    def _hide_status_window(self):
        """Hide status window"""
        if self.root:
            self.root.withdraw()
    
    def _view_logs(self):
        """Shows the log viewer window."""
        log_window = tk.Toplevel(self.root)
        log_window.title("Server Logs")
        log_window.geometry("800x600")

        text_area = tk.Text(log_window, wrap=tk.WORD, state=tk.DISABLED)
        text_area.pack(padx=10, pady=(10,0), expand=True, fill=tk.BOTH)

        scrollbar = ttk.Scrollbar(text_area, command=text_area.yview)
        text_area.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def load_logs():
            self._load_log_content(text_area)

        button_frame = ttk.Frame(log_window)
        button_frame.pack(pady=10)

        refresh_button = ttk.Button(button_frame, text="Refresh", command=load_logs)
        refresh_button.pack()

        load_logs() # Initial load

    def _load_log_content(self, text_widget: tk.Text):
        """Loads log content into the given text widget."""
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        try:
            log_file_path = "server.log"
            if os.path.exists(log_file_path):
                file_size = os.path.getsize(log_file_path)
                read_size = 10 * 1024  # Last 10KB

                with open(log_file_path, 'rb') as f:
                    if file_size > read_size:
                        f.seek(-read_size, os.SEEK_END)
                        # Read an extra line to ensure we don't cut off the first visible line
                        try:
                            # Skip the potentially partial first line
                            f.readline()
                        except Exception:
                             # In case readline fails (e.g. binary data or very small chunk)
                            f.seek(-read_size, os.SEEK_END) # Reset seek if readline failed

                    content = f.read().decode('utf-8', errors='replace')

                if not content.strip() and file_size > 0 : # if last 10k were all non-utf8
                    text_widget.insert(tk.END, f"[Could not decode the last {read_size/1024:.0f}KB of the log file. It might contain binary data or be corrupted.]\n\n")
                    text_widget.insert(tk.END, f"[Showing the beginning of the file instead...]\n\n")
                    with open(log_file_path, 'r', encoding='utf-8', errors='replace') as f_full:
                        content = f_full.read(read_size)


                text_widget.insert(tk.END, content)
                text_widget.see(tk.END) # Scroll to the end
            else:
                text_widget.insert(tk.END, "Log file (server.log) not found.")
        except Exception as e:
            text_widget.insert(tk.END, f"Error loading log file: {e}")
        finally:
            text_widget.config(state=tk.DISABLED)

    def _exit_server(self):
        """Exit the server application"""
        result = messagebox.askyesno("Exit Server", 
                                   "Are you sure you want to exit the backup server?")
        if result:
            if self.shutdown_callback:
                try:
                    self.shutdown_callback()
                except Exception as e:
                    print(f"Error during shutdown callback: {e}") # Log or handle as needed
            # os._exit(0) # Removed to allow graceful shutdown by the server itself

    def _on_refresh_stats_clicked(self):
        """Handles the Refresh Stats button click."""
        if self.refresh_callback:
            try:
                self.refresh_callback()
            except Exception as e:
                print(f"Error during refresh_callback: {e}") # Log or handle
        self._update_uptime() # Also refresh uptime immediately
    
    # Public API methods for server integration
    def update_server_status(self, running: bool, address: str = "", port: int = 0):
        """Update server running status"""
        self.update_queue.put({
            'type': 'server_status',
            'running': running,
            'address': address,
            'port': port
        })

    def update_client_stats(self, connected: Optional[int] = None, total: Optional[int] = None,
                           active_transfers: Optional[int] = None):
        """Update client statistics"""
        update: Dict[str, Any] = {'type': 'client_stats'}
        if connected is not None:
            update['connected'] = connected
        if total is not None:
            update['total'] = total
        if active_transfers is not None:
            update['active_transfers'] = active_transfers
        self.update_queue.put(update)

    def update_transfer_stats(self, bytes_transferred: Optional[int] = None,
                             last_activity: Optional[str] = None):
        """Update transfer statistics"""
        update: Dict[str, Any] = {'type': 'transfer_stats'}
        if bytes_transferred is not None:
            update['bytes_transferred'] = bytes_transferred
        if last_activity is not None:
            update['last_activity'] = last_activity
        self.update_queue.put(update)

    def update_maintenance_stats(self, stats: Dict[str, Any]):
        """Update maintenance statistics"""
        self.update_queue.put({
            'type': 'maintenance_stats',
            'stats': stats
        })

    def show_error(self, message: str):
        """Show error message"""
        self.update_queue.put({
            'type': 'error',
            'message': message,
            'error_type': 'error'
        })

    def show_success(self, message: str):
        """Show success message"""
        self.update_queue.put({
            'type': 'error',
            'message': message,
            'error_type': 'success'
        })

    def show_info(self, message: str):
        """Show info message"""
        self.update_queue.put({
            'type': 'error',
            'message': message,
            'error_type': 'info'
        })

    def show_notification(self, title: str, message: str):
        """Show notification popup"""
        self.update_queue.put({
            'type': 'notification',
            'title': title,
            'message': message
        })

# Global GUI instance (singleton pattern)
_server_gui_instance = None

def get_server_gui() -> ServerGUI:
    """Get the global ServerGUI instance"""
    global _server_gui_instance
    if _server_gui_instance is None:
        _server_gui_instance = ServerGUI()
    return _server_gui_instance

# Helper functions for easy integration
def initialize_server_gui() -> bool:
    """Initialize the server GUI system"""
    try:
        gui = get_server_gui()
        return gui.initialize()
    except Exception as e:
        print(f"Server GUI initialization failed: {e}")
        return False

def shutdown_server_gui():
    """Shutdown the server GUI system"""
    global _server_gui_instance
    if _server_gui_instance:
        _server_gui_instance.shutdown()
        _server_gui_instance = None

def update_server_status(running: bool, address: str = "", port: int = 0):
    """Update server status in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.update_server_status(running, address, port)
    except:
        pass

def update_client_stats(connected: Optional[int] = None, total: Optional[int] = None,
                       active_transfers: Optional[int] = None):
    """Update client statistics in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.update_client_stats(connected, total, active_transfers)
    except:
        pass

def update_transfer_stats(bytes_transferred: Optional[int] = None, last_activity: Optional[str] = None):
    """Update transfer statistics in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.update_transfer_stats(bytes_transferred, last_activity)
    except:
        pass

def update_maintenance_stats(stats: Dict[str, Any]):
    """Update maintenance statistics in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.update_maintenance_stats(stats)
    except:
        pass

def show_server_error(message: str):
    """Show server error message in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.show_error(message)
    except:
        pass

def show_server_success(message: str):
    """Show server success message in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.show_success(message)
    except:
        pass

def show_server_notification(title: str, message: str):
    """Show server notification in GUI"""
    try:
        gui = get_server_gui()
        if gui.gui_enabled:
            gui.show_notification(title, message)
    except:
        pass

# Test the GUI if run directly
if __name__ == "__main__":
    print("Testing Server GUI...")
    
    # Test GUI initialization
    if initialize_server_gui():
        print("GUI initialized successfully")
        
        # Simulate some updates
        time.sleep(1)
        update_server_status(True, "127.0.0.1", 8080)
        
        time.sleep(1)
        update_client_stats(connected=2, total=5, active_transfers=1)
        
        time.sleep(1)
        update_transfer_stats(bytes_transferred=1024*1024*50)
        
        time.sleep(1)
        show_server_success("Test server started successfully")
        
        # Keep GUI running for testing
        try:
            gui = get_server_gui()
            if gui.gui_thread:
                gui.gui_thread.join()
        except KeyboardInterrupt:
            print("\nShutting down...")
            shutdown_server_gui()
    else:
        print("GUI initialization failed")
