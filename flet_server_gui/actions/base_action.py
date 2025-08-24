"""
Base Action Classes and Result Types

Provides consistent interfaces for all business logic operations.
"""

from dataclasses import dataclass
from typing import Any, Optional, List, Dict
from abc import ABC, abstractmethod


@dataclass
class ActionResult:
    """
    Consistent return type for all action operations.
    
    Attributes:
        success: Whether the operation completed successfully
        data: Result data (if any)
        error_message: Human-readable error message (if failed)
        error_code: Machine-readable error code (if failed) 
        metadata: Additional context information
    """
    success: bool
    data: Any = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_result(cls, data: Any = None, metadata: Dict[str, Any] = None) -> 'ActionResult':
        """Create a successful result."""
        return cls(success=True, data=data, metadata=metadata or {})
    
    @classmethod 
    def error_result(cls, error_message: str, error_code: str = None, metadata: Dict[str, Any] = None) -> 'ActionResult':
        """Create an error result."""
        return cls(
            success=False, 
            error_message=error_message,
            error_code=error_code,
            metadata=metadata or {}
        )
    
    @classmethod
    def from_results(cls, results: List['ActionResult']) -> 'ActionResult':
        """
        Combine multiple results into a single result.
        Success only if all operations succeeded.
        """
        if not results:
            return cls.error_result("No operations to process")
        
        successes = [r for r in results if r.success]
        failures = [r for r in results if not r.success]
        
        if not failures:
            return cls.success_result(
                data=[r.data for r in successes],
                metadata={'total_operations': len(results), 'all_succeeded': True}
            )
        else:
            return cls.error_result(
                error_message=f"{len(failures)} of {len(results)} operations failed",
                error_code="PARTIAL_FAILURE",
                metadata={
                    'total_operations': len(results),
                    'successful_operations': len(successes), 
                    'failed_operations': len(failures),
                    'failure_messages': [f.error_message for f in failures]
                }
            )


class BaseAction(ABC):
    """
    Base class for all action implementations.
    
    Provides common functionality and enforces consistent patterns.
    """
    
    def __init__(self, server_bridge):
        """
        Initialize action with server bridge dependency.
        
        Args:
            server_bridge: Server integration interface
        """
        self.server_bridge = server_bridge
    
    async def execute_with_retry(self, operation, max_retries: int = 3) -> ActionResult:
        """
        Execute an operation with automatic retry logic.
        
        Args:
            operation: Async function to execute
            max_retries: Maximum number of retry attempts
            
        Returns:
            ActionResult with operation outcome
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                result = await operation()
                return ActionResult.success_result(
                    data=result,
                    metadata={'attempts': attempt + 1}
                )
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    # Log retry attempt (in production, use proper logging)
                    print(f"Attempt {attempt + 1} failed, retrying: {str(e)}")
                    continue
                
        return ActionResult.error_result(
            error_message=f"Operation failed after {max_retries + 1} attempts: {str(last_error)}",
            error_code="MAX_RETRIES_EXCEEDED",
            metadata={'attempts': max_retries + 1, 'final_error': str(last_error)}
        )