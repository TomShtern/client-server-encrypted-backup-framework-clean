"""
Base Action Classes and Result Types

Provides consistent interfaces for all business logic operations.
"""

from dataclasses import dataclass
from typing import Any, Optional, List, Dict
from abc import ABC
from flet_server_gui.utils.action_result import ActionResult as UnifiedActionResult
from flet_server_gui.utils.trace_center import get_trace_center


@dataclass
class ActionResultBridge:
    """Backwards-compatible facade for legacy ActionResult usage within actions.

    Provides success_result / error_result / from_results that emit unified
    ActionResult objects while keeping existing call semantics minimal.
    """
    success: bool
    data: Any = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    # Factory bridging to unified ActionResult
    @classmethod
    def success_result(cls, data: Any = None, metadata: Dict[str, Any] = None):
        cid = get_trace_center().new_correlation_id()
        return UnifiedActionResult.make_success(
            code="ACTION_OK", message="Action succeeded", correlation_id=cid, data=data if isinstance(data, dict) else ({"value": data} if data is not None else None), meta=metadata or {}
        )

    @classmethod
    def error_result(cls, error_message: str, error_code: str = None, metadata: Dict[str, Any] = None):
        cid = get_trace_center().new_correlation_id()
        return UnifiedActionResult.make_error(
            code=error_code or "ACTION_ERROR", message=error_message, correlation_id=cid, error_code=error_code, meta=metadata or {}
        )

    @classmethod
    def from_results(cls, results: List[UnifiedActionResult]):
        if not results:
            return cls.error_result("No operations to process")
        successes = [r for r in results if r.success]
        failures = [r for r in results if not r.success]
        cid = get_trace_center().new_correlation_id()
        if not failures:
            return UnifiedActionResult.make_success(
                code="BATCH_OK",
                message="All operations succeeded",
                correlation_id=cid,
                data={"items": [r.data for r in successes]},
                meta={"total_operations": len(results), "all_succeeded": True},
            )
        else:
            return UnifiedActionResult.make_partial(
                code="BATCH_PARTIAL",
                message=f"{len(failures)} of {len(results)} operations failed",
                correlation_id=cid,
                failed=[{"code": f.code, "message": f.message} for f in failures],
                data={"successful": len(successes), "failed": len(failures), "total": len(results)},
                meta={
                    "total_operations": len(results),
                    "successful_operations": len(successes),
                    "failed_operations": len(failures),
                },
            )

# Alias used by other action modules
ActionResult = UnifiedActionResult


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
                cid = get_trace_center().new_correlation_id()
                result = await operation()
                data = result if isinstance(result, dict) else {"value": result}
                return ActionResult.make_success(
                    code="RETRY_OK",
                    message="Operation succeeded",
                    correlation_id=cid,
                    data=data,
                    meta={'attempts': attempt + 1}
                )
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    get_trace_center().emit(
                        type="ACTION_RETRY",
                        level="WARN",
                        message="retrying operation",
                        meta={"attempt": attempt + 1, "error": str(last_error)},
                    )
                    continue
        cid = get_trace_center().new_correlation_id()
        return ActionResult.error(
            code="MAX_RETRIES_EXCEEDED",
            message=f"Operation failed after {max_retries + 1} attempts: {str(last_error)}",
            correlation_id=cid,
            error_code="MAX_RETRIES_EXCEEDED",
            data=None,
            meta={'attempts': max_retries + 1, 'final_error': str(last_error)}
        )