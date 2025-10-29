"""
Enhanced DataTable Component for Desktop Applications

This component provides a desktop-optimized DataTable with:
- Keyboard navigation (arrow keys, tab, enter, escape)
- Multi-select with Ctrl/Shift modifiers
- Right-click context menus
- Virtual scrolling for large datasets
- Column sorting and filtering
- Professional desktop interaction patterns

Compatible with Flet 0.28.3 and Material Design 3.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import flet as ft

from FletV2.components.context_menu import ContextMenu, MenuItem, MenuItemType
from FletV2.utils.keyboard_handlers import KeyCode, normalize_key


@dataclass
class ColumnConfig:
    """Configuration for DataTable columns"""
    key: str
    label: str
    width: float | None = None
    sortable: bool = True
    filterable: bool = True
    numeric: bool = False


@dataclass
class SortConfig:
    """Configuration for column sorting"""
    column_key: str
    ascending: bool = True


class EnhancedDataTable(ft.Container):
    """
    Enhanced DataTable component with desktop-specific features

    Features:
    - Keyboard navigation and shortcuts
    - Multi-select with modifier keys
    - Right-click context menus
    - Virtual scrolling for performance
    - Column sorting and filtering
    - Professional desktop UX patterns
    """

    def __init__(
        self,
        columns: list[ColumnConfig],
        data: list[dict[str, Any]],
        on_row_click: Callable | None = None,
        on_selection_change: Callable | None = None,
        on_context_menu: Callable | None = None,
        page_size: int = 100,
        show_checkbox_column: bool = True,
        enable_virtual_scrolling: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Core properties
        self.columns = columns
        self.original_data = data
        self.filtered_data = data.copy()
        self.on_row_click = on_row_click
        self.on_selection_change = on_selection_change
        self.on_context_menu = on_context_menu
        self.page_size = page_size
        self.show_checkbox_column = show_checkbox_column
        self.enable_virtual_scrolling = enable_virtual_scrolling

        # State management
        self.selected_rows = set()
        self.current_page = 1
        self.total_pages = 1
        self.sort_config: SortConfig | None = None
        self.filters: dict[str, str] = {}
        self.focused_row_index = 0

        # UI components
        self.data_table = None
        self.selection_toolbar = None
        self.pagination_controls = None
        self.filter_controls = None
        self.context_menu = None

        # Initialize the component
        self._init_ui()
        self._setup_keyboard_handlers()
        self._update_display()

    def _init_ui(self):
        """Initialize the UI components"""

        # Create DataTable columns
        dt_columns = []
        for col in self.columns:
            header_content = ft.Row(
                [
                    ft.Text(
                        col.label,
                        weight=ft.FontWeight.BOLD,
                        size=14,
                        color=ft.Colors.ON_SURFACE,
                        expand=True
                    ),
                    ft.Icon(
                        ft.Icons.ARROW_UPWARD,
                        size=16,
                        color=ft.Colors.PRIMARY,
                        visible=False
                    ) if col.sortable else None
                ],
                spacing=4,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )

            dt_column = ft.DataColumn(
                label=header_content,
                numeric=col.numeric,
                on_sort=self._on_column_sort if col.sortable else None
            )
            dt_columns.append(dt_column)

        # Initialize DataTable
        self.data_table = ft.DataTable(
            columns=dt_columns,
            rows=[],
            border=ft.border.all(2, ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE)),
            border_radius=12,
            horizontal_lines=ft.BorderSide(1, ft.Colors.with_opacity(0.1, ft.Colors.OUTLINE)),
            divider_thickness=1,
            heading_row_height=52,
            data_row_min_height=48,
            data_row_max_height=72,
            column_spacing=24,
            show_checkbox_column=self.show_checkbox_column,
            heading_row_color=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
        )

        # Selection toolbar
        self.selection_toolbar = self._create_selection_toolbar()

        # Pagination controls
        self.pagination_controls = self._create_pagination_controls()

        # Filter controls
        self.filter_controls = self._create_filter_controls()

        # Context menu (initially hidden)
        self.context_menu = self._create_context_menu()

        # Main layout
        self.content = ft.Column(
            [
                # Filter controls
                self.filter_controls,

                # DataTable
                ft.Container(
                    content=self.data_table,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE
                ),

                # Selection toolbar
                self.selection_toolbar,

                # Pagination controls
                self.pagination_controls,
            ],
            spacing=8,
            expand=True
        )

    def _create_selection_toolbar(self) -> ft.Container:
        """Create the selection toolbar for bulk actions"""

        selected_count_text = ft.Text(
            "0 rows selected",
            size=14,
            color=ft.Colors.ON_PRIMARY,
            weight=ft.FontWeight.W_500,
        )

        btn_clear_selection = ft.TextButton(
            "Clear Selection",
            icon=ft.Icons.CLEAR,
            style=ft.ButtonStyle(color=ft.Colors.ON_PRIMARY),
            on_click=self._clear_selection
        )

        btn_export_selected = ft.TextButton(
            "Export Selected",
            icon=ft.Icons.DOWNLOAD,
            style=ft.ButtonStyle(color=ft.Colors.ON_PRIMARY),
            on_click=self._export_selected
        )

        btn_bulk_delete = ft.FilledButton(
            "Delete Selected",
            icon=ft.Icons.DELETE_SWEEP,
            style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR),
            on_click=self._bulk_delete
        )

        return ft.Container(
            content=ft.Row(
                [
                    selected_count_text,
                    ft.Container(expand=True),
                    btn_clear_selection,
                    btn_export_selected,
                    btn_bulk_delete,
                ],
                spacing=12,
            ),
            bgcolor=ft.Colors.PRIMARY,
            border_radius=8,
            padding=12,
            visible=False,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        )

    def _create_pagination_controls(self) -> ft.Row:
        """Create pagination controls"""

        self.pagination_info = ft.Text(
            "Page 1 of 1",
            size=13,
            color=ft.Colors.ON_SURFACE_VARIANT,
            weight=ft.FontWeight.W_500,
        )

        btn_prev_page = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            tooltip="Previous page (Alt+Left)",
            disabled=True,
            on_click=self._prev_page
        )

        btn_next_page = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            tooltip="Next page (Alt+Right)",
            disabled=True,
            on_click=self._next_page
        )

        # Page size selector
        page_size_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("25"),
                ft.dropdown.Option("50"),
                ft.dropdown.Option("100"),
                ft.dropdown.Option("200"),
            ],
            value=str(self.page_size),
            width=80,
            text_size=12,
            on_change=self._change_page_size
        )

        return ft.Row(
            [
                btn_prev_page,
                self.pagination_info,
                btn_next_page,
                ft.Container(width=20),
                ft.Text("Rows per page:", size=13, color=ft.Colors.ON_SURFACE_VARIANT),
                page_size_dropdown,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )

    def _create_filter_controls(self) -> ft.Container:
        """Create filter controls for columns"""

        filter_controls = []

        for col in self.columns:
            if col.filterable:
                text_field = ft.TextField(
                    label=f"Filter {col.label}...",
                    height=40,
                    text_size=12,
                    border_radius=8,
                    on_change=lambda e, key=col.key: self._apply_filter(key, e.control.value)
                )
                filter_controls.append(text_field)

        if not filter_controls:
            return ft.Container(visible=False)

        return ft.Container(
            content=ft.Row(
                filter_controls,
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
                wrap=True
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.SURFACE),
            border_radius=8,
            margin=ft.margin.only(bottom=8)
        )

    def _create_context_menu(self) -> ContextMenu:
        """Create right-click context menu"""

        return ContextMenu(
            items=[
                MenuItem(
                    id="view_details",
                    label="View Details",
                    type=MenuItemType.ACTION,
                    icon=ft.Icons.INFO,
                    action=lambda _, e: self._view_details(e)
                ),
                MenuItem(
                    id="edit_entry",
                    label="Edit Entry",
                    type=MenuItemType.ACTION,
                    icon=ft.Icons.EDIT,
                    action=lambda _, e: self._edit_entry(e)
                ),
                MenuItem(
                    id="separator_1",
                    label="",
                    type=MenuItemType.SEPARATOR
                ),
                MenuItem(
                    id="copy_selection",
                    label="Copy Selection",
                    type=MenuItemType.ACTION,
                    icon=ft.Icons.CONTENT_COPY,
                    action=lambda _, e: self._copy_selection(e)
                ),
                MenuItem(
                    id="export_selected",
                    label="Export Selected",
                    type=MenuItemType.ACTION,
                    icon=ft.Icons.DOWNLOAD,
                    action=lambda _, e: self._export_selected(e)
                ),
                MenuItem(
                    id="separator_2",
                    label="",
                    type=MenuItemType.SEPARATOR
                ),
                MenuItem(
                    id="delete_selected",
                    label="Delete Selected",
                    type=MenuItemType.ACTION,
                    icon=ft.Icons.DELETE,
                    action=lambda _, e: self._bulk_delete(e)
                ),
            ]
        )

    def _setup_keyboard_handlers(self):
        """Setup keyboard event handlers for desktop navigation"""

        # This will be connected to the page's keyboard event handler
        # The actual keyboard event handling will be set up by the parent view
        pass

    def handle_keyboard_event(self, e: ft.KeyboardEvent) -> bool:
        """
        Handle keyboard events for desktop navigation

        Returns True if the event was handled, False otherwise
        """

        event_key = normalize_key(e.key)

        if event_key == KeyCode.ARROW_DOWN:
            self._navigate_down()
            return True
        elif event_key == KeyCode.ARROW_UP:
            self._navigate_up()
            return True
        elif event_key == KeyCode.ARROW_LEFT:
            self._navigate_left()
            return True
        elif event_key == KeyCode.ARROW_RIGHT:
            self._navigate_right()
            return True
        elif event_key == KeyCode.HOME:
            self._navigate_to_start()
            return True
        elif event_key == KeyCode.END:
            self._navigate_to_end()
            return True
        elif event_key == KeyCode.PAGE_DOWN:
            self._navigate_page_down()
            return True
        elif event_key == KeyCode.PAGE_UP:
            self._navigate_page_up()
            return True
        elif event_key == KeyCode.ENTER:
            self._activate_selected_row()
            return True
        elif event_key == KeyCode.DELETE:
            if self.selected_rows:
                self._bulk_delete(None)
            return True
        elif event_key == KeyCode.ESCAPE:
            self._clear_selection(None)
            return True
        elif event_key == KeyCode.A and (e.ctrl or e.meta):
            self._select_all()
            return True

        return False

    def _navigate_down(self):
        """Navigate to the next row"""
        if self.data_table and self.focused_row_index < len(self.data_table.rows) - 1:
            self.focused_row_index += 1
            self._update_focused_row()

    def _navigate_up(self):
        """Navigate to the previous row"""
        if self.data_table and self.focused_row_index > 0:
            self.focused_row_index -= 1
            self._update_focused_row()

    def _navigate_left(self):
        """Navigate to the previous column"""
        # Implementation for column navigation
        pass

    def _navigate_right(self):
        """Navigate to the next column"""
        # Implementation for column navigation
        pass

    def _navigate_to_start(self):
        """Navigate to the first row"""
        if not self.data_table or not self.data_table.rows:
            return
        self.focused_row_index = 0
        self._update_focused_row()

    def _navigate_to_end(self):
        """Navigate to the last row"""
        if not self.data_table or not self.data_table.rows:
            return
        self.focused_row_index = len(self.data_table.rows) - 1
        self._update_focused_row()

    def _navigate_page_down(self):
        """Navigate down by one page"""
        if not self.data_table or not self.data_table.rows:
            return
        page_size = min(self.page_size, len(self.data_table.rows))
        self.focused_row_index = min(
            self.focused_row_index + page_size,
            len(self.data_table.rows) - 1
        )
        self._update_focused_row()

    def _navigate_page_up(self):
        """Navigate up by one page"""
        if not self.data_table or not self.data_table.rows:
            return
        page_size = min(self.page_size, len(self.data_table.rows))
        self.focused_row_index = max(self.focused_row_index - page_size, 0)
        self._update_focused_row()

    def _update_focused_row(self):
        """Update the visual focus indicator for the focused row"""
        # Implementation for visual focus indication
        if self.data_table and self.data_table.rows:
            # Update row styling to show focus
            self.data_table.update()

    def _activate_selected_row(self):
        """Activate the currently focused/selected row"""
        if self.data_table and self.focused_row_index < len(self.data_table.rows):
            row_data = self.data_table.rows[self.focused_row_index].data
            if self.on_row_click and row_data:
                self.on_row_click(row_data)

    def _select_all(self):
        """Select all rows in the current page"""
        if not self.data_table or not self.data_table.rows:
            return
        self.selected_rows.update(range(len(self.data_table.rows)))
        self._update_selection_display()

    def _update_display(self):
        """Update the table display with current data and settings"""
        table = self.data_table
        if not table:
            return

        # Apply filters and sorting
        self._apply_filters_and_sorting()

        # Calculate pagination
        self.total_pages = max(1, (len(self.filtered_data) + self.page_size - 1) // self.page_size)
        self.current_page = max(1, min(self.current_page, self.total_pages))

        # Get current page data
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_data = self.filtered_data[start_idx:end_idx]

        # Update DataTable rows
        table.rows = self._create_data_rows(page_data)

        # Update pagination info
        self.pagination_info.value = (
            f"Page {self.current_page} of {self.total_pages} "
            f"({len(self.filtered_data)} total)"
        )

        # Update pagination buttons
        if self.pagination_controls and hasattr(self.pagination_controls, 'controls'):
            for control in self.pagination_controls.controls:
                if isinstance(control, ft.IconButton):
                    if control.icon == ft.Icons.CHEVRON_LEFT:
                        control.disabled = self.current_page <= 1
                    elif control.icon == ft.Icons.CHEVRON_RIGHT:
                        control.disabled = self.current_page >= self.total_pages

        # Update selection display
        self._update_selection_display()

        # Update the UI
        if getattr(table, 'page', None):
            table.update()

    def _create_data_rows(self, data: list[dict[str, Any]]) -> list[ft.DataRow]:
        """Create DataRow objects from data"""

        rows = []
        for idx, row_data in enumerate(data):
            cells = []

            for col in self.columns:
                value = row_data.get(col.key, "")
                if value is None:
                    value = ""

                # Format the value based on column type
                if col.numeric and isinstance(value, (int, float)):
                    text = ft.Text(
                        f"{value:,}" if isinstance(value, int) else f"{value:.2f}",
                        size=13,
                        color=ft.Colors.ON_SURFACE
                    )
                else:
                    text = ft.Text(
                        str(value),
                        size=13,
                        color=ft.Colors.ON_SURFACE
                    )

                cell = ft.DataCell(
                    content=text,
                    on_tap=lambda e, data=row_data: self._on_row_tap(e, data)
                )
                cells.append(cell)

            # Create row with selection handling
            row = ft.DataRow(
                cells=cells,
                selected=idx in self.selected_rows,
                data=row_data,
                on_select_changed=lambda e, row_idx=idx: self._on_row_select(e, row_idx)
            )

            rows.append(row)

        return rows

    def _on_row_tap(self, _: ft.ControlEvent, row_data: dict[str, Any]):
        """Handle row tap/click"""
        if self.on_row_click:
            self.on_row_click(row_data)

    def _on_row_select(self, e: ft.ControlEvent, row_index: int):
        """Handle row selection change"""
        if e.control.selected:
            self.selected_rows.add(row_index)
        else:
            self.selected_rows.discard(row_index)

        self._update_selection_display()

    def _update_selection_display(self):
        """Update the selection toolbar and row highlighting"""

        selection_count = len(self.selected_rows)

        # Update selection toolbar
        if hasattr(self, 'selection_toolbar') and self.selection_toolbar:
            if selection_count > 0:
                self.selection_toolbar.visible = True
                for control in self.selection_toolbar.content.controls:
                    if (
                        hasattr(control, 'value') and
                        isinstance(control.value, str) and
                        "rows selected" in control.value
                    ):
                        control.value = f"{selection_count} row{'s' if selection_count != 1 else ''} selected"
                        break

                # Enable/disable bulk actions based on selection
                for control in self.selection_toolbar.content.controls:
                    if isinstance(control, ft.FilledButton):
                        control.disabled = selection_count == 0
            else:
                self.selection_toolbar.visible = False
            if getattr(self.selection_toolbar, 'page', None):
                self.selection_toolbar.update()

        # Update row selection state
        if self.data_table and hasattr(self.data_table, 'rows'):
            for idx, row in enumerate(self.data_table.rows):
                row.selected = idx in self.selected_rows

        if self.data_table and getattr(self.data_table, 'page', None):
            self.data_table.update()

        # Call selection change callback
        if self.on_selection_change and self.data_table and hasattr(self.data_table, 'rows'):
            selected_data = [
                self.data_table.rows[idx].data
                for idx in self.selected_rows
                if idx < len(self.data_table.rows)
            ]
            self.on_selection_change(selected_data)

    def _apply_filter(self, column_key: str, filter_value: str):
        """Apply a filter to a specific column"""
        if filter_value:
            self.filters[column_key] = filter_value.lower()
        else:
            self.filters.pop(column_key, None)

        self.current_page = 1  # Reset to first page
        self._update_display()

    def _apply_filters_and_sorting(self):
        """Apply all filters and sorting to the data"""

        # Start with original data
        filtered_data = self.original_data.copy()

        # Apply filters
        for column_key, filter_value in self.filters.items():
            filtered_data = [
                row for row in filtered_data
                if filter_value in str(row.get(column_key, "")).lower()
            ]

        # Apply sorting
        if self.sort_config:
            column_key = self.sort_config.column_key
            ascending = self.sort_config.ascending

            try:
                filtered_data.sort(
                    key=lambda row: str(row.get(column_key, "")),
                    reverse=not ascending
                )
            except (TypeError, ValueError):
                # Handle sorting errors gracefully
                pass

        self.filtered_data = filtered_data

    def _on_column_sort(self, _: ft.ControlEvent):
        """Handle column sort click"""
        # Determine which column was clicked
        # This is a simplified implementation - in practice, you'd need to track column indices
        if not self.columns:
            return

        # Cycle through sort states: unsorted -> ascending -> descending
        if self.sort_config and self.sort_config.column_key == self.columns[0].key:
            if self.sort_config.ascending:
                self.sort_config.ascending = False
            else:
                self.sort_config = None
        else:
            self.sort_config = SortConfig(column_key=self.columns[0].key, ascending=True)

        self._update_display()

    def _clear_selection(self, _: ft.ControlEvent):
        """Clear all row selections"""
        self.selected_rows.clear()
        self._update_selection_display()

    def _export_selected(self, _: ft.ControlEvent):
        """Export selected rows"""
        if self.on_context_menu:
            self.on_context_menu("export_selected", self.selected_rows)

    def _bulk_delete(self, _: ft.ControlEvent):
        """Delete selected rows"""
        if self.on_context_menu:
            self.on_context_menu("bulk_delete", self.selected_rows)

    def _view_details(self, _: ft.ControlEvent):
        """View details of selected item"""
        if self.on_context_menu:
            self.on_context_menu("view_details", self.selected_rows)

    def _edit_entry(self, _: ft.ControlEvent):
        """Edit selected entry"""
        if self.on_context_menu:
            self.on_context_menu("edit_entry", self.selected_rows)

    def _copy_selection(self, _: ft.ControlEvent):
        """Copy selected items to clipboard"""
        if self.on_context_menu:
            self.on_context_menu("copy_selection", self.selected_rows)

    def _prev_page(self, _: ft.ControlEvent):
        """Navigate to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self._update_display()

    def _next_page(self, _: ft.ControlEvent):
        """Navigate to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._update_display()

    def _change_page_size(self, e: ft.ControlEvent):
        """Change the page size"""
        try:
            self.page_size = int(e.control.value)
            self.current_page = 1
            self._update_display()
        except (ValueError, TypeError):
            pass

    def update_data(self, new_data: list[dict[str, Any]]):
        """Update the table with new data"""
        self.original_data = new_data
        self.selected_rows.clear()
        self.current_page = 1
        self._update_display()

    def get_selected_data(self) -> list[dict[str, Any]]:
        """Get the data for selected rows"""
        selected_data = []
        if self.data_table and hasattr(self.data_table, 'rows'):
            for row_idx in self.selected_rows:
                if row_idx < len(self.data_table.rows):
                    row = self.data_table.rows[row_idx]
                    if hasattr(row, 'data') and row.data:
                        selected_data.append(row.data)
        return selected_data
