# Convenience functions for common connection management patterns
async def create_and_connect(host: str = "localhost", port: int = 1256, 
                           timeout: int = 10, server_bridge=None) -> 'ConnectionStatusManager':
    """
    Create connection manager and immediately attempt connection
    
    Returns:
        ConnectionStatusManager: Initialized and connected connection manager
    """
    config = ConnectionConfig(host=host, port=port, timeout_seconds=timeout)
    manager = ConnectionStatusManager(config, server_bridge)
    await manager.connect()
    return manager