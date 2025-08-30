"""error_boundary_demo.py

Demonstration of the Centralized Error Boundary System
=====================================================

This demo shows how to use the error boundary system in a real Flet application.
It demonstrates various error scenarios and how they are handled gracefully
with professional error dialogs and proper logging.

Features demonstrated:
- Error boundary initialization
- Safe UI callbacks with error protection
- Different error types and severities
- Error dialog functionality
- Copy to clipboard feature
- Custom error reporting
"""

import flet as ft
import asyncio
import traceback
from datetime import datetime

# Import our error boundary components
from flet_server_gui.components.error_boundary import GlobalErrorBoundary, ErrorBoundary
from flet_server_gui.components.error_dialog import show_error_dialog, show_simple_error
from flet_server_gui.utils.error_context import create_error_context


class ErrorBoundaryDemo:
    """Demo application showcasing the error boundary system."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Error Boundary System Demo"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        
        # Initialize global error boundary
        self.error_boundary = GlobalErrorBoundary.initialize(page)
        
        # Set up custom error reporting
        self.error_reports = []
        self.error_boundary.set_error_report_callback(self.handle_error_report)
        
        # Create the demo UI
        self.create_demo_ui()
    
    def handle_error_report(self, error_context):
        """Handle error reports from the error boundary."""
        self.error_reports.append({
            "timestamp": datetime.now().isoformat(),
            "error_type": error_context.error_type,
            "error_message": error_context.error_message,
            "operation": error_context.operation,
            "correlation_id": error_context.correlation_id
        })
        print(f"Error reported: {error_context.error_type} - {error_context.error_message}")
    
    def create_demo_ui(self):
        """Create the demo user interface."""
        
        # Title
        title = ft.Text(
            "🛡️ Error Boundary System Demo",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.PRIMARY
        )
        
        subtitle = ft.Text(
            "Click the buttons below to trigger different types of errors and see how they are handled gracefully.",
            size=16,
            color=ft.colors.ON_SURFACE_VARIANT
        )
        
        # Error trigger buttons
        error_buttons = self.create_error_buttons()
        
        # Info section
        info_section = self.create_info_section()
        
        # Layout
        self.page.add(
            ft.Column([
                title,
                subtitle,
                ft.Divider(height=20),
                ft.Text("Error Scenarios:", size=20, weight=ft.FontWeight.BOLD),
                error_buttons,
                ft.Divider(height=20),
                info_section
            ], spacing=20)
        )
    
    def create_error_buttons(self):
        """Create buttons that trigger different error types."""
        
        # Protected button callbacks using the error boundary
        buttons = [
            ft.ElevatedButton(
                text="💥 Value Error",
                on_click=self.error_boundary.safe_callback(self.trigger_value_error),
                tooltip="Triggers a ValueError with user-friendly message",
                width=200
            ),
            ft.ElevatedButton(
                text="📁 File Not Found",
                on_click=self.error_boundary.safe_callback(self.trigger_file_error),
                tooltip="Triggers a FileNotFoundError",
                width=200
            ),
            ft.ElevatedButton(
                text="🔒 Permission Error",
                on_click=self.error_boundary.safe_callback(self.trigger_permission_error),
                tooltip="Triggers a PermissionError",
                width=200
            ),
            ft.ElevatedButton(
                text="🌐 Connection Error",
                on_click=self.error_boundary.safe_callback(self.trigger_connection_error),
                tooltip="Triggers a ConnectionError",
                width=200
            ),
            ft.ElevatedButton(
                text="⚠️ Runtime Error",
                on_click=self.error_boundary.safe_callback(self.trigger_runtime_error),
                tooltip="Triggers a RuntimeError with stack trace",
                width=200
            ),
            ft.ElevatedButton(
                text="🔧 Custom Error",
                on_click=self.error_boundary.safe_callback(self.trigger_custom_error),
                tooltip="Triggers a custom error with detailed context",
                width=200
            ),
            ft.ElevatedButton(
                text="💀 Critical Error",
                on_click=self.error_boundary.safe_callback(self.trigger_critical_error),
                tooltip="Triggers a critical system error",
                width=200,
                bgcolor=ft.colors.ERROR
            ),
            ft.ElevatedButton(
                text="🚀 Async Error",
                on_click=self.error_boundary.safe_callback(self.trigger_async_error),
                tooltip="Triggers an error in async operation",
                width=200
            ),
            ft.ElevatedButton(
                text="📄 Simple Error Dialog",
                on_click=self.show_simple_error_demo,
                tooltip="Shows a simple error dialog",
                width=200,
                color=ft.colors.SECONDARY
            )
        ]
        
        # Arrange in rows
        button_rows = []
        for i in range(0, len(buttons), 3):
            button_rows.append(
                ft.Row(
                    buttons[i:i+3],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.START
                )
            )
        
        return ft.Column(button_rows, spacing=10)
    
    def create_info_section(self):
        """Create information section about the error boundary."""
        
        return ft.Container(
            content=ft.Column([
                ft.Text("ℹ️ How the Error Boundary Works:", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("• Catches unhandled exceptions in UI callbacks", size=14),
                ft.Text("• Shows professional error dialogs with user-friendly messages", size=14),
                ft.Text("• Provides collapsible technical details for debugging", size=14),
                ft.Text("• Includes copy-to-clipboard functionality for error reports", size=14),
                ft.Text("• Logs errors with correlation IDs for tracking", size=14),
                ft.Text("• Supports custom error reporting callbacks", size=14),
                ft.Text("• Prevents application crashes from unhandled exceptions", size=14),
                ft.Divider(),
                ft.Text(f"📊 Error Reports Captured: {len(self.error_reports)}", size=14, weight=ft.FontWeight.BOLD)
            ], spacing=8),
            bgcolor=ft.colors.SURFACE_VARIANT,
            padding=20,
            border_radius=10
        )
    
    # Error trigger methods
    def trigger_value_error(self, e):
        """Trigger a ValueError."""
        raise ValueError("Invalid input provided - this is a test error to demonstrate error handling")
    
    def trigger_file_error(self, e):
        """Trigger a FileNotFoundError."""
        # Simulate file operation
        with open("nonexistent_file.txt", "r") as f:
            content = f.read()
    
    def trigger_permission_error(self, e):
        """Trigger a PermissionError."""
        raise PermissionError("Access denied to protected resource")
    
    def trigger_connection_error(self, e):
        """Trigger a ConnectionError."""
        import socket
        raise socket.error("Unable to connect to remote server")
    
    def trigger_runtime_error(self, e):
        """Trigger a RuntimeError with nested calls."""
        def nested_function():
            def deeply_nested():
                raise RuntimeError("Something went wrong in deeply nested function")
            deeply_nested()
        nested_function()
    
    def trigger_custom_error(self, e):
        """Trigger a custom error with detailed context."""
        # Simulate some local variables
        user_id = 12345
        operation_type = "data_processing"
        batch_size = 100
        
        try:
            # Simulate operation failure
            result = self.simulate_complex_operation(user_id, operation_type, batch_size)
        except Exception as exc:
            # Re-raise with additional context
            raise RuntimeError(f"Complex operation failed for user {user_id}") from exc
    
    def simulate_complex_operation(self, user_id, operation_type, batch_size):
        """Simulate a complex operation that fails."""
        if batch_size > 50:
            raise ValueError("Batch size too large for processing")
        return True
    
    def trigger_critical_error(self, e):
        """Trigger a critical system error."""
        raise MemoryError("Insufficient memory to complete operation - this is a critical error")
    
    async def trigger_async_error(self, e):
        """Trigger an error in async operation."""
        await asyncio.sleep(0.1)  # Simulate async work
        raise ConnectionError("Async network operation failed")
    
    def show_simple_error_demo(self, e):
        """Show a simple error dialog without the full error boundary."""
        show_simple_error(
            self.page,
            "This is a simple error message for quick notifications.",
            "Simple Error Demo",
            "Technical details: Error code 404, operation failed"
        )


async def main(page: ft.Page):
    """Main entry point for the demo application."""
    demo = ErrorBoundaryDemo(page)


if __name__ == "__main__":
    # Run the demo
    print("🚀 Starting Error Boundary Demo...")
    print("Click the buttons in the app to see different error handling scenarios.")
    ft.app(target=main, view=ft.WEB_BROWSER)
