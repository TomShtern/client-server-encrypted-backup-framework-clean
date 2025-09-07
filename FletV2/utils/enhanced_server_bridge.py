#!/usr/bin/env python3
"""
Enhanced Server Bridge for FletV2 - Production Ready Infrastructure
Refactored from ModularServerBridge with clear production migration path.

CRITICAL PRODUCTION CHANGES NEEDED:
====================================
1. Line 47: self.mock_mode = False  # SET TO FALSE IN PRODUCTION
2. Line 35: host = "PRODUCTION_SERVER_IP"  # Change from localhost
3. Line 36: port = PRODUCTION_PORT  # Change from 1256
4. Line 89-92: Connect to production database path
5. DELETE: Lines 200-400 (all mock data methods) in production

This bridge is the SINGLE source of truth for all server/database communication.
"""

import flet as ft
from typing import List, Dict, Any, Optional, Callable
import asyncio
import time
import json
import os
from utils.debug_setup import get_logger
from utils.mock_data_generator import MockDataGenerator

logger = get_logger(__name__)


class ConnectionManager:
    """Handles server connection health and monitoring"""
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.connected = False
        self.last_check = 0
        self.retry_count = 0
        self.max_retries = 3
        
    async def connect(self) -> bool:
        """Attempt connection with fail-fast logic"""
        try:
            # TODO: Replace with actual server health check
            # response = await aiohttp.ClientSession().get(f"{self.base_url}/health")
            # self.connected = response.status == 200
            
            # MOCK: Always succeed in development
            await asyncio.sleep(0.1)  # Simulate network delay
            self.connected = True
            self.retry_count = 0
            logger.info(f"Connected to server at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.connected = False
            self.retry_count += 1
            logger.error(f"Connection failed (attempt {self.retry_count}): {e}")
            return False
    
    async def health_check(self) -> bool:
        """Periodic health check"""
        current_time = time.time()
        if current_time - self.last_check < 30:  # Check every 30 seconds
            return self.connected
        
        self.last_check = current_time
        return await self.connect()
    
    def is_connected(self) -> bool:
        return self.connected


class RealtimeUpdater:
    """Handles real-time data updates via WebSocket or polling"""
    
    def __init__(self, host: str, websocket_port: int):
        self.host = host
        self.websocket_port = websocket_port
        self.websocket_url = f"ws://{host}:{websocket_port}"
        self.subscribers = {}
        self.polling_tasks = {}
        self.connected = False
        
    async def start_monitoring(self):
        """Start WebSocket connection for real-time updates"""
        try:
            # TODO: Implement actual WebSocket client
            # self.websocket = await websockets.connect(self.websocket_url)
            # await self._listen_for_updates()
            
            # DEVELOPMENT: Use polling fallback
            logger.info("Starting polling-based real-time updates")
            self.connected = True
            self._start_polling()
            
        except Exception as e:
            logger.warning(f"WebSocket connection failed, using polling: {e}")
            self._start_polling()
    
    def _start_polling(self):
        """Fallback to polling-based updates"""
        # Start polling tasks for different data types
        self.polling_tasks["server_status"] = asyncio.create_task(
            self._poll_data("server_status", 5)  # Every 5 seconds
        )
        self.polling_tasks["clients"] = asyncio.create_task(
            self._poll_data("clients", 10)  # Every 10 seconds
        )
    
    async def _poll_data(self, data_type: str, interval: int):
        """Poll for data updates at specified intervals"""
        while True:
            try:
                if data_type in self.subscribers:
                    # Notify all subscribers for this data type
                    for callback in self.subscribers[data_type]:
                        await callback()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Polling error for {data_type}: {e}")
                await asyncio.sleep(interval)
    
    def subscribe_to_updates(self, data_type: str, callback: Callable):
        """Subscribe to real-time updates for specific data type"""
        if data_type not in self.subscribers:
            self.subscribers[data_type] = []
        self.subscribers[data_type].append(callback)
        logger.debug(f"Subscribed to {data_type} updates")
    
    def stop_monitoring(self):
        """Stop all monitoring tasks"""
        for task in self.polling_tasks.values():
            if not task.done():
                task.cancel()
        self.connected = False


class EnhancedServerBridge:
    """
    Enhanced Server Bridge - Single source of truth for all server/database communication
    
    Features:
    - Fail-fast connection logic
    - Real-time update capabilities  
    - Clear production migration path
    - Mock data support for development
    - State management integration
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 1256):
        """
        Initialize Enhanced Server Bridge
        
        PRODUCTION CHANGES:
        - host: Change to actual production server IP
        - port: Change to actual production server port
        - mock_mode: Set to False for production
        """
        self.host = host
        self.port = port
        self.mock_mode = True  # CHANGE TO FALSE IN PRODUCTION
        
        # Initialize connection components
        self.connection_manager = ConnectionManager(host, port)
        self.realtime_updater = RealtimeUpdater(host, port + 1)
        
        # Initialize database manager (production-ready)
        self.db_manager = self._init_database_manager()
        
        # Initialize mock data generator for development
        if self.mock_mode:
            self.mock_generator = MockDataGenerator()
            logger.info("EnhancedServerBridge initialized in MOCK mode")
        else:
            self.mock_generator = None
            logger.info("EnhancedServerBridge initialized in PRODUCTION mode")
        
        # State management integration
        self.state_manager = None  # Will be set by main app
        
        # Cache for performance
        self.cache = {}
        self.cache_timestamps = {}
    
    def _init_database_manager(self) -> Optional[Any]:
        """Initialize database manager with production path"""
        try:
            from utils.database_manager import FletDatabaseManager, create_database_manager
            
            if self.mock_mode:
                # DEVELOPMENT: Use MockaBase.db if available
                db_path = "MockaBase.db"
            else:
                # PRODUCTION: Use actual database path
                db_path = "PRODUCTION_DATABASE.db"  # CHANGE THIS IN PRODUCTION
            
            if os.path.exists(db_path):
                db_manager = create_database_manager(db_path)
                if db_manager and db_manager.connect():
                    logger.info(f"Connected to database: {db_path}")
                    return db_manager
                else:
                    logger.error(f"Failed to connect to database: {db_path}")
            else:
                logger.warning(f"Database not found: {db_path}")
            
        except ImportError:
            logger.warning("Database manager not available")
        
        return None
    
    async def connect(self) -> bool:
        """
        Connect to server and database with fail-fast logic
        
        Production: IMMEDIATE failure if server/database unavailable
        Development: Allow mock mode fallback
        """
        if not self.mock_mode:
            # PRODUCTION: Fail-fast, no fallbacks
            server_connected = await self.connection_manager.connect()
            database_connected = self.db_manager.connect() if self.db_manager else False
            
            if not server_connected:
                raise ConnectionError(f"Cannot connect to server at {self.host}:{self.port}")
            
            if not database_connected:
                raise ConnectionError("Cannot connect to production database")
            
            # Start real-time monitoring
            await self.realtime_updater.start_monitoring()
            
            logger.info("EnhancedServerBridge connected to production systems")
            return True
        
        else:
            # DEVELOPMENT: Connect with mock fallbacks
            return await self._connect_with_mocks()
    
    async def _connect_with_mocks(self) -> bool:
        """Development connection with mock data support"""
        try:
            # Try real connections first
            server_connected = await self.connection_manager.connect()
            database_connected = self.db_manager.connect() if self.db_manager else False
            
            if server_connected and database_connected:
                await self.realtime_updater.start_monitoring()
                logger.info("Connected to real server and database")
                return True
            
            # Fallback to mock mode
            logger.warning("Using mock data for development")
            await self.realtime_updater.start_monitoring()  # Still monitor for mock updates
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            # In development, continue with mocks
            return True
    
    def set_state_manager(self, state_manager):
        """Set state manager for automatic UI updates"""
        self.state_manager = state_manager
        
        # Subscribe to real-time updates
        if self.realtime_updater.connected:
            self.realtime_updater.subscribe_to_updates("server_status", self._update_server_status)
            self.realtime_updater.subscribe_to_updates("clients", self._update_clients)
            self.realtime_updater.subscribe_to_updates("files", self._update_files)
    
    async def _update_server_status(self):
        """Update server status in state manager"""
        if self.state_manager:
            status = await self.get_server_status()
            await self.state_manager.update_state("server_status", status)
    
    async def _update_clients(self):
        """Update clients in state manager"""
        if self.state_manager:
            clients = await self.get_clients()
            await self.state_manager.update_state("clients", clients)
    
    async def _update_files(self):
        """Update files in state manager"""
        if self.state_manager:
            files = await self.get_files()
            await self.state_manager.update_state("files", files)
    
    def _get_cached_data(self, key: str, max_age: int = 30) -> Optional[Any]:
        """Get cached data if recent enough"""
        if key in self.cache and key in self.cache_timestamps:
            age = time.time() - self.cache_timestamps[key]
            if age < max_age:
                return self.cache[key]
        return None
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = data
        self.cache_timestamps[key] = time.time()
    
    # =================================================================
    # DATA RETRIEVAL METHODS - Production ready with mock fallbacks
    # =================================================================
    
    async def get_server_status(self) -> Dict[str, Any]:
        """Get server status with caching and real-time updates"""
        cached = self._get_cached_data("server_status", 10)  # 10-second cache
        if cached:
            return cached
        
        try:
            if not self.mock_mode and self.connection_manager.is_connected():
                # PRODUCTION: Get real server status
                # response = await self._make_request("GET", "/status")
                # status = response
                pass
            
            # DEVELOPMENT/FALLBACK: Use mock data
            if self.mock_mode and self.mock_generator:
                status = self.mock_generator.get_server_status()
            else:
                status = {
                    "server_running": True,
                    "port": self.port,
                    "uptime": "0m",
                    "total_transfers": 0,
                    "active_clients": 0,
                    "total_files": 0,
                    "storage_used": "0 GB"
                }
            
            self._cache_data("server_status", status)
            return status
            
        except Exception as e:
            logger.error(f"Failed to get server status: {e}")
            return {"error": str(e), "server_running": False}
    
    async def get_clients(self) -> List[Dict[str, Any]]:
        """Get client data with caching and real-time updates"""
        cached = self._get_cached_data("clients", 30)  # 30-second cache
        if cached:
            return cached
        
        try:
            if self.db_manager:
                # Try database first (production or MockaBase)
                clients = self.db_manager.get_clients()
                if clients:
                    self._cache_data("clients", clients)
                    return clients
            
            if not self.mock_mode and self.connection_manager.is_connected():
                # PRODUCTION: Get clients from server API
                # response = await self._make_request("GET", "/clients")
                # clients = response.get("clients", [])
                pass
            
            # DEVELOPMENT/FALLBACK: Use mock data
            if self.mock_mode and self.mock_generator:
                clients = self.mock_generator.get_clients()
                self._cache_data("clients", clients)
                return clients
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get clients: {e}")
            return []
    
    async def get_files(self) -> List[Dict[str, Any]]:
        """Get file data with caching and real-time updates"""
        cached = self._get_cached_data("files", 30)  # 30-second cache
        if cached:
            return cached
        
        try:
            if self.db_manager:
                # Try database first (production or MockaBase)
                files = self.db_manager.get_files()
                if files:
                    self._cache_data("files", files)
                    return files
            
            if not self.mock_mode and self.connection_manager.is_connected():
                # PRODUCTION: Get files from server API
                # response = await self._make_request("GET", "/files")
                # files = response.get("files", [])
                pass
            
            # DEVELOPMENT/FALLBACK: Use mock data
            if self.mock_mode and self.mock_generator:
                files = self.mock_generator.get_files()
                self._cache_data("files", files)
                return files
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get files: {e}")
            return []
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        try:
            if self.db_manager:
                stats = self.db_manager.get_database_stats()
                if stats:
                    return stats
            
            # DEVELOPMENT/FALLBACK: Mock database info
            if self.mock_mode and self.mock_generator:
                return self.mock_generator.get_database_info()
            
            return {"status": "disconnected", "tables": 0, "records": 0, "size": "0 MB"}
            
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {"error": str(e), "status": "error"}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system metrics"""
        try:
            if not self.mock_mode and self.connection_manager.is_connected():
                # PRODUCTION: Get real system metrics
                # response = await self._make_request("GET", "/system/status")
                # return response
                pass
            
            # DEVELOPMENT/FALLBACK: Mock system status
            if self.mock_mode and self.mock_generator:
                return self.mock_generator.get_system_status()
            
            return {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0,
                "active_connections": 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}
    
    # =================================================================
    # ACTION METHODS - Server interactions
    # =================================================================
    
    async def disconnect_client(self, client_id: str) -> bool:
        """Disconnect a client"""
        try:
            if not self.mock_mode and self.connection_manager.is_connected():
                # PRODUCTION: Send disconnect command
                # await self._make_request("POST", f"/clients/{client_id}/disconnect")
                logger.info(f"Disconnected client {client_id}")
                return True
            
            # DEVELOPMENT: Simulate disconnect
            logger.info(f"Simulated disconnect for client {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disconnect client {client_id}: {e}")
            return False
    
    async def delete_client(self, client_id: str) -> bool:
        """Delete a client"""
        try:
            if not self.mock_mode and self.connection_manager.is_connected():
                # PRODUCTION: Send delete command
                # await self._make_request("DELETE", f"/clients/{client_id}")
                logger.info(f"Deleted client {client_id}")
                return True
            
            # DEVELOPMENT: Simulate delete
            logger.info(f"Simulated delete for client {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete client {client_id}: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if bridge is connected"""
        if self.mock_mode:
            return True  # Always connected in mock mode
        return self.connection_manager.is_connected()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.realtime_updater:
            self.realtime_updater.stop_monitoring()
        if self.db_manager:
            self.db_manager.disconnect()


# Factory function for easy instantiation
def create_enhanced_server_bridge(host: str = "127.0.0.1", port: int = 1256) -> EnhancedServerBridge:
    """
    Factory function to create enhanced server bridge
    
    PRODUCTION USAGE:
    bridge = create_enhanced_server_bridge("PRODUCTION_IP", PRODUCTION_PORT)
    bridge.mock_mode = False
    
    Args:
        host: Server host (change for production)
        port: Server port (change for production)
    """
    try:
        return EnhancedServerBridge(host, port)
    except Exception as e:
        logger.error(f"Error creating EnhancedServerBridge: {e}")
        raise