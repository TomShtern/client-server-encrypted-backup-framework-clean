#!/usr/bin/env python3
"""
Card Components - Flet-style implementation

Purpose: Provide card components following Flet's best practices
Logic: Inherit from Flet's native Card control with added functionality
UI: Material Design 3 styled cards with enhanced features
"""

import flet as ft
from typing import Optional, List, Callable, Union
from flet_server_gui.managers.theme_manager import TOKENS


class Card(ft.Card):
    """Card with additional features"""
    
    def __init__(
        self,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        content: Optional[Union[str, ft.Control, List[ft.Control]]] = None,
        actions: Optional[List[ft.Control]] = None,
        size: str = "medium",  # small, medium, large, xlarge
        show_header: bool = True,
        show_divider: bool = True,
        show_footer: bool = True,
        on_click: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.title = title
        self.subtitle = subtitle
        self._content = content
        self.actions = actions
        self.size = size
        self.show_header = show_header
        self.show_divider = show_divider
        self.show_footer = show_footer
        self.on_click = on_click
        
        # Set size-based width
        self._set_size()
        
        # Create and set card content
        self.content = self._create_card_content()
    
    def _set_size(self):
        """Set card width based on size"""
        size_widths = {
            "small": 280,
            "medium": 320,
            "large": 360,
            "xlarge": 400
        }
        self.width = size_widths.get(self.size, 320)
    
    def _create_card_content(self) -> ft.Control:
        """Create card content with header, body, and footer"""
        controls = []
        
        # Header
        if self.show_header and (self.title or self.subtitle):
            if header := self._create_header():
                controls.append(header)
                if self.show_divider:
                    controls.append(ft.Divider(height=1))
        
        # Body
        if body := self._create_body():
            controls.append(body)
        
        # Footer/Actions
        if self.show_footer and self.actions:
            if footer := self._create_footer():
                controls.append(footer)
        
        # Wrap in container for padding
        return ft.Container(
            content=ft.Column(
                controls,
                spacing=0,
                expand=True
            ),
            padding=16,
            border_radius=ft.BorderRadius(12, 12, 12, 12)
        )
    
    def _create_header(self) -> Optional[ft.Control]:
        """Create card header with title and subtitle"""
        if not self.title and not self.subtitle:
            return None
        
        header_controls = []
        
        # Title
        if self.title:
            header_controls.append(
                ft.Text(
                    self.title,
                    size=16,
                    weight=ft.FontWeight.W_500
                )
            )
        
        # Subtitle
        if self.subtitle:
            header_controls.append(
                ft.Text(
                    self.subtitle,
                    size=14,
                    color=TOKENS['outline']
                )
            )
        
        return ft.Column(header_controls, spacing=4)
    
    def _create_body(self) -> Optional[ft.Control]:
        """Create card body content"""
        if not self._content:
            return None
        
        if isinstance(self._content, str):
            return ft.Text(self._content, size=14)
        elif isinstance(self._content, list):
            return ft.Column(self._content, spacing=12)
        else:
            return self._content
    
    def _create_footer(self) -> Optional[ft.Control]:
        """Create card footer with actions"""
        if not self.actions:
            return None
        
        return ft.Row(
            self.actions,
            alignment=ft.MainAxisAlignment.END,
            spacing=8
        )
    
    def update_content(self, content: Union[str, ft.Control, List[ft.Control]]):
        """Update card content"""
        self._content = content
        self.content = self._create_card_content()
        self.update()
    
    def update_title(self, title: str):
        """Update card title"""
        self.title = title
        self.content = self._create_card_content()
        self.update()
    
    def update_subtitle(self, subtitle: str):
        """Update card subtitle"""
        self.subtitle = subtitle
        self.content = self._create_card_content()
        self.update()


class StatisticCard(Card):
    """Specialized card for displaying statistics"""
    
    def __init__(
        self,
        title: str,
        value: Union[str, int, float],
        unit: Optional[str] = None,
        icon: Optional[str] = None,
        trend: Optional[str] = None,
        trend_color: Optional[str] = None,
        **kwargs
    ):
        # Format value
        if isinstance(value, (int, float)):
            formatted_value = f"{value:,}"
        else:
            formatted_value = str(value)
        
        # Create content
        content_controls = []
        
        # Icon and value row
        value_row_controls = []
        
        if icon:
            value_row_controls.append(ft.Icon(icon, size=24))
        
        value_text = ft.Text(
            formatted_value,
            size=24,
            weight=ft.FontWeight.W_300
        )
        value_row_controls.append(value_text)
        
        if unit:
            value_row_controls.append(
                ft.Text(
                    unit,
                    size=16,
                    color=TOKENS['outline']
                )
            )
        
        content_controls.append(
            ft.Row(
                value_row_controls,
                alignment=ft.MainAxisAlignment.START,
                spacing=8
            )
        )
        
        # Trend indicator
        if trend:
            trend_color = trend_color or TOKENS['on_background']
            content_controls.append(
                ft.Text(
                    trend,
                    size=14,
                    color=trend_color
                )
            )
        
        super().__init__(
            title=title,
            content=ft.Column(content_controls, spacing=8),
            size="small",
            **kwargs
        )


class DataTableCard(Card):
    """Specialized card for displaying data in a table format"""
    
    def __init__(
        self,
        title: str,
        data: List[dict],
        columns: Optional[List[str]] = None,
        **kwargs
    ):
        # Create table content
        if not data:
            content = ft.Text("No data available", size=14)
        else:
            # Determine columns
            if not columns:
                columns = list(data[0].keys()) if data else []

            header_cells = [
                ft.DataCell(
                    ft.Text(
                        str(col).replace("_", " ").title(),
                        weight=ft.FontWeight.W_500,
                    )
                )
                for col in columns
            ]
            rows = [ft.DataRow(cells=header_cells)]
            # Data rows
            for item in data:
                cells = []
                for col in columns:
                    value = item.get(col, "")
                    cells.append(ft.DataCell(ft.Text(str(value))))
                rows.append(ft.DataRow(cells=cells))

            # Create table
            content = ft.DataTable(
                columns=[ft.DataColumn(ft.Text("")) for _ in columns],
                rows=rows,
                heading_row_color=TOKENS['surface_variant'],
                border=ft.BorderSide(1, TOKENS['outline'])
            )

        super().__init__(
            title=title,
            content=content,
            size="large",
            **kwargs
        )


# Convenience functions with descriptive names
def create_basic_card(
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    content: Optional[Union[str, ft.Control, List[ft.Control]]] = None,
    actions: Optional[List[ft.Control]] = None,
    **kwargs
) -> Card:
    """Create a basic card"""
    return Card(
        title=title,
        subtitle=subtitle,
        content=content,
        actions=actions,
        **kwargs
    )

def create_statistic_card(
    title: str,
    value: Union[str, int, float],
    unit: Optional[str] = None,
    icon: Optional[str] = None,
    trend: Optional[str] = None,
    trend_color: Optional[str] = None,
    **kwargs
) -> StatisticCard:
    """Create a statistic card"""
    return StatisticCard(
        title=title,
        value=value,
        unit=unit,
        icon=icon,
        trend=trend,
        trend_color=trend_color,
        **kwargs
    )

def create_data_table_card(
    title: str,
    data: List[dict],
    columns: Optional[List[str]] = None,
    **kwargs
) -> DataTableCard:
    """Create a data table card"""
    return DataTableCard(
        title=title,
        data=data,
        columns=columns,
        **kwargs
    )

def create_info_card(
    title: str,
    content: Union[str, ft.Control, List[ft.Control]],
    **kwargs
) -> Card:
    """Create an information card"""
    return Card(
        title=title,
        content=content,
        size="medium",
        **kwargs
    )

def create_notification_card(
    title: str,
    message: str,
    actions: Optional[List[ft.Control]] = None,
    **kwargs
) -> Card:
    """Create a notification card"""
    return Card(
        title=title,
        content=message,
        actions=actions,
        size="small",
        **kwargs
    )


# Test function
async def test_cards(page: ft.Page):
    """Test cards functionality"""
    print("Testing cards...")
    
    # Create different card types
    stat_card = create_statistic_card(
        title="Total Files",
        value=1250,
        unit="files",
        icon=ft.icons.FOLDER,
        trend="+12% from last week"
    )
    
    data_card = create_data_table_card(
        title="Recent Activity",
        data=[
            {"action": "File uploaded", "user": "admin", "time": "2 min ago"},
            {"action": "Backup completed", "user": "system", "time": "5 min ago"},
            {"action": "User logged in", "user": "john_doe", "time": "10 min ago"}
        ]
    )
    
    # Create layout
    layout = ft.Column([
        ft.Text("Cards Test", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([
            stat_card,
            data_card
        ], spacing=20)
    ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
    
    # Add to page
    page.add(layout)
    page.update()
    
    # Test updates
    await asyncio.sleep(2)
    # stat_card.update_value(1300)  # This would need to be implemented
    # await asyncio.sleep(1)
    # stat_card.update_trend("+15% from last week")
    
    print("Cards test completed")


if __name__ == "__main__":
    print("Card Components Module")
    print("This module provides card components following Flet best practices")