#!/usr/bin/env python3
"""
Real Data Clients Component for Flet Server GUI
Displays actual client data from the database with real usernames and connection info.
"""

import flet as ft
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..utils.server_bridge import ServerBridge


class RealDataClientsView:
    """Component for displaying real client data from the database."""
    
    def __init__(self, server_bridge: ServerBridge):
        self.server_bridge = server_bridge
        self.clients_table = None
        self.refresh_button = None
        self.status_text = None
        
    def build(self) -> ft.Control:
        """Build the real data clients view."""
        # Status indicator
        self.status_text = ft.Text(
            "Loading real client data...",
            size=14,
            color=ft.Colors.BLUE_600
        )
        
        # Refresh button
        self.refresh_button = ft.ElevatedButton(
            "Refresh Client Data",
            icon=ft.Icons.REFRESH,
            on_click=self.refresh_data,
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE
        )
        
        # Clients data table
        self.clients_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Username", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Last Seen", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Client ID", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        )
        
        # Container with scrollable table
        table_container = ft.Container(
            content=ft.Column([
                self.clients_table
            ], scroll=ft.ScrollMode.AUTO),
            height=400,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10,
        )
        
        # Main container
        return ft.Container(
            content=ft.Column([
                ft.Text("Real Client Data", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self.status_text,
                ft.Row([
                    self.refresh_button,
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(height=10),  # Spacer
                table_container,
            ], spacing=10),
            padding=20,
        )
    
    def refresh_data(self, e=None):
        """Refresh client data from the server."""
        try:
            self.status_text.value = "🔄 Refreshing client data..."
            self.status_text.color = ft.Colors.BLUE_600
            # Update handled by parent
            
            # Get real client data
            clients = self.server_bridge.get_client_list()
            
            # Clear existing rows
            self.clients_table.rows.clear()
            
            if not clients:
                # No clients found
                self.clients_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text("No clients registered", italic=True)),
                        ft.DataCell(ft.Text("", italic=True)),
                        ft.DataCell(ft.Text("", italic=True)),
                        ft.DataCell(ft.Text("", italic=True)),
                    ])
                )
                self.status_text.value = "⚠️ No registered clients found"
                self.status_text.color = ft.Colors.ORANGE_600
            else:
                # Add real client data
                for client in clients:
                    # Format last activity time
                    try:
                        if hasattr(client, 'last_activity'):
                            time_diff = datetime.now() - client.last_activity
                            if time_diff.total_seconds() < 300:  # 5 minutes
                                last_seen = "Just now"
                            elif time_diff.total_seconds() < 3600:  # 1 hour
                                mins = int(time_diff.total_seconds() / 60)
                                last_seen = f"{mins}m ago"
                            else:
                                last_seen = client.last_activity.strftime('%Y-%m-%d %H:%M')
                        else:
                            last_seen = "Unknown"
                    except Exception:
                        last_seen = "Unknown"
                    
                    # Determine status icon and color
                    status_icon = "🟢" if client.status == "Connected" else "🟡"
                    status_text = f"{status_icon} {client.status}"
                    
                    # Add row to table
                    self.clients_table.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(client.client_id), weight=ft.FontWeight.BOLD)),
                            ft.DataCell(ft.Text(status_text)),
                            ft.DataCell(ft.Text(last_seen)),
                            ft.DataCell(ft.Text(client.address if hasattr(client, 'address') else "N/A", 
                                               size=12, color=ft.Colors.GREY_600)),
                        ])
                    )
                
                # Update status
                mode_text = "📊 Mock Data" if getattr(self.server_bridge, 'mock_mode', False) else "🗄️ Real Database"
                self.status_text.value = f"✅ Found {len(clients)} clients ({mode_text})"
                self.status_text.color = ft.Colors.GREEN_600
            
            # Force update by returning the parent control
            
        except Exception as e:
            self.status_text.value = f"❌ Error loading clients: {str(e)}"
            self.status_text.color = ft.Colors.RED_600
            print(f"[ERROR] Failed to refresh client data: {e}")


class RealDataStatsCard:
    """Statistics card showing real database metrics."""
    
    def __init__(self, server_bridge: ServerBridge):
        self.server_bridge = server_bridge
        
    def build(self) -> ft.Control:
        """Build the stats card."""
        # Get real data counts
        try:
            clients = self.server_bridge.get_client_list()
            files = self.server_bridge.get_file_list() 
            
            client_count = len(clients) if clients else 0
            file_count = len(files) if files else 0
            
            # Calculate total file size
            total_size = 0
            if files:
                for file_info in files:
                    size = file_info.get('size', 0)
                    if size:
                        total_size += size
            
            size_mb = total_size / (1024 * 1024) if total_size > 0 else 0
            
            # Data source indicator
            data_source = "📊 Mock Data" if getattr(self.server_bridge, 'mock_mode', False) else "🗄️ Real Database"
            
        except Exception as e:
            client_count = 0
            file_count = 0
            size_mb = 0
            data_source = f"❌ Error: {str(e)}"
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Database Statistics", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_600),
                        ft.Text(f"Registered Clients: {client_count}", size=16),
                    ]),
                    ft.Row([
                        ft.Icon(ft.Icons.FOLDER, color=ft.Colors.GREEN_600),
                        ft.Text(f"Stored Files: {file_count}", size=16),
                    ]),
                    ft.Row([
                        ft.Icon(ft.Icons.STORAGE, color=ft.Colors.ORANGE_600),
                        ft.Text(f"Total Size: {size_mb:.1f} MB", size=16),
                    ]),
                    ft.Divider(),
                    ft.Text(data_source, size=12, color=ft.Colors.GREY_600, italic=True),
                ], spacing=8),
                padding=20,
            ),
            elevation=2,
        )