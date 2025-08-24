    def _download_file(self, file_info):
        """Download a file."""
        async def download_action():
            try:
                filename = file_info.get('filename', 'Unknown')
                # Use action system to download file
                # For now, we'll just show a dialog - in a real implementation, this would trigger a file save dialog
                result = await self.file_actions.download_file(filename, f"./downloads/{filename}")
                
                if result.success:
                    self.show_dialog("success", "Download Complete", f"File '{filename}' downloaded successfully")
                else:
                    self.show_dialog("error", "Download Failed", f"Failed to download file '{filename}': {result.error_message}")
            except Exception as e:
                self.show_dialog("error", "Error", f"Failed to download file: {str(e)}")
        
        # Run the async function
        import asyncio
        asyncio.create_task(download_action())

    def _verify_file(self, file_info):
        """Verify a file's integrity."""
        async def verify_action():
            try:
                filename = file_info.get('filename', 'Unknown')
                # Use action system to verify file
                result = await self.file_actions.verify_file_integrity(filename)
                
                if result.success:
                    if result.data.get('is_valid'):
                        self.show_dialog("success", "Verification Complete", f"File '{filename}' is valid")
                    else:
                        self.show_dialog("warning", "Verification Failed", f"File '{filename}' is invalid")
                else:
                    self.show_dialog("error", "Verification Failed", f"Failed to verify file '{filename}': {result.error_message}")
            except Exception as e:
                self.show_dialog("error", "Error", f"Failed to verify file: {str(e)}")
        
        # Run the async function
        import asyncio
        asyncio.create_task(verify_action())