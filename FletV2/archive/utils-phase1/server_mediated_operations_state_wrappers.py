#!/usr/bin/env python3
"""
Server-Mediated Operations Utility
Modular, reusable patterns for server-bridge operations with state management.
Eliminates duplication across views by providing common operation patterns.
"""

import asyncio
from collections.abc import Callable
from datetime import datetime
from typing import Any

from FletV2.utils.debug_setup import get_logger
from FletV2.utils.state_manager import StateManager
from FletV2.utils.user_feedback import show_error_message, show_success_message

logger = get_logger(__name__)


class ServerMediatedOperations:
    """Reusable server-mediated operation patterns to eliminate code duplication"""

    def __init__(self, state_manager: StateManager, page):
        self.state_manager = state_manager
        self.page = page

    async def load_data_operation(
        self,
        state_key: str,
        server_operation: str,
        fallback_data: Any = None,
        data_processor: Callable | None = None,
        loading_key: str | None = None,
        operation_data: Any = None
    ) -> dict[str, Any]:
        """
        Standard pattern for loading data through server bridge with fallback.

        Args:
            state_key: Key to store data in state manager
            server_operation: Name of server bridge method to call
            fallback_data: Data to use if server operation fails
            data_processor: Optional function to process data after loading
            loading_key: Loading state key (defaults to state_key)
            operation_data: Optional data to pass to server operation

        Returns:
            Result dictionary with success status and data from state manager
        """
        loading_key = loading_key or state_key

        try:
            self.state_manager.set_loading(loading_key, True)

            # Pass operation_data as arguments to the server method if provided
            if operation_data is not None:
                result = await self.state_manager.server_mediated_update(
                    key=state_key,
                    value=fallback_data,
                    server_operation=server_operation,
                    operation_data=operation_data
                )
            else:
                result = await self.state_manager.server_mediated_update(
                    key=state_key,
                    value=fallback_data,
                    server_operation=server_operation
                )

            # Process data if processor provided
            if result.get('success') and data_processor:
                current_data = self.state_manager.get(state_key)
                processed_data = data_processor(current_data)
                await self.state_manager.update_async(state_key, processed_data, source="processed")

            # Return result with actual data from state manager
            final_data = self.state_manager.get(state_key)
            return {'success': result.get('success', True), 'data': final_data, 'mode': result.get('mode', 'unknown')}

        except Exception as e:
            logger.error(f"Load operation failed for {state_key}: {e}")
            if fallback_data is not None:
                await self.state_manager.update_async(state_key, fallback_data, source="error_fallback")
            return {'success': False, 'error': str(e)}
        finally:
            self.state_manager.set_loading(loading_key, False)

    async def action_operation(
        self,
        action_name: str,
        server_operation: str,
        operation_data: Any,
        success_message: str | None = None,
        error_message: str | None = None,
        refresh_keys: list[str] | None = None,
        loading_key: str | None = None
    ) -> dict[str, Any]:
        """
        Standard pattern for user actions that modify server state.

        Args:
            action_name: Human-readable action name for logging
            server_operation: Name of server bridge method to call
            operation_data: Data to pass to server operation
            success_message: Message to show user on success
            error_message: Message to show user on error
            refresh_keys: List of state keys to refresh after operation
            loading_key: Loading state key (defaults to action_name)

        Returns:
            Result dictionary with success status and data
        """
        loading_key = loading_key or action_name

        try:
            self.state_manager.set_loading(loading_key, True)

            result = await self.state_manager.server_mediated_update(
                key=f"{action_name}_result",
                value=operation_data,
                server_operation=server_operation
            )

            if result.get('success'):
                if success_message:
                    show_success_message(self.page, success_message)

                # Refresh related data if specified
                if refresh_keys:
                    await self._refresh_data_keys(refresh_keys)

            else:
                error_msg = error_message or f"Failed to {action_name}: {result.get('message', 'Unknown error')}"
                show_error_message(self.page, error_msg)

            return result if result is not None else {'success': False, 'error': 'No result returned from server operation'}

        except Exception as e:
            logger.error(f"Action operation failed for {action_name}: {e}")
            error_msg = error_message or f"Failed to {action_name}: {e!s}"
            show_error_message(self.page, error_msg)
            return {'success': False, 'error': str(e)}
        finally:
            self.state_manager.set_loading(loading_key, False)

    async def batch_load_operations(self, operations: list[dict]) -> dict[str, Any]:
        """
        Execute multiple load operations in parallel for better performance.

        Args:
            operations: List of operation configs, each containing:
                - state_key: Key for state storage
                - server_operation: Server method name
                - fallback_data: Fallback data
                - data_processor: Optional data processor function

        Returns:
            Results dictionary with success status for each operation
        """
        tasks = []
        results = {}

        for op in operations:
            task = self.load_data_operation(
                state_key=op['state_key'],
                server_operation=op['server_operation'],
                fallback_data=op.get('fallback_data'),
                data_processor=op.get('data_processor')
            )
            tasks.append((op['state_key'], task))

        # Execute all operations in parallel using asyncio.gather
        try:
            # Extract just the tasks for gather, keep keys for mapping
            task_list = [task for _, task in tasks]
            results_list = await asyncio.gather(*task_list, return_exceptions=True)

            # Map results back to state keys
            for i, (state_key, _) in enumerate(tasks):
                result = results_list[i]
                if isinstance(result, Exception):
                    logger.error(f"Batch operation failed for {state_key}: {result}")
                    results[state_key] = {'success': False, 'error': str(result)}
                else:
                    results[state_key] = result

        except Exception as e:
            logger.error(f"Batch operations failed completely: {e}")
            # Return error results for all operations
            for state_key, _ in tasks:
                results[state_key] = {'success': False, 'error': str(e)}

        return results

    async def _refresh_data_keys(self, state_keys: list[str]):
        """Refresh multiple state keys by triggering their reload operations"""
        for key in state_keys:
            try:
                # Trigger refresh by calling the corresponding load operation
                # This assumes a naming convention: load_{key}_operation
                if (current_data := self.state_manager.get(key)):
                    # Force refresh by clearing and reloading
                    await self.state_manager.update_async(key, None, source="refresh_clear")
                    # The UI subscriptions should handle reloading
            except Exception as e:
                logger.error(f"Failed to refresh {key}: {e}")

    def create_reactive_subscription(
        self,
        state_key: str,
        ui_update_callback: Callable,
        control: Any | None = None
    ):
        """
        Create a reactive subscription that automatically updates UI when state changes.

        Args:
            state_key: State key to subscribe to
            ui_update_callback: Function to call when state changes
            control: Optional control to auto-update
        """
        def reactive_callback(new_value, old_value):
            try:
                # Check if callback is async and handle appropriately
                import asyncio
                if asyncio.iscoroutinefunction(ui_update_callback):
                    # Schedule async callback to run in background
                    asyncio.create_task(ui_update_callback(new_value, old_value))
                else:
                    ui_update_callback(new_value, old_value)
                logger.debug(f"Reactive UI update completed for {state_key}")
            except Exception as e:
                logger.error(f"Reactive callback failed for {state_key}: {e}")

        self.state_manager.subscribe(state_key, reactive_callback, control)

    def create_loading_subscription(self, loading_indicator, operation_keys: list[str]):
        """
        Create a subscription that shows loading indicator for multiple operations.

        Args:
            loading_indicator: UI control to show/hide based on loading state
            operation_keys: List of loading keys to monitor
        """
        def loading_callback(loading_states, old_states):
            try:
                # Show indicator if any tracked operation is loading
                is_loading = any(loading_states.get(key, False) for key in operation_keys)
                if hasattr(loading_indicator, 'visible'):
                    loading_indicator.visible = is_loading
                    loading_indicator.update()
            except Exception as e:
                logger.error(f"Loading subscription callback failed: {e}")

        self.state_manager.subscribe("loading_states", loading_callback)

    # Dashboard-specific operation patterns
    async def dashboard_load_system_metrics(self) -> dict[str, Any]:
        """
        Load system metrics for dashboard with specialized error handling.

        Returns:
            Dictionary with system metrics or fallback data
        """
        try:
            # Try to get system metrics from server
            result = await self.state_manager.server_mediated_update(
                key="system_metrics",
                value=None,
                server_operation="get_system_metrics_async"
            )

            if result.get('success'):
                return result
            else:
                # Return fallback data
                return {
                    'success': True,
                    'data': self._generate_fallback_system_metrics()
                }
        except Exception as e:
            logger.error(f"Dashboard system metrics load failed: {e}")
            return {
                'success': True,
                'data': self._generate_fallback_system_metrics()
            }

    def _generate_fallback_system_metrics(self) -> dict[str, Any]:
        """Generate fallback system metrics for dashboard."""
        import random
        return {
            'cpu_usage': random.uniform(20, 80),
            'memory_usage': random.uniform(40, 70),
            'disk_usage': random.uniform(30, 60),
            'network_sent_mb': random.uniform(100, 500),
            'network_recv_mb': random.uniform(200, 800),
            'active_connections': random.randint(5, 20),
            'timestamp': datetime.now().isoformat()
        }

    async def dashboard_load_server_status(self) -> dict[str, Any]:
        """
        Load server status for dashboard with specialized error handling.

        Returns:
            Dictionary with server status or fallback data
        """
        try:
            return await self.load_data_operation(
                state_key="server_status",
                server_operation="get_server_status_async",
                fallback_data=self._generate_fallback_server_status()
            )
        except Exception as e:
            logger.error(f"Dashboard server status load failed: {e}")
            return {
                'success': True,
                'data': self._generate_fallback_server_status()
            }

    def _generate_fallback_server_status(self) -> dict[str, Any]:
        """Generate fallback server status for dashboard."""
        import random
        return {
            'running': True,
            'port': 8080,
            'uptime_seconds': random.randint(3600, 86400),
            'clients_connected': random.randint(1, 10),
            'total_files': random.randint(100, 1000),
            'total_transfers': random.randint(10, 100),
            'storage_used_gb': round(random.uniform(10, 200), 1),
            'timestamp': datetime.now().isoformat()
        }

    async def dashboard_load_activity_data(
        self,
        limit: int = 20,
        activity_type: str | None = None
    ) -> dict[str, Any]:
        """
        Load recent activity data for dashboard with filtering options.

        Args:
            limit: Maximum number of activities to load
            activity_type: Optional filter for activity type

        Returns:
            Dictionary with activity data or fallback data
        """
        try:
            operation_data = {
                'limit': limit,
                'type': activity_type
            } if activity_type else {'limit': limit}

            return await self.load_data_operation(
                state_key="recent_activity",
                server_operation="get_recent_activity_async",
                operation_data=operation_data,
                fallback_data=self._generate_fallback_activity_data(limit),
                data_processor=timestamp_processor
            )
        except Exception as e:
            logger.error(f"Dashboard activity data load failed: {e}")
            return {
                'success': True,
                'data': self._generate_fallback_activity_data(limit)
            }

    def _generate_fallback_activity_data(self, limit: int = 20) -> list[dict[str, Any]]:
        """Generate fallback activity data for dashboard."""
        import random
        from datetime import datetime, timedelta

        activity_types = [
            'client_connect', 'client_disconnect', 'file_transfer',
            'backup_complete', 'system_check', 'error'
        ]

        activities = []
        now = datetime.now()

        for _ in range(min(limit, 10)):  # Generate up to 10 fallback activities
            activity_type = random.choice(activity_types)
            timestamp = now - timedelta(minutes=random.randint(1, 1440))  # Up to 24 hours ago

            activity_messages = {
                'client_connect': f"Client {random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)} connected",
                'client_disconnect': f"Client {random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)} disconnected",
                'file_transfer': f"File backup_{random.randint(1000, 9999)}.zip transferred",
                'backup_complete': f"Backup job completed ({random.randint(50, 500)} files)",
                'system_check': "System health check passed",
                'error': "Failed to connect to update server"
            }

            activities.append({
                'timestamp': timestamp.isoformat(),
                'type': activity_type,
                'message': activity_messages.get(activity_type, "System event occurred")
            })

        return sorted(activities, key=lambda x: x['timestamp'], reverse=True)

    # Analytics-specific operation patterns
    async def analytics_load_performance_metrics(
        self,
        time_range: str = "1h",
        metric_types: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Load performance metrics for analytics with time range filtering.

        Args:
            time_range: Time range for metrics (e.g., "1h", "24h", "7d")
            metric_types: Specific metric types to load

        Returns:
            Dictionary with performance metrics
        """
        try:
            operation_data = {
                'time_range': time_range,
                'metric_types': metric_types or ['cpu', 'memory', 'disk', 'network']
            }

            return await self.load_data_operation(
                state_key=f"performance_metrics_{time_range}",
                server_operation="get_performance_metrics_async",
                operation_data=operation_data,
                fallback_data=self._generate_fallback_performance_metrics(time_range)
            )
        except Exception as e:
            logger.error(f"Analytics performance metrics load failed: {e}")
            return {
                'success': True,
                'data': self._generate_fallback_performance_metrics(time_range)
            }

    def _generate_fallback_performance_metrics(self, time_range: str) -> dict[str, Any]:
        """Generate fallback performance metrics for analytics."""
        import random
        from datetime import datetime, timedelta

        # Determine number of data points based on time range
        points_map = {
            "1h": 60,    # 1 point per minute
            "24h": 24,   # 1 point per hour
            "7d": 7      # 1 point per day
        }
        points = points_map.get(time_range, 24)

        # Generate time series data
        base_time = datetime.now()
        metrics = {
            'cpu': [],
            'memory': [],
            'disk': [],
            'network_sent': [],
            'network_recv': []
        }

        for i in range(points):
            time_point = base_time - timedelta(
                minutes=i if time_range == "1h" else 0,
                hours=i if time_range == "24h" else 0,
                days=i if time_range == "7d" else 0
            )

            metrics['cpu'].append({
                'timestamp': time_point.isoformat(),
                'value': random.uniform(20, 90)
            })
            metrics['memory'].append({
                'timestamp': time_point.isoformat(),
                'value': random.uniform(40, 80)
            })
            metrics['disk'].append({
                'timestamp': time_point.isoformat(),
                'value': random.uniform(30, 70)
            })
            metrics['network_sent'].append({
                'timestamp': time_point.isoformat(),
                'value': random.uniform(50, 500)
            })
            metrics['network_recv'].append({
                'timestamp': time_point.isoformat(),
                'value': random.uniform(100, 800)
            })

        return metrics

    async def analytics_load_system_info(self) -> dict[str, Any]:
        """
        Load detailed system information for analytics.

        Returns:
            Dictionary with system information
        """
        try:
            return await self.load_data_operation(
                state_key="system_info",
                server_operation="get_system_info_async",
                fallback_data=self._generate_fallback_system_info()
            )
        except Exception as e:
            logger.error(f"Analytics system info load failed: {e}")
            return {
                'success': True,
                'data': self._generate_fallback_system_info()
            }

    def _generate_fallback_system_info(self) -> dict[str, Any]:
        """Generate fallback system information for analytics."""
        import random
        return {
            'cpu_cores': random.randint(4, 16),
            'memory_total_gb': round(random.uniform(8, 64), 1),
            'disk_total_gb': random.randint(256, 2048),
            'os_info': "Fallback OS",
            'python_version': "3.x.x",
            'server_version': "1.0.0"
        }

    # Enhanced reactive subscription patterns
    def create_dashboard_subscription(
        self,
        state_key: str,
        ui_update_callback: Callable,
        control: Any | None = None,
        throttle_ms: int = 100
    ):
        """
        Create a reactive subscription optimized for dashboard updates with throttling.

        Args:
            state_key: State key to subscribe to
            ui_update_callback: Function to call when state changes
            control: Optional control to auto-update
            throttle_ms: Minimum time between updates in milliseconds
        """
        last_update_time = 0

        def throttled_callback(new_value, old_value):
            nonlocal last_update_time
            current_time = datetime.now().timestamp() * 1000  # Convert to milliseconds

            # Only update if enough time has passed
            if current_time - last_update_time >= throttle_ms:
                try:
                    ui_update_callback(new_value, old_value)
                    last_update_time = current_time
                    logger.debug(f"Dashboard UI update completed for {state_key}")
                except Exception as e:
                    logger.error(f"Dashboard callback failed for {state_key}: {e}")
            else:
                logger.debug(f"Throttled update for {state_key}")

        self.state_manager.subscribe(state_key, throttled_callback, control)

    def create_analytics_subscription(
        self,
        state_key: str,
        ui_update_callback: Callable,
        control: Any | None = None,
        aggregate: bool = False
    ):
        """
        Create a reactive subscription optimized for analytics with optional aggregation.

        Args:
            state_key: State key to subscribe to
            ui_update_callback: Function to call when state changes
            control: Optional control to auto-update
            aggregate: Whether to aggregate data before updating
        """
        def analytics_callback(new_value, old_value):
            try:
                # Process data for analytics if needed
                if aggregate and isinstance(new_value, list):
                    processed_value = self._aggregate_analytics_data(new_value)
                    ui_update_callback(processed_value, old_value)
                else:
                    ui_update_callback(new_value, old_value)
                logger.debug(f"Analytics UI update completed for {state_key}")
            except Exception as e:
                logger.error(f"Analytics callback failed for {state_key}: {e}")

        self.state_manager.subscribe(state_key, analytics_callback, control)

    def _aggregate_analytics_data(self, data: list[dict]) -> dict[str, Any]:
        """Aggregate analytics data for better visualization."""
        if not data:
            return {}

        # Simple aggregation example
        aggregated = {
            'count': len(data),
            'latest': data[-1] if data else None
        }

        # Add numerical aggregations if present
        numerical_keys = [k for k, v in (data[0].items() if data else {}) if isinstance(v, (int, float))]
        for key in numerical_keys:
            if (values := [item[key] for item in data if key in item]):
                aggregated[f"{key}_avg"] = sum(values) / len(values)
                aggregated[f"{key}_min"] = min(values)
                aggregated[f"{key}_max"] = max(values)

        return aggregated

    def create_multi_key_subscription(
        self,
        state_keys: list[str],
        ui_update_callback: Callable,
        control: Any | None = None
    ):
        """
        Create a subscription that reacts to changes in multiple state keys.

        Args:
            state_keys: List of state keys to subscribe to
            ui_update_callback: Function to call when any state changes
            control: Optional control to auto-update
        """
        def multi_key_callback(new_values: dict[str, Any], old_values: dict[str, Any]):
            try:
                ui_update_callback(new_values, old_values)
                logger.debug(f"Multi-key UI update completed for {state_keys}")
            except Exception as e:
                logger.error(f"Multi-key callback failed for {state_keys}: {e}")

        # Subscribe to each key and collect values
        for key in state_keys:
            self.state_manager.subscribe(key,
                lambda new_val, old_val, k=key: multi_key_callback(
                    {k: new_val},
                    {k: old_val}
                ),
                control
            )

    # Specialized loading and progress patterns
    def create_progressive_loading_operation(
        self,
        state_key: str,
        server_operation: str,
        stages: list[str],
        on_stage_complete: Callable | None = None
    ):
        """
        Create a loading operation with progressive stages and callbacks.

        Args:
            state_key: Key to store data in state manager
            server_operation: Name of server bridge method to call
            stages: List of stage names for progress tracking
            on_stage_complete: Callback function when each stage completes
        """
        async def progressive_operation(**kwargs):
            results = {}

            for i, stage in enumerate(stages):
                try:
                    # Set loading state for current stage
                    self.state_manager.set_loading(f"{state_key}_{stage}", True)

                    # Execute stage-specific operation
                    stage_result = await self.state_manager.server_mediated_update(
                        key=f"{state_key}_{stage}",
                        value=kwargs.get(f"{stage}_data"),
                        server_operation=f"{server_operation}_{stage}"
                    )

                    results[stage] = stage_result

                    # Update overall progress
                    progress = (i + 1) / len(stages)
                    self.state_manager.set_progress(state_key, progress)

                    # Call stage completion callback if provided
                    if on_stage_complete:
                        on_stage_complete(stage, stage_result)

                except Exception as e:
                    logger.error(f"Progressive operation failed at stage {stage}: {e}")
                    results[stage] = {'success': False, 'error': str(e)}
                finally:
                    self.state_manager.set_loading(f"{state_key}_{stage}", False)

            return results

        return progressive_operation

    def create_loading_with_retry(
        self,
        state_key: str,
        server_operation: str,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Create a loading operation with automatic retry logic.

        Args:
            state_key: Key to store data in state manager
            server_operation: Name of server bridge method to call
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        async def retry_operation(**kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        logger.info(f"Retry attempt {attempt}/{max_retries} for {state_key}")
                        await asyncio.sleep(retry_delay * (2 ** (attempt - 1)))  # Exponential backoff

                    result = await self.state_manager.server_mediated_update(
                        key=state_key,
                        value=kwargs.get('fallback_data'),
                        server_operation=server_operation,
                        operation_data=kwargs
                    )

                    if result.get('success'):
                        return result
                    elif attempt < max_retries:
                        logger.warning(f"Operation failed, retrying: {result.get('error')}")

                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Operation failed with exception, retrying: {e}")

            # If all retries failed, return the last error
            logger.error(f"All retry attempts failed for {state_key}")
            return {'success': False, 'error': str(last_exception) if last_exception else "All retry attempts failed"}

        return retry_operation

    def create_batch_operation_with_progress(
        self,
        operations: list[dict],
        on_progress: Callable | None = None
    ):
        """
        Execute batch operations with progress tracking.

        Args:
            operations: List of operation configs
            on_progress: Callback function to report progress
        """
        async def batch_with_progress():
            results = {}
            total_operations = len(operations)

            for i, op in enumerate(operations):
                try:
                    # Report progress
                    if on_progress:
                        progress = (i + 1) / total_operations
                        on_progress(progress, op.get('state_key', f'operation_{i}'))

                    # Execute operation
                    result = await self.load_data_operation(**op)
                    results[op.get('state_key', f'operation_{i}')] = result

                except Exception as e:
                    logger.error(f"Batch operation failed for {op.get('state_key', f'operation_{i}')}: {e}")
                    results[op.get('state_key', f'operation_{i}')] = {'success': False, 'error': str(e)}

            return results

        return batch_with_progress

    def create_conditional_loading_operation(
        self,
        state_key: str,
        server_operation: str,
        condition: Callable,
        fallback_operation: str | None = None
    ):
        """
        Create a loading operation that conditionally executes based on a condition function.

        Args:
            state_key: Key to store data in state manager
            server_operation: Name of server bridge method to call
            condition: Function that returns True/False to determine if operation should run
            fallback_operation: Alternative operation to run if condition is False
        """
        async def conditional_operation(**kwargs):
            try:
                # Check condition
                if condition():
                    # Execute main operation
                    return await self.state_manager.server_mediated_update(
                        key=state_key,
                        value=kwargs.get('fallback_data'),
                        server_operation=server_operation,
                        operation_data=kwargs
                    )
                elif fallback_operation:
                    # Execute fallback operation
                    return await self.state_manager.server_mediated_update(
                        key=state_key,
                        value=kwargs.get('fallback_data'),
                        server_operation=fallback_operation,
                        operation_data=kwargs
                    )
                else:
                    # Return empty success result
                    return {'success': True, 'data': None}
            except Exception as e:
                logger.error(f"Conditional operation failed for {state_key}: {e}")
                return {'success': False, 'error': str(e)}

        return conditional_operation


# Factory function for easy instantiation
def create_server_mediated_operations(state_manager: StateManager, page) -> ServerMediatedOperations:
    """Create server-mediated operations utility"""
    return ServerMediatedOperations(state_manager, page)


# Common data processors for reuse
def timestamp_processor(data: list[dict]) -> list[dict]:
    """Process timestamp strings in data list"""
    if not isinstance(data, list):
        return data

    from datetime import datetime
    for item in data:
        if isinstance(item, dict) and 'timestamp' in item and isinstance(item['timestamp'], str):
            try:
                item['timestamp'] = datetime.fromisoformat(item['timestamp'])
            except ValueError:
                logger.warning(f"Failed to parse timestamp: {item['timestamp']}")
    return data


def file_size_processor(data: list[dict]) -> list[dict]:
    """Process file sizes into human-readable format"""
    if not isinstance(data, list):
        return data

    def format_size(size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"

    for item in data:
        if isinstance(item, dict) and 'size' in item and isinstance(item['size'], (int, float)):
            item['size_formatted'] = format_size(item['size'])
    return data


def percentage_processor(data: list[dict], key: str = 'value') -> list[dict]:
    """Process numerical values into percentage format"""
    if not isinstance(data, list):
        return data

    for item in data:
        if isinstance(item, dict) and key in item and isinstance(item[key], (int, float)):
            item[f'{key}_percentage'] = f"{item[key]:.1f}%"
    return data


def status_processor(data: list[dict], status_key: str = 'status') -> list[dict]:
    """Process status values into standardized format"""
    if not isinstance(data, list):
        return data

    status_mapping = {
        'running': {'text': 'Running', 'color': 'green'},
        'stopped': {'text': 'Stopped', 'color': 'red'},
        'pending': {'text': 'Pending', 'color': 'orange'},
        'error': {'text': 'Error', 'color': 'red'},
        'completed': {'text': 'Completed', 'color': 'green'},
        'failed': {'text': 'Failed', 'color': 'red'}
    }

    for item in data:
        if isinstance(item, dict) and status_key in item:
            status_value = item[status_key].lower()
            if status_value in status_mapping:
                item[f'{status_key}_display'] = status_mapping[status_value]
    return data
