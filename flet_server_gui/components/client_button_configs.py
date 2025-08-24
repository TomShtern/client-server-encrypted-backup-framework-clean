    'client_view_details': ButtonConfig(
        text="View Details",
        icon=ft.Icons.INFO,
        tooltip="View detailed client information",
        action_class="ClientActions",
        action_method="get_client_details",
        confirmation_text="View details for client {item}?",
        success_message="Client details loaded",
        progress_message="Loading client details...",
        requires_selection=False,
        operation_type="single"
    ),
    
    'client_view_files': ButtonConfig(
        text="View Files",
        icon=ft.Icons.FOLDER,
        tooltip="View files uploaded by this client",
        action_class="ClientActions",
        action_method="get_client_files",
        confirmation_text="View files for client {item}?",
        success_message="Client files loaded",
        progress_message="Loading client files...",
        requires_selection=False,
        operation_type="single"
    ),