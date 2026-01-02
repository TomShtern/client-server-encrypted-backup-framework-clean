I have created the following plan after thorough exploration and analysis of the codebase. Follow the below plan verbatim. Trust the files and references. Do not re-verify what's written in the plan. Explore only when absolutely necessary. First implement all the proposed file changes and then I'll review all the changes together at the end.

### Observations

I analyzed the FletV2 GUI codebase and found it's a comprehensive backup management application with server-mediated operations. The main issues are in three view files: missing event handlers, undefined control references, incomplete CRUD operations, and improper update patterns. The server bridge and state manager are well-implemented and ready to support the fixes. The codebase follows a consistent pattern of user action → server bridge → state manager → reactive UI updates.

### Approach

I'll fix the critical CRUD operations infrastructure by addressing missing event handlers, implementing proper control references, completing CRUD operation handlers, and ensuring efficient UI updates. The approach focuses on making minimal targeted fixes to existing code rather than rewriting, maintaining the established server-mediated patterns, and ensuring all operations work correctly with the mock data fallback system.

### Reasoning

I explored the FletV2 codebase structure and identified the main view files (clients.py, files.py, database.py) along with supporting utilities (server_bridge.py, state_manager.py). I analyzed the server-mediated operation patterns, identified specific missing handlers and undefined references, and mapped out the CRUD operation implementation status across all three views.

## Mermaid Diagram

sequenceDiagram
    participant User
    participant View
    participant StateManager
    participant ServerBridge
    participant UI

    User->>View: Trigger CRUD Action (disconnect, delete, verify)
    View->>StateManager: set_loading(operation, true)
    View->>StateManager: server_mediated_update(key, data, server_operation)
    StateManager->>ServerBridge: call server_operation_async()
    
    alt Server Available
        ServerBridge->>ServerBridge: Execute real server operation
        ServerBridge-->>StateManager: Return success result
    else Server Unavailable
        ServerBridge->>ServerBridge: Execute mock fallback
        ServerBridge-->>StateManager: Return mock result
    end
    
    StateManager->>StateManager: update_async(key, result_data)
    StateManager->>View: Trigger reactive callbacks
    View->>UI: control.update() (not page.update())
    StateManager->>StateManager: set_loading(operation, false)
    View->>User: Show success/error message

## Proposed File Changes

### views\clients.py(MODIFY)

References: 

- utils\dialog_consolidation_helper.py
- utils\server_bridge.py
- utils\state_manager.py

Fix the missing `confirmation_dialog` reference in the `disconnect_action` function by removing the direct dialog reference and relying solely on the imported `show_confirmation` helper. Remove lines 147-149 that reference undefined `confirmation_dialog.open` and `confirmation_dialog.update()`. 

Add missing `ft.Ref` definitions for better control management:
- Add `add_client_dialog_ref = ft.Ref[ft.AlertDialog]()`
- Add `client_details_dialog_ref = ft.Ref[ft.AlertDialog]()`

Implement the missing `add_client_action` UI integration by creating an "Add Client" button in the header row and implementing the corresponding dialog with form fields for client name, IP address, and initial status.

Complete the `delete_client_action` implementation by adding a confirmation dialog wrapper similar to the disconnect action, ensuring it calls the server bridge's `delete_client_async` method and refreshes the clients list afterward.

Ensure all control updates use `control.update()` instead of `page.update()` by reviewing and fixing any remaining instances in the feedback text and loading indicator updates.

Add proper error handling for edge cases where `clients_table_ref.current` might be None before attempting to update the table rows.

### views\files.py(MODIFY)

References: 

- utils\state_manager.py
- utils\server_bridge.py
- utils\dialog_consolidation_helper.py

Fix the undefined `update_table` function call in `apply_filters()` by renaming the existing `update_table_display()` function to `update_table()` to match the caller expectations.

Fix variable scoping issues in filter lambdas by converting the inline lambda functions to proper named functions that can access nonlocal variables:
- Replace `on_change=lambda e: apply_search(e.control.value)` with a proper function
- Replace `on_change=lambda e: apply_filter("status", e.control.value)` with a proper function
- Replace `on_change=lambda e: apply_filter("type", e.control.value)` with a proper function

Add missing `ft.Ref` definitions for better control management:
- Add `files_table_ref = ft.Ref[ft.DataTable]()`
- Add `status_text_ref = ft.Ref[ft.Text]()`
- Add `search_field_ref = ft.Ref[ft.TextField]()`
- Add `loading_indicator_ref = ft.Ref[ft.ProgressRing]()`

Update the `delete_file_async` success path to properly refresh the state manager with updated files data by calling `await state_manager.update_async("files_data", updated_files_data, source="local_delete")` to maintain state consistency.

Ensure all async operations properly set and clear loading states using `state_manager.set_loading()` in try/finally blocks.

Replace any remaining `page.update()` calls with targeted `control.update()` calls for better performance.

### views\database.py(MODIFY)

References: 

- utils\state_manager.py
- utils\server_bridge.py
- utils\dialog_consolidation_helper.py

Add missing `ft.Ref` definitions for better control management:
- Add `data_table_ref = ft.Ref[ft.DataTable]()`
- Add `status_text_ref = ft.Ref[ft.Text]()`
- Add `tables_count_text_ref = ft.Ref[ft.Text]()`
- Add `records_count_text_ref = ft.Ref[ft.Text]()`
- Add `size_text_ref = ft.Ref[ft.Text]()`
- Add `table_info_text_ref = ft.Ref[ft.Text]()`
- Add `last_updated_text_ref = ft.Ref[ft.Text]()`
- Add `loading_indicator_ref = ft.Ref[ft.ProgressRing]()`

Fix the `load_table_data_action` function to properly handle both dropdown change events and direct table name parameters by adding parameter validation and ensuring the function signature matches all call sites.

Complete the missing CRUD operation handlers:
- Enhance `update_row_action` with proper validation and error handling for different data types
- Improve `delete_row_action` with cascading delete support for related records
- Add `add_row_action` for creating new database records with proper form validation

Implement proper export error handling for real server failure scenarios by adding retry logic and fallback to client-side export when server export fails.

Ensure all database operations properly integrate with the server bridge by validating return values and handling both success and failure cases appropriately.

Replace all `control.update()` calls with proper ref-based updates using the newly added control references for consistent and safe UI updates.

Add proper loading state management for all database operations to provide user feedback during long-running queries or exports.