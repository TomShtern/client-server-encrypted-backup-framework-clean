"""
Usage examples for responsive layout utilities.

This file demonstrates how to use the responsive layout utilities to replace
hardcoded dimensions and create adaptive UI components.
"""

import flet as ft
from .responsive_utils import ResponsiveBuilder
from .breakpoint_manager import BreakpointManager


class ResponsiveExamples:
    """Examples of how to implement responsive layouts using the utilities."""
    
    @staticmethod
    def create_responsive_server_status_card(page: ft.Page) -> ft.Card:
        """
        Example: Replace hardcoded 350px width with responsive design.
        
        Before:
            ft.Container(width=350, ...)  # Hardcoded!
            
        After:
            Responsive container that adapts to screen size
        """
        width = page.window.width or 1200
        
        # Get responsive configuration
        config = BreakpointManager.get_grid_breakpoint_config(width)
        
        # Create responsive content
        status_content = ft.Column([
            ft.Text(
                "Server Status",
                size=ResponsiveBuilder.get_responsive_font_size(width, 18),
                weight=ft.FontWeight.BOLD
            ),
            ft.Text(
                "Running",
                color=ft.Colors.GREEN,
                size=ResponsiveBuilder.get_responsive_font_size(width, 14)
            ),
            ft.Text(
                f"Port: 1256",
                size=ResponsiveBuilder.get_responsive_font_size(width, 12)
            )
        ])
        
        # Create adaptive container instead of fixed width
        return ResponsiveBuilder.create_responsive_card(
            content=ResponsiveBuilder.create_adaptive_container(
                content=status_content,
                responsive_padding=True,
                # No hardcoded width - adapts to available space
            ),
            elevation=2
        )
    
    @staticmethod
    def create_responsive_dashboard_layout(page: ft.Page) -> ft.Control:
        """
        Example: Create a complete responsive dashboard layout.
        
        Demonstrates:
        - Responsive grid system
        - Adaptive spacing
        - Breakpoint-specific layouts
        - Mobile-first design
        """
        width = page.window.width or 1200
        
        # Create responsive cards
        cards = [
            ResponsiveExamples.create_responsive_server_status_card(page),
            ResponsiveExamples.create_responsive_stats_card(page),
            ResponsiveExamples.create_responsive_activity_card(page),
        ]
        
        # Set responsive column configuration
        for i, card in enumerate(cards):
            if BreakpointManager.is_mobile(width):
                card.col = 12  # Full width on mobile
            elif BreakpointManager.is_tablet(width):
                card.col = 6 if i < 2 else 12  # 2 columns, then full width
            else:
                card.col = 4  # 3 columns on desktop
        
        return ft.Container(
            content=ft.ResponsiveRow(
                controls=cards,
                spacing=BreakpointManager.get_responsive_spacing(width, "medium")
            ),
            padding=ResponsiveBuilder.get_adaptive_padding(width, "large"),
            expand=True
        )
    
    @staticmethod
    def create_responsive_stats_card(page: ft.Page) -> ft.Card:
        """Example responsive stats card with adaptive layout."""
        width = page.window.width or 1200
        
        # Different layouts for different screen sizes
        if BreakpointManager.is_mobile(width):
            # Stack stats vertically on mobile
            stats_layout = ft.Column([
                ft.Text("Active Clients: 5", size=14),
                ft.Text("Files Transferred: 142", size=14),
                ft.Text("Success Rate: 98.5%", size=14),
            ], spacing=8)
        else:
            # Horizontal layout on larger screens
            stats_layout = ft.Row([
                ft.Column([ft.Text("5", size=24, weight=ft.FontWeight.BOLD), ft.Text("Clients", size=12)]),
                ft.Column([ft.Text("142", size=24, weight=ft.FontWeight.BOLD), ft.Text("Files", size=12)]),
                ft.Column([ft.Text("98.5%", size=24, weight=ft.FontWeight.BOLD), ft.Text("Success", size=12)]),
            ], spacing=20, alignment=ft.MainAxisAlignment.SPACE_AROUND)
        
        return ResponsiveBuilder.create_responsive_card(
            content=ResponsiveBuilder.create_adaptive_container(
                content=stats_layout,
                responsive_padding=True
            )
        )
    
    @staticmethod
    def create_responsive_activity_card(page: ft.Page) -> ft.Card:
        """Example responsive activity card with adaptive height."""
        width = page.window.width or 1200
        
        # Adjust visible items based on screen size
        if BreakpointManager.is_mobile(width):
            max_items = 3
        elif BreakpointManager.is_tablet(width):
            max_items = 5
        else:
            max_items = 8
            
        activity_items = [
            ft.Text(f"Activity item {i+1}", size=12) 
            for i in range(max_items)
        ]
        
        return ResponsiveBuilder.create_responsive_card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Recent Activity", weight=ft.FontWeight.BOLD),
                        *activity_items
                    ],
                    spacing=8
                ),
                padding=ResponsiveBuilder.get_adaptive_padding(width),
                # Height adapts to content instead of fixed value
            )
        )
    
    @staticmethod
    def create_responsive_data_table(page: ft.Page, data: list) -> ft.Container:
        """
        Example: Responsive data table that adapts to screen size.
        
        Features:
        - Column visibility based on screen size
        - Adaptive row height
        - Responsive pagination
        """
        width = page.window.width or 1200
        
        # Define columns with priority (higher priority = shown on smaller screens)
        all_columns = [
            {"key": "name", "label": "Name", "priority": 1},
            {"key": "status", "label": "Status", "priority": 2}, 
            {"key": "date", "label": "Date", "priority": 4},
            {"key": "size", "label": "Size", "priority": 5},
            {"key": "actions", "label": "Actions", "priority": 3},
        ]
        
        # Show columns based on screen size
        if BreakpointManager.is_mobile(width):
            visible_columns = [col for col in all_columns if col["priority"] <= 2]
        elif BreakpointManager.is_tablet(width):
            visible_columns = [col for col in all_columns if col["priority"] <= 3]
        else:
            visible_columns = all_columns
            
        # Create responsive table columns
        table_columns = [
            ft.DataColumn(ft.Text(col["label"])) 
            for col in visible_columns
        ]
        
        # Create responsive table rows (limit on mobile)
        max_rows = 5 if BreakpointManager.is_mobile(width) else 10
        table_rows = []
        
        for i, item in enumerate(data[:max_rows]):
            cells = []
            for col in visible_columns:
                cell_value = item.get(col["key"], "")
                cells.append(ft.DataCell(ft.Text(str(cell_value))))
            table_rows.append(ft.DataRow(cells=cells))
            
        return ft.Container(
            content=ft.DataTable(
                columns=table_columns,
                rows=table_rows,
            ),
            # Horizontal scroll on mobile if needed
            scroll=ft.ScrollMode.AUTO if BreakpointManager.is_mobile(width) else None,
            expand=True
        )
    
    @staticmethod
    def create_responsive_form(page: ft.Page) -> ft.Container:
        """
        Example: Responsive form layout.
        
        Features:
        - Single column on mobile
        - Two columns on tablet/desktop
        - Adaptive field sizing
        - Responsive button layout
        """
        width = page.window.width or 1200
        
        # Form fields
        name_field = ft.TextField(label="Name", expand=True)
        email_field = ft.TextField(label="Email", expand=True)
        phone_field = ft.TextField(label="Phone", expand=True)
        address_field = ft.TextField(label="Address", expand=True, multiline=True)
        
        # Responsive layout
        if BreakpointManager.should_stack_components(width):
            # Single column on mobile/tablet
            form_layout = ft.Column([
                name_field,
                email_field,
                phone_field,
                address_field,
            ], spacing=16)
        else:
            # Two columns on desktop
            form_layout = ft.Column([
                ft.ResponsiveRow([
                    ft.Container(name_field, col=6),
                    ft.Container(email_field, col=6),
                ]),
                ft.ResponsiveRow([
                    ft.Container(phone_field, col=6),
                    ft.Container(address_field, col=6),
                ]),
            ], spacing=16)
        
        # Responsive buttons
        if BreakpointManager.is_mobile(width):
            button_layout = ft.Column([
                ft.ElevatedButton("Submit", expand=True),
                ft.OutlinedButton("Cancel", expand=True),
            ], spacing=8)
        else:
            button_layout = ft.Row([
                ft.OutlinedButton("Cancel"),
                ft.ElevatedButton("Submit"),
            ], spacing=16, alignment=ft.MainAxisAlignment.END)
        
        return ResponsiveBuilder.create_adaptive_container(
            content=ft.Column([
                form_layout,
                ft.Divider(),
                button_layout,
            ], spacing=24),
            max_width=800,  # Maximum form width
            responsive_padding=True
        )


# Migration guide for existing components
class MigrationGuide:
    """
    Examples showing how to migrate existing hardcoded components
    to use responsive utilities.
    """
    
    @staticmethod
    def before_and_after_examples():
        """
        Show before/after examples of common migration patterns.
        """
        examples = {
            "Fixed Width Container": {
                "before": """
                ft.Container(
                    width=350,  # Hardcoded!
                    content=content,
                    padding=20  # Hardcoded!
                )
                """,
                "after": """
                ResponsiveBuilder.create_adaptive_container(
                    content=content,
                    responsive_padding=True,  # Adapts to screen size
                    # No hardcoded width - uses available space
                )
                """
            },
            
            "Fixed Grid Layout": {
                "before": """
                ft.GridView(
                    max_extent=200,  # Hardcoded!
                    spacing=10,      # Hardcoded!
                    controls=controls
                )
                """,
                "after": """
                ResponsiveBuilder.create_responsive_grid(
                    controls=controls,
                    width=page.window.width,  # Adapts to screen
                    # max_extent and spacing calculated automatically
                )
                """
            },
            
            "Fixed Font Sizes": {
                "before": """
                ft.Text(
                    "Title",
                    size=24,  # Hardcoded!
                    weight=ft.FontWeight.BOLD
                )
                """,
                "after": """
                ft.Text(
                    "Title",
                    size=ResponsiveBuilder.get_responsive_font_size(width, 24),
                    weight=ft.FontWeight.BOLD
                )
                """
            },
            
            "Fixed Spacing": {
                "before": """
                ft.Column(
                    controls=controls,
                    spacing=20,  # Hardcoded!
                )
                """,
                "after": """
                ResponsiveBuilder.create_responsive_column(
                    controls=controls,
                    spacing=BreakpointManager.get_responsive_spacing(width),
                )
                """
            }
        }
        
        return examples