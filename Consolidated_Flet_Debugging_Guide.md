# Advanced Flet Debugging Techniques and Tools (September 2025)

This comprehensive guide provides all debugging techniques, tools, and best practices for Flet applications as of September 2025. It combines basic, intermediate, and advanced debugging methods with specialized tools and expert practices for debugging complex Flet applications.

## 1. Basic Debugging Setup

### 1.1 Enable Debug Logging

To enable debug-level logging for all Flet modules, add this at the beginning of your main Python file:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 1.2 Environment Variables for Debugging

Set these environment variables to control Flet's logging behavior:

```bash
# Enable debug-level logging for the Flet server
export FLET_LOG_LEVEL=debug

# Redirect logs to a file (optional)
export FLET_LOG_TO_FILE=true

# Disable rich output for cleaner terminal output
export FLET_CLI_NO_RICH_OUTPUT=true
```

### 1.3 Page-Level Debugging

Enable page debugging to track page lifecycle events:

```python
import flet as ft

def main(page: ft.Page):
    # Enable page debugging
    page.debug = True
    
    # Track page lifecycle events
    def on_app_lifecycle_change(e):
        debug_log(f"App lifecycle changed to: {e.state}", "LIFECYCLE")
    
    def on_route_change(e):
        debug_log(f"Route changed to: {e.route}", "ROUTE")
    
    def on_view_pop(e):
        debug_log("View popped", "NAVIGATION")
    
    def on_error(e):
        debug_log(f"Page error: {e}", "ERROR")
    
    # Set up event handlers
    page.on_app_lifecycle_change = on_app_lifecycle_change
    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop
    page.on_error = on_error

ft.app(target=main)
```

## 2. Custom Debug Logging Functions

### 2.1 Timestamp-Based Debug Logging

Create a custom logging function to track events with timestamps:

```python
from datetime import datetime

def debug_log(message: str, level: str = "INFO"):
    """Custom logging function to print debug information to terminal with timestamps"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{level}] {message}")
```

### 2.2 Advanced Logging Configuration

#### 2.2.1 Structured Logging with Context

Implement structured logging with contextual information:

```python
import json
import logging
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.propagate = False
    
    def log_event(self, event_type: str, message: str, context: Dict[str, Any] = None, level: str = "INFO"):
        """Log structured events with context"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "event_type": event_type,
            "message": message,
            "context": context or {}
        }
        
        if level == "ERROR":
            self.logger.error(json.dumps(log_entry))
        elif level == "WARNING":
            self.logger.warning(json.dumps(log_entry))
        else:
            self.logger.info(json.dumps(log_entry))

# Usage
debug_logger = StructuredLogger("flet_app")

def log_user_action(action: str, user_id: str = None, details: Dict = None):
    """Log user actions with structured data"""
    debug_logger.log_event(
        "USER_ACTION",
        f"User performed action: {action}",
        {
            "user_id": user_id,
            "action": action,
            "details": details or {}
        }
    )
```

#### 2.2.2 Conditional Debug Logging

Implement conditional logging based on debug levels:

```python
import os

DEBUG_LEVEL = os.getenv("FLET_DEBUG_LEVEL", "INFO").upper()

DEBUG_LEVELS = {
    "NONE": 0,
    "ERROR": 1,
    "WARNING": 2,
    "INFO": 3,
    "DEBUG": 4,
    "VERBOSE": 5
}

CURRENT_DEBUG_LEVEL = DEBUG_LEVELS.get(DEBUG_LEVEL, DEBUG_LEVELS["INFO"])

def debug_print(message: str, level: str = "INFO"):
    """Print debug messages conditionally based on debug level"""
    if DEBUG_LEVELS.get(level, 0) <= CURRENT_DEBUG_LEVEL:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")

# Usage
debug_print("This is a debug message", "DEBUG")
debug_print("This is an info message", "INFO")
debug_print("This is a warning message", "WARNING")
```

## 3. State Management Debugging

### 3.1 Simple State Tracking

Create a comprehensive state tracker for your application:

```python
class AppStateTracker:
    def __init__(self):
        self.state = {}
        self.event_history = []
    
    def update_state(self, key, value):
        old_value = self.state.get(key)
        self.state[key] = value
        self.log_event("STATE_UPDATE", f"{key}: {old_value} -> {value}")
    
    def log_event(self, event_type, details):
        timestamp = datetime.now().isoformat()
        event = {
            "timestamp": timestamp,
            "type": event_type,
            "details": details
        }
        self.event_history.append(event)
        print(f"[{timestamp}] {event_type}: {details}")
    
    def get_state(self):
        return self.state.copy()
    
    def get_recent_events(self, count=10):
        return self.event_history[-count:]

# Global state tracker
app_tracker = AppStateTracker()
```

### 3.2 Advanced State Tracking

#### 3.2.1 State Diff Tracking

Track changes in application state with diffs:

```python
from typing import Dict, Any
from copy import deepcopy
import json

class StateTracker:
    def __init__(self):
        self.current_state = {}
        self.previous_state = {}
        self.changes = []
    
    def update_state(self, key: str, value: Any):
        """Update state and track changes"""
        # Store previous state
        self.previous_state = deepcopy(self.current_state)
        
        # Update current state
        self.current_state[key] = value
        
        # Calculate differences
        diff = self._calculate_diff(self.previous_state, self.current_state)
        
        # Log changes
        if diff:
            change_record = {
                "timestamp": datetime.now().isoformat(),
                "key": key,
                "diff": diff,
                "previous_value": self.previous_state.get(key),
                "new_value": value
            }
            self.changes.append(change_record)
            debug_print(f"State changed: {key} = {value}", "STATE")
            if len(diff) > 1:
                debug_print(f"Full diff: {json.dumps(diff, indent=2)}", "STATE")
    
    def _calculate_diff(self, old_state: Dict, new_state: Dict) -> Dict:
        """Calculate differences between two states"""
        diff = {}
        
        # Find new or changed keys
        for key, new_value in new_state.items():
            if key not in old_state:
                diff[key] = {"type": "added", "value": new_value}
            elif old_state[key] != new_value:
                diff[key] = {
                    "type": "changed", 
                    "old_value": old_state[key], 
                    "new_value": new_value
                }
        
        # Find removed keys
        for key in old_state:
            if key not in new_state:
                diff[key] = {"type": "removed", "value": old_state[key]}
        
        return diff
    
    def get_state_history(self, limit: int = 10) -> list:
        """Get recent state changes"""
        return self.changes[-limit:] if self.changes else []
    
    def export_state_snapshot(self) -> str:
        """Export current state as JSON"""
        return json.dumps(self.current_state, indent=2, default=str)

# Global state tracker
state_tracker = StateTracker()
```

#### 3.2.2 State Tracking Class

Create a comprehensive state tracking system:

```python
class FletStateDebugger:
    def __init__(self):
        self.states = {}
        self.history = []
        self.watchers = {}
    
    def set_state(self, key, value):
        """Set application state with tracking"""
        old_value = self.states.get(key)
        self.states[key] = value
        self._log_change(key, old_value, value)
        self._notify_watchers(key, old_value, value)
    
    def get_state(self, key, default=None):
        """Get application state"""
        return self.states.get(key, default)
    
    def watch_state(self, key, callback):
        """Watch state changes"""
        if key not in self.watchers:
            self.watchers[key] = []
        self.watchers[key].append(callback)
    
    def _log_change(self, key, old_value, new_value):
        """Log state changes"""
        timestamp = datetime.now().isoformat()
        self.history.append({
            "timestamp": timestamp,
            "key": key,
            "old_value": old_value,
            "new_value": new_value
        })
        debug_log(f"State '{key}' changed: {old_value} -> {new_value}", "STATE")
    
    def _notify_watchers(self, key, old_value, new_value):
        """Notify watchers of state changes"""
        if key in self.watchers:
            for watcher in self.watchers[key]:
                try:
                    watcher(key, old_value, new_value)
                except Exception as ex:
                    debug_log(f"Watcher error for {key}: {ex}", "ERROR")
    
    def dump_state(self):
        """Dump current state to console"""
        debug_log("=== Current Application State ===", "DUMP")
        for key, value in self.states.items():
            debug_log(f"  {key}: {value}", "DUMP")
        debug_log("=================================", "DUMP")

# Global state debugger
state_debugger = FletStateDebugger()
```

## 4. Event Tracking for All Controls

### 4.1 Button Click Debugging

#### 4.1.1 Debug Button Creator

Create buttons with automatic debug logging:

```python
def create_debug_button(text, on_click_handler=None, **kwargs):
    """Create a button with automatic debug logging"""
    
    def debug_click_handler(e):
        # Log button click details
        debug_log(f"Button clicked: {text}", "CLICK")
        debug_log(f"Control ID: {e.control.uid}", "CLICK")
        debug_log(f"Control data: {getattr(e.control, 'data', 'No data')}", "CLICK")
        
        # Call the original handler if provided
        if on_click_handler:
            try:
                on_click_handler(e)
                debug_log(f"Button handler completed: {text}", "CLICK")
            except Exception as ex:
                debug_log(f"Button handler error: {ex}", "ERROR")
    
    # Create the button with the debug handler
    button = ft.ElevatedButton(text, on_click=debug_click_handler, **kwargs)
    return button
```

#### 4.1.2 Button Click with State Tracking

Track button clicks with application state:

```python
def create_state_tracking_button(text, state_key, on_click_handler=None):
    """Create a button that tracks state changes"""
    
    def state_tracking_handler(e):
        # Update state tracker
        current_count = app_tracker.get_state().get(state_key, 0)
        app_tracker.update_state(state_key, current_count + 1)
        
        # Call original handler
        if on_click_handler:
            on_click_handler(e)
    
    return create_debug_button(text, state_tracking_handler)
```

### 4.2 Text Field Change Tracking

Track changes in text fields:

```python
def create_tracked_textfield(label, on_change_handler=None):
    """Create a TextField with change tracking"""
    
    def on_textfield_change(e):
        debug_log(f"TextField '{label}' value changed to: '{e.control.value}'", "INPUT")
        if on_change_handler:
            on_change_handler(e)
    
    return ft.TextField(label=label, on_change=on_textfield_change)
```

### 4.3 Dropdown Selection Tracking

Track dropdown selections:

```python
def create_tracked_dropdown(options, label, on_change_handler=None):
    """Create a Dropdown with selection tracking"""
    
    def on_dropdown_change(e):
        debug_log(f"Dropdown '{label}' selection changed to: {e.control.value}", "INPUT")
        if on_change_handler:
            on_change_handler(e)
    
    dropdown_options = [ft.dropdown.Option(opt) for opt in options]
    return ft.Dropdown(
        label=label,
        options=dropdown_options,
        on_change=on_dropdown_change
    )
```

### 4.4 Checkbox State Tracking

Track checkbox state changes:

```python
def create_tracked_checkbox(label, on_change_handler=None):
    """Create a Checkbox with state tracking"""
    
    def on_checkbox_change(e):
        debug_log(f"Checkbox '{label}' is now {'checked' if e.control.value else 'unchecked'}", "INPUT")
        if on_change_handler:
            on_change_handler(e)
    
    return ft.Checkbox(label=label, on_change=on_checkbox_change)
```

### 4.5 Switch State Tracking

Track switch state changes:

```python
def create_tracked_switch(label, on_change_handler=None):
    """Create a Switch with state tracking"""
    
    def on_switch_change(e):
        debug_log(f"Switch '{label}' is now {'ON' if e.control.value else 'OFF'}", "INPUT")
        if on_change_handler:
            on_switch_change(e)
    
    return ft.Switch(label=label, on_change=on_switch_change)
```

### 4.6 Event Timeline Tracker

Track events chronologically with detailed timing:

```python
from collections import deque
import time

class EventTimeline:
    def __init__(self, max_events: int = 1000):
        self.events = deque(maxlen=max_events)
        self.start_time = time.time()
    
    def record_event(self, event_type: str, description: str, data: Dict = None):
        """Record an event with precise timing"""
        event_time = time.time()
        elapsed_time = event_time - self.start_time
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed_time, 6),
            "type": event_type,
            "description": description,
            "data": data or {}
        }
        
        self.events.append(event)
        debug_print(f"[{elapsed_time:.3f}s] {event_type}: {description}", "TIMELINE")
    
    def get_events(self, event_type: str = None) -> list:
        """Get events, optionally filtered by type"""
        if event_type:
            return [e for e in self.events if e["type"] == event_type]
        return list(self.events)
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        if not self.events:
            return {"event_count": 0}
        
        event_types = {}
        for event in self.events:
            event_type = event["type"]
            if event_type not in event_types:
                event_types[event_type] = []
            event_types[event_type].append(event["elapsed_seconds"])
        
        stats = {"event_count": len(self.events)}
        for event_type, times in event_types.items():
            stats[event_type] = {
                "count": len(times),
                "first_occurrence": min(times),
                "last_occurrence": max(times),
                "avg_time": sum(times) / len(times)
            }
        
        return stats

# Global timeline tracker
event_timeline = EventTimeline()
```

## 5. Container and Layout Debugging

### 5.1 Interactive Container Debugging

Track container interactions:

```python
def create_debug_container(content, on_click_handler=None, on_hover_handler=None):
    """Create a container with click and hover debugging"""
    
    def on_container_click(e):
        debug_log(f"Container clicked at position: ({e.local_x}, {e.local_y})", "CLICK")
        if on_click_handler:
            on_click_handler(e)
        e.control.bgcolor = ft.colors.PINK_ACCENT_400
        e.control.update()
    
    def on_container_hover(e):
        hover_state = "entered" if e.data == "true" else "left"
        debug_log(f"Container hover {hover_state}", "HOVER")
        if on_hover_handler:
            on_hover_handler(e)
        e.control.bgcolor = ft.colors.BLUE_GREY_100 if e.data == "true" else ft.colors.BLUE_ACCENT_100
        e.control.update()
    
    return ft.Container(
        content=content,
        alignment=ft.alignment.center,
        width=200,
        height=100,
        bgcolor=ft.colors.BLUE_ACCENT_100,
        border_radius=5,
        on_click=on_container_click,
        on_hover=on_container_hover
    )
```

## 6. Keyboard Event Debugging

### 6.1 Comprehensive Keyboard Event Tracking

Track all keyboard events:

```python
def setup_keyboard_debugging(page):
    """Set up comprehensive keyboard event debugging"""
    
    def on_keyboard(e: ft.KeyboardEvent):
        debug_log(f"Keyboard event: key={e.key}, ctrl={e.ctrl}, shift={e.shift}, meta={e.meta}", "KEYBOARD")
    
    page.on_keyboard_event = on_keyboard
    debug_log("Keyboard debugging enabled", "INIT")
```

## 7. Route and Navigation Debugging

### 7.1 Route Change Tracking

Track route changes in your application:

```python
def setup_route_debugging(page):
    """Set up route change debugging"""
    
    def on_route_change(e: ft.RouteChangeEvent):
        debug_log(f"Route changed to: {e.route}", "ROUTE")
        debug_log(f"Route data: {getattr(e, 'data', 'No data')}", "ROUTE")
    
    page.on_route_change = on_route_change
    debug_log("Route debugging enabled", "INIT")
```

## 8. Error Handling and Exception Tracking

### 8.1 Comprehensive Error Handler

Implement comprehensive error handling:

```python
def setup_error_handling(page):
    """Set up comprehensive error handling"""
    
    def handle_page_error(e):
        debug_log(f"Page error occurred: {e}", "ERROR")
        # Show error to user
        page.snack_bar = ft.SnackBar(
            ft.Text(f"An error occurred: {str(e)}"),
            open=True,
        )
        page.update()
    
    # Set up error handler
    page.on_error = handle_page_error
    debug_log("Error handling set up", "INIT")

def create_safe_button(text, unsafe_handler):
    """Create a button with error handling"""
    
    def safe_handler(e):
        try:
            unsafe_handler(e)
        except Exception as ex:
            debug_log(f"Exception in button handler: {ex}", "ERROR")
            # Handle the error gracefully
            e.page.snack_bar = ft.SnackBar(
                ft.Text(f"Error: {str(ex)}"),
                open=True,
            )
            e.page.update()
    
    return ft.ElevatedButton(text, on_click=safe_handler)
```

### 8.2 Advanced Error Handling and Recovery

#### 8.2.1 Comprehensive Error Reporter

Advanced error tracking with context and recovery options:

```python
import traceback
import sys
from typing import Callable, Dict, Any

class ErrorReporter:
    def __init__(self):
        self.error_history = []
        self.error_handlers = {}
        self.max_errors = 100
    
    def register_error_handler(self, error_type: type, handler: Callable):
        """Register a handler for specific error types"""
        self.error_handlers[error_type] = handler
        debug_print(f"Registered error handler for {error_type.__name__}", "ERROR_HANDLING")
    
    def report_error(self, error: Exception, context: Dict[str, Any] = None):
        """Report and handle an error"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "handled": False
        }
        
        # Try to handle with registered handlers
        for error_type, handler in self.error_handlers.items():
            if isinstance(error, error_type):
                try:
                    handler(error, context)
                    error_info["handled"] = True
                    error_info["handler"] = error_type.__name__
                    debug_print(f"Error handled by {error_type.__name__} handler", "ERROR_HANDLED")
                    break
                except Exception as handler_error:
                    debug_print(f"Error handler failed: {handler_error}", "ERROR_HANDLER_FAILED")
        
        # Add to history
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_errors:
            self.error_history.pop(0)
        
        # Log the error
        debug_print(f"Error reported: {type(error).__name__}: {error}", "ERROR")
        debug_print(f"Context: {context}", "ERROR")
        
        return error_info
    
    def get_error_statistics(self) -> Dict:
        """Get error statistics"""
        if not self.error_history:
            return {"total_errors": 0}
        
        error_types = {}
        handled_count = 0
        
        for error in self.error_history:
            error_type = error["error_type"]
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1
            
            if error.get("handled", False):
                handled_count += 1
        
        return {
            "total_errors": len(self.error_history),
            "handled_errors": handled_count,
            "unhandled_errors": len(self.error_history) - handled_count,
            "error_types": error_types
        }
    
    def export_error_report(self, filename: str = None) -> str:
        """Export error report to file"""
        if not filename:
            filename = f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "statistics": self.get_error_statistics(),
            "errors": self.error_history
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            debug_print(f"Error report exported to {filename}", "ERROR_REPORT")
            return filename
        except Exception as ex:
            debug_print(f"Failed to export error report: {ex}", "ERROR")
            return None

# Global error reporter
error_reporter = ErrorReporter()

# Set up global exception handler
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't handle keyboard interrupts
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Report the error
    error_reporter.report_error(exc_value, {
        "exception_type": exc_type.__name__,
        "traceback": ''.join(traceback.format_tb(exc_traceback))
    })

# Register the global handler
sys.excepthook = global_exception_handler
```

#### 8.2.2 Auto-Recovery System

Implement automatic recovery from common errors:

```python
import time
from typing import Callable, Any

class AutoRecoverySystem:
    def __init__(self):
        self.recovery_strategies = {}
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
        self.recovery_cooldown = 60  # seconds
    
    def register_recovery_strategy(self, error_type: type, strategy: Callable, max_attempts: int = None):
        """Register a recovery strategy for specific error types"""
        self.recovery_strategies[error_type] = {
            "strategy": strategy,
            "max_attempts": max_attempts or self.max_recovery_attempts
        }
        debug_print(f"Registered recovery strategy for {error_type.__name__}", "RECOVERY")
    
    def attempt_recovery(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Attempt to recover from an error"""
        error_type = type(error)
        strategy_info = None
        
        # Find matching strategy
        for registered_type, info in self.recovery_strategies.items():
            if issubclass(error_type, registered_type):
                strategy_info = info
                break
        
        if not strategy_info:
            debug_print(f"No recovery strategy for {error_type.__name__}", "RECOVERY")
            return False
        
        # Check attempt limits
        error_key = f"{error_type.__name__}_{hash(str(context))}"
        attempts = self.recovery_attempts.get(error_key, 0)
        
        if attempts >= strategy_info["max_attempts"]:
            debug_print(f"Max recovery attempts exceeded for {error_type.__name__}", "RECOVERY")
            return False
        
        # Check cooldown
        last_attempt = self.recovery_attempts.get(f"{error_key}_last", 0)
        if time.time() - last_attempt < self.recovery_cooldown:
            debug_print(f"Recovery cooldown for {error_type.__name__}", "RECOVERY")
            return False
        
        # Attempt recovery
        try:
            self.recovery_attempts[error_key] = attempts + 1
            self.recovery_attempts[f"{error_key}_last"] = time.time()
            
            result = strategy_info["strategy"](error, context)
            
            if result:
                debug_print(f"Successful recovery from {error_type.__name__}", "RECOVERY_SUCCESS")
                # Reset attempt count on success
                self.recovery_attempts[error_key] = 0
                return True
            else:
                debug_print(f"Recovery attempt failed for {error_type.__name__}", "RECOVERY_FAILED")
                return False
                
        except Exception as recovery_error:
            debug_print(f"Recovery strategy failed: {recovery_error}", "RECOVERY_ERROR")
            return False

# Global auto-recovery system
recovery_system = AutoRecoverySystem()
```

## 9. Advanced UI Element Debugging

### 9.1 Comprehensive Control Event Tracker

Track all events for any Flet control:

```python
import uuid
from typing import Callable, Any

class ControlEventTracker:
    def __init__(self):
        self.tracked_controls = {}
        self.event_history = []
    
    def track_control(self, control, control_name: str = None):
        """Track all events for a control"""
        control_id = str(uuid.uuid4())[:8]
        control_name = control_name or f"Control_{control_id}"
        
        # Store control info
        self.tracked_controls[control_id] = {
            "control": control,
            "name": control_name,
            "events": [],
            "created_at": datetime.now().isoformat()
        }
        
        # Wrap existing event handlers
        self._wrap_event_handlers(control, control_id)
        
        debug_print(f"Started tracking control: {control_name} ({control_id})", "CONTROL_TRACKING")
        return control_id
    
    def _wrap_event_handlers(self, control, control_id: str):
        """Wrap existing event handlers with tracking"""
        event_attributes = [
            'on_click', 'on_change', 'on_hover', 'on_focus', 'on_blur',
            'on_keyboard_event', 'on_scroll', 'on_animation_end'
        ]
        
        for attr_name in event_attributes:
            if hasattr(control, attr_name):
                original_handler = getattr(control, attr_name)
                if callable(original_handler):
                    wrapped_handler = self._create_wrapped_handler(
                        original_handler, control_id, attr_name
                    )
                    setattr(control, attr_name, wrapped_handler)
    
    def _create_wrapped_handler(self, original_handler: Callable, control_id: str, event_type: str):
        """Create a wrapped event handler"""
        def wrapped_handler(e):
            # Record the event
            event_record = {
                "timestamp": datetime.now().isoformat(),
                "control_id": control_id,
                "event_type": event_type,
                "event_data": {
                    "control_uid": getattr(e.control, 'uid', 'unknown'),
                    "data": getattr(e, 'data', None),
                    "local_x": getattr(e, 'local_x', None),
                    "local_y": getattr(e, 'local_y', None)
                }
            }
            
            self.event_history.append(event_record)
            
            control_info = self.tracked_controls[control_id]
            control_info["events"].append(event_record)
            
            control_name = control_info["name"]
            debug_print(f"Control '{control_name}' received {event_type} event", "CONTROL_EVENT")
            
            # Call original handler
            try:
                return original_handler(e)
            except Exception as ex:
                debug_print(f"Error in {event_type} handler for {control_name}: {ex}", "ERROR")
                raise
        
        return wrapped_handler
    
    def get_control_events(self, control_id: str) -> list:
        """Get all events for a specific control"""
        if control_id in self.tracked_controls:
            return self.tracked_controls[control_id]["events"]
        return []
    
    def get_all_events(self) -> list:
        """Get all tracked events"""
        return self.event_history

# Global control event tracker
control_tracker = ControlEventTracker()
```

### 9.2 Visual Debug Overlay

Create a debug overlay that shows real-time information:

```python
class DebugOverlay:
    def __init__(self, page: ft.Page):
        self.page = page
        self.overlay_visible = False
        self.debug_info = ft.Column([], scroll=ft.ScrollMode.AUTO)
        
        # Create overlay container
        self.overlay = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Debug Overlay", size=16, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.icons.CLOSE,
                        on_click=self.hide_overlay
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.debug_info,
                ft.Divider(),
                ft.ElevatedButton("Refresh", on_click=self.refresh_debug_info),
                ft.ElevatedButton("Export Logs", on_click=self.export_logs)
            ]),
            width=300,
            height=400,
            bgcolor=ft.colors.BLACK87,
            border_radius=10,
            padding=10,
            right=20,
            top=20,
            visible=False,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.colors.BLACK54
            )
        )
        
        # Add toggle button
        self.toggle_button = ft.FloatingActionButton(
            icon=ft.icons.BUG_REPORT,
            on_click=self.toggle_overlay,
            tooltip="Toggle Debug Overlay"
        )
        
        # Add to page
        page.overlay.append(self.overlay)
        page.add(self.toggle_button)
        page.update()
    
    def toggle_overlay(self, e):
        """Toggle debug overlay visibility"""
        self.overlay_visible = not self.overlay_visible
        self.overlay.visible = self.overlay_visible
        self.page.update()
        debug_print(f"Debug overlay {'shown' if self.overlay_visible else 'hidden'}", "UI")
    
    def hide_overlay(self, e):
        """Hide the debug overlay"""
        self.overlay_visible = False
        self.overlay.visible = False
        self.page.update()
    
    def refresh_debug_info(self, e):
        """Refresh debug information"""
        # Clear existing info
        self.debug_info.controls.clear()
        
        # Add current state info
        state_info = state_tracker.current_state
        self.debug_info.controls.append(
            ft.Text(f"Current State ({len(state_info)} items):", weight=ft.FontWeight.BOLD)
        )
        
        for key, value in list(state_info.items())[-10:]:  # Show last 10 items
            self.debug_info.controls.append(
                ft.Text(f"  {key}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
            )
        
        # Add recent events
        recent_events = list(event_timeline.events)[-5:]  # Last 5 events
        self.debug_info.controls.append(
            ft.Text(f"\nRecent Events ({len(recent_events)}):", weight=ft.FontWeight.BOLD)
        )
        
        for event in recent_events:
            self.debug_info.controls.append(
                ft.Text(f"  [{event['elapsed_seconds']:.3f}s] {event['type']}: {event['description'][:30]}...")
            )
        
        self.page.update()
    
    def export_logs(self, e):
        """Export debug logs to file"""
        try:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "state": state_tracker.export_state_snapshot(),
                "events": list(event_timeline.events),
                "control_events": control_tracker.get_all_events()
            }
            
            filename = f"flet_debug_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(log_data, f, indent=2, default=str)
            
            debug_print(f"Debug logs exported to {filename}", "EXPORT")
            
            # Show confirmation
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Debug logs exported to {filename}"),
                open=True,
            )
            self.page.update()
            
        except Exception as ex:
            debug_print(f"Error exporting logs: {ex}", "ERROR")

# Global debug overlay instance
debug_overlay = None
```

## 10. Performance Monitoring and Profiling

### 10.1 Performance Timer

Track performance of operations:

```python
import time

class PerformanceTimer:
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        debug_log(f"Starting operation: {self.operation_name}", "PERF")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        duration = end_time - self.start_time
        if exc_type is None:
            debug_log(f"Operation '{self.operation_name}' completed in {duration:.4f}s", "PERF")
        else:
            debug_log(f"Operation '{self.operation_name}' failed after {duration:.4f}s: {exc_val}", "PERF")

# Usage:
# with PerformanceTimer("Data Processing"):
#     # Your operation here
#     process_data()
```

### 10.2 Function Performance Profiler

Profile function performance with detailed metrics:

```python
import functools
import time
from collections import defaultdict

class PerformanceProfiler:
    def __init__(self):
        self.function_stats = defaultdict(list)
        self.call_stack = []
    
    def profile(self, func_name: str = None):
        """Decorator to profile function performance"""
        def decorator(func):
            nonlocal func_name
            if func_name is None:
                func_name = func.__name__
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                call_id = f"{func_name}_{len(self.call_stack)}"
                
                # Track call entry
                self.call_stack.append({
                    "id": call_id,
                    "function": func_name,
                    "start_time": start_time,
                    "args": args,
                    "kwargs": kwargs
                })
                
                try:
                    result = func(*args, **kwargs)
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    
                    # Record statistics
                    self.function_stats[func_name].append({
                        "duration": duration,
                        "timestamp": datetime.now().isoformat(),
                        "success": True
                    })
                    
                    debug_print(f"Function '{func_name}' executed in {duration:.4f}s", "PERFORMANCE")
                    return result
                    
                except Exception as ex:
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    
                    self.function_stats[func_name].append({
                        "duration": duration,
                        "timestamp": datetime.now().isoformat(),
                        "success": False,
                        "error": str(ex)
                    })
                    
                    debug_print(f"Function '{func_name}' failed after {duration:.4f}s: {ex}", "PERFORMANCE_ERROR")
                    raise
                finally:
                    # Remove from call stack
                    if self.call_stack:
                        self.call_stack.pop()
            
            return wrapper
        return decorator
    
    def get_function_stats(self, func_name: str = None) -> Dict:
        """Get performance statistics"""
        if func_name:
            calls = self.function_stats[func_name]
            if not calls:
                return {"function": func_name, "calls": 0}
            
            durations = [call["duration"] for call in calls if call["success"]]
            return {
                "function": func_name,
                "calls": len(calls),
                "successful_calls": len(durations),
                "failed_calls": len(calls) - len(durations),
                "avg_duration": sum(durations) / len(durations) if durations else 0,
                "min_duration": min(durations) if durations else 0,
                "max_duration": max(durations) if durations else 0,
                "total_duration": sum(durations)
            }
        
        # Return stats for all functions
        return {name: self.get_function_stats(name) for name in self.function_stats.keys()}
    
    def reset_stats(self):
        """Reset all collected statistics"""
        self.function_stats.clear()
        debug_print("Performance statistics reset", "PERFORMANCE")

# Global profiler
profiler = PerformanceProfiler()
```

### 10.3 Memory Usage Monitor

Monitor application memory usage:

```python
import psutil
import gc
import threading

class MemoryMonitor:
    def __init__(self, interval: float = 5.0):
        self.interval = interval
        self.monitoring = False
        self.memory_history = []
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start memory monitoring in background thread"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        debug_print("Memory monitoring started", "MEMORY")
    
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        debug_print("Memory monitoring stopped", "MEMORY")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        process = psutil.Process()
        
        while self.monitoring:
            try:
                # Get memory info
                memory_info = process.memory_info()
                memory_percent = process.memory_percent()
                
                # Get garbage collector stats
                gc_stats = gc.get_stats()
                
                # Record memory snapshot
                snapshot = {
                    "timestamp": datetime.now().isoformat(),
                    "rss": memory_info.rss,  # Resident Set Size
                    "vms": memory_info.vms,  # Virtual Memory Size
                    "percent": memory_percent,
                    "gc_collections": sum(stat['collections'] for stat in gc_stats)
                }
                
                self.memory_history.append(snapshot)
                
                # Log if memory usage is high
                if memory_percent > 80:
                    debug_print(f"High memory usage: {memory_percent:.1f}%", "MEMORY_WARNING")
                
                time.sleep(self.interval)
                
            except Exception as ex:
                debug_print(f"Memory monitoring error: {ex}", "MEMORY_ERROR")
                time.sleep(self.interval)
    
    def get_current_memory_usage(self) -> Dict:
        """Get current memory usage"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent(),
                "num_threads": process.num_threads()
            }
        except Exception as ex:
            debug_print(f"Error getting memory usage: {ex}", "MEMORY_ERROR")
            return {}
    
    def get_memory_history(self, limit: int = 50) -> list:
        """Get memory usage history"""
        return self.memory_history[-limit:] if self.memory_history else []

# Global memory monitor
memory_monitor = MemoryMonitor()
```

### 10.4 Memory Usage Monitor (Basic)

Monitor memory usage with a simpler approach:

```python
def log_memory_usage():
    """Log current memory usage"""
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        debug_log(f"Memory usage: {memory_mb:.2f} MB", "MEMORY")
    except ImportError:
        debug_log("psutil not available for memory monitoring", "MEMORY")
```

## 11. File and Storage Debugging

### 11.1 File Operation Tracking

Track file operations:

```python
import os

def debug_file_operation(operation, filepath, result=None):
    """Debug file operations"""
    file_exists = os.path.exists(filepath)
    file_size = os.path.getsize(filepath) if file_exists else 0
    debug_log(f"File {operation}: {filepath} (exists: {file_exists}, size: {file_size} bytes)", "FILE")
    if result:
        debug_log(f"  Result: {result}", "FILE")

def debug_read_file(filepath):
    """Debug file reading"""
    try:
        debug_file_operation("READ", filepath)
        with open(filepath, 'r') as f:
            content = f.read()
            debug_log(f"  Read {len(content)} characters", "FILE")
            return content
    except Exception as ex:
        debug_log(f"  Error reading file: {ex}", "FILE_ERROR")
        raise

def debug_write_file(filepath, content):
    """Debug file writing"""
    try:
        debug_file_operation("WRITE", filepath)
        with open(filepath, 'w') as f:
            f.write(content)
            debug_log(f"  Wrote {len(content)} characters", "FILE")
    except Exception as ex:
        debug_log(f"  Error writing file: {ex}", "FILE_ERROR")
        raise
```

## 12. Network and API Debugging

### 12.1 API Call Tracking

Track API calls and responses:

```python
import json

def debug_api_call(method, url, data=None, headers=None):
    """Debug API calls"""
    debug_log(f"API CALL: {method} {url}", "API")
    if data:
        debug_log(f"  Request data: {json.dumps(data, indent=2)}", "API")
    if headers:
        debug_log(f"  Headers: {headers}", "API")

def debug_api_response(status_code, response_data):
    """Debug API responses"""
    debug_log(f"API RESPONSE: Status {status_code}", "API")
    if response_data:
        debug_log(f"  Response data: {json.dumps(response_data, indent=2)}", "API")
```

## 13. Integration with External Debugging Tools

### 13.1 Remote Debugging Server

Set up a remote debugging interface:

```python
import socket
import threading
import json
from typing import Dict, Any

class RemoteDebugServer:
    def __init__(self, host: str = 'localhost', port: int = 9999):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.running = False
        self.command_handlers = {}
        
        # Register default command handlers
        self.register_command_handler("get_state", self._handle_get_state)
        self.register_command_handler("get_events", self._handle_get_events)
        self.register_command_handler("get_errors", self._handle_get_errors)
        self.register_command_handler("execute_command", self._handle_execute_command)
    
    def register_command_handler(self, command: str, handler: Callable):
        """Register a handler for remote commands"""
        self.command_handlers[command] = handler
        debug_print(f"Registered remote command handler: {command}", "REMOTE_DEBUG")
    
    def start_server(self):
        """Start the remote debugging server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            debug_print(f"Remote debug server started on {self.host}:{self.port}", "REMOTE_DEBUG")
            
            # Start server thread
            server_thread = threading.Thread(target=self._server_loop, daemon=True)
            server_thread.start()
            
        except Exception as ex:
            debug_print(f"Failed to start remote debug server: {ex}", "REMOTE_DEBUG_ERROR")
    
    def stop_server(self):
        """Stop the remote debugging server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        debug_print("Remote debug server stopped", "REMOTE_DEBUG")
    
    def _server_loop(self):
        """Main server loop"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                debug_print(f"Remote debug client connected from {address}", "REMOTE_DEBUG")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as ex:
                if self.running:
                    debug_print(f"Error accepting client: {ex}", "REMOTE_DEBUG_ERROR")
    
    def _handle_client(self, client_socket, address):
        """Handle a connected client"""
        try:
            while self.running:
                # Receive command
                data = client_socket.recv(4096)
                if not data:
                    break
                
                try:
                    command_data = json.loads(data.decode('utf-8'))
                    command = command_data.get("command")
                    params = command_data.get("params", {})
                    
                    # Execute command
                    if command in self.command_handlers:
                        result = self.command_handlers[command](params)
                        response = {"status": "success", "result": result}
                    else:
                        response = {"status": "error", "message": f"Unknown command: {command}"}
                
                except json.JSONDecodeError:
                    response = {"status": "error", "message": "Invalid JSON"}
                except Exception as ex:
                    response = {"status": "error", "message": str(ex)}
                
                # Send response
                client_socket.send(json.dumps(response).encode('utf-8'))
                
        except Exception as ex:
            debug_print(f"Error handling client {address}: {ex}", "REMOTE_DEBUG_ERROR")
        finally:
            client_socket.close()
            debug_print(f"Remote debug client {address} disconnected", "REMOTE_DEBUG")
    
    # Default command handlers
    def _handle_get_state(self, params: Dict) -> Dict:
        """Handle get_state command"""
        return {
            "current_state": state_tracker.current_state,
            "state_history": state_tracker.get_state_history(params.get("limit", 10))
        }
    
    def _handle_get_events(self, params: Dict) -> Dict:
        """Handle get_events command"""
        return {
            "recent_events": list(event_timeline.events)[-params.get("limit", 50):],
            "performance_stats": event_timeline.get_performance_stats()
        }
    
    def _handle_get_errors(self, params: Dict) -> Dict:
        """Handle get_errors command"""
        return {
            "recent_errors": error_reporter.error_history[-params.get("limit", 10):],
            "error_statistics": error_reporter.get_error_statistics()
        }
    
    def _handle_execute_command(self, params: Dict) -> Dict:
        """Handle execute_command command"""
        command = params.get("command")
        if command == "clear_state":
            state_tracker.current_state.clear()
            state_tracker.previous_state.clear()
            return {"message": "State cleared"}
        elif command == "reset_profiler":
            profiler.reset_stats()
            return {"message": "Profiler reset"}
        elif command == "export_logs":
            filename = error_reporter.export_error_report()
            return {"message": f"Logs exported to {filename}"}
        else:
            return {"message": f"Unknown execution command: {command}"}

# Global remote debug server
remote_debug_server = RemoteDebugServer()
```

### 13.2 Remote Debugging Client Example

```python
# Example remote debugging client
import socket
import json

def send_remote_command(host: str, port: int, command: str, params: Dict = None):
    """Send a command to the remote debug server"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        command_data = {
            "command": command,
            "params": params or {}
        }
        
        client_socket.send(json.dumps(command_data).encode('utf-8'))
        response_data = client_socket.recv(8192)
        response = json.loads(response_data.decode('utf-8'))
        
        client_socket.close()
        return response
        
    except Exception as ex:
        print(f"Remote command failed: {ex}")
        return None

# Example usage:
# Get current application state
# state_response = send_remote_command('localhost', 9999, 'get_state', {'limit': 20})
# 
# Get recent events
# events_response = send_remote_command('localhost', 9999, 'get_events', {'limit': 100})
# 
# Execute commands
# execute_response = send_remote_command('localhost', 9999, 'execute_command', {'command': 'clear_state'})
```

## 14. Complete Advanced Debugging Integration

### 14.1 Master Debug Controller

Integrate all advanced debugging components:

```python
class MasterDebugController:
    def __init__(self):
        self.components = {
            "state_tracker": state_tracker,
            "event_timeline": event_timeline,
            "control_tracker": control_tracker,
            "profiler": profiler,
            "memory_monitor": memory_monitor,
            "error_reporter": error_reporter,
            "recovery_system": recovery_system,
            "remote_server": remote_debug_server
        }
        self.enabled_features = set()
    
    def enable_feature(self, feature_name: str):
        """Enable a debugging feature"""
        if feature_name in self.components:
            self.enabled_features.add(feature_name)
            debug_print(f"Enabled debugging feature: {feature_name}", "MASTER_DEBUG")
            
            # Start components that need initialization
            if feature_name == "memory_monitor":
                memory_monitor.start_monitoring()
            elif feature_name == "remote_server":
                remote_debug_server.start_server()
    
    def disable_feature(self, feature_name: str):
        """Disable a debugging feature"""
        if feature_name in self.enabled_features:
            self.enabled_features.remove(feature_name)
            debug_print(f"Disabled debugging feature: {feature_name}", "MASTER_DEBUG")
            
            # Stop components that need cleanup
            if feature_name == "memory_monitor":
                memory_monitor.stop_monitoring()
            elif feature_name == "remote_server":
                remote_debug_server.stop_server()
    
    def get_system_status(self) -> Dict:
        """Get status of all debugging components"""
        status = {}
        for name, component in self.components.items():
            status[name] = {
                "enabled": name in self.enabled_features,
                "component": str(component)
            }
        return status
    
    def export_full_debug_report(self, filename: str = None) -> str:
        """Export a comprehensive debug report"""
        if not filename:
            filename = f"full_debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "system_status": self.get_system_status(),
            "state_data": {
                "current_state": state_tracker.current_state,
                "state_history": state_tracker.changes
            },
            "event_data": {
                "timeline": list(event_timeline.events),
                "performance_stats": event_timeline.get_performance_stats()
            },
            "error_data": {
                "errors": error_reporter.error_history,
                "error_stats": error_reporter.get_error_statistics()
            },
            "performance_data": {
                "function_stats": profiler.get_function_stats(),
                "memory_usage": memory_monitor.get_current_memory_usage()
            }
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            debug_print(f"Full debug report exported to {filename}", "MASTER_DEBUG")
            return filename
        except Exception as ex:
            debug_print(f"Failed to export full debug report: {ex}", "MASTER_DEBUG_ERROR")
            return None

# Global master debug controller
debug_controller = MasterDebugController()
```

## 15. Usage Examples and Best Practices

### 15.1 Enabling Advanced Debugging in Your App

```python
def setup_advanced_debugging(page: ft.Page):
    """Set up advanced debugging for your Flet application"""
    
    # Enable specific debugging features
    debug_controller.enable_feature("state_tracker")
    debug_controller.enable_feature("event_timeline")
    debug_controller.enable_feature("control_tracker")
    debug_controller.enable_feature("profiler")
    debug_controller.enable_feature("memory_monitor")
    debug_controller.enable_feature("error_reporter")
    debug_controller.enable_feature("recovery_system")
    
    # Start remote debugging server for external tools
    debug_controller.enable_feature("remote_server")
    
    # Set up error handlers
    def handle_network_error(error, context):
        debug_print(f"Handling network error: {error}", "RECOVERY")
        # Implement retry logic or fallback behavior
        return True  # Indicate successful handling
    
    def handle_ui_error(error, context):
        debug_print(f"Handling UI error: {error}", "RECOVERY")
        # Reset UI state or show error message
        return True
    
    # Register recovery strategies
    recovery_system.register_recovery_strategy(ConnectionError, handle_network_error)
    recovery_system.register_recovery_strategy(Exception, handle_ui_error, max_attempts=5)
    
    # Track important controls
    # control_tracker.track_control(your_important_button, "MainActionButton")
    
    # Set up profiling for critical functions
    # @profiler.profile("data_processing")
    # def process_data():
    #     # Your data processing logic
    #     pass
    
    debug_print("Advanced debugging system initialized", "MASTER_DEBUG")

# Example usage in main function
def main(page: ft.Page):
    # Set up basic debugging
    page.debug = True
    
    # Set up advanced debugging
    setup_advanced_debugging(page)
    
    # Your application code here
    # ...
    
    # Export debug report on demand or periodically
    # debug_controller.export_full_debug_report()

ft.app(target=main)
```

### 15.2 Complete Debugging Example

Here's a complete example that incorporates all debugging techniques:

```python
import flet as ft
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any
import uuid

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def debug_log(message: str, level: str = "INFO"):
    """Custom debug logging function"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{level}] {message}")

# Global state trackers
class AppState:
    def __init__(self):
        self.counter = 0
        self.user_input = ""
        self.button_clicks = 0
        self.checkbox_states = {}
        self.dropdown_selection = None
        self.switch_states = {}

app_state = AppState()

class StateTracker:
    def __init__(self):
        self.state_history = []
    
    def log_state_change(self, key: str, old_value: Any, new_value: Any):
        self.state_history.append({
            "timestamp": datetime.now().isoformat(),
            "key": key,
            "old_value": old_value,
            "new_value": new_value
        })
        debug_log(f"State '{key}': {old_value} -> {new_value}", "STATE")

state_tracker = StateTracker()

class EventTracker:
    def __init__(self):
        self.event_history = []
    
    def log_event(self, event_type: str, details: str, data: Dict = None):
        self.event_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details,
            "data": data or {}
        })
        debug_log(f"{event_type}: {details}", event_type.upper())

event_tracker = EventTracker()

# Performance timer
class PerformanceTimer:
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        debug_log(f"Starting operation: {self.operation_name}", "PERF")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        duration = end_time - self.start_time
        if exc_type is None:
            debug_log(f"Operation '{self.operation_name}' completed in {duration:.4f}s", "PERF")
        else:
            debug_log(f"Operation '{self.operation_name}' failed after {duration:.4f}s: {exc_val}", "PERF_ERROR")

# Error handling
class ErrorHandler:
    def __init__(self):
        self.errors = []
    
    def handle_error(self, error: Exception, context: str = ""):
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
            "context": context
        }
        self.errors.append(error_info)
        debug_log(f"Error in {context}: {error}", "ERROR")

error_handler = ErrorHandler()

# Main application
def main(page: ft.Page):
    # Enable page debugging
    page.debug = True
    
    # Set up page event handlers
    def on_app_lifecycle_change(e):
        debug_log(f"App lifecycle changed to: {e.state}", "LIFECYCLE")
        event_tracker.log_event("LIFECYCLE", f"State changed to {e.state}")
    
    def on_route_change(e):
        debug_log(f"Route changed to: {e.route}", "ROUTE")
        event_tracker.log_event("ROUTE", f"Changed to {e.route}")
    
    def on_view_pop(e):
        debug_log("View popped", "NAVIGATION")
        event_tracker.log_event("NAVIGATION", "View popped")
    
    def on_error(e):
        debug_log(f"Page error: {e}", "ERROR")
        error_handler.handle_error(Exception(str(e)), "Page error")
    
    def on_keyboard(e: ft.KeyboardEvent):
        debug_log(f"Keyboard: key={e.key}, ctrl={e.ctrl}, shift={e.shift}", "KEYBOARD")
        event_tracker.log_event("KEYBOARD", f"Key {e.key} pressed")
    
    # Assign event handlers
    page.on_app_lifecycle_change = on_app_lifecycle_change
    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop
    page.on_error = on_error
    page.on_keyboard_event = on_keyboard
    
    debug_log("Application started", "INIT")
    event_tracker.log_event("APP", "Application started")
    
    # UI Event Handlers
    def increment_counter(e):
        with PerformanceTimer("increment_counter"):
            old_value = app_state.counter
            app_state.counter += 1
            app_state.button_clicks += 1
            
            state_tracker.log_state_change("counter", old_value, app_state.counter)
            event_tracker.log_event("CLICK", f"Increment button clicked, count={app_state.counter}")
            
            counter_text.value = str(app_state.counter)
            click_counter_text.value = f"Total clicks: {app_state.button_clicks}"
            page.update()
    
    def decrement_counter(e):
        with PerformanceTimer("decrement_counter"):
            old_value = app_state.counter
            app_state.counter -= 1
            app_state.button_clicks += 1
            
            state_tracker.log_state_change("counter", old_value, app_state.counter)
            event_tracker.log_event("CLICK", f"Decrement button clicked, count={app_state.counter}")
            
            counter_text.value = str(app_state.counter)
            click_counter_text.value = f"Total clicks: {app_state.button_clicks}"
            page.update()
    
    def on_textfield_change(e):
        old_value = app_state.user_input
        app_state.user_input = e.control.value
        state_tracker.log_state_change("user_input", old_value, app_state.user_input)
        event_tracker.log_event("INPUT", f"TextField changed to '{e.control.value}'")
        debug_log(f"TextField value: '{e.control.value}'", "INPUT")
    
    def on_checkbox_change(e):
        checkbox_name = e.control.data or "Unnamed"
        old_value = app_state.checkbox_states.get(checkbox_name, False)
        new_value = e.control.value
        app_state.checkbox_states[checkbox_name] = new_value
        state_tracker.log_state_change(f"checkbox_{checkbox_name}", old_value, new_value)
        event_tracker.log_event("INPUT", f"Checkbox '{checkbox_name}' changed to {new_value}")
        debug_log(f"Checkbox '{checkbox_name}' is now {'checked' if new_value else 'unchecked'}", "INPUT")
    
    def on_dropdown_change(e):
        old_value = app_state.dropdown_selection
        new_value = e.control.value
        app_state.dropdown_selection = new_value
        state_tracker.log_state_change("dropdown_selection", old_value, new_value)
        event_tracker.log_event("INPUT", f"Dropdown changed to '{new_value}'")
        debug_log(f"Dropdown selection: {new_value}", "INPUT")
    
    def on_switch_change(e):
        switch_name = e.control.data or "Unnamed"
        old_value = app_state.switch_states.get(switch_name, False)
        new_value = e.control.value
        app_state.switch_states[switch_name] = new_value
        state_tracker.log_state_change(f"switch_{switch_name}", old_value, new_value)
        event_tracker.log_event("INPUT", f"Switch '{switch_name}' changed to {new_value}")
        debug_log(f"Switch '{switch_name}' is now {'ON' if new_value else 'OFF'}", "INPUT")
    
    def on_container_click(e):
        event_tracker.log_event("CLICK", f"Container clicked at ({e.local_x}, {e.local_y})")
        debug_log(f"Container clicked at ({e.local_x}, {e.local_y})", "CLICK")
        e.control.bgcolor = ft.colors.PINK_ACCENT_400
        e.control.update()
    
    def on_container_hover(e):
        hover_state = "entered" if e.data == "true" else "left"
        event_tracker.log_event("HOVER", f"Container hover {hover_state}")
        debug_log(f"Container hover {hover_state}", "HOVER")
        e.control.bgcolor = ft.colors.BLUE_GREY_100 if e.data == "true" else ft.colors.BLUE_ACCENT_100
        e.control.update()
    
    def simulate_error(e):
        try:
            with PerformanceTimer("simulate_error"):
                event_tracker.log_event("ACTION", "Simulating error")
                debug_log("Simulating error...", "ACTION")
                # This will intentionally cause an error
                result = 10 / 0
        except Exception as ex:
            error_handler.handle_error(ex, "simulate_error")
            debug_log(f"Caught error: {ex}", "ERROR_HANDLED")
            page.snack_bar = ft.SnackBar(ft.Text(f"Error caught: {str(ex)}"), open=True)
            page.update()
    
    def show_debug_info(e):
        with PerformanceTimer("show_debug_info"):
            debug_info = {
                "app_state": {
                    "counter": app_state.counter,
                    "user_input": app_state.user_input,
                    "button_clicks": app_state.button_clicks,
                    "checkbox_states": app_state.checkbox_states,
                    "dropdown_selection": app_state.dropdown_selection,
                    "switch_states": app_state.switch_states
                },
                "state_history_count": len(state_tracker.state_history),
                "event_history_count": len(event_tracker.event_history),
                "error_count": len(error_handler.errors)
            }
            
            debug_log("=== DEBUG INFO ===", "DEBUG")
            debug_log(f"App State: {json.dumps(debug_info, indent=2)}", "DEBUG")
            debug_log("===================", "DEBUG")
            
            # Show in UI
            page.dialog = ft.AlertDialog(
                title=ft.Text("Debug Information"),
                content=ft.Text(json.dumps(debug_info, indent=2)),
                scrollable=True,
            )
            page.dialog.open = True
            page.update()
    
    def export_debug_report(e):
        with PerformanceTimer("export_debug_report"):
            debug_log("Exporting debug report...", "EXPORT")
            try:
                report_data = {
                    "timestamp": datetime.now().isoformat(),
                    "app_state": vars(app_state),
                    "state_history": state_tracker.state_history,
                    "event_history": event_tracker.event_history,
                    "errors": error_handler.errors
                }
                
                filename = f"debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(report_data, f, indent=2, default=str)
                
                debug_log(f"Debug report exported to {filename}", "EXPORT")
                page.snack_bar = ft.SnackBar(ft.Text(f"Report exported to {filename}"), open=True)
                page.update()
                
            except Exception as ex:
                error_handler.handle_error(ex, "export_debug_report")
                debug_log(f"Export error: {ex}", "EXPORT_ERROR")
    
    # UI Elements
    counter_text = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)
    click_counter_text = ft.Text(f"Total clicks: {app_state.button_clicks}")
    
    text_field = ft.TextField(
        label="Enter text", 
        on_change=on_textfield_change,
        hint_text="Type something here..."
    )
    
    checkbox1 = ft.Checkbox(
        label="Option 1", 
        data="option1",
        on_change=on_checkbox_change
    )
    
    checkbox2 = ft.Checkbox(
        label="Option 2", 
        data="option2",
        on_change=on_checkbox_change
    )
    
    dropdown = ft.Dropdown(
        label="Select an option",
        options=[
            ft.dropdown.Option("Option A"),
            ft.dropdown.Option("Option B"),
            ft.dropdown.Option("Option C"),
        ],
        on_change=on_dropdown_change
    )
    
    switch1 = ft.Switch(
        label="Feature 1", 
        data="feature1",
        on_change=on_switch_change
    )
    
    switch2 = ft.Switch(
        label="Feature 2", 
        data="feature2",
        on_change=on_switch_change
    )
    
    hover_container = ft.Container(
        content=ft.Text("Hover and click me"),
        alignment=ft.alignment.center,
        width=200,
        height=100,
        bgcolor=ft.colors.BLUE_ACCENT_100,
        border_radius=5,
        on_click=on_container_click,
        on_hover=on_container_hover
    )
    
    # Layout
    page.add(
        ft.Text("Flet Debugging Example", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        
        ft.Text("Counter Controls:", size=18, weight=ft.FontWeight.W_500),
        ft.Row([
            ft.IconButton(ft.icons.REMOVE, on_click=decrement_counter),
            counter_text,
            ft.IconButton(ft.icons.ADD, on_click=increment_counter),
        ]),
        click_counter_text,
        ft.Divider(),
        
        ft.Text("Input Controls:", size=18, weight=ft.FontWeight.W_500),
        text_field,
        ft.Row([checkbox1, checkbox2]),
        dropdown,
        ft.Row([switch1, switch2]),
        ft.Divider(),
        
        ft.Text("Interactive Elements:", size=18, weight=ft.FontWeight.W_500),
        hover_container,
        ft.Divider(),
        
        ft.Text("Debug Actions:", size=18, weight=ft.FontWeight.W_500),
        ft.Row([
            ft.ElevatedButton("Show Debug Info", on_click=show_debug_info),
            ft.ElevatedButton("Simulate Error", on_click=simulate_error),
            ft.ElevatedButton("Export Debug Report", on_click=export_debug_report),
        ]),
        ft.Divider(),
        
        ft.Text("Instructions:", size=16, weight=ft.FontWeight.W_500),
        ft.Column([
            ft.Text("• All debug information is printed to the terminal"),
            ft.Text("• Try clicking buttons, typing in fields, and hovering over elements"),
            ft.Text("• Press any key to see keyboard events"),
            ft.Text("• Click 'Simulate Error' to test error handling"),
            ft.Text("• Click 'Show Debug Info' to see current application state"),
            ft.Text("• Click 'Export Debug Report' to save a JSON debug report"),
        ])
    )
    
    debug_log("UI initialized", "INIT")

# Run the application
if __name__ == "__main__":
    debug_log("Starting Flet debugging example...", "STARTUP")
    ft.app(target=main)
```

## 16. Best Practices Summary

### 16.1 Debugging Best Practices

1. **Use consistent logging format**: Always include timestamps and log levels
2. **Categorize log messages**: Use different categories (STATE, CLICK, INPUT, ERROR, etc.)
3. **Track state changes**: Monitor all important application state changes
4. **Handle errors gracefully**: Always wrap handlers in try-catch blocks
5. **Use meaningful log messages**: Include context and relevant data in logs
6. **Monitor performance**: Track operation durations and resource usage
7. **Enable/disable selectively**: Use environment variables to control debug output

### 16.2 Environment Variables for Debug Control

```bash
# Enable debug logging
export FLET_LOG_LEVEL=debug

# Disable rich output for cleaner logs
export FLET_CLI_NO_RICH_OUTPUT=true

# Redirect logs to file
export FLET_LOG_TO_FILE=true
```

### 16.3 Production Considerations

For production, reduce logging verbosity:

```python
import logging
import os

# In production, use INFO level
if os.getenv("ENVIRONMENT") == "production":
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)
```

### 16.4 Quick Debug Panel

```python
def create_debug_panel(page):
    def show_debug_info(e):
        debug_info = f"""
State: {state_tracker.state}
Events: {len(getattr(event_timeline, 'events', []))}
Errors: {len(getattr(error_reporter, 'error_history', []))}
        """.strip()
        debug_log(debug_info, "DEBUG_PANEL")
    
    return ft.Row([
        ft.ElevatedButton("Debug Info", on_click=show_debug_info),
        ft.ElevatedButton("Export Logs", on_click=lambda e: debug_log("Exporting logs...", "EXPORT"))
    ])
```

## 17. Flet Debugging Implementation Checklist

This checklist guides you through implementing comprehensive debugging in your existing Flet application. Follow these steps in order for the most effective debugging setup.

### Pre-Implementation Preparation

- [ ] **Backup your current code** before implementing debugging features
- [ ] **Review existing error handling** to identify gaps
- [ ] **Identify critical components** that need debugging (state management, user interactions, data flows)
- [ ] **Determine debugging level needed** (basic logging vs. advanced monitoring)
- [ ] **Set up development environment variables** for debugging

### Phase 1: Basic Debugging Setup

#### 1.1 Enable Core Debugging
- [ ] Add `import logging` and `logging.basicConfig(level=logging.DEBUG)` to main file
- [ ] Set `page.debug = True` in your main function
- [ ] Implement basic debug print function:
```python
from datetime import datetime

def debug_log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{level}] {message}")
```

#### 1.2 Add Page Event Handlers
- [ ] Add page lifecycle change handler:
```python
def on_app_lifecycle_change(e):
    debug_log(f"App lifecycle changed to: {e.state}", "LIFECYCLE")
page.on_app_lifecycle_change = on_app_lifecycle_change
```
- [ ] Add route change handler:
```python
def on_route_change(e):
    debug_log(f"Route changed to: {e.route}", "ROUTE")
page.on_route_change = on_route_change
```
- [ ] Add error handler:
```python
def on_error(e):
    debug_log(f"Page error: {e}", "ERROR")
page.on_error = on_error
```
- [ ] Add keyboard event handler:
```python
def on_keyboard(e: ft.KeyboardEvent):
    debug_log(f"Keyboard event: key={e.key}, ctrl={e.ctrl}", "KEYBOARD")
page.on_keyboard_event = on_keyboard
```

### Phase 2: UI Component Debugging

#### 2.1 Button Click Tracking
- [ ] Wrap existing button click handlers:
```python
# Instead of: on_click=my_handler
# Use:
def debug_button_handler(e):
    debug_log(f"Button clicked: {e.control.text if hasattr(e.control, 'text') else 'Unnamed'}", "CLICK")
    # Call original handler
    my_handler(e)
```

#### 2.2 Input Field Change Tracking
- [ ] Add change handlers to TextFields:
```python
def on_textfield_change(e):
    debug_log(f"TextField '{e.control.label}' changed to: '{e.control.value}'", "INPUT")
    # Call original handler if exists
    if hasattr(e.control, '_original_on_change') and e.control._original_on_change:
        e.control._original_on_change(e)
```

#### 2.3 Checkbox/Radio/Switch State Tracking
- [ ] Add change handlers:
```python
def on_checkbox_change(e):
    checkbox_name = getattr(e.control, 'data', 'Unnamed')
    debug_log(f"Checkbox '{checkbox_name}' is now {'checked' if e.control.value else 'unchecked'}", "INPUT")
```

#### 2.4 Dropdown Selection Tracking
- [ ] Add change handlers:
```python
def on_dropdown_change(e):
    debug_log(f"Dropdown '{e.control.label}' selection changed to: {e.control.value}", "INPUT")
```

#### 2.5 Container Interaction Tracking
- [ ] Add click and hover handlers:
```python
def on_container_click(e):
    debug_log(f"Container clicked at position: ({e.local_x}, {e.local_y})", "CLICK")

def on_container_hover(e):
    hover_state = "entered" if e.data == "true" else "left"
    debug_log(f"Container hover {hover_state}", "HOVER")
```

### Phase 3: State Management Debugging

#### 3.1 Implement State Tracker
- [ ] Create state tracking class:
```python
class StateTracker:
    def __init__(self):
        self.current_state = {}
        self.state_history = []
    
    def update_state(self, key, value):
        old_value = self.current_state.get(key)
        self.current_state[key] = value
        self.state_history.append({
            "timestamp": datetime.now().isoformat(),
            "key": key,
            "old_value": old_value,
            "new_value": value
        })
        debug_log(f"State '{key}': {old_value} -> {value}", "STATE")

# Global instance
state_tracker = StateTracker()
```

#### 3.2 Track Important State Changes
- [ ] Replace direct state assignments with tracked updates:
```python
# Instead of: app_state.counter += 1
# Use: state_tracker.update_state("counter", app_state.counter + 1)
```

### Phase 4: Error Handling Enhancement

#### 4.1 Implement Error Reporter
- [ ] Create error tracking class:
```python
import traceback

class ErrorReporter:
    def __init__(self):
        self.error_history = []
    
    def report_error(self, error, context=""):
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context
        }
        self.error_history.append(error_info)
        debug_log(f"Error in {context}: {error}", "ERROR")

error_reporter = ErrorReporter()
```

#### 4.2 Wrap Risky Operations
- [ ] Add try-catch blocks around risky operations:
```python
def safe_operation(e):
    try:
        # Original risky operation
        risky_function()
    except Exception as ex:
        error_reporter.report_error(ex, "safe_operation")
        # Show user-friendly error
        e.page.snack_bar = ft.SnackBar(ft.Text("An error occurred"), open=True)
        e.page.update()
```

### Phase 5: Performance Monitoring

#### 5.1 Add Performance Timing
- [ ] Create timing decorator:
```python
import time
import functools

def timed_function(func_name=None):
    def decorator(func):
        nonlocal func_name
        if func_name is None:
            func_name = func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                debug_log(f"Function '{func_name}' took {duration:.4f}s", "PERF")
                return result
            except Exception as ex:
                end_time = time.time()
                duration = end_time - start_time
                debug_log(f"Function '{func_name}' failed after {duration:.4f}s: {ex}", "PERF_ERROR")
                raise
        return wrapper
    return decorator
```

#### 5.2 Apply to Critical Functions
- [ ] Add timing to data-intensive operations:
```python
@timed_function("data_processing")
def process_data():
    # Your data processing logic
    pass
```

### Phase 6: Event and Interaction Tracking

#### 6.1 Implement Event Timeline
- [ ] Create event tracking class:
```python
class EventTimeline:
    def __init__(self):
        self.events = []
    
    def log_event(self, event_type, description, data=None):
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
            "data": data or {}
        }
        self.events.append(event)
        debug_log(f"{event_type}: {description}", event_type.upper())

event_timeline = EventTimeline()
```

#### 6.2 Track All Major Events
- [ ] Log user interactions, system events, and state changes:
```python
event_timeline.log_event("USER_ACTION", "Button clicked", {"button": "submit"})
```

### Phase 7: Advanced Features (Optional)

#### 7.1 Add Debug Overlay
- [ ] Create on-screen debug information panel:
```python
def create_debug_overlay(page):
    overlay = ft.Container(
        content=ft.Column([
            ft.Text("Debug Info", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("Click 'Refresh' to update"),
            ft.ElevatedButton("Refresh", on_click=lambda e: update_debug_info(e)),
            ft.ElevatedButton("Export Logs", on_click=lambda e: export_logs(e))
        ]),
        width=300,
        height=200,
        bgcolor=ft.colors.BLACK87,
        right=20,
        top=20,
        visible=False
    )
    return overlay
```

#### 7.2 Implement Log Export
- [ ] Add functionality to export debug information:
```python
def export_debug_info():
    debug_data = {
        "timestamp": datetime.now().isoformat(),
        "state": state_tracker.current_state,
        "events": event_timeline.events,
        "errors": error_reporter.error_history
    }
    
    filename = f"debug_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(debug_data, f, indent=2, default=str)
    debug_log(f"Debug info exported to {filename}", "EXPORT")
```

### Phase 8: Production Considerations

#### 8.1 Add Environment-Based Debugging
- [ ] Conditionally enable debugging based on environment:
```python
import os

DEBUG_MODE = os.getenv("FLET_DEBUG", "false").lower() == "true"

if DEBUG_MODE:
    logging.basicConfig(level=logging.DEBUG)
    debug_enabled = True
else:
    logging.basicConfig(level=logging.WARNING)
    debug_enabled = False
```

#### 8.2 Implement Debug Level Controls
- [ ] Add different levels of debugging detail:
```python
DEBUG_LEVELS = {
    "NONE": 0,
    "ERROR": 1,
    "WARNING": 2,
    "INFO": 3,
    "DEBUG": 4,
    "VERBOSE": 5
}

CURRENT_DEBUG_LEVEL = DEBUG_LEVELS.get(os.getenv("FLET_DEBUG_LEVEL", "INFO").upper(), 3)
```

## Testing Your Debugging Implementation

### 1. Verify Debug Output
- [ ] Run your application and verify debug logs appear in terminal
- [ ] Test all UI components to ensure event tracking works
- [ ] Verify state changes are logged correctly
- [ ] Test error handling with simulated errors

### 2. Performance Impact Assessment
- [ ] Measure application startup time with and without debugging
- [ ] Check memory usage during extended operation
- [ ] Verify UI responsiveness remains acceptable

### 3. Log Completeness Check
- [ ] Perform typical user workflows and verify all actions are logged
- [ ] Check that error conditions are properly captured
- [ ] Validate that state changes are tracked accurately

## Maintenance and Monitoring

### Ongoing Tasks
- [ ] Regularly review debug logs for recurring issues
- [ ] Monitor log file sizes in production
- [ ] Update debugging instrumentation as application evolves
- [ ] Periodically export and analyze debug data for insights

### Optimization Opportunities
- [ ] Remove unnecessary debug logging in stable components
- [ ] Add more detailed tracing for problematic areas
- [ ] Implement automated alerting for critical errors
- [ ] Enhance debugging tools based on usage patterns

## Troubleshooting Common Issues

### No Debug Output
- [ ] Verify logging level is set correctly
- [ ] Check that debug_log function is called
- [ ] Ensure terminal output is not redirected/suppressed
- [ ] Confirm event handlers are properly attached

### Performance Degradation
- [ ] Review frequency of debug logging
- [ ] Check for expensive operations in debug handlers
- [ ] Verify memory usage of debug tracking objects
- [ ] Consider conditional logging for verbose debug info

### Missing Event Tracking
- [ ] Verify all UI components have debug handlers attached
- [ ] Check that event propagation isn't blocked
- [ ] Confirm that wrapped handlers call original functions
- [ ] Test edge cases and error conditions

This comprehensive debugging guide provides everything needed to effectively debug Flet applications, from simple logging to enterprise-level monitoring systems. Choose the components that match your application's complexity and debugging requirements.