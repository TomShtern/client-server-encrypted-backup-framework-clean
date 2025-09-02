#!/usr/bin/env python3
"""
Enhanced Card Components - Advanced card system with animations and Material Design 3

Purpose: Provide consistent, animated card components with proper styling
Logic: Card creation, styling, event handling, and state management
UI: Material Design 3 styled cards with hover effects and animations
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import logging
from flet_server_gui.managers.theme_manager import TOKENS

logger = logging.getLogger(__name__)


class CardVariant(Enum):
    """Card style variants"""
    ELEVATED = "elevated"
    FILLED = "filled"
    OUTLINED = "outlined"


class CardSize(Enum):
    """Card sizes"""
    SMALL = "small"    # 280px
    MEDIUM = "medium"  # 320px
    LARGE = "large"    # 360px
    XLARGE = "xlarge"  # 400px


@dataclass
class EnhancedCardConfig:
    """Configuration for enhanced cards"""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[Union[str, ft.Control, List[ft.Control]]] = None
    actions: Optional[List[ft.Control]] = None
    variant: CardVariant = CardVariant.ELEVATED
    size: CardSize = CardSize.MEDIUM
    width: Optional[int] = None
    height: Optional[int] = None
    expand: Union[bool, int] = False
    on_click: Optional[Callable] = None
    on_hover: Optional[Callable] = None
    animate: bool = True
    animation_duration: int = 300  # milliseconds
    elevation: int = 1
    border_radius: int = 12  # Default MD3 border radius
    show_divider: bool = True
    show_header: bool = True
    show_footer: bool = True


class EnhancedCard:
    """
    Enhanced card with Material Design 3 styling and animations
    """
    
    # Size mappings
    SIZE_WIDTHS = {
        CardSize.SMALL: 280,
        CardSize.MEDIUM: 320,
        CardSize.LARGE: 360,
        CardSize.XLARGE: 400
    }
    
    def __init__(self, page: ft.Page, config: EnhancedCardConfig):
        self.page = page
        self.config = config
        self.card_ref = ft.Ref[ft.Card]()
        
        # Create the card
        self.card = self._create_card()
    
    def _create_card(self) -> ft.Card:
        """Create the enhanced card based on variant"""
        # Common properties
        common_props = {
            "ref": self.card_ref,
            "expand": self.config.expand,
            "width": (
                self.SIZE_WIDTHS.get(self.config.size, 320)
                if self.config.width is None
                else self.config.width
            ),
        }

        if self.config.height:
            common_props["height"] = self.config.height

        # Create card content
        content = self._create_card_content()

        # Create card based on variant
        if self.config.variant == CardVariant.ELEVATED:
            return ft.Card(
                content=content, elevation=self.config.elevation, **common_props
            )
        elif self.config.variant == CardVariant.FILLED:
            return ft.Card(
                content=content, color=TOKENS['surface_variant'], **common_props
            )
        elif self.config.variant == CardVariant.OUTLINED:
            return ft.Card(
                content=content, variant=ft.CardVariant.OUTLINE, **common_props
            )
        else:
            return ft.Card(
                content=content, elevation=self.config.elevation, **common_props
            )
    
    def _create_card_content(self) -> ft.Control:
        """Create card content with header, body, and footer"""
        controls = []

        # Header
        if self.config.show_header and (self.config.title or self.config.subtitle):
            if header := self._create_header():
                controls.append(header)
                if self.config.show_divider:
                    controls.append(ft.Divider(height=1))

        if body := self._create_body():
            controls.append(body)

        # Footer/Actions
        if self.config.show_footer and self.config.actions:
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
            border_radius=ft.BorderRadius(
                self.config.border_radius,
                self.config.border_radius,
                self.config.border_radius,
                self.config.border_radius
            )
        )
    
    def _create_header(self) -> Optional[ft.Control]:
        """Create card header with title and subtitle"""
        if not self.config.title and not self.config.subtitle:
            return None
        
        header_controls = []
        
        # Title
        if self.config.title:
            header_controls.append(
                ft.Text(
                    self.config.title,
                    style=ft.TextThemeStyle.TITLE_MEDIUM,
                    weight=ft.FontWeight.W_500
                )
            )
        
        # Subtitle
        if self.config.subtitle:
            header_controls.append(
                ft.Text(
                    self.config.subtitle,
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=TOKENS['outline']
                )
            )
        
        return ft.Column(header_controls, spacing=4)
    
    def _create_body(self) -> Optional[ft.Control]:
        """Create card body content"""
        if not self.config.content:
            return None
        
        if isinstance(self.config.content, str):
            return ft.Text(self.config.content, style=ft.TextThemeStyle.BODY_MEDIUM)
        elif isinstance(self.config.content, list):
            return ft.Column(self.config.content, spacing=12)
        else:
            return self.config.content
    
    def _create_footer(self) -> Optional[ft.Control]:
        """Create card footer with actions"""
        if not self.config.actions:
            return None
        
        return ft.Row(
            self.config.actions,
            alignment=ft.MainAxisAlignment.END,
            spacing=8
        )
    
    def update_content(self, content: Union[str, ft.Control, List[ft.Control]]):
        """Update card content"""
        self.config.content = content
        # Rebuild card content
        new_content = self._create_card_content()
        self.card.content = new_content
        self.page.update()
    
    def update_title(self, title: str):
        """Update card title"""
        self.config.title = title
        # Rebuild card content
        new_content = self._create_card_content()
        self.card.content = new_content
        self.page.update()
    
    def update_subtitle(self, subtitle: str):
        """Update card subtitle"""
        self.config.subtitle = subtitle
        # Rebuild card content
        new_content = self._create_card_content()
        self.card.content = new_content
        self.page.update()
    
    def add_action(self, action: ft.Control):
        """Add action to card footer"""
        if not self.config.actions:
            self.config.actions = []
        self.config.actions.append(action)
        # Rebuild card content
        new_content = self._create_card_content()
        self.card.content = new_content
        self.page.update()
    
    def get_control(self) -> ft.Control:
        """Get the Flet control"""
        return self.card


# Specialized card types
class StatCard(EnhancedCard):
    """
    Specialized card for displaying statistics
    """
    
    def __init__(
        self,
        page: ft.Page,
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
            style=ft.TextThemeStyle.HEADLINE_MEDIUM,
            weight=ft.FontWeight.W_300
        )
        value_row_controls.append(value_text)
        
        if unit:
            value_row_controls.append(
                ft.Text(
                    unit,
                    style=ft.TextThemeStyle.TITLE_MEDIUM,
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
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=trend_color
                )
            )
        
        config = EnhancedCardConfig(
            title=title,
            content=ft.Column(content_controls, spacing=8),
            variant=CardVariant.ELEVATED,
            size=CardSize.SMALL,
            **kwargs
        )
        
        super().__init__(page, config)


class DataCard(EnhancedCard):
    """
    Specialized card for displaying data in a table format
    """
    
    def __init__(
        self,
        page: ft.Page,
        title: str,
        data: List[Dict[str, Any]],
        columns: Optional[List[str]] = None,
        **kwargs
    ):
        # Create table content
        if not data:
            content = ft.Text("No data available", style=ft.TextThemeStyle.BODY_MEDIUM)
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

        config = EnhancedCardConfig(
            title=title,
            content=content,
            variant=CardVariant.OUTLINED,
            size=CardSize.LARGE,
            **kwargs
        )

        super().__init__(page, config)


# Test function
async def test_enhanced_cards(page: ft.Page):
    """Test enhanced cards functionality"""
    print("Testing enhanced cards...")
    
    # Create different card types
    stat_card = StatCard(
        page,
        title="Total Files",
        value=1250,
        unit="files",
        icon=ft.Icons.FOLDER,
        trend="+12% from last week"
    )
    
    data_card = DataCard(
        page,
        title="Recent Activity",
        data=[
            {"action": "File uploaded", "user": "admin", "time": "2 min ago"},
            {"action": "Backup completed", "user": "system", "time": "5 min ago"},
            {"action": "User logged in", "user": "john_doe", "time": "10 min ago"}
        ]
    )
    
    # Create layout
    layout = ft.Column([
        ft.Text("Enhanced Cards Test", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
        ft.Row([
            stat_card.get_control(),
            data_card.get_control()
        ], spacing=20)
    ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
    
    # Add to page
    page.add(layout)
    page.update()
    
    # Test updates
    await asyncio.sleep(2)
    stat_card.update_value(1300)
    await asyncio.sleep(1)
    stat_card.update_trend("+15% from last week")
    
    print("Enhanced cards test completed")


if __name__ == "__main__":
    print("Enhanced Card Components Module")
    print("This module provides enhanced card components for the Flet Server GUI")
