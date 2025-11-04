"""
Shared error handling utilities for CyberBackup 3.0
"""
import logging
from functools import wraps
from typing import Callable, Any, Optional, Union, TYPE_CHECKING

# Import NetworkServer only for type checking to avoid circular imports
if TYPE_CHECKING:
    from python_server.server.network_server import NetworkServer


# Configure logger for this module
logger = logging.getLogger(__name__)


def handle_request_errors(network_server, error_response_code: int = 0x00000001):
    """
    Decorator for handling request errors consistently across request handlers.
    
    Args:
        network_server: The network server instance for sending responses
        error_response_code: The response code to send on errors
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(sock, client, payload, *args, **kwargs):
            try:
                # Call the original function
                result = func(sock, client, payload, *args, **kwargs)
                return result
            except Exception as e:
                # Log the error with context
                client_name = getattr(client, 'name', 'unknown') if client else 'unknown'
                logger.error(f"Error in request handler {func.__name__} for client '{client_name}': {e}", exc_info=True)
                
                # Send error response
                if network_server:
                    network_server.send_response(sock, error_response_code)
                
                # Return None or appropriate error indicator
                return None
        return wrapper
    return decorator


def handle_request_errors_detailed(network_server, 
                                  protocol_error_code: int = 0x00000002,
                                  generic_error_code: int = 0x00000001,
                                  crypto_error_code: int = 0x00000001):
    """
    Decorator for handling request errors with more specific error types.
    
    Args:
        network_server: The network server instance for sending responses
        protocol_error_code: Response code for protocol errors
        generic_error_code: Response code for generic errors
        crypto_error_code: Response code for cryptography-related errors
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(sock, client, payload, *args, **kwargs):
            try:
                # Call the original function
                result = func(sock, client, payload, *args, **kwargs)
                return result
            except Exception as e:
                # Log the error with context
                client_name = getattr(client, 'name', 'unknown') if client else 'unknown'
                
                # Determine error type and send appropriate response
                exc_type_name = type(e).__name__
                if exc_type_name == 'ProtocolError' or 'protocol' in str(e).lower():
                    logger.error(f"Protocol error in {func.__name__} for client '{client_name}': {e}")
                    response_code = protocol_error_code
                elif any(crypto_term in exc_type_name.lower() or crypto_term in str(e).lower() 
                        for crypto_term in ['crypto', 'rsa', 'encryption', 'decryption', 'key']):
                    logger.critical(f"Cryptography error in {func.__name__} for client '{client_name}': {e}", exc_info=True)
                    response_code = crypto_error_code
                else:
                    logger.error(f"Error in {func.__name__} for client '{client_name}': {e}", exc_info=True)
                    response_code = generic_error_code
                
                # Send error response
                if network_server:
                    network_server.send_response(sock, response_code)
                
                # Return None or appropriate error indicator
                return None
        return wrapper
    return decorator


def handle_specific_request_errors(network_server, 
                                 protocol_error_code: int = 0x00000002,
                                 server_error_code: int = 0x00000003,
                                 crypto_error_code: int = 0x00000001,
                                 generic_error_code: int = 0x00000001,
                                 protocol_error_handler: Optional[Callable] = None,
                                 server_error_handler: Optional[Callable] = None,
                                 crypto_error_handler: Optional[Callable] = None):
    """
    Advanced decorator for handling specific request errors with custom handlers.
    
    Args:
        network_server: The network server instance for sending responses
        protocol_error_code: Response code for protocol errors
        server_error_code: Response code for server errors
        crypto_error_code: Response code for cryptography-related errors
        generic_error_code: Response code for other errors
        protocol_error_handler: Optional custom handler for protocol errors
        server_error_handler: Optional custom handler for server errors
        crypto_error_handler: Optional custom handler for crypto errors
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(sock, client, payload, *args, **kwargs):
            try:
                # Call the original function
                result = func(sock, client, payload, *args, **kwargs)
                return result
            except Exception as e:
                # Log the error with context
                client_name = getattr(client, 'name', 'unknown') if client else 'unknown'
                
                # Determine error type and handle appropriately
                exc_type = type(e).__name__
                
                if exc_type == 'ProtocolError' or 'protocol' in str(e).lower():
                    logger.error(f"Protocol error in {func.__name__} for client '{client_name}': {e}")
                    response_code = protocol_error_code
                    if protocol_error_handler:
                        protocol_error_handler(sock, client, e)
                elif exc_type == 'ServerError' or 'server' in str(e).lower():
                    logger.error(f"Server error in {func.__name__} for client '{client_name}': {e}")
                    response_code = server_error_code
                    if server_error_handler:
                        server_error_handler(sock, client, e)
                elif any(crypto_term in exc_type.lower() or crypto_term in str(e).lower() 
                        for crypto_term in ['crypto', 'rsa', 'encryption', 'decryption', 'key']):
                    logger.critical(f"Cryptography error in {func.__name__} for client '{client_name}': {e}", exc_info=True)
                    response_code = crypto_error_code
                    if crypto_error_handler:
                        crypto_error_handler(sock, client, e)
                else:
                    logger.error(f"Unexpected error in {func.__name__} for client '{client_name}': {e}", exc_info=True)
                    response_code = generic_error_code
                
                # Send error response unless already handled by custom handler
                if network_server and not (protocol_error_handler and exc_type == 'ProtocolError'):
                    network_server.send_response(sock, response_code)
                
                # Return None or appropriate error indicator
                return None
        return wrapper
    return decorator


def handle_registration_request_errors(network_server, 
                                     protocol_error_code: int = 0x00000002,
                                     server_error_code: int = 0x00000003,
                                     generic_error_code: int = 0x00000001):
    """
    Specialized decorator for handling registration request errors.
    Used for requests where the client doesn't exist yet (registration).
    
    Args:
        network_server: The network server instance for sending responses
        protocol_error_code: Response code for protocol errors
        server_error_code: Response code for server errors
        generic_error_code: Response code for other errors
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(sock, payload, *args, **kwargs):
            try:
                # Call the original function
                result = func(sock, payload, *args, **kwargs)
                return result
            except Exception as e:
                # Log the error
                logger.error(f"Error in registration handler {func.__name__}: {e}", exc_info=True)
                
                # Determine error type and send appropriate response
                exc_type = type(e).__name__
                
                if exc_type == 'ProtocolError' or 'protocol' in str(e).lower():
                    logger.error(f"Registration protocol error: {e}")
                    response_code = protocol_error_code
                elif exc_type == 'ServerError' or 'server' in str(e).lower():
                    logger.error(f"Registration server error: {e}")
                    response_code = server_error_code
                else:
                    logger.error(f"Unexpected registration error: {e}", exc_info=True)
                    response_code = generic_error_code
                
                # Send error response
                if network_server:
                    network_server.send_response(sock, response_code)
                
                # Return None or appropriate error indicator
                return None
        return wrapper
    return decorator


def safe_execute_with_error_handling(
    operation: str,
    func: Callable,
    network_server: 'NetworkServer',
    sock,
    error_response_code: int = 0x00000001,
    *args,
    **kwargs
) -> Any:
    """
    Execute a function with consistent error handling.
    
    Args:
        operation: Name of the operation for logging
        func: The function to execute
        network_server: Network server instance
        sock: Socket for error response
        error_response_code: Error response code
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        Result of function execution or None if error occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error during {operation}: {e}", exc_info=True)
        if network_server:
            network_server.send_response(sock, error_response_code)
        return None


def handle_protocol_error(network_server: 'NetworkServer', sock, client_name: str, error_msg: str):
    """
    Handle protocol errors consistently.
    
    Args:
        network_server: Network server instance
        sock: Socket for response
        client_name: Name of the client
        error_msg: Error message
    """
    logger.error(f"Protocol error for client '{client_name}': {error_msg}")
    if network_server:
        network_server.send_response(sock, 0x00000004)  # Assuming this is protocol error response


def handle_file_error(network_server: 'NetworkServer', sock, client_name: str, error_msg: str):
    """
    Handle file-related errors consistently.
    
    Args:
        network_server: Network server instance
        sock: Socket for response
        client_name: Name of the client
        error_msg: Error message
    """
    logger.error(f"File error for client '{client_name}': {error_msg}")
    if network_server:
        network_server.send_response(sock, 0x00000005)  # Assuming this is file error response


def handle_validation_error(network_server: 'NetworkServer', sock, client_name: str, error_msg: str):
    """
    Handle validation errors consistently.
    
    Args:
        network_server: Network server instance
        sock: Socket for response
        client_name: Name of the client
        error_msg: Error message
    """
    logger.warning(f"Validation error for client '{client_name}': {error_msg}")
    if network_server:
        network_server.send_response(sock, 0x00000002)  # Assuming this is validation error response


def safe_db_operation(func: Callable, *args, **kwargs) -> Union[Any, None]:
    """
    Execute a database operation safely with consistent error handling.
    
    Args:
        func: The database function to execute
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        Result of database operation or None if error occurred
    """
    try:
        result = func(*args, **kwargs)
        return result
    except Exception as e:
        logger.error(f"Database operation error: {e}", exc_info=True)
        return None