return ActionResult.error_result(
                error_message=f"File upload failed: {str(e)}",
                error_code="FILE_UPLOAD_EXCEPTION"
            )

    async def get_file_details(self, file_id: str) -> ActionResult:
        """
        Get detailed information about a specific file.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            ActionResult with file details
        """
        try:
            # Get file details from server bridge
            file_data = await self.server_bridge.get_file_details(file_id)
            if file_data:
                return ActionResult.success_result(
                    data=file_data,
                    metadata={'file_id': file_id, 'operation_type': 'file_details'}
                )
            else:
                return ActionResult.error_result(
                    error_message=f"File {file_id} not found",
                    error_code="FILE_NOT_FOUND"
                )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting file details for {file_id}: {str(e)}",
                error_code="FILE_DETAILS_EXCEPTION"
            )

    async def get_file_content(self, file_id: str) -> ActionResult:
        """
        Get content of a specific file.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            ActionResult with file content
        """
        try:
            # Get file content from server bridge
            file_content = await self.server_bridge.get_file_content(file_id)
            if file_content is not None:
                return ActionResult.success_result(
                    data=file_content,
                    metadata={'file_id': file_id, 'operation_type': 'file_content'}
                )
            else:
                return ActionResult.error_result(
                    error_message=f"File {file_id} content not available",
                    error_code="FILE_CONTENT_UNAVAILABLE"
                )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting file content for {file_id}: {str(e)}",
                error_code="FILE_CONTENT_EXCEPTION"
            )