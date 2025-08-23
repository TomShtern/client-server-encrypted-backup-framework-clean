#!/usr/bin/env python3
"""
Enhanced UI Components Library
Custom Material Design 3 components with advanced interactions and animations.
"""

import flet as ft
from typing import Optional, Callable, List, Union
from enum import Enum
import asyncio
import math


class ComponentSize(Enum):
    """Standard component sizes following Material Design 3 guidelines"""
    XS = 24
    S = 32
    M = 40
    L = 48
    XL = 56


class EnhancedButton(ft.FilledButton):
    """Enhanced button with advanced animations and interactions"""
    
    def __init__(self, 
                 text: str = "",
                 icon: Optional[ft.Icons] = None,
                 on_click: Optional[Callable] = None,
                 size: ComponentSize = ComponentSize.M,
                 elevation: int = 2,
                 animate_duration: int = 150,
                 ripple_effect: bool = True,
                 **kwargs):
        super().__init__(text=text, icon=icon, on_click=on_click, **kwargs)
        
        # Enhanced animation properties
        self.animate_scale = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
        self.animate_elevation = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
        
        # Ripple effect for advanced feedback
        self.ripple_effect = ripple_effect
        if ripple_effect:
            self.ink = True
            
        # Store original properties for animations
        self.original_elevation = elevation
        self.original_scale = 1
        
        # Add hover effects
        self.on_hover = self._on_hover
        
    def _on_hover(self, e):
        """Handle hover events for enhanced feedback"""
        if e.data == "true":
            # Hover enter
            self.elevation = self.original_elevation + 2
            self.scale = 1.02
        else:
            # Hover exit
            self.elevation = self.original_elevation
            self.scale = 1
        self.page.update()


class EnhancedIconButton(ft.IconButton):
    """Enhanced icon button with advanced animations and interactions"""
    
    def __init__(self, 
                 icon: ft.Icons,
                 tooltip: Optional[str] = None,
                 on_click: Optional[Callable] = None,
                 size: int = 24,
                 animate_duration: int = 100,
                 hover_scale: float = 1.15,
                 **kwargs):
        super().__init__(icon=icon, tooltip=tooltip, on_click=on_click, **kwargs)
        
        # Animation properties
        self.animate_scale = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
        self.hover_scale = hover_scale
        self.original_scale = 1
        
        # Add hover effects
        self.on_hover = self._on_hover
        
    def _on_hover(self, e):
        """Handle hover events for enhanced feedback"""
        if e.data == "true":
            # Hover enter
            self.scale = self.hover_scale
        else:
            # Hover exit
            self.scale = 1
        self.page.update()


class EnhancedDataTable(ft.DataTable):
    """Enhanced data table with sorting, filtering, and animations"""
    
    def __init__(self, 
                 columns: List[ft.DataColumn],
                 rows: Optional[List[ft.DataRow]] = None,
                 sortable: bool = True,
                 filterable: bool = True,
                 striped_rows: bool = True,
                 hover_highlight: bool = True,
                 animate_duration: int = 200,
                 **kwargs):
        super().__init__(columns=columns, rows=rows or [], **kwargs)
        
        self.sortable = sortable
        self.filterable = filterable
        self.striped_rows = striped_rows
        self.hover_highlight = hover_highlight
        self.animate_duration = animate_duration
        self.original_rows = rows or []
        
        # Add sorting functionality to columns if enabled
        if sortable:
            self._add_sorting_to_columns()
            
        # Add hover effects to rows if enabled
        if hover_highlight and self.rows:
            self._add_hover_effects_to_rows()
    
    def _add_sorting_to_columns(self):
        """Add sorting functionality to columns"""
        for i, column in enumerate(self.columns):
            if column.on_click is None:  # Only add if not already set
                column.on_click = lambda e, col_index=i: self._sort_column(col_index)
    
    def _add_hover_effects_to_rows(self):
        """Add hover effects to table rows"""
        for row in self.rows:
            row.on_hover = self._on_row_hover
            row.animate_bgcolor = ft.Animation(self.animate_duration, ft.AnimationCurve.EASE_OUT)
    
    def _on_row_hover(self, e):
        """Handle row hover events"""
        if e.data == "true":
            # Hover enter - lighten background
            row = e.control
            if hasattr(row, 'bgcolor') and row.bgcolor:
                # Store original color and lighten
                pass
            else:
                row.bgcolor = ft.colors.SURFACE_VARIANT
        else:
            # Hover exit - restore original
            row = e.control
            row.bgcolor = None
        self.page.update()
    
    def _sort_column(self, column_index: int):
        """Sort table by column index"""
        # Simple sorting implementation
        if self.rows:
            # Get current sort direction (ascending by default)
            ascending = True
            
            # Sort rows based on column values
            try:
                self.rows.sort(key=lambda row: str(row.cells[column_index].content.value), reverse=not ascending)
                self.page.update()
            except Exception as e:
                print(f"Sorting error: {e}")
    
    def filter_rows(self, filter_text: str, column_indices: Optional[List[int]] = None):
        """Filter rows based on text"""
        if not filter_text:
            # Restore all rows
            self.rows = self.original_rows.copy()
        else:
            # Filter rows
            filtered_rows = []
            for row in self.original_rows:
                match_found = False
                # Check specified columns or all columns
                columns_to_check = column_indices if column_indices else range(len(row.cells))
                for col_idx in columns_to_check:
                    if col_idx < len(row.cells):
                        cell_content = str(getattr(row.cells[col_idx].content, 'value', ''))
                        if filter_text.lower() in cell_content.lower():
                            match_found = True
                            break
                if match_found:
                    filtered_rows.append(row)
            self.rows = filtered_rows
        
        self.page.update()


class EnhancedChip(ft.Chip):
    """Enhanced chip with advanced animations and interactions"""
    
    def __init__(self, 
                 label: ft.Control,
                 on_click: Optional[Callable] = None,
                 selected: bool = False,
                 selectable: bool = False,
                 animate_duration: int = 150,
                 hover_scale: float = 1.05,
                 **kwargs):
        super().__init__(label=label, on_click=on_click, selected=selected, **kwargs)
        
        self.selectable = selectable
        self.animate_duration = animate_duration
        self.hover_scale = hover_scale
        self.original_scale = 1
        
        # Animation properties
        self.animate_scale = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
        
        # Add hover effects
        self.on_hover = self._on_hover
    
    def _on_hover(self, e):
        """Handle hover events for enhanced feedback"""
        if e.data == "true":
            # Hover enter
            self.scale = self.hover_scale
        else:
            # Hover exit
            self.scale = 1
        self.page.update()
    
    def toggle_selection(self):
        """Toggle chip selection state"""
        if self.selectable:
            self.selected = not self.selected
            self.page.update()


class EnhancedTextField(ft.TextField):
    """Enhanced text field with floating label and advanced interactions"""
    
    def __init__(self, 
                 label: str = "",
                 icon: Optional[ft.Icons] = None,
                 on_change: Optional[Callable] = None,
                 animate_duration: int = 150,
                 floating_label: bool = True,
                 helper_text: Optional[str] = None,
                 **kwargs):
        super().__init__(label=label, icon=icon, on_change=on_change, **kwargs)
        
        self.floating_label = floating_label
        self.helper_text_original = helper_text
        self.animate_duration = animate_duration
        
        # Animation properties
        self.animate_scale = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
        
        # Add focus effects
        self.on_focus = self._on_focus
        self.on_blur = self._on_blur
        
        # Add helper text if provided
        if helper_text:
            self.helper_text = helper_text
    
    def _on_focus(self, e):
        """Handle focus events"""
        # Scale up slightly when focused
        self.scale = 1.02
        self.page.update()
    
    def _on_blur(self, e):
        """Handle blur events"""
        # Return to normal scale
        self.scale = 1
        self.page.update()


class EnhancedCard(ft.Card):
    """Enhanced card with advanced animations and interactions"""
    
    def __init__(self, 
                 content: ft.Control,
                 elevation: int = 1,
                 animate_duration: int = 200,
                 hover_elevation_increase: int = 2,
                 **kwargs):
        super().__init__(content=content, elevation=elevation, **kwargs)
        
        self.original_elevation = elevation
        self.hover_elevation_increase = hover_elevation_increase
        self.animate_duration = animate_duration
        
        # Animation properties
        self.animate_elevation = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
        self.animate_scale = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
        
        # Add hover effects
        self.on_hover = self._on_hover
    
    def _on_hover(self, e):
        """Handle hover events for enhanced feedback"""
        if e.data == "true":
            # Hover enter - increase elevation
            self.elevation = self.original_elevation + self.hover_elevation_increase
            self.scale = 1.01
        else:
            # Hover exit - restore original
            self.elevation = self.original_elevation
            self.scale = 1
        self.page.update()


class CircularProgressIndicator(ft.ProgressRing):
    """Enhanced circular progress indicator with animations"""
    
    def __init__(self, 
                 width: int = 40,
                 height: int = 40,
                 stroke_width: int = 4,
                 animate_duration: int = 300,
                 color: Optional[str] = None,
                 **kwargs):
        super().__init__(width=width, height=height, stroke_width=stroke_width, **kwargs)
        
        self.animate_duration = animate_duration
        if color:
            self.color = color
            
        # Add rotation animation
        self.animate_rotation = ft.Animation(animate_duration, ft.AnimationCurve.LINEAR)
    
    async def start_indeterminate(self):
        """Start indeterminate animation"""
        while getattr(self, '_animating', True):
            self.rotate = getattr(self, 'rotate', 0) + 1
            await self.page.update_async()
            await asyncio.sleep(0.016)  # ~60fps
    
    def stop_indeterminate(self):
        """Stop indeterminate animation"""
        self._animating = False


# Factory functions for easy component creation
def create_enhanced_button(text: str, 
                          icon: Optional[ft.Icons] = None,
                          on_click: Optional[Callable] = None,
                          **kwargs) -> EnhancedButton:
    """Create an enhanced button with default settings"""
    return EnhancedButton(text=text, icon=icon, on_click=on_click, **kwargs)

def create_enhanced_icon_button(icon: ft.Icons,
                               tooltip: Optional[str] = None,
                               on_click: Optional[Callable] = None,
                               **kwargs) -> EnhancedIconButton:
    """Create an enhanced icon button with default settings"""
    return EnhancedIconButton(icon=icon, tooltip=tooltip, on_click=on_click, **kwargs)

def create_enhanced_chip(label: str,
                        on_click: Optional[Callable] = None,
                        selected: bool = False,
                        **kwargs) -> EnhancedChip:
    """Create an enhanced chip with default settings"""
    return EnhancedChip(label=ft.Text(label), on_click=on_click, selected=selected, **kwargs)

def create_enhanced_text_field(label: str,
                               icon: Optional[ft.Icons] = None,
                               on_change: Optional[Callable] = None,
                               **kwargs) -> EnhancedTextField:
    """Create an enhanced text field with default settings"""
    return EnhancedTextField(label=label, icon=icon, on_change=on_change, **kwargs)

def create_enhanced_card(content: ft.Control,
                        elevation: int = 1,
                        **kwargs) -> EnhancedCard:
    """Create an enhanced card with default settings"""
    return EnhancedCard(content=content, elevation=elevation, **kwargs)

def create_progress_indicator(**kwargs) -> CircularProgressIndicator:
    """Create a progress indicator with default settings"""
    return CircularProgressIndicator(**kwargs)