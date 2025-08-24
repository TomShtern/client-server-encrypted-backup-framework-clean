    async def get_client_details(self, client_id: str) -> ActionResult:
        """
        Get detailed information about a specific client through server bridge.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            ActionResult with client details
        """
        try:
            client_data = await self.server_bridge.get_client_details(client_id)
            if client_data:
                return ActionResult.success_result(
                    data=client_data,
                    metadata={'client_id': client_id, 'operation_type': 'client_details'}
                )
            else:
                return ActionResult.error_result(
                    error_message=f"Client {client_id} not found",
                    error_code="CLIENT_NOT_FOUND"
                )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting client details for {client_id}: {str(e)}",
                error_code="CLIENT_DETAILS_EXCEPTION"
            )

    async def get_file_list(self) -> ActionResult:
        """
        Get list of all files from the server.
        
        Returns:
            ActionResult with file list
        """
        try:
            files = await self.server_bridge.get_file_list()
            return ActionResult.success_result(
                data=files,
                metadata={
                    'file_count': len(files),
                    'operation_type': 'file_list'
                }
            )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting file list: {str(e)}",
                error_code="FILE_LIST_EXCEPTION"
            )

    async def get_client_list(self) -> ActionResult:
        """
        Get list of all clients from the server.
        
        Returns:
            ActionResult with client list
        """
        try:
            clients = await self.server_bridge.get_client_list()
            return ActionResult.success_result(
                data=clients,
                metadata={
                    'client_count': len(clients),
                    'operation_type': 'client_list'
                }
            )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting client list: {str(e)}",
                error_code="CLIENT_LIST_EXCEPTION"
            )