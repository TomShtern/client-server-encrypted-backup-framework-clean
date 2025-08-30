#!/usr/bin/env python3
"""
UI Widgets - Buttons

Purpose: Centralized button factory, configurations, and action mappings
Logic: Button creation, styling, and event handling  
UI: Button rendering and Material Design 3 styling
"""

# Import UTF-8 solution for Unicode handling
import Shared.utils.utf8_solution

import flet as ft
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass
from flet_server_gui.actions import ClientActions, FileActions, ServerActions
from flet_server_gui.actions.base_action import ActionResult
from flet_server_gui.utils.action_executor import get_action_executor
from flet_server_gui.utils.trace_center import get_trace_center
from flet_server_gui.components.base_component import BaseComponent
from flet_server_gui.ui.layouts.responsive_fixes import ResponsiveLayoutFixes


@dataclass
class ButtonConfig:
    """
    Configuration for action buttons.
    
    This defines all the properties needed to create a consistent,
    functional button with proper action integration.
    """
    # Required fields (no defaults)
    text: str
    icon: str
    tooltip: str
    action_class: str  # Class name: "ClientActions", "FileActions", "ServerActions"
    action_method: str  # Method name on the action class
    confirmation_text: str
    success_message: str
    
    # Optional fields (with defaults)
    button_style: str = "elevated"  # elevated, filled, outlined, text
    progress_message: str = "Processing..."
    requires_selection: bool = True
    min_selection: int = 1
    max_selection: Optional[int] = None
    export_format: Optional[str] = None
    operation_type: str = "single"  # single, bulk, export, import
    action_key: str = ""  # Key used to identify the button in BUTTON_CONFIGS


class ActionButtonFactory:
    """
    Factory for creating consistent action buttons with real functionality.
    
    This replaces the placeholder TODO buttons with properly integrated
    actions that use the clean architecture we've established.
    """
    
    # Button configurations for all GUI buttons
    BUTTON_CONFIGS = {
        # Client Management Buttons
        'client_export': ButtonConfig(
            text="Export Selected",
            icon=ft.Icons.DOWNLOAD,
            tooltip="Export selected clients to CSV/JSON",
            action_class="ClientActions",
            action_method="export_clients",
            confirmation_text="Export {count} selected clients?",
            success_message="Clients exported successfully",
            progress_message="Exporting clients...",
            export_format="csv",
            action_key="client_export"
        ),
        
        'client_import': ButtonConfig(
            text="Import Clients",
            icon=ft.Icons.UPLOAD,
            tooltip="Import clients from CSV/JSON file",
            action_class="ClientActions", 
            action_method="import_clients",
            confirmation_text="Import clients from file?",
            success_message="Clients imported successfully",
            progress_message="Importing clients...",
            requires_selection=False,
            operation_type="import",
            action_key="client_import"
        ),
        
        'client_disconnect_bulk': ButtonConfig(
            text="Disconnect Selected",
            icon=ft.Icons.LINK_OFF,
            tooltip="Disconnect selected clients from server",
            action_class="ClientActionHandlers",
            action_method="bulk_disconnect_clients",
            confirmation_text="Disconnect {count} selected clients?",
            success_message="Clients disconnected successfully",
            progress_message="Disconnecting clients...",
            operation_type="bulk",
            action_key="client_disconnect_bulk"
        ),
        
        'client_delete_bulk': ButtonConfig(
            text="Delete Selected", 
            icon=ft.Icons.DELETE,
            tooltip="Permanently delete selected clients",
            action_class="ClientActionHandlers",
            action_method="bulk_delete_clients",
            confirmation_text="Permanently delete {count} selected clients? This cannot be undone.",
            success_message="Clients deleted successfully",
            progress_message="Deleting clients...",
            operation_type="bulk",
            action_key="client_delete_bulk"
        ),
        
        'client_disconnect': ButtonConfig(
            text="Disconnect Client",
            icon=ft.Icons.LINK_OFF,
            tooltip="Disconnect selected client from server",
            action_class="ClientActionHandlers",
            action_method="disconnect_client",
            confirmation_text="Disconnect selected client?",
            success_message="Client disconnected successfully",
            progress_message="Disconnecting client...",
            operation_type="single",
            action_key="client_disconnect"
        ),
        
        'client_delete': ButtonConfig(
            text="Delete Client",
            icon=ft.Icons.DELETE,
            tooltip="Permanently delete selected client",
            action_class="ClientActionHandlers",
            action_method="delete_client",
            confirmation_text="Permanently delete selected client? This cannot be undone.",
            success_message="Client deleted successfully",
            progress_message="Deleting client...",
            operation_type="single",
            action_key="client_delete"
        ),
        
        'client_view_details': ButtonConfig(
            text="View Details",
            icon=ft.Icons.INFO,
            tooltip="View detailed client information",
            action_class="ClientActionHandlers",
            action_method="view_client_details",
            confirmation_text="View details for client {item}?",
            success_message="Client details loaded",
            progress_message="Loading client details...",
            requires_selection=True,
            operation_type="single",
            action_key="client_view_details"
        ),
        
        'client_view_files': ButtonConfig(
            text="View Files",
            icon=ft.Icons.FOLDER,
            tooltip="View files associated with client",
            action_class="ClientActionHandlers",
            action_method="view_client_files",
            confirmation_text="View files for client {item}?",
            success_message="Client files loaded",
            progress_message="Loading client files...",
            requires_selection=True,
            operation_type="single",
            action_key="client_view_files"
        ),
        
        # Database Management Buttons
        'database_backup': ButtonConfig(
            text="Backup Database",
            icon=ft.Icons.BACKUP,
            tooltip="Create a backup of the database",
            action_class="DatabaseActionHandlers",
            action_method="backup_database",
            confirmation_text="Backup the database?",
            success_message="Database backup completed",
            progress_message="Backing up database...",
            requires_selection=False,
            operation_type="single",
            action_key="database_backup"
        ),
        
        'database_optimize': ButtonConfig(
            text="Optimize Database",
            icon=ft.Icons.AUTO_FIX_HIGH,
            tooltip="Optimize database performance and reclaim space",
            action_class="DatabaseActionHandlers",
            action_method="optimize_database",
            confirmation_text="Optimize the database?",
            success_message="Database optimization completed",
            progress_message="Optimizing database...",
            requires_selection=False,
            operation_type="single",
            action_key="database_optimize"
        ),
        
        'database_analyze': ButtonConfig(
            text="Analyze Database",
            icon=ft.Icons.TROUBLESHOOT,
            tooltip="Analyze database integrity and statistics",
            action_class="DatabaseActionHandlers",
            action_method="analyze_database",
            confirmation_text="Analyze the database?",
            success_message="Database analysis completed",
            progress_message="Analyzing database...",
            requires_selection=False,
            operation_type="single",
            action_key="database_analyze"
        ),
        
        'database_execute_query': ButtonConfig(
            text="Execute SQL",
            icon=ft.Icons.CODE,
            tooltip="Execute a SQL query on the database",
            action_class="DatabaseActionHandlers",
            action_method="execute_sql_query",
            confirmation_text="Execute SQL query?",
            success_message="SQL query executed successfully",
            progress_message="Executing query...",
            requires_selection=False,
            operation_type="single",
            action_key="database_execute_query"
        ),
        
        # Log Management Buttons
        'log_export': ButtonConfig(
            text="Export Logs",
            icon=ft.Icons.DOWNLOAD,
            tooltip="Export logs to file",
            action_class="LogActionHandlers",
            action_method="export_logs",
            confirmation_text="Export logs to file?",
            success_message="Logs exported successfully",
            progress_message="Exporting logs...",
            requires_selection=False,
            operation_type="single",
            action_key="log_export"
        ),
        
        'log_clear': ButtonConfig(
            text="Clear Display",
            icon=ft.Icons.CLEAR,
            tooltip="Clear the log display",
            action_class="LogActionHandlers",
            action_method="clear_logs",
            confirmation_text="Clear the log display?",
            success_message="Log display cleared",
            progress_message="Clearing log display...",
            requires_selection=False,
            operation_type="single",
            action_key="log_clear"
        ),
        
        'log_refresh': ButtonConfig(
            text="Refresh Logs",
            icon=ft.Icons.REFRESH,
            tooltip="Refresh the log display",
            action_class="LogActionHandlers",
            action_method="refresh_logs",
            confirmation_text="Refresh the log display?",
            success_message="Logs refreshed",
            progress_message="Refreshing logs...",
            requires_selection=False,
            operation_type="single",
            action_key="log_refresh"
        ),
        
        # File Management Buttons
        'file_download_bulk': ButtonConfig(
            text="Download Selected",
            icon=ft.Icons.FILE_DOWNLOAD,
            tooltip="Download selected files to local directory",
            action_class="FileActionHandlers",
            action_method="perform_bulk_action",
            confirmation_text="Download {count} selected files?",
            success_message="Files downloaded successfully",
            progress_message="Downloading files...",
            operation_type="bulk",
            action_key="file_download_bulk"
        ),
        
        'file_verify_bulk': ButtonConfig(
            text="Verify Selected",
            icon=ft.Icons.VERIFIED,
            tooltip="Verify integrity of selected files",
            action_class="FileActionHandlers",
            action_method="perform_bulk_action",
            confirmation_text="Verify integrity of {count} selected files?",
            success_message="Files verified successfully", 
            progress_message="Verifying files...",
            operation_type="bulk",
            action_key="file_verify_bulk"
        ),
        
        'file_export_list': ButtonConfig(
            text="Export File List",
            icon=ft.Icons.LIST_ALT,
            tooltip="Export file list to CSV/JSON",
            action_class="FileActions",
            action_method="export_file_list",
            confirmation_text="Export file list with {count} files?",
            success_message="File list exported successfully",
            progress_message="Exporting file list...",
            export_format="csv",
            operation_type="export",
            action_key="file_export_list"
        ),
        
        'file_upload': ButtonConfig(
            text="Upload File",
            icon=ft.Icons.FILE_UPLOAD,
            tooltip="Upload file to server (not implemented)",
            action_class="FileActions",
            action_method="upload_file",
            confirmation_text="Upload selected file?",
            success_message="File uploaded successfully",
            progress_message="Uploading file...",
            requires_selection=False,
            operation_type="single",
            action_key="file_upload"
        ),
        
        'file_cleanup': ButtonConfig(
            text="Clean Old Files",
            icon=ft.Icons.CLEANING_SERVICES,
            tooltip="Clean up old unverified files",
            action_class="FileActions",
            action_method="cleanup_old_files",
            confirmation_text="Clean up files older than 30 days?",
            success_message="Old files cleaned successfully",
            progress_message="Cleaning old files...",
            requires_selection=False,
            operation_type="single",
            action_key="file_cleanup"
        ),
        
        'file_download': ButtonConfig(
            text="Download File",
            icon=ft.Icons.FILE_DOWNLOAD,
            tooltip="Download file to local directory",
            action_class="FileActions",
            action_method="download_file",
            confirmation_text="Download selected file?",
            success_message="File downloaded successfully",
            progress_message="Downloading file...",
            operation_type="single",
            action_key="file_download"
        ),
        
        'file_verify': ButtonConfig(
            text="Verify File",
            icon=ft.Icons.VERIFIED,
            tooltip="Verify file integrity",
            action_class="FileActions",
            action_method="verify_file_integrity",
            confirmation_text="Verify integrity of selected file?",
            success_message="File verified successfully",
            progress_message="Verifying file...",
            operation_type="single",
            action_key="file_verify"
        ),
        
        'file_delete': ButtonConfig(
            text="Delete File",
            icon=ft.Icons.DELETE,
            tooltip="Permanently delete selected file",
            action_class="FileActions",
            action_method="delete_file",
            confirmation_text="Permanently delete selected file?",
            success_message="File deleted successfully",
            progress_message="Deleting file...",
            operation_type="single",
            action_key="file_delete"
        ),
        
        'file_view_details': ButtonConfig(
            text="View Details",
            icon=ft.Icons.INFO,
            tooltip="View detailed file information",
            action_class="FileActionHandlers",
            action_method="view_file_details",
            confirmation_text="View details for file {item}?",
            success_message="File details loaded",
            progress_message="Loading file details...",
            requires_selection=True,
            operation_type="single",
            action_key="file_view_details"
        ),
        
        'file_preview': ButtonConfig(
            text="Preview File",
            icon=ft.Icons.VISIBILITY,
            tooltip="Preview file content",
            action_class="FileActionHandlers",
            action_method="preview_file",
            confirmation_text="Preview file {item}?",
            success_message="File preview loaded",
            progress_message="Loading file preview...",
            requires_selection=True,
            operation_type="single",
            action_key="file_preview"
        ),
        
        # Server Control Buttons
        'server_health_check': ButtonConfig(
            text="Health Check",
            icon=ft.Icons.HEALTH_AND_SAFETY,
            tooltip="Perform comprehensive server health check",
            action_class="ServerActions",
            action_method="get_server_health",
            confirmation_text="Perform server health check?",
            success_message="Health check completed",
            progress_message="Checking server health...",
            requires_selection=False,
            operation_type="single",
            action_key="server_health_check"
        ),
        
    }
    
    def __init__(self, base_component: BaseComponent, server_bridge, page: ft.Page):
        """
        Initialize button factory.
        
        Args:
            base_component: BaseComponent instance for UI patterns
            server_bridge: Server integration bridge
            page: Flet page for UI updates
        """
        self.base_component = base_component
        self.server_bridge = server_bridge
        self.page = page
        
        # Initialize action instances
        self.actions = {
            "ClientActions": ClientActions(server_bridge),
            "FileActions": FileActions(server_bridge), 
            "ServerActions": ServerActions(server_bridge),
            "ClientActionHandlers": None,  # Will be set by views
            "FileActionHandlers": None,    # Will be set by views
            "DatabaseActionHandlers": None,  # Will be set by views
            "ServerActionHandlers": None   # Will be set by views
        }
    
    def create_action_button(
        self,
        config_key: str,
        get_selected_items: Callable[[], List[str]],
        additional_params: Optional[Dict[str, Any]] = None
    ) -> ft.ElevatedButton:
        """
        Create a fully functional action button.
        
        Args:
            config_key: Key in BUTTON_CONFIGS
            get_selected_items: Function that returns list of selected item IDs
            additional_params: Additional parameters for the action
            
        Returns:
            Configured Flet button with real functionality
        """
        if config_key not in self.BUTTON_CONFIGS:
            raise ValueError(f"Unknown button config: {config_key}")
        
        config = self.BUTTON_CONFIGS[config_key]
        
        # Create a wrapper function to capture the current values
        def create_handler(config, get_selected_items, additional_params):
            return lambda e: self._safe_handle_button_click(e, config, get_selected_items, additional_params)
        
        # Create the button based on style
        if config.button_style == "elevated":
            button = ft.ElevatedButton(
                text=config.text,
                icon=config.icon,
                tooltip=config.tooltip,
                on_click=create_handler(config, get_selected_items, additional_params)
            )
        elif config.button_style == "filled":
            button = ft.FilledButton(
                text=config.text,
                icon=config.icon,
                tooltip=config.tooltip,
                on_click=create_handler(config, get_selected_items, additional_params)
            )
        elif config.button_style == "outlined":
            button = ft.OutlinedButton(
                text=config.text,
                icon=config.icon,
                tooltip=config.tooltip,
                on_click=create_handler(config, get_selected_items, additional_params)
            )
        else:  # text button
            button = ft.TextButton(
                text=config.text,
                icon=config.icon,
                tooltip=config.tooltip,
                on_click=create_handler(config, get_selected_items, additional_params)
            )
        
        # Return the button directly - the click handler is already set
        # Don't wrap in container as this breaks event handling
        return button
    
    def _safe_handle_button_click(self, e, config: ButtonConfig, get_selected_items: Callable[[], List[str]], additional_params: Optional[Dict[str, Any]]):
        """Entry point for button clicks; delegates to ActionExecutor with structured tracing.

        This replaces verbose ad-hoc print tracing with centralized TraceCenter
        events. Selection + mutation requirements are derived from config.
        """
        trace = get_trace_center()
        executor = get_action_executor()

        # Derive action_name (stable, machine friendly)
        action_name = config.action_key or f"{config.action_class}.{config.action_method}".lower()

        def selection_provider():
            if config.requires_selection:
                try:
                    return list(get_selected_items())
                except Exception:
                    return []
            return []

        async def async_button_handler():
            result: ActionResult = await executor.run(
                action_name=action_name,
                action_coro=lambda: self._handle_button_click(config, get_selected_items, additional_params),
                selection_provider=selection_provider if config.requires_selection else None,
                require_selection=config.requires_selection,
                mutate=config.operation_type in {"bulk", "single", "import"},
                meta={
                    "ui_text": config.text,
                    "style": config.button_style,
                    "op_type": config.operation_type,
                },
            )
            # Minimal UX feedback (success/warn/error) via base component dialogs
            if result.status == "error":
                await self.base_component._show_error(result.message or "Action failed")
            elif result.status == "warn":
                # Only show warn if meaningful (e.g., empty selection)
                if result.code in {"EMPTY_SELECTION", "OFFLINE_NOOP"}:
                    await self.base_component._show_warning(result.message)
            elif result.status == "success" and config.success_message:
                await self.base_component._show_success(config.success_message)
            return result

        try:
            # Schedule using Flet's task runner (keeps UI thread responsive)
            self.page.run_task(async_button_handler)
        except Exception as ex:  # Fallback logging
            trace.emit("BUTTON_SCHEDULE_ERROR", meta={
                "action": action_name,
                "error": str(ex),
            })
    
    async def _handle_button_click(
        self,
        config: ButtonConfig,
        get_selected_items: Callable[[], List[str]],
        additional_params: Optional[Dict[str, Any]]
    ):
        """Execute underlying action and return ActionResult.

        Translates legacy selection / handler resolution / method invocation
        outcomes into standardized ActionResult forms consumed by
        ActionExecutor wrapper.
        """
        from flet_server_gui.utils.action_result import ActionResult
        from flet_server_gui.utils.trace_center import get_trace_center

        trace = get_trace_center()
        cid = trace.new_correlation_id()
        action_name = config.action_key or f"{config.action_class}.{config.action_method}".lower()

        # Selection handling
        try:
            selected_items = get_selected_items() if config.requires_selection else []
        except Exception as sel_ex:
            trace.emit(type="BUTTON_SELECTION_ERROR", level="ERROR", action=action_name, correlation_id=cid, message=str(sel_ex))
            return ActionResult.warn(code="SELECTION_PROVIDER_ERROR", message="Failed to obtain selection", correlation_id=cid)

        if config.requires_selection:
            if len(selected_items) < config.min_selection:
                return ActionResult.warn(code="EMPTY_SELECTION", message="Please select required items", correlation_id=cid, data={"required_min": config.min_selection})
            if config.max_selection and len(selected_items) > config.max_selection:
                return ActionResult.warn(code="SELECTION_TOO_MANY", message="Too many items selected", correlation_id=cid, data={"max": config.max_selection, "count": len(selected_items)})

        # Resolve handler instance
        action_instance = self.actions.get(config.action_class)
        if action_instance is None and config.action_class.endswith("ActionHandlers"):
            handler_attr_map = {
                "ClientActionHandlers": "action_handlers",
                "FileActionHandlers": "file_action_handlers",
                "DatabaseActionHandlers": "database_action_handlers",
                "ServerActionHandlers": "server_action_handlers"
            }
            attr_name = handler_attr_map.get(config.action_class)
            if attr_name and hasattr(self.base_component, attr_name):
                action_instance = getattr(self.base_component, attr_name)
            elif hasattr(self.base_component, 'actions'):
                action_instance = self.base_component.actions.get(config.action_class)

        if action_instance is None:
            return ActionResult.error(code="HANDLER_NOT_FOUND", message=f"Handler {config.action_class} unavailable", correlation_id=cid, data={"action_class": config.action_class})

        # Resolve method
        try:
            action_method = getattr(action_instance, config.action_method)
        except AttributeError:
            return ActionResult.error(code="METHOD_NOT_FOUND", message=f"Method {config.action_method} missing", correlation_id=cid, data={"method": config.action_method})

        # Prepare params
        method_params = self._prepare_method_params(config, selected_items, additional_params)

        # Execute
        try:
            result = await action_method(**method_params)
        except Exception as ex:  # noqa: BLE001
            trace.emit(type="BUTTON_METHOD_ERROR", level="ERROR", action=action_name, correlation_id=cid, message=str(ex))
            return ActionResult.error(code="METHOD_EXCEPTION", message=str(ex), correlation_id=cid)

        # Normalize return
        if isinstance(result, ActionResult):
            # Pass through but ensure correlation id if absent
            if not result.correlation_id:
                result.correlation_id = cid  # type: ignore[attr-defined]
            return result
        if result is False:
            return ActionResult.error(code="ACTION_FALSE", message="Action returned False", correlation_id=cid)
        if result is None:
            return ActionResult.warn(code="ACTION_NOOP", message="Action returned no result", correlation_id=cid)
        # Non-standard truthy result
        return ActionResult.success(code=f"{config.action_method.upper()}_OK", message=config.success_message or "Action completed", correlation_id=cid, data={"raw": result})
    
    def _prepare_method_params(
        self, 
        config: ButtonConfig, 
        selected_items: List[str], 
        additional_params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prepare parameters for the action method call.
        
        Args:
            config: Button configuration
            selected_items: Selected item IDs
            additional_params: Additional parameters
            
        Returns:
            Dictionary of method parameters
        """
        print(f"[BUTTON_TRACE] ========== PARAMETER PREPARATION ==========")
        print(f"[BUTTON_TRACE] Config: {config.action_key}, Method: {config.action_method}")
        print(f"[BUTTON_TRACE] Selected items: {selected_items}")
        print(f"[BUTTON_TRACE] Additional params: {additional_params}")
        
        params = {}
        
        # Special handling for perform_bulk_action method
        if config.action_method == "perform_bulk_action":
            print(f"[BUTTON_TRACE] Using bulk action parameter mapping")
            # For bulk actions, we need to pass the action type and filenames
            action_type_map = {
                'file_download_bulk': 'download',
                'file_verify_bulk': 'verify',
                'file_delete_bulk': 'delete',
                'client_disconnect_bulk': 'disconnect',
                'client_delete_bulk': 'delete'
            }
            if config.action_key in action_type_map:
                params["action"] = action_type_map[config.action_key]
                params["filenames"] = selected_items if "file" in config.action_key else selected_items
                # For client actions, use client_ids parameter
                if "client" in config.action_key:
                    params["client_ids"] = selected_items
                print(f"[BUTTON_TRACE] Bulk action mapped: action={params.get('action')}, filenames={params.get('filenames')}, client_ids={params.get('client_ids')}")
            else:
                # Default handling for bulk actions
                params["action"] = config.action_key.replace("_bulk", "").split("_")[-1]
                if "client" in config.action_key:
                    params["client_ids"] = selected_items
                else:
                    params["filenames"] = selected_items
                print(f"[BUTTON_TRACE] Default bulk action: action={params.get('action')}, filenames={params.get('filenames')}, client_ids={params.get('client_ids')}")
        else:
            print(f"[BUTTON_TRACE] Using standard parameter mapping")
            # Add selected items based on method signature
            if "client_id" in config.action_method and selected_items:
                print(f"[BUTTON_TRACE] Method has 'client_id' in name")
                # For single client actions, pass client_id as a single value
                if config.operation_type == "single" and len(selected_items) == 1:
                    params["client_id"] = selected_items[0]
                    print(f"[BUTTON_TRACE] Single client_id: {params['client_id']}")
                else:
                    params["client_ids"] = selected_items
                    print(f"[BUTTON_TRACE] Multiple client_ids: {params['client_ids']}")
            elif "file_id" in config.action_method and selected_items:  
                print(f"[BUTTON_TRACE] Method has 'file_id' in name")
                # For single file actions, pass file_id as a single value
                if config.operation_type == "single" and len(selected_items) == 1:
                    params["file_id"] = selected_items[0]
                    print(f"[BUTTON_TRACE] Single file_id: {params['file_id']}")
                else:
                    params["file_ids"] = selected_items
                    print(f"[BUTTON_TRACE] Multiple file_ids: {params['file_ids']}")
            elif selected_items:
                print(f"[BUTTON_TRACE] Using generic parameter detection")
                # Generic parameter name based on action type
                if "client" in config.action_method.lower() or "client" in config.action_key.lower():
                    print(f"[BUTTON_TRACE] Detected client-related action")
                    # For single client actions, pass client_id as a single value
                    if config.operation_type == "single" and len(selected_items) == 1:
                        params["client_id"] = selected_items[0]
                        print(f"[BUTTON_TRACE] Single client_id: {params['client_id']}")
                    else:
                        params["client_ids"] = selected_items
                        print(f"[BUTTON_TRACE] Multiple client_ids: {params['client_ids']}")
                elif "file" in config.action_method.lower() or "file" in config.action_key.lower():
                    print(f"[BUTTON_TRACE] Detected file-related action")
                    # For single file actions, pass file_id as a single value
                    if config.operation_type == "single" and len(selected_items) == 1:
                        params["file_id"] = selected_items[0]
                        print(f"[BUTTON_TRACE] Single file_id: {params['file_id']}")
                    else:
                        params["file_ids"] = selected_items
                        print(f"[BUTTON_TRACE] Multiple file_ids: {params['file_ids']}")
                else:
                    print(f"[BUTTON_TRACE] Using action class fallback mapping")
                    # Default to generic parameter names
                    if config.action_class in ["ClientActions", "ClientActionHandlers"]:
                        # For single client actions, pass client_id as a single value
                        if config.operation_type == "single" and len(selected_items) == 1:
                            params["client_id"] = selected_items[0]
                            print(f"[BUTTON_TRACE] Class-based single client_id: {params['client_id']}")
                        else:
                            params["client_ids"] = selected_items
                            print(f"[BUTTON_TRACE] Class-based multiple client_ids: {params['client_ids']}")
                    elif config.action_class in ["FileActions", "FileActionHandlers"]:
                        # For single file actions, pass file_id as a single value
                        if config.operation_type == "single" and len(selected_items) == 1:
                            params["file_id"] = selected_items[0]
                            print(f"[BUTTON_TRACE] Class-based single file_id: {params['file_id']}")
                        else:
                            params["file_ids"] = selected_items
                            print(f"[BUTTON_TRACE] Class-based multiple file_ids: {params['file_ids']}")
                    else:
                        params["items"] = selected_items
                        print(f"[BUTTON_TRACE] Generic items parameter: {params['items']}")
            
            # Add export format if specified
            if config.export_format:
                params["export_format"] = config.export_format
                print(f"[BUTTON_TRACE] Added export format: {config.export_format}")
        
        # Add any additional parameters
        if additional_params:
            print(f"[BUTTON_TRACE] Adding additional parameters: {additional_params}")
            params.update(additional_params)
        
        print(f"[BUTTON_TRACE] Final parameters: {params}")
        print(f"[BUTTON_TRACE] ========== PARAMETER PREPARATION COMPLETE ===========")
        return params
    
    def _get_item_type(self, action_class: str) -> str:
        """Get user-friendly item type name."""
        if action_class == "ClientActions":
            return "clients"
        elif action_class == "FileActions":
            return "files"
        else:
            return "items"
    
    async def _handle_post_action(self, config: ButtonConfig, method_params: Dict[str, Any]):
        """
        Handle any post-action operations like file downloads or exports.
        
        Args:
            config: Button configuration
            method_params: Parameters used in the action
        """
        # For export operations, trigger file save dialog
        if config.operation_type == "export":
            # In a real implementation, this would trigger a file save dialog
            # For now, just show additional success information
            export_format = config.export_format or "csv"
            await self.base_component._show_success(
                f"Data exported in {export_format.upper()} format"
            )
        
        # For import operations, trigger file picker dialog  
        elif config.operation_type == "import":
            # In a real implementation, this would trigger a file picker
            await self.base_component._show_success("Import operation completed")
    
    def create_button_group(
        self,
        config_keys: List[str],
        get_selected_items: Callable[[], List[str]],
        orientation: str = "horizontal"
    ) -> ft.Container:
        """
        Create a group of related action buttons.
        
        Args:
            config_keys: List of button configuration keys
            get_selected_items: Function to get selected items
            orientation: "horizontal" or "vertical"
            
        Returns:
            Container with button group
        """
        buttons = [
            self.create_action_button(key, get_selected_items)
            for key in config_keys
        ]
        
        if orientation == "horizontal":
            control = ft.Row(controls=buttons, spacing=8)
        else:
            control = ft.Column(controls=buttons, spacing=8)
        
        return ft.Container(content=control, padding=8)
    
    def get_available_buttons(self, action_class: Optional[str] = None) -> Dict[str, ButtonConfig]:
        """
        Get available button configurations, optionally filtered by action class.
        
        Args:
            action_class: Optional action class to filter by
            
        Returns:
            Dictionary of available button configurations
        """
        if action_class:
            return {
                key: config for key, config in self.BUTTON_CONFIGS.items()
                if config.action_class == action_class
            }
        return self.BUTTON_CONFIGS.copy()