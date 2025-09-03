
import flet as ft
from datetime import datetime, timedelta

# --- Mock Data ---
def get_mock_files():
    """Generates a list of mock files for UI development."""
    base_time = datetime.now()
    return [
        {"id": "1", "name": "report_final_v2.docx", "size": 1572864, "type": "docx", "owner": "user1", "modified": (base_time - timedelta(days=1)).isoformat(), "status": "Verified"},
        {"id": "2", "name": "project_data.xlsx", "size": 4823449, "type": "xlsx", "owner": "user2", "modified": (base_time - timedelta(hours=5)).isoformat(), "status": "Pending"},
        {"id": "3", "name": "logo_draft.png", "size": 891234, "type": "png", "owner": "user1", "modified": (base_time - timedelta(days=3)).isoformat(), "status": "Verified"},
        {"id": "4", "name": "main_script.py", "size": 12345, "type": "py", "owner": "user3", "modified": (base_time - timedelta(minutes=30)).isoformat(), "status": "Unverified"},
        {"id": "5", "name": "backup_archive.zip", "size": 254857600, "type": "zip", "owner": "user2", "modified": (base_time - timedelta(days=10)).isoformat(), "status": "Verified"},
        {"id": "6", "name": "notes.txt", "size": 512, "type": "txt", "owner": "user1", "modified": (base_time - timedelta(hours=1)).isoformat(), "status": "Verified"},
    ]

def format_size(size_bytes):
    """Formats size in bytes to a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/1024**2:.1f} MB"
    else:
        return f"{size_bytes/1024**3:.1f} GB"

def create_files_view():
    """
    Creates the 'Files' view with full functionality using simple, idiomatic Flet components.
    This version includes a preview pane, select-all, and status text.
    """
    mock_data = get_mock_files()

    # --- UI Components and Refs ---
    action_buttons = ft.Ref[ft.Row]()
    select_all_checkbox = ft.Ref[ft.Checkbox]()
    status_text = ft.Ref[ft.Text]()
    preview_container = ft.Ref[ft.Container]()

    def show_file_details(file_data):
        """Updates the preview pane with details of the selected file."""
        if not file_data:
            preview_container.current.content = ft.Column([
                ft.Icon(ft.icons.INFO_OUTLINE, size=40, color=ft.colors.BLUE_GREY_400),
                ft.Text("Select a file to see details", color=ft.colors.BLUE_GREY_400)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
        else:
            details_column = ft.Column(
                controls=[
                    ft.Text("File Details", style=ft.TextThemeStyle.HEADLINE_SMALL),
                    ft.Divider(),
                    ft.Text(f"Name: {file_data['name']}"),
                    ft.Text(f"Size: {format_size(file_data['size'])} ({file_data['size']} bytes)"),
                    ft.Text(f"Owner: {file_data['owner']}"),
                    ft.Text(f"Modified: {datetime.fromisoformat(file_data['modified']).strftime('%Y-%m-%d %H:%M:%S')}"),
                    ft.Text(f"Status: {file_data['status']}"),
                ],
                spacing=10
            )
            preview_container.current.content = details_column
        preview_container.current.update()

    files_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("File Name")),
            ft.DataColumn(ft.Text("Size"), numeric=True),
            ft.DataColumn(ft.Text("Type")),
            ft.DataColumn(ft.Text("Modified")),
            ft.DataColumn(ft.Text("Actions"), numeric=True), # For view button
        ],
        rows=[],
        expand=True,
    )

    # --- Functions and Handlers ---
    def update_ui_state(e=None):
        """Central function to update UI elements based on table selection."""
        selected_count = sum(1 for row in files_table.rows if row.selected)
        total_rows = len(files_table.rows)

        # Update bulk action buttons
        has_selection = selected_count > 0
        if action_buttons.current:
            for control in action_buttons.current.controls:
                control.disabled = not has_selection
            action_buttons.current.update()

        # Update 'Select All' checkbox state
        if select_all_checkbox.current:
            if selected_count == 0:
                select_all_checkbox.current.value = False
            elif selected_count == total_rows:
                select_all_checkbox.current.value = True
            else:
                select_all_checkbox.current.value = None  # Indeterminate state
            select_all_checkbox.current.update()

    def handle_select_all(e):
        """Selects or deselects all rows."""
        for row in files_table.rows:
            row.selected = e.control.value
        files_table.update()
        update_ui_state()

    def create_table_rows():
        """Creates ft.DataRow list from mock data."""
        rows = []
        for file_data in mock_data:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(file_data["name"])),
                        ft.DataCell(ft.Text(format_size(file_data["size"]))),
                        ft.DataCell(ft.Text(file_data["type"])),
                        ft.DataCell(ft.Text(datetime.fromisoformat(file_data["modified"]).strftime("%Y-%m-%d"))),
                        ft.DataCell(ft.IconButton(icon=ft.icons.VISIBILITY, icon_color=ft.colors.BLUE, on_click=lambda e, d=file_data: show_file_details(d))),
                    ],
                    selected=False,
                    on_select_changed=update_ui_state,
                    data=file_data # Attach data to row for easy access
                )
            )
        return rows

    files_table.rows = create_table_rows()

    # --- Main Layout ---
    main_content = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("File Management", style=ft.TextThemeStyle.HEADLINE_SMALL),
                    ft.Row(controls=[
                        ft.TextField(label="Search files...", prefix_icon=ft.Icons.SEARCH, expand=True, border_radius=8),
                        ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Refresh Files", on_click=lambda e: print("Refresh clicked!"))
                    ])
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(),
            ft.Row(
                controls=[
                    ft.Checkbox(ref=select_all_checkbox, label="Select All", on_change=handle_select_all),
                    ft.Row(ref=action_buttons, controls=[
                        ft.ElevatedButton("Download", icon=ft.Icons.DOWNLOAD, disabled=True, on_click=lambda e: print("Download clicked")),
                        ft.ElevatedButton("Verify", icon=ft.Icons.VERIFIED, disabled=True, on_click=lambda e: print("Verify clicked")),
                        ft.ElevatedButton("Delete", icon=ft.Icons.DELETE_SWEEP, disabled=True, on_click=lambda e: print("Delete clicked"), color=ft.colors.RED_700),
                    ])
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Text(ref=status_text, value=f"Showing {len(mock_data)} files"),
            files_table,
        ],
        expand=True,
        spacing=10
    )

    preview_pane = ft.Container(
        ref=preview_container,
        expand=1,
        padding=20,
        border=ft.border.all(1, ft.colors.BLUE_GREY_100),
        border_radius=8,
    )
    
    # Initialize the preview pane content
    show_file_details(None)

    return ft.Row(controls=[ft.Column([main_content], expand=3), ft.VerticalDivider(), preview_pane], expand=True)
