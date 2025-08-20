# -*- coding: utf-8 -*-
"""
logs.py - Log viewer screen with real-time log monitoring
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivymd.uix.textfield import MDTextField, MDTextFieldLeadingIcon, MDTextFieldHintText
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
import os
import threading
import queue

class LogsScreen(MDScreen):
    """Material Design 3 Logs Screen with Real-time Monitoring"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "logs"
        self.auto_refresh = BooleanProperty(True)
        self.log_text = StringProperty("")
        self.log_queue = queue.Queue()
        self.monitor_thread = None
        self._build_ui()
    
    def _build_ui(self):
        """Build logs UI with real-time monitoring"""
        layout = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(16))
        
        # Header with controls
        header = MDBoxLayout(size_hint_y=None, height=dp(56))
        header.add_widget(MDLabel(
            text="Server Logs",
            font_style="Display",
            theme_text_color="Primary"
        ))
        
        # Search field
        self.search_field = MDTextField(
            MDTextFieldLeadingIcon(icon="magnify"),
            MDTextFieldHintText(text="Filter logs..."),
            mode="outlined",
            size_hint_x=0.3
        )
        header.add_widget(self.search_field)
        
        # Auto-refresh switch
        switch_layout = MDBoxLayout(size_hint_x=None, width=dp(120), spacing=dp(8))
        switch_layout.add_widget(MDLabel(
            text="Auto-refresh",
            size_hint_x=None,
            width=dp(80),
            font_style="Body"
        ))
        self.auto_switch = MDSwitch(
            on_active=self.toggle_auto_refresh
        )
        # Set active state after widget creation to avoid KivyMD 2.0.x internal animation issues
        Clock.schedule_once(lambda dt: setattr(self.auto_switch, 'active', True), 0.1)
        switch_layout.add_widget(self.auto_switch)
        header.add_widget(switch_layout)
        
        # Clear button
        clear_btn = MDIconButton(
            icon="delete",
            on_release=self.clear_logs
        )
        header.add_widget(clear_btn)
        
        layout.add_widget(header)
        
        # Log levels filter (horizontal buttons)
        filter_layout = MDBoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        filter_layout.add_widget(MDLabel(
            text="Levels:",
            size_hint_x=None,
            width=dp(60),
            font_style="Body"
        ))
        
        log_levels = ["ALL", "DEBUG", "INFO", "WARNING", "ERROR"]
        self.level_buttons = {}
        for level in log_levels:
            btn = MDIconButton(
                icon="check-circle" if level == "ALL" else "circle-outline",
                theme_icon_color="Custom",
                icon_color=self.theme_cls.primaryColor if level == "ALL" else self.theme_cls.onSurfaceColor,
                on_release=lambda x, l=level: self.toggle_level_filter(l)
            )
            btn.level = level
            btn.active = level == "ALL"
            self.level_buttons[level] = btn
            filter_layout.add_widget(btn)
        
        layout.add_widget(filter_layout)
        
        # Log display area
        # Log display container with FAB
        log_container = MDRelativeLayout()
        
        log_card = MDCard(
            md_bg_color=self.theme_cls.surfaceColor,
            elevation=1,
            radius=dp(8),
            padding=dp(12)
        )
        
        scroll = MDScrollView()
        self.log_label = MDLabel(
            text="[INFO] KivyMD GUI started\\n[INFO] Waiting for log data...\\n",
            font_name="RobotoMono-Regular",
            font_size=dp(12),
            text_size=(None, None),
            halign="left",
            valign="top",
            markup=True,
            theme_text_color="Custom",
            text_color=[0.8, 0.8, 0.8, 1]
        )
        scroll.add_widget(self.log_label)
        log_card.add_widget(scroll)
        log_container.add_widget(log_card)
        
        # Export button (replacing FAB with IconButton)
        fab = MDIconButton(
            icon="download",
            pos_hint={"right": 0.95, "bottom": 0.05},
            on_release=self.export_logs
        )
        log_container.add_widget(fab)
        
        layout.add_widget(log_container)
        
        self.add_widget(layout)
        self._load_initial_logs()
    
    def _load_initial_logs(self):
        """Load initial log data"""
        log_files = [
            "server.log",
            "kivymd_gui.log", 
            "app.log",
            "backup_server.log"
        ]
        
        initial_logs = []
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[-50:]  # Last 50 lines
                        for line in lines:
                            if line.strip():
                                initial_logs.append(f"[{log_file}] {line.strip()}")
                except Exception as e:
                    initial_logs.append(f"[ERROR] Could not read {log_file}: {e}")
        
        if initial_logs:
            formatted_logs = self._format_logs(initial_logs)
            self.log_label.text = formatted_logs
        else:
            self.log_label.text = "[INFO] No log files found. Logs will appear here when available."
        
        # Scroll to bottom
        Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)
    
    def _format_logs(self, logs):
        """Format logs with color coding"""
        formatted = []
        for log in logs:
            if "ERROR" in log.upper():
                formatted.append(f"[color=ff5555]{log}[/color]")
            elif "WARNING" in log.upper() or "WARN" in log.upper():
                formatted.append(f"[color=ffaa55]{log}[/color]")
            elif "INFO" in log.upper():
                formatted.append(f"[color=55ff55]{log}[/color]")
            elif "DEBUG" in log.upper():
                formatted.append(f"[color=5555ff]{log}[/color]")
            else:
                formatted.append(log)
        
        return "\\n".join(formatted)
    
    def _scroll_to_bottom(self):
        """Scroll log view to bottom"""
        try:
            scroll = None
            for child in self.walk():
                if isinstance(child, MDScrollView):
                    scroll = child
                    break
            
            if scroll:
                scroll.scroll_y = 0  # 0 is bottom in Kivy
        except Exception as e:
            print(f"Error scrolling to bottom: {e}")
    
    def toggle_auto_refresh(self, switch, active):
        """Toggle auto-refresh mode"""
        self.auto_refresh = active
        if active:
            self._start_monitoring()
        else:
            self._stop_monitoring()
    
    def toggle_level_filter(self, level):
        """Toggle log level filter"""
        btn = self.level_buttons[level]
        
        if level == "ALL":
            # Toggle all levels
            all_active = not btn.active
            for l, b in self.level_buttons.items():
                b.active = all_active if l == "ALL" else False
                b.icon = "check-circle" if b.active else "circle-outline"
                b.icon_color = self.theme_cls.primaryColor if b.active else self.theme_cls.onSurfaceColor
        else:
            # Toggle individual level
            btn.active = not btn.active
            btn.icon = "check-circle" if btn.active else "circle-outline"
            btn.icon_color = self.theme_cls.primaryColor if btn.active else self.theme_cls.onSurfaceColor
            
            # Update ALL button
            all_btn = self.level_buttons["ALL"]
            all_btn.active = False
            all_btn.icon = "circle-outline"
            all_btn.icon_color = self.theme_cls.onSurfaceColor
        
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply current filters to log display"""
        # Get active levels
        active_levels = []
        for level, btn in self.level_buttons.items():
            if btn.active and level != "ALL":
                active_levels.append(level)
        
        # If ALL is active or no specific levels, show all
        if self.level_buttons["ALL"].active or not active_levels:
            active_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        
        # Apply search filter
        search_text = self.search_field.text.lower()
        
        # Re-filter logs (this is a simplified implementation)
        # In a real implementation, you'd store the raw logs and re-filter them
        print(f"Applying filters - Levels: {active_levels}, Search: '{search_text}'")
    
    def _start_monitoring(self):
        """Start monitoring log files for changes"""
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self._monitor_logs, daemon=True)
            self.monitor_thread.start()
    
    def _stop_monitoring(self):
        """Stop monitoring log files"""
        # In a real implementation, you'd use a threading.Event to stop the thread
        pass
    
    def _monitor_logs(self):
        """Monitor log files for changes (simplified implementation)"""
        import time
        while self.auto_refresh:
            try:
                # Simulate new log entries
                time.sleep(2)
                new_log = f"[{time.strftime('%H:%M:%S')}] [INFO] Log monitoring active..."
                
                # Add to queue for main thread processing
                self.log_queue.put(new_log)
                Clock.schedule_once(self._process_log_queue, 0)
                
                time.sleep(3)
            except Exception as e:
                print(f"Log monitoring error: {e}")
                break
    
    def _process_log_queue(self, dt):
        """Process queued log entries on main thread"""
        try:
            while not self.log_queue.empty():
                new_log = self.log_queue.get_nowait()
                current_text = self.log_label.text
                
                # Add new log entry
                formatted_log = self._format_logs([new_log])
                self.log_label.text = current_text + "\\n" + formatted_log
                
                # Limit log size to prevent memory issues
                lines = self.log_label.text.split("\\n")
                if len(lines) > 1000:
                    self.log_label.text = "\\n".join(lines[-500:])  # Keep last 500 lines
                
                # Auto-scroll to bottom
                Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)
                
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Error processing log queue: {e}")
    
    def clear_logs(self, *args):
        """Clear the log display"""
        self.log_label.text = "[INFO] Logs cleared"
    
    def export_logs(self, *args):
        """Export logs to file"""
        try:
            timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
            export_file = f"exported_logs_{timestamp}.txt"
            
            with open(export_file, 'w', encoding='utf-8') as f:
                # Remove markup for export
                clean_text = self.log_label.text.replace('[/color]', '').replace('\\n', '\\n')
                import re
                clean_text = re.sub(r'\\[color=[^\\]]*\\]', '', clean_text)
                f.write(clean_text)
            
            print(f"Logs exported to {export_file}")
            
        except Exception as e:
            print(f"Error exporting logs: {e}")
    
    def on_enter(self):
        """Called when the screen is entered"""
        if self.auto_refresh:
            self._start_monitoring()
    
    def on_leave(self):
        """Called when the screen is left"""
        self._stop_monitoring()