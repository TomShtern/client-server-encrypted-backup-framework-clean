#!/usr/bin/env python3
"""
Dashboard loading manager for progressive data loading with retry mechanism.

Handles phased loading of dashboard data with proper state management
and user-triggered retry functionality.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

import flet as ft

try:  # pragma: no cover - UTF-8 bootstrap required by project
    import Shared.utils.utf8_solution as _
except Exception:  # pragma: no cover - allow running in isolation
    pass


class LoadingPhase(Enum):
    """Loading phases for progressive enhancement."""
    INITIAL = "initial"
    CRITICAL_METRICS = "critical_metrics"
    PERFORMANCE_DATA = "performance_data"
    ACTIVITY_DATA = "activity_data"
    COMPLETE = "complete"


@dataclass
class LoadingState:
    """Represents the state of a loading phase."""
    phase: LoadingPhase
    is_loading: bool = False
    is_complete: bool = False
    has_error: bool = False
    error_message: str = ""
    data: Any = None
    retry_count: int = 0
    last_attempt: float = 0.0


class DashboardLoadingManager:
    """
    Manages progressive loading of dashboard data with retry mechanisms.

    Implements user-triggered retry with exponential backoff and
    progressive enhancement following Flet 0.28.3 best practices.
    """

    def __init__(
        self,
        page: ft.Page,
        server_bridge: Any,
        on_state_change: Callable[[LoadingPhase, LoadingState], None] | None = None,
    ):
        self.page = page
        self.server_bridge = server_bridge
        self.on_state_change = on_state_change

        # Initialize loading states
        self.loading_states: Dict[LoadingPhase, LoadingState] = {
            phase: LoadingState(phase=phase)
            for phase in LoadingPhase
        }

        # Control variables
        self._disposed = False
        self._loading_lock = asyncio.Lock()

        # Retry configuration
        self.max_retries = 3
        self.base_retry_delay = 1.0
        self.retry_backoff_factor = 2.0

    def _get_state(self, phase: LoadingPhase) -> LoadingState:
        """Get the loading state for a specific phase."""
        return self.loading_states.get(phase, LoadingState(phase=phase))

    def _update_state(self, phase: LoadingPhase, **kwargs) -> None:
        """Update the loading state and notify listeners."""
        state = self._get_state(phase)
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)

        if self.on_state_change:
            self.on_state_change(phase, state)

    async def start_progressive_loading(self) -> None:
        """
        Start progressive loading of dashboard data.

        Loads data in phases:
        1. Critical metrics (server status, basic stats)
        2. Performance data (CPU, memory, database)
        3. Activity data (recent events, logs)
        """
        if self._disposed:
            return

        async with self._loading_lock:
            try:
                # Phase 1: Critical Metrics
                await self._load_critical_metrics()

                # Phase 2: Performance Data
                await self._load_performance_data()

                # Phase 3: Activity Data
                await self._load_activity_data()

                # Mark as complete
                self._update_state(
                    LoadingPhase.COMPLETE,
                    is_complete=True,
                    is_loading=False,
                )

            except Exception as e:
                # Log error but don't stop other phases
                print(f"Error in progressive loading: {e}")

    async def _load_critical_metrics(self) -> None:
        """Load critical metrics (server status, basic stats)."""
        phase = LoadingPhase.CRITICAL_METRICS
        self._update_state(phase, is_loading=True, last_attempt=time.time())

        try:
            # Load dashboard summary (server status, basic metrics)
            summary = await self._safe_bridge_call("get_dashboard_summary")

            if summary.get("success"):
                self._update_state(
                    phase,
                    is_loading=False,
                    is_complete=True,
                    data=summary.get("data", {}),
                )
            else:
                raise ValueError(summary.get("error", "Failed to load critical metrics"))

        except Exception as e:
            self._update_state(
                phase,
                is_loading=False,
                has_error=True,
                error_message=str(e),
            )

    async def _load_performance_data(self) -> None:
        """Load performance data (CPU, memory, database stats)."""
        phase = LoadingPhase.PERFORMANCE_DATA
        self._update_state(phase, is_loading=True, last_attempt=time.time())

        try:
            # Load performance metrics
            performance = await self._safe_bridge_call("get_performance_metrics")

            if performance.get("success"):
                self._update_state(
                    phase,
                    is_loading=False,
                    is_complete=True,
                    data=performance.get("data", {}),
                )
            else:
                raise ValueError(performance.get("error", "Failed to load performance data"))

        except Exception as e:
            self._update_state(
                phase,
                is_loading=False,
                has_error=True,
                error_message=str(e),
            )

    async def _load_activity_data(self) -> None:
        """Load activity data (recent events, logs)."""
        phase = LoadingPhase.ACTIVITY_DATA
        self._update_state(phase, is_loading=True, last_attempt=time.time())

        try:
            # Load recent activity
            activity = await self._safe_bridge_call("get_recent_activity_async", 12)

            if not activity.get("success"):
                activity = await self._safe_bridge_call("get_recent_activity", 12)

            if activity.get("success"):
                self._update_state(
                    phase,
                    is_loading=False,
                    is_complete=True,
                    data=activity.get("data", []),
                )
            else:
                raise ValueError(activity.get("error", "Failed to load activity data"))

        except Exception as e:
            self._update_state(
                phase,
                is_loading=False,
                has_error=True,
                error_message=str(e),
            )

    async def _safe_bridge_call(self, method_name: str, *args: Any) -> Dict[str, Any]:
        """
        Safely call server bridge method with proper async handling.

        Uses run_in_executor to prevent blocking the Flet event loop.
        """
        if not self.server_bridge:
            return {
                "success": False,
                "error": "Server bridge unavailable",
                "data": None,
            }

        loop = asyncio.get_running_loop()

        try:
            method = getattr(self.server_bridge, method_name, None)
            if method is None:
                return {
                    "success": False,
                    "error": f"Method {method_name} not found",
                    "data": None,
                }

            if asyncio.iscoroutinefunction(method):
                result = await method(*args)
            else:
                result = await loop.run_in_executor(None, method, *args)

            if isinstance(result, dict):
                return result
            else:
                return {
                    "success": True,
                    "data": result,
                    "error": None,
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None,
            }

    async def retry_phase(self, phase: LoadingPhase) -> None:
        """
        Retry a specific loading phase with user trigger.

        Implements user-triggered retry with backoff delay based on retry count.
        """
        if self._disposed:
            return

        state = self._get_state(phase)

        # Check retry limit
        if state.retry_count >= self.max_retries:
            return

        # Calculate backoff delay
        delay = self.base_retry_delay * (self.retry_backoff_factor ** state.retry_count)

        # Update retry count
        self._update_state(phase, retry_count=state.retry_count + 1)

        # Wait for backoff delay
        await asyncio.sleep(delay)

        # Retry the appropriate phase
        try:
            if phase == LoadingPhase.CRITICAL_METRICS:
                await self._load_critical_metrics()
            elif phase == LoadingPhase.PERFORMANCE_DATA:
                await self._load_performance_data()
            elif phase == LoadingPhase.ACTIVITY_DATA:
                await self._load_activity_data()
        except Exception as e:
            print(f"Retry failed for phase {phase.value}: {e}")

    def create_retry_handler(self, phase: LoadingPhase) -> Callable[[ft.ControlEvent], None]:
        """Create a retry handler for a specific phase."""
        def retry_handler(e: ft.ControlEvent) -> None:
            if not self._disposed:
                self.page.run_task(self.retry_phase, phase)
        return retry_handler

    def get_phase_data(self, phase: LoadingPhase) -> Any:
        """Get the loaded data for a specific phase."""
        return self._get_state(phase).data

    def is_phase_complete(self, phase: LoadingPhase) -> bool:
        """Check if a phase has completed successfully."""
        return self._get_state(phase).is_complete

    def is_phase_error(self, phase: LoadingPhase) -> bool:
        """Check if a phase has an error."""
        return self._get_state(phase).has_error

    def get_error_message(self, phase: LoadingPhase) -> str:
        """Get the error message for a specific phase."""
        return self._get_state(phase).error_message

    def dispose(self) -> None:
        """Dispose of the loading manager."""
        self._disposed = True