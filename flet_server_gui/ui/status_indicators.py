"""
PHASE 4: SERVER STATUS INDICATORS - Professional status pill components with real-time updates

SKELETON IMPLEMENTATION STATUS:
✅ Complete class structures with enums and dataclasses
✅ Method signatures with comprehensive parameter documentation
✅ Integration points with Phase 1-3 components clearly defined
✅ TODO sections with specific implementation guidance
✅ Material Design 3 compliance patterns
✅ Accessibility and responsive design considerations

NEXT AI AGENT INSTRUCTIONS:
This skeleton provides the complete architecture for server status indicators.
Fill in the TODO sections to implement:
1. Real-time status monitoring with WebSocket integration
2. Animated status transitions with Material Design 3 motion
3. Status pill interactions and click behaviors
4. Status history tracking and trend analysis
5. Integration with Phase 3 theme consistency and responsive layout

INTEGRATION DEPENDENCIES:
- Phase 1: Thread-safe UI updates via ui_updater patterns
- Phase 2: Error handling via ErrorHandler, notifications via ToastManager
- Phase 3: Theme integration via ThemeConsistencyManager, responsive via ResponsiveLayoutManager
- Existing: ServerBridge for real server status, DatabaseManager for persistence
"""

from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import asyncio
from datetime import datetime, timedelta
import flet as ft
from flet_server_gui.ui.theme_m3 import TOKENS


class ServerStatus(Enum):
    """Server operational status with clear semantic meaning"""
    RUNNING = "running"           # Server actively handling requests
    STOPPED = "stopped"           # Server intentionally stopped by user
    STARTING = "starting"         # Server in startup process
    STOPPING = "stopping"        # Server in shutdown process
    ERROR = "error"              # Server encountered critical error
    UNKNOWN = "unknown"          # Status cannot be determined
    MAINTENANCE = "maintenance"   # Server in maintenance mode


class StatusSeverity(Enum):
    """Status indicator severity levels for visual hierarchy"""
    SUCCESS = "success"     # Green indicators - everything working
    INFO = "info"          # Blue indicators - informational status
    WARNING = "warning"    # Orange indicators - attention needed
    ERROR = "error"        # Red indicators - critical issues
    NEUTRAL = "neutral"    # Gray indicators - neutral status


class StatusIndicatorSize(Enum):
    """Status pill size variants for different UI contexts"""
    COMPACT = "compact"    # Small pills for dense layouts (height: 24px)
    NORMAL = "normal"      # Standard pills for main UI (height: 32px)
    LARGE = "large"        # Prominent pills for dashboards (height: 40px)
    HERO = "hero"         # Extra large for main status display (height: 48px)


class StatusAnimation(Enum):
    """Animation patterns for status transitions"""
    NONE = "none"           # No animation - instant change
    FADE = "fade"           # Fade out/in transition
    SLIDE = "slide"         # Slide transition with direction
    PULSE = "pulse"         # Pulsing animation for active states
    BREATHING = "breathing" # Subtle breathing animation for waiting states
    BOUNCE = "bounce"       # Bounce animation for status changes


@dataclass
class StatusMetrics:
    """Real-time metrics for server status monitoring"""
    uptime: timedelta = field(default_factory=lambda: timedelta(0))
    total_connections: int = 0
    active_connections: int = 0
    failed_connections: int = 0
    avg_response_time: float = 0.0
    last_activity: Optional[datetime] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0


@dataclass
class StatusHistoryEntry:
    """Historical status entry for trend analysis"""
    timestamp: datetime
    status: ServerStatus
    severity: StatusSeverity
    message: str
    metrics: Optional[StatusMetrics] = None
    duration: Optional[timedelta] = None


@dataclass
class StatusPillConfig:
    """Configuration for status pill appearance and behavior"""
    size: StatusIndicatorSize = StatusIndicatorSize.NORMAL
    show_text: bool = True
    show_icon: bool = True
    show_metrics: bool = False
    clickable: bool = True
    tooltip: bool = True
    animation: StatusAnimation = StatusAnimation.FADE
    auto_refresh: bool = True
    refresh_interval: int = 5000  # milliseconds
    
    # Visual customization
    border_radius: int = 16
    elevation: int = 1
    padding: int = 12
    
    # Interaction settings
    hover_elevation: int = 4
    click_elevation: int = 8
    ripple_effect: bool = True


class StatusIndicatorManager:
    """
    PHASE 4 SKELETON: Professional server status indicator system
    
    Manages real-time status pills with Material Design 3 compliance,
    responsive behavior, and integration with Phase 1-3 components.
    
    ARCHITECTURE:
    - Real-time status monitoring via WebSocket/polling
    - Animated status transitions with accessibility support
    - Status history tracking and trend analysis
    - Integration with theme consistency and responsive layout
    - Professional tooltip system with detailed metrics
    """
    
    def __init__(self, page: ft.Page, server_bridge=None, theme_manager=None, layout_manager=None):
        self.page = page
        self.server_bridge = server_bridge
        self.theme_manager = theme_manager
        self.layout_manager = layout_manager
        
        # Status management
        self._current_status = ServerStatus.UNKNOWN
        self._current_severity = StatusSeverity.NEUTRAL
        self._current_metrics = StatusMetrics()
        self._status_history: List[StatusHistoryEntry] = []
        self._max_history_entries = 1000
        
        # UI components registry
        self._status_pills: Dict[str, ft.Control] = {}
        self._status_callbacks: Dict[str, List[Callable]] = {}
        self._update_tasks: Dict[str, asyncio.Task] = {}
        
        # Configuration
        self._default_config = StatusPillConfig()
        self._pill_configs: Dict[str, StatusPillConfig] = {}
        
        # State management
        self._is_monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._last_update: Optional[datetime] = None

    # ═══════════════════════════════════════════════════════════════════════════════════
    # CORE STATUS MONITORING - TODO: Implement real-time status tracking
    # ═══════════════════════════════════════════════════════════════════════════════════
    
    async def start_monitoring(self) -> bool:
        """
        TODO: Start real-time status monitoring
        
        IMPLEMENTATION REQUIREMENTS:
        1. Initialize WebSocket connection to server bridge
        2. Start periodic status polling with configurable intervals
        3. Set up metrics collection from system resources
        4. Begin status history tracking
        5. Register for server lifecycle events
        6. Handle reconnection logic for network issues
        
        INTEGRATION POINTS:
        - server_bridge.get_server_status() for current status
        - server_bridge.get_server_metrics() for performance data
        - Phase 1 ui_updater for thread-safe UI updates
        - Phase 2 error_handler for monitoring failures
        
        RETURNS:
        bool: True if monitoring started successfully, False otherwise
        """
        if self._is_monitoring:
            return True
            
        try:
            # TODO: Initialize server bridge connection
            # TODO: Start status polling task
            # TODO: Set up metrics collection
            # TODO: Begin history tracking
            
            self._is_monitoring = True
            self._monitor_task = asyncio.create_task(self._monitoring_loop())
            return True
        except Exception as e:
            # TODO: Handle monitoring startup errors
            # Integration: self.error_handler.handle_error(e, ErrorCategory.SYSTEM, ErrorSeverity.HIGH)
            return False
    
    async def stop_monitoring(self) -> bool:
        """
        TODO: Stop real-time status monitoring
        
        IMPLEMENTATION REQUIREMENTS:
        1. Cancel all monitoring tasks gracefully
        2. Close WebSocket connections
        3. Save final status history to persistence
        4. Clean up resources and timers
        5. Update all status pills to show offline state
        
        RETURNS:
        bool: True if monitoring stopped successfully, False otherwise
        """
        if not self._is_monitoring:
            return True
            
        try:
            # TODO: Cancel monitoring task
            # TODO: Close connections
            # TODO: Save final state
            # TODO: Clean up resources
            
            self._is_monitoring = False
            return True
        except Exception as e:
            # TODO: Handle monitoring shutdown errors
            return False
    
    async def _monitoring_loop(self):
        """
        TODO: Main monitoring loop for continuous status updates
        
        IMPLEMENTATION REQUIREMENTS:
        1. Implement configurable polling intervals
        2. Fetch current server status and metrics
        3. Compare with previous status for change detection
        4. Update status history when changes occur
        5. Notify all registered status pills
        6. Handle monitoring errors with exponential backoff
        7. Support graceful shutdown on cancellation
        
        PERFORMANCE CONSIDERATIONS:
        - Use asyncio.sleep() for non-blocking delays
        - Batch status updates to prevent UI flooding
        - Cache metrics to avoid redundant calculations
        - Implement circuit breaker for failed connections
        """
        while self._is_monitoring:
            try:
                # TODO: Fetch current server status
                # TODO: Get performance metrics
                # TODO: Compare with previous state
                # TODO: Update history if status changed
                # TODO: Notify all status pills
                # TODO: Sleep until next poll interval
                
                await asyncio.sleep(self._default_config.refresh_interval / 1000.0)
                
            except asyncio.CancelledError:
                # TODO: Handle graceful cancellation
                break
            except Exception as e:
                # TODO: Handle monitoring errors with backoff
                await asyncio.sleep(5.0)  # Error backoff

    # ═══════════════════════════════════════════════════════════════════════════════════
    # STATUS PILL CREATION - TODO: Implement Material Design 3 status pills
    # ═══════════════════════════════════════════════════════════════════════════════════
    
    def create_status_pill(self, pill_id: str, config: Optional[StatusPillConfig] = None) -> ft.Control:
        """
        TODO: Create a professional status pill with Material Design 3 styling
        
        IMPLEMENTATION REQUIREMENTS:
        1. Build Material Design 3 compliant pill container
        2. Add status icon with proper color coding
        3. Include status text with accessibility labels
        4. Implement tooltip with detailed metrics
        5. Add click handler for detailed status dialog
        6. Apply responsive sizing based on screen size
        7. Integrate with theme consistency manager
        8. Add smooth animations for status changes
        
        VISUAL SPECIFICATIONS:
        - Pill shape with configurable border radius
        - Color coding: Green(running), Red(error), Orange(warning), Gray(stopped)
        - Typography following Material Design 3 scale
        - Proper elevation and shadow effects
        - Hover and click states with elevation changes
        - Loading animations for transitional states
        
        ACCESSIBILITY REQUIREMENTS:
        - Semantic HTML roles and ARIA labels
        - Keyboard navigation support
        - Screen reader compatible tooltips
        - High contrast color ratios
        - Focus indicators meeting WCAG 2.1 AA
        
        PARAMETERS:
        pill_id: Unique identifier for this status pill
        config: Optional configuration override
        
        RETURNS:
        ft.Control: Complete status pill component ready for UI integration
        """
        effective_config = config or self._default_config
        
        try:
            # TODO: Build pill container with Material Design 3 styling
            # TODO: Add status icon with color coding
            # TODO: Create status text with proper typography
            # TODO: Implement detailed tooltip system
            # TODO: Add click handler for status details
            # TODO: Apply responsive sizing
            # TODO: Integrate theme colors
            # TODO: Add accessibility attributes
            
            # Placeholder pill structure
            pill_container = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=12, color=TOKENS['outline']),
                    ft.Text("Status", size=12, color=TOKENS['on_background']),
                ], tight=True),
                padding=effective_config.padding,
                border_radius=effective_config.border_radius,
                bgcolor=TOKENS['surface_variant'],
                # TODO: Replace with complete implementation
            )
            
            self._status_pills[pill_id] = pill_container
            self._pill_configs[pill_id] = effective_config
            
            return pill_container
            
        except Exception as e:
            # TODO: Handle pill creation errors
            # Return fallback pill
            return ft.Text(f"Status ({pill_id})", color=TOKENS['error'])
    
    def create_status_hero_pill(self, pill_id: str = "main_status") -> ft.Control:
        """
        TODO: Create large hero status pill for main dashboard
        
        IMPLEMENTATION REQUIREMENTS:
        1. Build prominent hero-sized status display
        2. Include large status icon with breathing animation
        3. Add primary status text with uptime display
        4. Include secondary metrics (connections, response time)
        5. Add progress indicators for transitional states
        6. Implement click-to-expand for detailed view
        7. Apply hero-specific styling and spacing
        
        VISUAL SPECIFICATIONS:
        - Large container (height: 48px minimum)
        - Prominent icon (24px) with status-appropriate animation
        - Primary text using Material Design 3 headline typography
        - Secondary metrics using body typography
        - Subtle background with appropriate elevation
        - Click affordance with hover elevation increase
        
        RETURNS:
        ft.Control: Hero status pill for main dashboard placement
        """
        hero_config = StatusPillConfig(
            size=StatusIndicatorSize.HERO,
            show_text=True,
            show_icon=True,
            show_metrics=True,
            animation=StatusAnimation.BREATHING
        )
        
        # TODO: Implement hero-specific styling and layout
        # TODO: Add large icon with breathing animation
        # TODO: Include uptime and connection metrics
        # TODO: Add click handler for detailed status view
        
        return self.create_status_pill(pill_id, hero_config)

    # ═══════════════════════════════════════════════════════════════════════════════════
    # STATUS UPDATES - TODO: Implement smooth status transitions
    # ═══════════════════════════════════════════════════════════════════════════════════
    
    async def update_status(self, new_status: ServerStatus, metrics: Optional[StatusMetrics] = None, message: str = "") -> bool:
        """
        TODO: Update server status with smooth animations
        
        IMPLEMENTATION REQUIREMENTS:
        1. Validate status transition (e.g., STOPPING -> STOPPED)
        2. Update internal status tracking
        3. Add entry to status history
        4. Determine appropriate severity level
        5. Update all registered status pills with animations
        6. Trigger status change callbacks
        7. Save status to persistence if configured
        8. Send notifications for critical status changes
        
        ANIMATION REQUIREMENTS:
        - Smooth color transitions using Material Design 3 motion curves
        - Icon changes with fade or morph animations
        - Text updates with slide or fade transitions
        - Breathing animations for active states
        - Pulse animations for error states
        
        INTEGRATION POINTS:
        - Phase 2: ToastManager for critical status notifications
        - Phase 2: ErrorHandler for status update failures
        - Phase 3: ThemeConsistencyManager for color updates
        - Existing: DatabaseManager for status persistence
        
        PARAMETERS:
        new_status: The new server status to display
        metrics: Optional performance metrics
        message: Human-readable status message
        
        RETURNS:
        bool: True if status update successful, False otherwise
        """
        try:
            previous_status = self._current_status
            
            # TODO: Validate status transition
            # TODO: Update internal state
            # TODO: Add to status history
            # TODO: Determine severity level
            # TODO: Update all status pills with animation
            # TODO: Trigger callbacks
            # TODO: Save to persistence
            # TODO: Send notifications for critical changes
            
            self._current_status = new_status
            if metrics:
                self._current_metrics = metrics
            self._last_update = datetime.now()
            
            return True
            
        except Exception as e:
            # TODO: Handle status update errors
            return False
    
    async def _update_pill_appearance(self, pill_id: str, status: ServerStatus, severity: StatusSeverity) -> bool:
        """
        TODO: Update individual status pill with new status
        
        IMPLEMENTATION REQUIREMENTS:
        1. Get pill configuration and current theme
        2. Calculate new colors based on status and severity
        3. Update icon based on status type
        4. Update text content with proper formatting
        5. Apply smooth animation based on configuration
        6. Update tooltip with current metrics
        7. Handle responsive adjustments if screen size changed
        
        ANIMATION IMPLEMENTATION:
        - Use ft.AnimatedContainer for smooth transitions
        - Coordinate color, size, and content changes
        - Respect user motion preferences (prefers-reduced-motion)
        - Apply Material Design 3 motion duration curves
        
        PARAMETERS:
        pill_id: Identifier of the pill to update
        status: New server status to display
        severity: Severity level for visual styling
        
        RETURNS:
        bool: True if pill update successful, False otherwise
        """
        if pill_id not in self._status_pills:
            return False
            
        try:
            pill = self._status_pills[pill_id]
            config = self._pill_configs.get(pill_id, self._default_config)
            
            # TODO: Calculate new appearance based on status
            # TODO: Update colors using theme manager
            # TODO: Change icon and text content
            # TODO: Apply configured animation
            # TODO: Update tooltip content
            # TODO: Handle responsive adjustments
            
            return True
            
        except Exception as e:
            # TODO: Handle pill update errors
            return False

    # ═══════════════════════════════════════════════════════════════════════════════════
    # STATUS HISTORY & ANALYTICS - TODO: Implement status tracking and trends
    # ═══════════════════════════════════════════════════════════════════════════════════
    
    def get_status_history(self, hours: int = 24) -> List[StatusHistoryEntry]:
        """
        TODO: Get status history for specified time period
        
        IMPLEMENTATION REQUIREMENTS:
        1. Filter history entries by time range
        2. Sort by timestamp in descending order
        3. Include metrics data if available
        4. Calculate status duration for each entry
        5. Return comprehensive history data
        
        PARAMETERS:
        hours: Number of hours of history to return
        
        RETURNS:
        List[StatusHistoryEntry]: Filtered status history
        """
        # TODO: Filter history by time range
        # TODO: Sort and format entries
        # TODO: Calculate status durations
        
        return self._status_history[-100:]  # Placeholder
    
    def get_status_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        TODO: Calculate status statistics and trends
        
        IMPLEMENTATION REQUIREMENTS:
        1. Calculate uptime percentage for time period
        2. Count status transitions and frequency
        3. Identify most common error states
        4. Calculate average metrics (response time, connections)
        5. Determine status stability trends
        6. Generate reliability score
        
        RETURN STRUCTURE:
        {
            'uptime_percentage': float,
            'total_transitions': int,
            'status_breakdown': Dict[ServerStatus, timedelta],
            'error_frequency': int,
            'avg_response_time': float,
            'avg_connections': float,
            'reliability_score': float,
            'trend': 'improving'|'stable'|'degrading'
        }
        """
        # TODO: Implement comprehensive statistics calculation
        return {
            'uptime_percentage': 95.5,
            'total_transitions': 12,
            'status_breakdown': {},
            'error_frequency': 2,
            'avg_response_time': 150.0,
            'avg_connections': 8.5,
            'reliability_score': 0.92,
            'trend': 'stable'
        }

    # ═══════════════════════════════════════════════════════════════════════════════════
    # CALLBACK & EVENT SYSTEM - TODO: Implement status change notifications
    # ═══════════════════════════════════════════════════════════════════════════════════
    
    def register_status_callback(self, callback_id: str, callback: Callable[[ServerStatus, StatusMetrics], None]) -> bool:
        """
        TODO: Register callback for status change notifications
        
        IMPLEMENTATION REQUIREMENTS:
        1. Validate callback function signature
        2. Store callback in registry with unique ID
        3. Support multiple callbacks per status change
        4. Handle callback errors gracefully
        5. Provide callback removal mechanism
        
        PARAMETERS:
        callback_id: Unique identifier for this callback
        callback: Function to call on status changes
        
        RETURNS:
        bool: True if callback registered successfully
        """
        if not callable(callback):
            return False
            
        # TODO: Validate callback signature
        # TODO: Store in callback registry
        # TODO: Set up error handling for callback execution
        
        if callback_id not in self._status_callbacks:
            self._status_callbacks[callback_id] = []
        self._status_callbacks[callback_id].append(callback)
        
        return True
    
    def remove_status_callback(self, callback_id: str) -> bool:
        """
        TODO: Remove status callback by ID
        
        PARAMETERS:
        callback_id: ID of callback to remove
        
        RETURNS:
        bool: True if callback removed successfully
        """
        # TODO: Remove callback from registry
        if callback_id in self._status_callbacks:
            del self._status_callbacks[callback_id]
            return True
        return False
    
    async def _trigger_status_callbacks(self, status: ServerStatus, metrics: StatusMetrics):
        """
        TODO: Trigger all registered status callbacks
        
        IMPLEMENTATION REQUIREMENTS:
        1. Iterate through all registered callbacks
        2. Execute callbacks asynchronously
        3. Handle callback errors without breaking other callbacks
        4. Log callback execution results
        5. Support callback timeout handling
        
        PARAMETERS:
        status: Current server status
        metrics: Current performance metrics
        """
        for callback_id, callbacks in self._status_callbacks.items():
            for callback in callbacks:
                try:
                    # TODO: Execute callback with error handling
                    # TODO: Implement callback timeout
                    # TODO: Log callback results
                    if asyncio.iscoroutinefunction(callback):
                        await callback(status, metrics)
                    else:
                        callback(status, metrics)
                except Exception as e:
                    # TODO: Handle callback errors gracefully
                    pass

    # ═══════════════════════════════════════════════════════════════════════════════════
    # INTEGRATION METHODS - TODO: Connect with Phase 1-3 systems
    # ═══════════════════════════════════════════════════════════════════════════════════
    
    def integrate_with_theme_manager(self, theme_manager) -> bool:
        """
        TODO: Integrate with Phase 3 Theme Consistency Manager
        
        IMPLEMENTATION REQUIREMENTS:
        1. Register for theme change notifications
        2. Update all status pills when theme changes
        3. Apply theme colors to status indicators
        4. Handle light/dark mode transitions
        5. Ensure accessibility compliance with new theme
        
        INTEGRATION POINTS:
        - theme_manager.register_component_callback()
        - theme_manager.get_component_colors()
        - theme_manager.validate_color_contrast()
        
        RETURNS:
        bool: True if integration successful
        """
        if not theme_manager:
            return False
            
        try:
            # TODO: Register for theme change notifications
            # TODO: Set up automatic pill updates on theme changes
            # TODO: Validate color accessibility compliance
            
            self.theme_manager = theme_manager
            return True
        except Exception as e:
            return False
    
    def integrate_with_layout_manager(self, layout_manager) -> bool:
        """
        TODO: Integrate with Phase 3 Responsive Layout Manager
        
        IMPLEMENTATION REQUIREMENTS:
        1. Register for screen size change notifications
        2. Update pill sizes based on responsive breakpoints
        3. Adjust pill spacing and layout in different screen sizes
        4. Handle orientation changes on mobile devices
        5. Update tooltip positioning for different layouts
        
        INTEGRATION POINTS:
        - layout_manager.register_responsive_component()
        - layout_manager.get_current_breakpoint()
        - layout_manager.get_responsive_properties()
        
        RETURNS:
        bool: True if integration successful
        """
        if not layout_manager:
            return False
            
        try:
            # TODO: Register for layout change notifications
            # TODO: Set up responsive pill size updates
            # TODO: Handle tooltip positioning updates
            
            self.layout_manager = layout_manager
            return True
        except Exception as e:
            return False
    
    # ═══════════════════════════════════════════════════════════════════════════════════
    # UTILITY & HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════════════════════
    
    def _get_status_severity(self, status: ServerStatus) -> StatusSeverity:
        """Determine appropriate severity level for given status"""
        severity_map = {
            ServerStatus.RUNNING: StatusSeverity.SUCCESS,
            ServerStatus.STOPPED: StatusSeverity.NEUTRAL,
            ServerStatus.STARTING: StatusSeverity.INFO,
            ServerStatus.STOPPING: StatusSeverity.INFO,
            ServerStatus.ERROR: StatusSeverity.ERROR,
            ServerStatus.UNKNOWN: StatusSeverity.WARNING,
            ServerStatus.MAINTENANCE: StatusSeverity.WARNING,
        }
        return severity_map.get(status, StatusSeverity.NEUTRAL)
    
    def _get_status_icon(self, status: ServerStatus) -> str:
        """Get appropriate Material Design icon for status"""
        icon_map = {
            ServerStatus.RUNNING: ft.Icons.PLAY_CIRCLE,
            ServerStatus.STOPPED: ft.Icons.STOP_CIRCLE,
            ServerStatus.STARTING: ft.Icons.REFRESH,
            ServerStatus.STOPPING: ft.Icons.PAUSE_CIRCLE,
            ServerStatus.ERROR: ft.Icons.ERROR,
            ServerStatus.UNKNOWN: ft.Icons.HELP,
            ServerStatus.MAINTENANCE: ft.Icons.BUILD,
        }
        return icon_map.get(status, ft.Icons.CIRCLE)
    
    def _get_status_color(self, status: ServerStatus) -> str:
        """Get Material Design 3 color for status"""
        color_map = {
            ServerStatus.RUNNING: TOKENS['secondary'],
            ServerStatus.STOPPED: TOKENS['outline'],
            ServerStatus.STARTING: TOKENS['primary'],
            ServerStatus.STOPPING: TOKENS['tertiary'],
            ServerStatus.ERROR: TOKENS['error'],
            ServerStatus.UNKNOWN: TOKENS['tertiary'],
            ServerStatus.MAINTENANCE: TOKENS['tertiary'],
        }
        return color_map.get(status, TOKENS['outline'])


# ═══════════════════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS - Convenience functions for common use cases
# ═══════════════════════════════════════════════════════════════════════════════════════

def create_status_indicator_manager(page: ft.Page, server_bridge=None, theme_manager=None, layout_manager=None) -> StatusIndicatorManager:
    """
    Factory function to create and initialize StatusIndicatorManager
    
    PARAMETERS:
    page: Flet page instance
    server_bridge: Optional server bridge for real status monitoring
    theme_manager: Optional Phase 3 theme consistency manager
    layout_manager: Optional Phase 3 responsive layout manager
    
    RETURNS:
    StatusIndicatorManager: Initialized status indicator system
    """
    manager = StatusIndicatorManager(page, server_bridge, theme_manager, layout_manager)
    
    # TODO: Perform initial integration setup
    if theme_manager:
        manager.integrate_with_theme_manager(theme_manager)
    if layout_manager:
        manager.integrate_with_layout_manager(layout_manager)
    
    return manager

def create_simple_status_pill(status: ServerStatus, text: str = None) -> ft.Control:
    """
    Quick factory for simple status pill without full manager
    
    PARAMETERS:
    status: Server status to display
    text: Optional text override
    
    RETURNS:
    ft.Control: Basic status pill component
    """
    # TODO: Implement simple pill creation
    # For prototyping and simple use cases
    return ft.Container(
        content=ft.Text(text or status.value),
        padding=8,
        border_radius=16,
        bgcolor=TOKENS['surface_variant']
    )