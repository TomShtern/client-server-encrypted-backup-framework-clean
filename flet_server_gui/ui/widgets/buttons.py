#!/usr/bin/env python3
"""
UI Widgets - Buttons

Purpose: Centralized button factory, configurations, and action mappings
Logic: Button creation, styling, and event handling  
UI: Button rendering and Material Design 3 styling
"""

import flet as ft
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass
from ...actions import ClientActions, FileActions, ServerActions
from ...actions.base_action import ActionResult
from ...components.base_component import BaseComponent


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
            operation_type="export"
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
            operation_type="import"
        ),
        
        'client_disconnect_bulk': ButtonConfig(
            text="Disconnect Selected",
            icon=ft.Icons.LINK_OFF,
            tooltip="Disconnect selected clients from server",
            action_class="ClientActions",
            action_method="disconnect_multiple_clients",
            confirmation_text="Disconnect {count} selected clients?",
            success_message="Clients disconnected successfully",
            progress_message="Disconnecting clients...",
            operation_type="bulk"
        ),
        
        'client_delete_bulk': ButtonConfig(
            text="Delete Selected", 
            icon=ft.Icons.DELETE,
            tooltip="Permanently delete selected clients",
            action_class="ClientActions",
            action_method="delete_multiple_clients",
            confirmation_text="Permanently delete {count} selected clients? This cannot be undone.",
            success_message="Clients deleted successfully",
            progress_message="Deleting clients...",
            operation_type="bulk"
        ),
        
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
        
        # File Management Buttons
        'file_download_bulk': ButtonConfig(
            text="Download Selected",
            icon=ft.Icons.FILE_DOWNLOAD,
            tooltip="Download selected files to local directory",
            action_class="FileActions",
            action_method="download_multiple_files", 
            confirmation_text="Download {count} selected files?",
            success_message="Files downloaded successfully",
            progress_message="Downloading files...",
            operation_type="bulk"
        ),
        
        'file_verify_bulk': ButtonConfig(
            text="Verify Selected",
            icon=ft.Icons.VERIFIED,
            tooltip="Verify integrity of selected files",
            action_class="FileActions",
            action_method="verify_multiple_files",
            confirmation_text="Verify integrity of {count} selected files?",
            success_message="Files verified successfully", 
            progress_message="Verifying files...",
            operation_type="bulk"
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
            operation_type="export"
        ),
        
        'file_upload': ButtonConfig(
            text="Upload File",
            icon=ft.Icons.UPLOAD_FILE,
            tooltip="Upload new file to server",
            action_class="FileActions",
            action_method="upload_file",
            confirmation_text="Upload selected file to server?",
            success_message="File uploaded successfully",
            progress_message="Uploading file...",
            requires_selection=False,
            operation_type="import"
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
            operation_type="single"
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
            operation_type="single"
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
            "ServerActions": ServerActions(server_bridge)
        }
    
    def create_action_button(
        self,
        config_key: str,
        get_selected_items: Callable[[], List[str]],
        additional_params: Optional[Dict[str, Any]] = None
    ) -> ft.Control:
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
        
        # Create the button based on style - use responsive design
        button_props = {
            "text": config.text,
            "icon": config.icon,
            "tooltip": config.tooltip,
            "on_click": lambda e: self._handle_button_click(config, get_selected_items, additional_params),
            "expand": True  # Responsive design
        }
        
        if config.button_style == "filled":
            button = ft.FilledButton(**button_props)
        elif config.button_style == "outlined":
            button = ft.OutlinedButton(**button_props)
        elif config.button_style == "text":
            button = ft.TextButton(**button_props)
        else:  # Default to elevated
            button = ft.ElevatedButton(**button_props)
        
        return button
    
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
        try:
            # Validate selection requirements
            selected_items = get_selected_items() if config.requires_selection else []
            
            if config.requires_selection:
                if len(selected_items) < config.min_selection:
                    await self.base_component._show_error(
                        f"Please select at least {config.min_selection} item(s)"
                    )
                    return
                
                if config.max_selection and len(selected_items) > config.max_selection:
                    await self.base_component._show_error(
                        f"Please select no more than {config.max_selection} item(s)"
                    )
                    return
            
            # Get the action instance and method
            action_instance = self.actions[config.action_class]
            action_method = getattr(action_instance, config.action_method)
            
            # Prepare method parameters
            method_params = self._prepare_method_params(config, selected_items, additional_params)
            
            # Use the base component's confirmation and execution pattern
            if config.operation_type == "bulk":
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
                
                success = await self.base_component.execute_with_confirmation(
                    action=lambda: action_method(**method_params),
                    confirmation_text=confirmation_text,
                    success_message=config.success_message,
                    operation_name=config.action_method
                )
            
            # Handle special post-action operations
            if success:
                await self._handle_post_action(config, method_params)
                
        except Exception as e:
            await self.base_component._show_error(f"Button action failed: {str(e)}")
    
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
        params = {}
        
        # Add selected items based on method signature
        if selected_items:
            if "client" in config.action_method.lower():
                params["client_ids"] = selected_items
            elif "file" in config.action_method.lower():
                params["file_ids"] = selected_items
        
        # Add export format if specified
        if config.export_format:
            params["export_format"] = config.export_format
        
        # Add any additional parameters
        if additional_params:
            params.update(additional_params)
        
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
        if config.operation_type == "export":
            export_format = config.export_format or "csv"
            await self.base_component._show_success(
                f"Data exported in {export_format.upper()} format"
            )
        elif config.operation_type == "import":
            await self.base_component._show_success("Import operation completed")
    
    def create_button_group(
        self,
        config_keys: List[str],
        get_selected_items: Callable[[], List[str]],
        orientation: str = "horizontal"
    ) -> ft.Container:
        """
        Create a responsive group of related action buttons.
        
        Args:
            config_keys: List of button configuration keys
            get_selected_items: Function to get selected items
            orientation: "horizontal" or "vertical"
            
        Returns:
            Container with responsive button group
        """
        buttons = [
            self.create_action_button(key, get_selected_items)
            for key in config_keys
        ]
        
        if orientation == "horizontal":
            control = ft.ResponsiveRow([
                ft.Column([button], col={"sm": 12, "md": 6, "lg": 3}, expand=True)
                for button in buttons
            ])
        else:
            control = ft.Column(controls=buttons, spacing=8, expand=True)
        
        return ft.Container(content=control, padding=8, expand=True)
    
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