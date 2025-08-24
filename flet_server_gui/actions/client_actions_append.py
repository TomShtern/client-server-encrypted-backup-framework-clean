    async def get_client_details(self, client_id: str) -> ActionResult:
        """
        Get detailed information about a specific client.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            ActionResult with client details
        """
        try:
            # Get client details from server bridge
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

    async def get_client_files(self, client_id: str) -> ActionResult:
        """
        Get list of files uploaded by a specific client.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            ActionResult with client files list
        """
        try:
            # Get all files and filter by client
            all_files = await self.server_bridge.get_file_list()
            client_files = [f for f in all_files if f.get('client') == client_id]
            
            return ActionResult.success_result(
                data=client_files,
                metadata={
                    'client_id': client_id, 
                    'file_count': len(client_files),
                    'operation_type': 'client_files'
                }
            )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting files for client {client_id}: {str(e)}",
                error_code="CLIENT_FILES_EXCEPTION"
            )

    async def import_clients(self, file_path: str) -> ActionResult:
        """
        Import clients from a file.
        
        Args:
            file_path: Path to the file containing client data
            
        Returns:
            ActionResult with import results
        """
        try:
            # This would be implemented based on server bridge capabilities
            # For now, return a placeholder result
            return ActionResult.success_result(
                data={'imported_clients': 0, 'file_path': file_path},
                metadata={'operation_type': 'client_import', 'implemented': False}
            )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Client import failed: {str(e)}",
                error_code="CLIENT_IMPORT_EXCEPTION"
            )