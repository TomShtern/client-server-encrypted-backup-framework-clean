"""
Shared client validation utilities for CyberBackup 3.0
"""
import re
import logging
from typing import Optional, Dict, Any


# Configure logger for this module
logger = logging.getLogger(__name__)


def validate_client_id(client_id: str) -> bool:
    """
    Validate a client ID format and security.
    
    Args:
        client_id: The client ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not client_id:
        return False
        
    # Check length
    if len(client_id) < 1 or len(client_id) > 128:  # Reasonable length limit
        return False
        
    # Check for valid characters (alphanumeric + some safe symbols)
    if not re.match(r'^[a-zA-Z0-9_-]+$', client_id):
        return False
        
    # Additional checks can be added here as needed
    return True


def validate_client_data(client_data: Dict[str, Any]) -> bool:
    """
    Validate client data structure and content.
    
    Args:
        client_data: The client data to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(client_data, dict):
        logger.warning("Client data validation failed: Not a dictionary")
        return False
        
    required_fields = ['name', 'created_at']  # Add other required fields as needed
    for field in required_fields:
        if field not in client_data:
            logger.warning(f"Client data validation failed: Missing required field '{field}'")
            return False
    
    # Validate client name
    if 'name' in client_data:
        from Shared.utils.validation_utils import is_valid_client_name
        if not is_valid_client_name(client_data['name']):
            logger.warning(f"Client data validation failed: Invalid client name '{client_data['name']}'")
            return False
            
    return True


def extract_client_info_from_bytes(client_id_bytes: bytes) -> Optional[str]:
    """
    Extract and validate client ID from bytes representation.
    
    Args:
        client_id_bytes: Raw bytes representing the client ID
        
    Returns:
        Validated client ID string or None if invalid
    """
    try:
        # Decode the client ID from bytes
        client_id = client_id_bytes.decode('utf-8', errors='ignore').strip('\x00')
        
        # Validate the client ID
        if not validate_client_id(client_id):
            logger.warning(f"Invalid client ID extracted from bytes: {client_id}")
            return None
            
        return client_id
    except Exception as e:
        logger.error(f"Error extracting client ID from bytes: {e}")
        return None


def is_valid_client_operation(client_id: str, operation: str) -> bool:
    """
    Validate if a client is allowed to perform a specific operation.
    
    Args:
        client_id: The client ID
        operation: The operation to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Currently, all authenticated clients can perform all operations
    # This can be extended with role-based access control in the future
    return validate_client_id(client_id) and bool(operation)