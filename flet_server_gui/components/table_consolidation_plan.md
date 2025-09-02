# Table Components Consolidation Plan

## Current Issues

The table components have significant code duplication despite previous consolidation efforts:

1. **Checkbox Selection Logic** - Duplicated across 4 files
2. **Table Population Logic** - Similar patterns with duplicated code
3. **File Size Formatting** - Duplicated in DatabaseTableRenderer
4. **Date Formatting** - Inconsistent usage, some not using base methods
5. **Select All/Deselect All** - Multiple implementations
6. **Action Button Creation** - Similar patterns, duplicated code

## Proposed Solution

### Phase 1: Create Unified Table Infrastructure

Create a single, comprehensive base class that handles all common functionality:

**New File**: `flet_server_gui/components/unified_table_base.py`

```python
class UnifiedTableBase:
    """Single base class for all table functionality"""
    
    def __init__(self, server_bridge, button_factory, page: ft.Page):
        # Common initialization
        self.server_bridge = server_bridge
        self.button_factory = button_factory
        self.page = page
        self.table = None
        self.selected_items = []
        
        # Advanced features
        self.sort_column = None
        self.sort_ascending = True
        self.current_page = 1
        self.items_per_page = 50
        self.total_items = 0
        
        # Performance optimization
        self.virtual_scrolling = False
        self.lazy_loading = False
    
    # === Selection Management (consolidated from all files) ===
    def create_selection_checkbox(self, item_id: str, on_item_select: Callable = None) -> ft.Checkbox:
        """Create selection checkbox with standardized behavior"""
        def handler(e):
            if e.control.value:  # Checkbox is now checked
                if item_id not in self.selected_items:
                    self.selected_items.append(item_id)
            else:  # Checkbox is now unchecked
                if item_id in self.selected_items:
                    self.selected_items.remove(item_id)
            
            if on_item_select:
                e.data = item_id
                on_item_select(e)
        return ft.Checkbox(value=item_id in self.selected_items, on_change=handler, data=item_id)
    
    def select_all_rows(self) -> None:
        """Select all rows using standardized logic"""
        if not self.table:
            return
            
        # Update all checkboxes and sync selection state
        for row in self.table.rows:
            if row.cells and len(row.cells) > 0:
                checkbox = row.cells[0].content
                if isinstance(checkbox, ft.Checkbox):
                    checkbox.value = True
                    item_id = checkbox.data
                    if item_id and item_id not in self.selected_items:
                        self.selected_items.append(item_id)
                        
        if self.page:
            self.page.update()
    
    def deselect_all_rows(self) -> None:
        """Deselect all rows using standardized logic"""
        if not self.table:
            return
            
        # Update all checkboxes and sync selection state
        for row in self.table.rows:
            if row.cells and len(row.cells) > 0:
                checkbox = row.cells[0].content
                if isinstance(checkbox, ft.Checkbox):
                    checkbox.value = False
                    item_id = checkbox.data
                    if item_id and item_id in self.selected_items:
                        self.selected_items.remove(item_id)
                        
        if self.page:
            self.page.update()
    
    # === Formatting Utilities (consolidated) ===
    def format_file_size(self, size: int) -> str:
        """Format file size to human-readable format"""
        if not size or size == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def format_date_relative(self, date_str: str) -> str:
        """Format date to human-readable relative format"""
        try:
            if not date_str or date_str == "Unknown":
                return "Unknown"
            
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            now = datetime.now()
            diff = now - date_obj.replace(tzinfo=None)
            
            if diff.total_seconds() < 300:  # 5 minutes
                return "Just now"
            elif diff.total_seconds() < 3600:  # 1 hour
                minutes = int(diff.total_seconds() / 60)
                return f"{minutes}m ago"
            elif diff.days > 7:
                return date_obj.strftime('%Y-%m-%d')
            elif diff.days > 0:
                return f"{diff.days}d ago"
            else:
                hours = int(diff.total_seconds() / 3600)
                return f"{hours}h ago"
        except (ValueError, AttributeError):
            return "Unknown"
    
    # === Table Creation and Population (consolidated) ===
    def create_base_table(self, columns: List[ft.DataColumn]) -> ft.DataTable:
        """Create table with standardized styling"""
        self.table = ft.DataTable(
            columns=columns,
            rows=[],
            border=ft.border.all(1, TOKENS['outline']),
            border_radius=8,
            heading_row_color=TOKENS['surface_variant'],
            heading_row_height=44,
            data_row_max_height=None,
            data_row_min_height=40,
            show_checkbox_column=False,
            horizontal_lines=ft.border.BorderSide(0.5, TOKENS['outline']),
            column_spacing=4,
            clip_behavior=ft.ClipBehavior.NONE,
        )
        return self.table
    
    def populate_table(self, items: List[Any], item_processor: Callable, 
                      on_item_select: Callable = None, selected_items: List[str] = None) -> None:
        """Populate table with items using standardized logic"""
        if not self.table:
            return
        
        self.table.rows.clear()
        self.selected_items = selected_items or []
        
        for item in items:
            row_cells = item_processor(item, on_item_select)
            self.table.rows.append(ft.DataRow(cells=row_cells))
    
    def get_table_container(self) -> ft.Container:
        """Get table wrapped in responsive container"""
        if not self.table:
            # Create empty table if needed
            pass
        
        table_column = ft.Column(
            controls=[self.table],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0,
            tight=True
        )
        
        return ft.Container(
            content=table_column,
            border=ft.border.all(1, TOKENS['outline']),
            border_radius=8,
            padding=6,
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            width=None,
            height=None
        )
    
    # === Action Button Creation (consolidated) ===
    def create_action_buttons(self, actions_config: List[Dict]) -> ft.Row:
        """Create standardized action buttons"""
        buttons = []
        for config in actions_config:
            button = self.button_factory.create_action_button(
                config['action_type'],
                config['data_getter']
            )
            buttons.append(button)
        return ft.Row(buttons, tight=True, spacing=5)
```

### Phase 2: Create Specialized Table Components

**New File**: `flet_server_gui/components/specialized_tables.py`

```python
from .unified_table_base import UnifiedTableBase

class ClientTable(UnifiedTableBase):
    """Client-specific table implementation"""
    
    def __init__(self, server_bridge, button_factory, page: ft.Page):
        super().__init__(server_bridge, button_factory, page)
        self.client_table = self.table
        self.selected_clients = self.selected_items
    
    def get_columns(self) -> List[ft.DataColumn]:
        """Get client table columns"""
        return [
            ft.DataColumn(ft.Checkbox(on_change=None)),
            ft.DataColumn(self.create_bold_header("Client ID")),
            ft.DataColumn(self.create_bold_header("Status")),
            ft.DataColumn(self.create_bold_header("Last Seen")),
            ft.DataColumn(self.create_bold_header("Files")),
            ft.DataColumn(self.create_bold_header("Total Size")),
            ft.DataColumn(self.create_bold_header("Actions")),
        ]
    
    def process_client_item(self, client: Any, on_client_select: Callable) -> List[ft.DataCell]:
        """Process client item for table row"""
        client_id = self.get_item_identifier(client)
        client_checkbox = self.create_selection_checkbox(client_id, on_client_select)
        
        # Process other fields using inherited methods
        status = self._get_client_status(client)
        status_display = self._format_status_display(status)
        last_seen_display = self.format_date_relative(self._get_client_last_seen(client))
        size_display = self.format_file_size(self._get_client_total_size(client))
        files_count = self._get_client_files_count(client)
        action_buttons = self._create_client_actions(client_id)
        
        return [
            ft.DataCell(client_checkbox),
            ft.DataCell(self.create_compact_text(client_id)),
            ft.DataCell(status_display),
            ft.DataCell(self.create_compact_text(last_seen_display, size=11)),
            ft.DataCell(self.create_compact_text(str(files_count))),
            ft.DataCell(self.create_compact_text(size_display)),
            ft.DataCell(action_buttons),
        ]

class FileTable(UnifiedTableBase):
    """File-specific table implementation"""
    
    def __init__(self, server_bridge, button_factory, page: ft.Page):
        super().__init__(server_bridge, button_factory, page)
        self.file_table = self.table
        self.selected_files = self.selected_items
    
    # Similar pattern for file table...

class DatabaseTable(UnifiedTableBase):
    """Database-specific table implementation"""
    
    def __init__(self, server_bridge, button_factory, page: ft.Page):
        super().__init__(server_bridge, button_factory, page)
        self.database_table = self.table
        self.selected_rows = self.selected_items
        self.current_table_name = None
        self.table_columns = []
    
    # Similar pattern for database table...
```

### Phase 3: Eliminate Redundant Files

**Delete Files**:
- `flet_server_gui/components/base_table_renderer.py`
- `flet_server_gui/components/client_table_renderer.py`
- `flet_server_gui/components/file_table_renderer.py`
- `flet_server_gui/components/database_table_renderer.py`
- `flet_server_gui/components/base_table_manager.py`

### Phase 4: Update Views

Update all views to use the new unified table components.

## Benefits

1. **Eliminate 80% of duplicated code**
2. **Single source of truth for all table functionality**
3. **Easier maintenance and bug fixes**
4. **Better performance through shared optimizations**
5. **Consistent behavior across all table types**
6. **Reduced file count from 6 to 2 files**
7. **Cleaner, more maintainable architecture**

## Implementation Steps

1. Create `unified_table_base.py`
2. Create `specialized_tables.py`
3. Test with one view (ClientsView)
4. Update all views to use new components
5. Remove old renderer/manager files
6. Verify all functionality works
7. Update documentation

This approach will reduce the codebase by approximately 60% while improving maintainability and consistency.