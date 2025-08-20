# -*- coding: utf-8 -*-
"""
Clients screen for the KivyMD Encrypted Backup Server GUI

This screen provides comprehensive client management functionality
with Material Design 3 styling including client list, search/filtering,
detail views, and real-time status updates.
"""

from __future__ import annotations
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

# KivyMD imports
try:
    from kivymd.uix.screen import MDScreen
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.gridlayout import MDGridLayout
    from kivymd.uix.card import MDCard
    from kivymd.uix.label import MDLabel
    from kivymd.uix.button import MDButton, MDIconButton
    from kivymd.uix.button import MDButtonText
    from kivymd.uix.scrollview import MDScrollView
    from kivymd.uix.divider import MDDivider
    from kivymd.uix.textfield import MDTextField
    from kivymd.uix.list import MDList, MDListItem
    from kivymd.uix.list import MDListItemHeadlineText, MDListItemSupportingText, MDListItemTrailingIcon, MDListItemTrailingSupportingText
    from kivymd.uix.badge import MDBadge
    from kivymd.uix.tooltip import MDTooltip
    # Data tables not available in KivyMD 2.0.x - use lists instead
    
    from kivymd.uix.dialog import MDDialog
    from kivymd.uix.dialog import MDDialogHeadlineText
    from kivymd.uix.dialog import MDDialogButtonContainer, MDDialogIcon
    from kivymd.uix.chip import MDChip, MDChipText
    
    from kivy.clock import Clock
    from kivy.metrics import dp
    from kivy.core.window import Window
    
    KIVYMD_AVAILABLE = True
except ImportError as e:
    print(f"[ERROR] KivyMD not available: {e}")
    KIVYMD_AVAILABLE = False

# Local imports
if KIVYMD_AVAILABLE:
    from ..utils.server_integration import ServerIntegrationBridge
    from ..models.data_models import ServerStats, ClientInfo


class ClientStatsCard(MDCard):
    """Card widget displaying client statistics overview"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 2
        self.padding = dp(16)
        self.size_hint_y = None
        self.height = dp(140)
        
        # Create layout
        layout = MDBoxLayout(orientation="vertical", spacing=dp(8))
        
        # Header
        title_label = MDLabel(
            text="Client Overview",
            theme_text_color="Primary",
            font_style="Headline",
            size_hint_y=None,
            height=dp(28)
        )
        layout.add_widget(title_label)
        layout.add_widget(MDDivider())
        
        # Stats grid
        stats_grid = MDGridLayout(cols=3, spacing=dp(16), adaptive_height=True)
        
        # Total clients
        total_col = MDBoxLayout(orientation="vertical", spacing=dp(4))
        self.total_count_label = MDLabel(
            text="0",
            theme_text_color="Primary",
            font_style="Display",
            size_hint_y=None,
            height=dp(32),
            halign="center"
        )
        total_col.add_widget(self.total_count_label)
        total_desc_label = MDLabel(
            text="Total Clients",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(16),
            halign="center"
        )
        total_col.add_widget(total_desc_label)
        stats_grid.add_widget(total_col)
        
        # Active clients
        active_col = MDBoxLayout(orientation="vertical", spacing=dp(4))
        self.active_count_label = MDLabel(
            text="0",
            theme_text_color="Primary",
            font_style="Display",
            size_hint_y=None,
            height=dp(32),
            halign="center"
        )
        active_col.add_widget(self.active_count_label)
        active_desc_label = MDLabel(
            text="Active",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(16),
            halign="center"
        )
        active_col.add_widget(active_desc_label)
        stats_grid.add_widget(active_col)
        
        # Files transferred
        files_col = MDBoxLayout(orientation="vertical", spacing=dp(4))
        self.files_count_label = MDLabel(
            text="0",
            theme_text_color="Primary",
            font_style="Display",
            size_hint_y=None,
            height=dp(32),
            halign="center"
        )
        files_col.add_widget(self.files_count_label)
        files_desc_label = MDLabel(
            text="Files Transferred",
            theme_text_color="Secondary",
            font_style="Body",
            size_hint_y=None,
            height=dp(16),
            halign="center"
        )
        files_col.add_widget(files_desc_label)
        stats_grid.add_widget(files_col)
        
        layout.add_widget(stats_grid)
        self.add_widget(layout)
    
    def update_stats(self, clients: List[ClientInfo]):
        """Update the stats card with client data"""
        try:
            total_clients = len(clients)
            active_clients = sum(1 for c in clients if c.status == "connected")
            total_files = sum(c.files_transferred for c in clients)
            
            self.total_count_label.text = str(total_clients)
            self.active_count_label.text = str(active_clients)
            self.files_count_label.text = str(total_files)
            
        except Exception as e:
            print(f"[ERROR] Failed to update client stats: {e}")


class ClientSearchCard(MDCard):
    """Card widget with client search and filtering"""
    
    def __init__(self, clients_screen, **kwargs):
        super().__init__(**kwargs)
        self.clients_screen = clients_screen
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 2
        self.padding = dp(16)
        self.size_hint_y = None
        self.height = dp(120)
        
        # Create layout
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(28),
            spacing=dp(8)
        )
        
        title_label = MDLabel(
            text="Search & Filter",
            theme_text_color="Primary",
            font_style="Headline"
        )
        header_layout.add_widget(title_label)
        
        # Refresh button
        refresh_button = MDIconButton(
            icon="refresh",
            on_release=self.refresh_clients
        )
        refresh_button.size_hint = (None, None)
        refresh_button.size = (dp(32), dp(32))
        header_layout.add_widget(refresh_button)
        
        layout.add_widget(header_layout)
        layout.add_widget(MDDivider())
        
        # Search and filter controls
        controls_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            adaptive_height=True
        )
        
        # Search field
        self.search_field = MDTextField(
            mode="outlined",
            hint_text="Search clients (username or IP address)...",
            on_text=self.on_search_text
        )
        self.search_field.size_hint_x = 0.6
        controls_layout.add_widget(self.search_field)
        
        # Status filter chips
        filter_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            adaptive_height=True
        )
        
        self.all_chip = MDChip(
            MDChipText(text="All"),
            on_release=lambda x: self.filter_by_status("all"),
            type="filter"
        )
        filter_layout.add_widget(self.all_chip)
        
        self.connected_chip = MDChip(
            MDChipText(text="Connected"),
            on_release=lambda x: self.filter_by_status("connected"),
            type="filter"
        )
        filter_layout.add_widget(self.connected_chip)
        
        self.disconnected_chip = MDChip(
            MDChipText(text="Disconnected"),
            on_release=lambda x: self.filter_by_status("disconnected"),
            type="filter"
        )
        filter_layout.add_widget(self.disconnected_chip)
        
        controls_layout.add_widget(filter_layout)
        layout.add_widget(controls_layout)
        
        self.add_widget(layout)
        
        # Current filter state
        self.current_filter = "all"
        self.current_search = ""
    
    def on_search_text(self, instance, text):
        """Handle search text changes"""
        self.current_search = text.lower()
        self.clients_screen.apply_filters()
    
    def filter_by_status(self, status: str):
        """Handle status filter changes"""
        # In KivyMD 2.0.x, MDChip doesn't have a 'selected' property
        # Visual feedback for active filter can be handled through theme/color changes if needed
        
        self.current_filter = status
        self.clients_screen.apply_filters()
    
    def refresh_clients(self, *args):
        """Refresh the client list"""
        self.clients_screen.refresh_data()


class ClientListCard(MDCard):
    """Card widget displaying the client list"""
    
    def __init__(self, clients_screen, **kwargs):
        super().__init__(**kwargs)
        self.clients_screen = clients_screen
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 2
        self.padding = dp(16)
        
        # Client data
        self.all_clients: List[ClientInfo] = []
        self.filtered_clients: List[ClientInfo] = []
        
        # Create layout
        layout = MDBoxLayout(orientation="vertical", spacing=dp(8))
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(32),
            spacing=dp(8)
        )
        
        title_label = MDLabel(
            text="Connected Clients",
            theme_text_color="Primary",
            font_style="Headline"
        )
        header_layout.add_widget(title_label)
        
        self.count_badge = MDBadge(
            text="0",
            md_bg_color=self.theme_cls.primaryColor,
            size_hint=(None, None),
            size=(dp(32), dp(20))
        )
        header_layout.add_widget(self.count_badge)
        
        layout.add_widget(header_layout)
        layout.add_widget(MDDivider())
        
        # Client list
        scroll = MDScrollView()
        self.client_list = MDList()
        scroll.add_widget(self.client_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def update_clients(self, clients: List[ClientInfo]):
        """Update the client list"""
        try:
            self.all_clients = clients.copy()
            self.apply_filters()
            
        except Exception as e:
            print(f"[ERROR] Failed to update clients: {e}")
    
    def apply_filters(self, search_text: str = "", status_filter: str = "all"):
        """Apply search and status filters"""
        try:
            filtered = []
            
            for client in self.all_clients:
                # Apply status filter
                if status_filter != "all" and client.status != status_filter:
                    continue
                
                # Apply search filter
                if search_text:
                    if (search_text not in client.username.lower() and
                        search_text not in client.ip_address.lower()):
                        continue
                
                filtered.append(client)
            
            self.filtered_clients = filtered
            self._rebuild_list()
            
        except Exception as e:
            print(f"[ERROR] Failed to apply filters: {e}")
    
    def _rebuild_list(self):
        """Rebuild the client list UI"""
        try:
            self.client_list.clear_widgets()
            
            # Update count
            self.count_badge.text = str(len(self.filtered_clients))
            
            # Add client items
            for client in self.filtered_clients:
                item = self._create_client_item(client)
                self.client_list.add_widget(item)
            
            # Show empty state if no clients
            if not self.filtered_clients:
                empty_item = MDListItem(
                    MDListItemHeadlineText(text="No clients found"),
                    MDListItemSupportingText(text="Check your filters or refresh the list")
                )
                empty_item.theme_text_color = "Custom"
                empty_item.text_color = self.theme_cls.onSurfaceVariantColor
                self.client_list.add_widget(empty_item)
                
        except Exception as e:
            print(f"[ERROR] Failed to rebuild client list: {e}")
    
    def _create_client_item(self, client: ClientInfo) -> MDListItem:
        """Create a client list item"""
        try:
            # Format last seen time
            time_diff = datetime.now() - client.last_seen
            if time_diff.total_seconds() < 60:
                last_seen = "Just now"
            elif time_diff.total_seconds() < 3600:
                minutes = int(time_diff.total_seconds() // 60)
                last_seen = f"{minutes}m ago"
            elif time_diff.total_seconds() < 86400:
                hours = int(time_diff.total_seconds() // 3600)
                last_seen = f"{hours}h ago"
            else:
                last_seen = client.last_seen.strftime("%Y-%m-%d")
            
            # Create list item
            item = MDListItem(
                MDListItemHeadlineText(text=f"{client.username} ({client.ip_address})"),
                MDListItemSupportingText(
                    text=f"Status: {client.status.title()} • Last seen: {last_seen} • Files: {client.files_transferred}"
                ),
                MDListItemTrailingIcon(
                    icon="account-circle" if client.status == "connected" else "account-circle-outline"
                ),
                on_release=lambda x, c=client: self.on_client_selected(c)
            )
            
            # Color coding by status
            if client.status == "connected":
                item.theme_text_color = "Custom"
                item.text_color = self.theme_cls.primaryColor
            else:
                item.theme_text_color = "Secondary"
            
            return item
            
        except Exception as e:
            print(f"[ERROR] Failed to create client item: {e}")
            # Return simple fallback item
            return MDListItem(
                MDListItemHeadlineText(text="Error loading client"),
                MDListItemSupportingText(text=str(e))
            )
    
    def on_client_selected(self, client: ClientInfo):
        """Handle client selection"""
        try:
            self.clients_screen.show_client_details(client)
        except Exception as e:
            print(f"[ERROR] Failed to handle client selection: {e}")


class ClientsScreen(MDScreen):
    """
    Comprehensive client management screen
    
    Features:
    - Client overview statistics
    - Search and filtering capabilities
    - Real-time client list updates
    - Client detail views and actions
    - Material Design 3 components
    """
    
    def __init__(self, server_bridge: Optional[ServerIntegrationBridge] = None,
                 config: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        
        # Store references
        self.server_bridge = server_bridge
        self.config = config or {}
        
        # UI components
        self.stats_card: Optional[ClientStatsCard] = None
        self.search_card: Optional[ClientSearchCard] = None
        self.list_card: Optional[ClientListCard] = None
        
        # State tracking
        self.clients_data: List[ClientInfo] = []
        self.update_event = None
        self.detail_dialog: Optional[MDDialog] = None
        
        # Build UI
        self.build_ui()
        
        # Schedule initial data load
        Clock.schedule_once(self.initial_data_load, 0.5)
    
    def build_ui(self):
        """Build the clients UI"""
        try:
            # Main scroll layout
            scroll = MDScrollView()
            main_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(16),
                padding=dp(16),
                adaptive_height=True
            )
            
            # Stats overview
            self.stats_card = ClientStatsCard()
            main_layout.add_widget(self.stats_card)
            
            # Search and filter section
            self.search_card = ClientSearchCard(self)
            main_layout.add_widget(self.search_card)
            
            # Client list section
            self.list_card = ClientListCard(self)
            main_layout.add_widget(self.list_card)
            
            scroll.add_widget(main_layout)
            self.add_widget(scroll)
            
        except Exception as e:
            print(f"[ERROR] Failed to build clients UI: {e}")
            traceback.print_exc()
            
            # Fallback UI
            error_layout = MDBoxLayout(orientation="vertical", padding=dp(16))
            error_label = MDLabel(
                text=f"Failed to load clients screen: {e}",
                theme_text_color="Error",
                halign="center"
            )
            error_layout.add_widget(error_label)
            self.add_widget(error_layout)
    
    def on_enter(self):
        """Called when the screen is entered"""
        try:
            # Start periodic updates
            self.schedule_updates()
            
            # Refresh data immediately
            self.refresh_data()
            
        except Exception as e:
            print(f"[ERROR] Clients on_enter failed: {e}")
    
    def on_leave(self):
        """Called when the screen is left"""
        try:
            # Stop periodic updates
            self.stop_updates()
            
            # Close any open dialogs
            if self.detail_dialog:
                self.detail_dialog.dismiss()
                self.detail_dialog = None
            
        except Exception as e:
            print(f"[ERROR] Clients on_leave failed: {e}")
    
    def schedule_updates(self):
        """Schedule periodic updates"""
        try:
            self.stop_updates()  # Stop any existing updates
            
            update_interval = self.config.get("ui", {}).get("auto_refresh_interval", 3.0)
            self.update_event = Clock.schedule_interval(self.periodic_update, update_interval)
            
        except Exception as e:
            print(f"[ERROR] Failed to schedule updates: {e}")
    
    def stop_updates(self):
        """Stop periodic updates"""
        try:
            if self.update_event:
                self.update_event.cancel()
                self.update_event = None
        except Exception as e:
            print(f"[ERROR] Failed to stop updates: {e}")
    
    def initial_data_load(self, dt):
        """Perform initial data loading"""
        try:
            self.refresh_data()
        except Exception as e:
            print(f"[ERROR] Initial data load failed: {e}")
    
    def periodic_update(self, dt):
        """Perform periodic updates"""
        try:
            self.refresh_data()
        except Exception as e:
            print(f"[ERROR] Periodic update failed: {e}")
    
    def refresh_data(self):
        """Refresh client data"""
        try:
            if not self.server_bridge:
                return
            
            # Get client list from server bridge
            clients = self.server_bridge.get_client_list()
            
            # Update UI components
            self.clients_data = clients
            
            if self.stats_card:
                self.stats_card.update_stats(clients)
            
            if self.list_card:
                self.list_card.update_clients(clients)
                self.apply_filters()
            
        except Exception as e:
            print(f"[ERROR] Data refresh failed: {e}")
    
    def apply_filters(self):
        """Apply current search and filter settings"""
        try:
            if not self.search_card or not self.list_card:
                return
            
            search_text = self.search_card.current_search
            status_filter = self.search_card.current_filter
            
            self.list_card.apply_filters(search_text, status_filter)
            
        except Exception as e:
            print(f"[ERROR] Failed to apply filters: {e}")
    
    def show_client_details(self, client: ClientInfo):
        """Show detailed client information dialog"""
        try:
            if self.detail_dialog:
                self.detail_dialog.dismiss()
            
            # Create detail content
            content_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(12),
                adaptive_height=True
            )
            
            # Client info grid
            info_grid = MDGridLayout(cols=2, spacing=dp(8), adaptive_height=True)
            
            # Add client details
            details = [
                ("Client ID", client.client_id[:16] + "..." if len(client.client_id) > 16 else client.client_id),
                ("Username", client.username),
                ("IP Address", client.ip_address),
                ("Status", client.status.title()),
                ("Files Transferred", str(client.files_transferred)),
                ("Last Seen", client.last_seen.strftime("%Y-%m-%d %H:%M:%S"))
            ]
            
            for label, value in details:
                label_widget = MDLabel(
                    text=f"{label}:",
                    theme_text_color="Secondary",
                    font_style="Body",
                    size_hint_y=None,
                    height=dp(24)
                )
                value_widget = MDLabel(
                    text=value,
                    theme_text_color="Primary",
                    font_style="Body",
                    size_hint_y=None,
                    height=dp(24)
                )
                info_grid.add_widget(label_widget)
                info_grid.add_widget(value_widget)
            
            content_layout.add_widget(info_grid)
            
            # Action buttons
            if client.status == "connected":
                button_layout = MDBoxLayout(
                    orientation="horizontal",
                    spacing=dp(8),
                    size_hint_y=None,
                    height=dp(40)
                )
                
                disconnect_button = MDButton(
                    MDButtonText(text="Disconnect"),
                    on_release=lambda x: self.disconnect_client(client)
                )
                disconnect_button.theme_bg_color = "Custom"
                disconnect_button.md_bg_color = self.theme_cls.errorColor
                button_layout.add_widget(disconnect_button)
                
                content_layout.add_widget(button_layout)
            
            # Create dialog
            self.detail_dialog = MDDialog(
                title=f"Client Details: {client.username}",
                type="custom",
                content_cls=content_layout,
                buttons=[
                    MDButton(
                        MDButtonText(text="Close"),
                        on_release=self.close_detail_dialog
                    )
                ]
            )
            
            # Replace content with our custom layout
            self.detail_dialog.ids.content.add_widget(content_layout)
            
            self.detail_dialog.open()
            
        except Exception as e:
            print(f"[ERROR] Failed to show client details: {e}")
    
    def disconnect_client(self, client: ClientInfo):
        """Disconnect a client"""
        try:
            if not self.server_bridge:
                return
            
            # TODO: Implement client disconnection in server bridge
            print(f"[INFO] Disconnect client: {client.username} ({client.client_id})")
            
            # Close detail dialog
            self.close_detail_dialog()
            
            # Refresh data
            Clock.schedule_once(lambda dt: self.refresh_data(), 1.0)
            
        except Exception as e:
            print(f"[ERROR] Failed to disconnect client: {e}")
    
    def close_detail_dialog(self, *args):
        """Close the client detail dialog"""
        try:
            if self.detail_dialog:
                self.detail_dialog.dismiss()
                self.detail_dialog = None
        except Exception as e:
            print(f"[ERROR] Failed to close detail dialog: {e}")