import unittest
from unittest.mock import Mock, patch
import pytest

try:
    import flet as ft  # type: ignore
    from flet_server_gui.main import ServerGUIApp  # type: ignore
    from flet_server_gui.utils.server_bridge import ServerBridge  # type: ignore
    from flet_server_gui.components.base_table_manager import BaseTableManager  # type: ignore
    from flet_server_gui.ui.widgets.status_pill import StatusPill  # type: ignore
    from flet_server_gui.utils.connection_manager import ConnectionStatus  # type: ignore
    _gui_import_error = None
except Exception as e:  # pragma: no cover - optional GUI deps missing
    _gui_import_error = str(e)

@pytest.mark.skipif(_gui_import_error is not None, reason=f"GUI stack not available: {_gui_import_error}")
class TestGUIIntegration(unittest.TestCase):
    """Integration tests for Flet GUI components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_page = Mock(spec=ft.Page)
        self.test_page.update = Mock()
        self.test_page.controls = []  # Make controls iterable
        self.test_page.add = Mock()   # Add method for adding controls
        
    def test_server_bridge_api_completeness(self):
        """Test that server bridge has all required API methods"""
        bridge = ServerBridge()
        
        required_methods = [
            'get_clients', 'get_files', 'is_server_running', 
            'get_notifications', 'register_connection_callback'
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(bridge, method), f"Missing method: {method}")
            
            # Test method is callable
            self.assertTrue(callable(getattr(bridge, method)), f"Method not callable: {method}")
    
    def test_base_table_manager_operations(self):
        """Test table manager basic operations"""
        container = Mock(spec=ft.Container)
        
        class TestTableManager(BaseTableManager):
            def get_table_columns(self):
                return [ft.DataColumn(ft.Text("Name")), ft.DataColumn(ft.Text("Status"))]
            
            def create_table_row(self, item, on_item_select):
                # Create a checkbox with item data for selection
                checkbox = ft.Checkbox(value=False, data=item['id'])
                return ft.DataRow(cells=[
                    ft.DataCell(checkbox),
                    ft.DataCell(ft.Text(item['name'])),
                    ft.DataCell(ft.Text(item['status']))
                ])
            
            def get_sortable_columns(self):
                return ["name", "status"]
                
            def sort_data(self, data, column: str, ascending: bool = True):
                return data
                
            def _apply_custom_filters(self, items):
                return items
                
            def _apply_search_filter(self, items, search_term: str):
                return items
                
            async def perform_bulk_action(self, action: str, item_ids):
                pass
        
        # Mock the required parameters for BaseTableManager constructor
        server_bridge = Mock()
        button_factory = Mock()
        manager = TestTableManager(server_bridge, button_factory, self.test_page)
        
        # Test table initialization with correct method name
        manager.initialize_phase2_components()
        # Create the data table (this is what actually creates the table)
        manager.create_data_table()
        # Test that data_table exists after creation
        self.assertIsNotNone(manager.data_table)
        if hasattr(manager.data_table, 'columns'):
            self.assertEqual(len(manager.data_table.columns), 2)
        
        # Test data update using the correct method from current implementation
        test_items = [{'id': '1', 'name': 'Test', 'status': 'Active'}]
        manager.populate_table(test_items, lambda e: None, [])
        self.assertEqual(len(manager.data_table.rows), 1)
        
        # Test selection operations
        manager.select_all_rows()
        self.assertGreater(len(manager.selected_items), 0)
        
        manager.clear_selection()
        self.assertEqual(len(manager.selected_items), 0)
    
    def test_status_pill_state_changes(self):
        """Test status pill state management"""
        from flet_server_gui.ui.widgets.status_pill import ServerStatus
        pill = StatusPill(ServerStatus.STOPPED)
        
        # Add pill to page to prevent update errors
        self.test_page.add(pill)
        pill.page = self.test_page
        
        # Test initial state
        self.assertEqual(pill.status, ServerStatus.STOPPED)
        
        # Test status change - use animate=False to avoid update calls
        pill.set_status(ServerStatus.RUNNING, animate=False)
        self.assertEqual(pill.status, ServerStatus.RUNNING)
        
        # Test status text mapping
        self.assertEqual(pill._get_status_text(), "ONLINE")
        self.assertEqual(pill._get_status_color(), ft.Colors.GREEN)
    
    @patch('flet_server_gui.utils.server_bridge.ServerBridge')
    def test_gui_app_initialization(self, mock_bridge):
        """Test GUI app initialization without errors"""
        mock_bridge_instance = Mock()
        mock_bridge.return_value = mock_bridge_instance
        
        # Mock bridge methods
        mock_bridge_instance.get_clients.return_value = []
        mock_bridge_instance.get_files.return_value = []
        mock_bridge_instance.is_server_running.return_value = False
        
        # Test app creation doesn't raise exceptions
        try:
            app = ServerGUIApp(self.test_page)
            self.assertIsNotNone(app)
        except Exception as e:
            self.fail(f"GUI app initialization failed: {e}")
    
    def test_navigation_state_sync(self):
        """Test navigation state synchronization"""
        from flet_server_gui.managers.navigation_manager import NavigationManager
        
        switch_callback = Mock()
        nav_manager = NavigationManager(self.test_page, switch_callback)
        nav_rail = nav_manager.build()
        
        # Test navigation to different routes
        nav_manager.navigate_to('clients')
        self.assertEqual(nav_manager.current_view.value, 'clients')
        self.assertEqual(nav_rail.selected_index, 1)
        
        nav_manager.navigate_to('files') 
        self.assertEqual(nav_manager.current_view.value, 'files')
        self.assertEqual(nav_rail.selected_index, 2)

if __name__ == '__main__':
    unittest.main()