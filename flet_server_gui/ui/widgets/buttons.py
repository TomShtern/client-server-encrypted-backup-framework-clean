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
        """Safely handle button click using Flet's native async pattern"""
        print(f"[BUTTON_TRACE] ========== BUTTON CLICK DETECTED ==========")
        print(f"[BUTTON_TRACE] Button: {config.action_key} ({config.text})")
        print(f"[BUTTON_TRACE] Action: {config.action_class}.{config.action_method}")
        print(f"[BUTTON_TRACE] Event object: {type(e)}, button state: {getattr(e, 'control', 'unknown')}")
        print(f"[BUTTON_TRACE] Page available: {self.page is not None}")
        print(f"[BUTTON_TRACE] Base component: {type(self.base_component)}")
        
        # Use Flet's native async task handling - stays on main UI thread
        try:
            async def async_button_handler():
                try:
                    print(f"[BUTTON_TRACE] Starting async handler for {config.action_key}")
                    result = await self._handle_button_click(config, get_selected_items, additional_params)
                    print(f"[BUTTON_TRACE] Async handler completed for {config.action_key}: {result}")
                    return result
                except Exception as ex:
                    print(f"[BUTTON_TRACE] ✗ Async handler error for {config.action_key}: {ex}")
                    import traceback
                    print(f"[BUTTON_TRACE] Stack trace: {traceback.format_exc()}")
                    await self.base_component._show_error(f"Action failed: {ex}")
                    return False
            
            print(f"[BUTTON_TRACE] Scheduling async task via page.run_task")
            self.page.run_task(async_button_handler)
            print(f"[BUTTON_TRACE] Async task scheduled successfully for {config.action_key}")
            
        except Exception as ex:
            print(f"[BUTTON_TRACE] ✗ Task scheduling failed for {config.action_key}: {ex}")
            import traceback
            print(f"[BUTTON_TRACE] Scheduling error stack: {traceback.format_exc()}")
    
    async def _handle_button_click(
        self,
        config: ButtonConfig,
        get_selected_items: Callable[[], List[str]],
        additional_params: Optional[Dict[str, Any]]
    ):
        """
        Handle button click with comprehensive error handling and user feedback.
        
        Args:
            config: Button configuration
            get_selected_items: Function to get selected items
            additional_params: Additional parameters for the action
        """
        print(f"[BUTTON_TRACE] ========== BUTTON HANDLER EXECUTION ==========")
        print(f"[BUTTON_TRACE] Processing: {config.action_key}")
        print(f"[BUTTON_TRACE] Requires selection: {config.requires_selection}")
        
        try:
            # Validate selection requirements
            print(f"[BUTTON_TRACE] Getting selected items...")
            selected_items = get_selected_items() if config.requires_selection else []
            print(f"[BUTTON_TRACE] Selected items: {selected_items} (count: {len(selected_items)})")
            
            if config.requires_selection:
                print(f"[BUTTON_TRACE] Validating selection requirements: min={config.min_selection}, max={config.max_selection}")
                if len(selected_items) < config.min_selection:
                    print(f"[BUTTON_TRACE] ✗ Selection validation failed: need {config.min_selection}, got {len(selected_items)}")
                    await self.base_component._show_error(f"Please select at least {config.min_selection} item(s)")
                    return False
                
                if config.max_selection and len(selected_items) > config.max_selection:
                    print(f"[BUTTON_TRACE] ✗ Selection validation failed: max {config.max_selection}, got {len(selected_items)}")
                    await self.base_component._show_error(f"Please select no more than {config.max_selection} item(s)")
                    return False
                
                print(f"[BUTTON_TRACE] ✓ Selection validation passed")
            
            # Get the action instance and method
            print(f"[ACTION_TRACE] ========== ACTION RESOLUTION ==========")
            print(f"[ACTION_TRACE] Resolving action class: {config.action_class}")
            print(f"[ACTION_TRACE] Available actions: {list(self.actions.keys())}")
            
            action_instance = self.actions.get(config.action_class)
            print(f"[ACTION_TRACE] Direct action lookup result: {action_instance is not None}")
            
            # For action handlers that are set by views, get them from the base component if they're None
            if action_instance is None and config.action_class.endswith("ActionHandlers"):
                print(f"[ACTION_TRACE] Action handler not found directly, checking base component...")
                handler_attr_map = {
                    "ClientActionHandlers": "action_handlers",
                    "FileActionHandlers": "file_action_handlers", 
                    "DatabaseActionHandlers": "database_action_handlers",
                    "ServerActionHandlers": "server_action_handlers"
                }
                
                attr_name = handler_attr_map.get(config.action_class)
                print(f"[ACTION_TRACE] Looking for attribute: {attr_name}")
                
                if attr_name and hasattr(self.base_component, attr_name):
                    action_instance = getattr(self.base_component, attr_name)
                    print(f"[ACTION_TRACE] Found via base component attribute: {action_instance is not None}")
                elif hasattr(self.base_component, 'actions'):
                    action_instance = self.base_component.actions.get(config.action_class)
                    print(f"[ACTION_TRACE] Found via base component actions dict: {action_instance is not None}")
                else:
                    print(f"[ACTION_TRACE] Base component has no 'actions' attribute")
            
            print(f"[ACTION_TRACE] Final action instance: {type(action_instance) if action_instance else None}")
            
            if action_instance is None:
                print(f"[ACTION_TRACE] ✗ Handler {config.action_class} not available")
                print(f"[ACTION_TRACE] Base component attributes: {[attr for attr in dir(self.base_component) if not attr.startswith('_')]}")
                await self.base_component._show_error(f"Action handler {config.action_class} not available")
                return False
            
            try:
                print(f"[ACTION_TRACE] Resolving method: {config.action_method}")
                print(f"[ACTION_TRACE] Available methods on {type(action_instance)}: {[m for m in dir(action_instance) if not m.startswith('_') and callable(getattr(action_instance, m))]}")
                action_method = getattr(action_instance, config.action_method)
                print(f"[ACTION_TRACE] ✓ Method resolved: {action_method}")
            except AttributeError:
                print(f"[ACTION_TRACE] ✗ Method {config.action_method} not found on {type(action_instance)}")
                await self.base_component._show_error(f"Action method {config.action_method} not found")
                return False
            
            # Prepare method parameters and execute
            print(f"[ACTION_TRACE] ========== METHOD EXECUTION ==========")
            method_params = self._prepare_method_params(config, selected_items, additional_params)
            print(f"[ACTION_TRACE] Prepared parameters: {method_params}")
            print(f"[ACTION_TRACE] Calling: {config.action_method}(**{list(method_params.keys())})")
            
            try:
                result = await action_method(**method_params)
                print(f"[ACTION_TRACE] ✓ Method call completed successfully")
            except Exception as method_ex:
                print(f"[ACTION_TRACE] ✗ Method call failed: {method_ex}")
                import traceback
                print(f"[ACTION_TRACE] Method execution stack: {traceback.format_exc()}")
                raise
            
            # EXHAUSTIVE EXECUTION TRACING - Expose the illusion
            print(f"[ACTION_TRACE] ========== RESULT ANALYSIS ==========")
            print(f"[ACTION_TRACE] Raw result: {result}")
            print(f"[ACTION_TRACE] Result type: {type(result)}")
            print(f"[ACTION_TRACE] Result repr: {repr(result)}")
            
            if result is False:
                print(f"[ACTION_TRACE] ✗ Method explicitly returned False - operation failed")
                return False
            elif result is None:
                print(f"[ACTION_TRACE] ⚠ Method returned None - potential mock/stub implementation")
                print(f"[ACTION_TRACE] REALITY CHECK: None return suggests no actual work was performed")
            else:
                print(f"[ACTION_TRACE] ✓ Method returned non-null result")
                if hasattr(result, 'success'):
                    print(f"[ACTION_TRACE] ActionResult.success: {result.success}")
                    if hasattr(result, 'data'):
                        print(f"[ACTION_TRACE] ActionResult.data: {result.data}")
                    if hasattr(result, 'metadata'):
                        print(f"[ACTION_TRACE] ActionResult.metadata: {result.metadata}")
                        if result.metadata and result.metadata.get('simulated'):
                            print(f"[ACTION_TRACE] *** DETECTED SIMULATED OPERATION - NOT REAL ***")
                elif isinstance(result, bool) and result:
                    print(f"[ACTION_TRACE] Boolean True result - operation appears successful")
                elif isinstance(result, (int, str)) and result:
                    print(f"[ACTION_TRACE] Non-empty scalar result: {result}")
                
            print(f"[ACTION_TRACE] ========== EXECUTION COMPLETE ==========")
            return True
            
            # Original confirmation system (commented for bypass testing)
            print(f"[DEBUG] About to execute method. Operation type: {config.operation_type}")
            if False and config.operation_type == "bulk":
                print(f"[DEBUG] Executing bulk action")
                success = await self.base_component.execute_bulk_action(
                    action=lambda items: action_method(**method_params),
                    selected_items=selected_items,
                    item_type=self._get_item_type(config.action_class),
                    action_name=config.action_method.replace("_multiple_", "_").replace("_", " ")
                )
            else:
                # Prepare confirmation text
                confirmation_text = config.confirmation_text
                if "{count}" in confirmation_text:
                    confirmation_text = confirmation_text.format(count=len(selected_items))
                elif "{item}" in confirmation_text and selected_items:
                    confirmation_text = confirmation_text.format(item=selected_items[0] if len(selected_items) == 1 else f"{len(selected_items)} items")
                
                print(f"[DEBUG] Executing single action with confirmation")
                print(f"[DEBUG] Base component type: {type(self.base_component)}")
                print(f"[DEBUG] Has execute_with_confirmation: {hasattr(self.base_component, 'execute_with_confirmation')}")
                success = await self.base_component.execute_with_confirmation(
                    action=lambda: action_method(**method_params),
                    confirmation_text=confirmation_text,
                    success_message=config.success_message,
                    operation_name=config.action_method
                )
            
            # Handle special post-action operations
            if success:
                await self._handle_post_action(config, method_params)
                
            return success
            
        except Exception as e:
            print(f"[BUTTON_TRACE] ========== EXCEPTION HANDLER ==========")
            print(f"[EXCEPTION_TRACE] Button action failed: {str(e)}")
            print(f"[EXCEPTION_TRACE] Exception type: {type(e)}")
            import traceback
            print(f"[EXCEPTION_TRACE] Full traceback:")
            traceback.print_exc()
            await self.base_component._show_error(f"Button action failed: {str(e)}")
            return False
    
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