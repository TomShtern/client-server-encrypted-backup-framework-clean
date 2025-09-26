"""
Custom exception classes for the secure file transfer server.

This module defines server-specific exceptions that provide meaningful error handling
and proper error categorization throughout the server application.
"""


class ServerError(Exception):
    """
    Base class for server-specific exceptions.
    
    This is the root exception class for all server-related errors. It should be used
    as the base class for more specific server exceptions to allow for hierarchical
    exception handling.
    """
    pass


class ProtocolError(ServerError):
    """
    Indicates an error in protocol adherence by the client.
    
    This exception is raised when the client sends malformed requests, violates
    the communication protocol, or sends unexpected message types. Examples include:
    - Invalid message format
    - Unexpected message sequence
    - Protocol version mismatches
    - Malformed headers or payloads
    """
    pass


class ClientError(ServerError):
    """
    Indicates an error related to client state or validity.
    
    This exception is raised when there are issues with client authentication,
    registration, or client-specific state management. Examples include:
    - Client not registered
    - Invalid client credentials
    - Client authentication failures
    - Client state inconsistencies
    """
    pass


class FileError(ServerError):
    """
    Indicates an error related to file operations or validity.
    
    This exception is raised when there are issues with file handling, validation,
    or file system operations. Examples include:
    - File not found
    - File permission errors
    - File corruption or integrity issues
    - Invalid file formats or sizes
    - File system I/O errors
    """
    pass
