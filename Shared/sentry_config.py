#!/usr/bin/env python3
"""
Shared Sentry Configuration for CyberBackup Framework
====================================================

Centralized Sentry setup for consistent error monitoring across all Python components:
- Flask API Server
- Python Backup Server  
- Server GUI (already integrated)
- Launch scripts

Usage:
    from Shared.sentry_config import init_sentry
    init_sentry(component_name="api-server")
"""

import logging
import os
from typing import Optional

# Sentry DSN Configuration
SENTRY_DSN = "https://094a0bee5d42a7f7e8ec8a78a37c8819@o4509746411470848.ingest.us.sentry.io/4509747877773312"
SENTRY_ENVIRONMENT = os.getenv("CYBERBACKUP_ENV", "development")

logger = logging.getLogger(__name__)


def init_sentry(
    component_name: str,
    dsn: Optional[str] = None,
    environment: Optional[str] = None,
    debug: bool = False,
    sample_rate: float = 1.0,
    traces_sample_rate: float = 0.1
) -> bool:
    """
    Initialize Sentry error monitoring for a component.
    
    Args:
        component_name: Name of the component (e.g., "api-server", "backup-server")
        dsn: Optional custom DSN (defaults to SENTRY_DSN)
        environment: Environment name (defaults to SENTRY_ENVIRONMENT)
        debug: Enable Sentry debug mode
        sample_rate: Error sampling rate (1.0 = all errors)
        traces_sample_rate: Performance tracing sample rate
        
    Returns:
        bool: True if Sentry was successfully initialized, False otherwise
    """
    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.threading import ThreadingIntegration
        
        # Configure logging integration
        logging_integration = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors and above as events
        )
        
        # Initialize Sentry
        sentry_sdk.init(
            dsn=dsn or SENTRY_DSN,
            environment=environment or SENTRY_ENVIRONMENT,
            debug=debug,
            sample_rate=sample_rate,
            traces_sample_rate=traces_sample_rate,
            send_default_pii=True,  # Send user IP, etc.
            integrations=[
                logging_integration,
                ThreadingIntegration(propagate_hub=True),
            ],
            before_send=_before_send_filter,
            release=_get_release_version()
        )
        
        # Set component context
        sentry_sdk.set_tag("component", component_name)
        sentry_sdk.set_tag("framework", "cyberbackup")
        
        # Add system context
        import platform
        sentry_sdk.set_tag("os", platform.system())
        sentry_sdk.set_tag("python_version", platform.python_version())
        
        logger.info(f"[SENTRY] Initialized for component: {component_name}")
        return True
        
    except ImportError:
        logger.warning(f"[SENTRY] SDK not available for {component_name} - error tracking disabled")
        return False
    except Exception as e:
        logger.error(f"[SENTRY] Failed to initialize for {component_name}: {e}")
        return False


def _before_send_filter(event, hint):
    """
    Filter events before sending to Sentry.
    Can be used to sanitize sensitive data or filter noise.
    """
    # Filter out common non-critical errors
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        
        # Filter out expected network timeouts
        if isinstance(exc_value, (ConnectionResetError, BrokenPipeError)):
            return None
            
        # Filter out file not found errors for optional files
        if isinstance(exc_value, FileNotFoundError):
            filename = str(exc_value).lower()
            if any(optional in filename for optional in ['optional', 'cache', 'temp']):
                return None
    
    return event


def _get_release_version() -> str:
    """Get the current release version for Sentry."""
    try:
        # Try to get git commit hash
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return f"cyberbackup@{result.stdout.strip()}"
    except (Exception):
        pass
    
    # Fallback to static version
    return "cyberbackup@3.0.0"


def capture_error(error: Exception, component: str, extra_context: Optional[dict] = None):
    """
    Capture an error with additional context.
    
    Args:
        error: The exception to capture
        component: Component where the error occurred
        extra_context: Additional context dictionary
    """
    try:
        import sentry_sdk
        
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("error_component", component)
            
            if extra_context:
                for key, value in extra_context.items():
                    scope.set_extra(key, value)
            
            sentry_sdk.capture_exception(error)
            
    except ImportError:
        logger.error(f"[{component}] Error occurred but Sentry not available: {error}")
    except Exception as e:
        logger.error(f"[{component}] Failed to capture error in Sentry: {e}")


def capture_message(message: str, level: str = "info", component: str = "unknown", extra_context: Optional[dict] = None):
    """
    Capture a message with additional context.
    
    Args:
        message: Message to capture
        level: Message level (debug, info, warning, error, fatal)
        component: Component sending the message
        extra_context: Additional context dictionary
    """
    try:
        import sentry_sdk
        
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("message_component", component)
            
            if extra_context:
                for key, value in extra_context.items():
                    scope.set_extra(key, value)
            
            # Map string level to Sentry level
            from sentry_sdk._types import LogLevelStr
            level_mapping: dict[str, LogLevelStr] = {
                "debug": "debug",
                "info": "info", 
                "warning": "warning",
                "error": "error",
                "fatal": "fatal"
            }
            sentry_level = level_mapping.get(level.lower(), "info")
            sentry_sdk.capture_message(message, sentry_level)
            
    except ImportError:
        logger.info(f"[{component}] Message: {message} (Sentry not available)")
    except Exception as e:
        logger.error(f"[{component}] Failed to capture message in Sentry: {e}")


def set_user_context(user_id: str, username: Optional[str] = None, ip_address: Optional[str] = None):
    """Set user context for Sentry events."""
    try:
        import sentry_sdk
        sentry_sdk.set_user({
            "id": user_id,
            "username": username,
            "ip_address": ip_address
        })
    except ImportError:
        pass


# Test function for Sentry integration
def test_sentry_integration(component_name: str):
    """Test Sentry integration by sending a test message."""
    try:
        capture_message(
            f"Sentry integration test from {component_name}",
            level="info",
            component=component_name,
            extra_context={"test": True}
        )
        logger.info(f"[SENTRY] Test message sent from {component_name}")
        return True
    except Exception as e:
        logger.error(f"[SENTRY] Test failed for {component_name}: {e}")
        return False
