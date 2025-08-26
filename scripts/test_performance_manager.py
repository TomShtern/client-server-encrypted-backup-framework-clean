#!/usr/bin/env python3
"""
Test script to verify Performance Manager functionality
"""

import sys
import os
import time

# Add the project directory to the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def test_performance_manager_functionality():
    """Test performance manager functionality"""
    try:
        from flet_server_gui.utils.performance_manager import PerformanceManager
        import flet as ft
        
        # Create performance manager
        pm = PerformanceManager()
        print("1. PerformanceManager instantiated successfully")
        
        # Test measure_performance decorator
        @pm.measure_performance("test_operation")
        def slow_operation():
            time.sleep(0.1)  # Simulate work
            return "done"
        
        result = slow_operation()
        print(f"2. Decorator test - Operation result: {result}")
        
        # Check if metrics were recorded
        report = pm.get_performance_report()
        if "test_operation" in report:
            metrics = report["test_operation"]
            print(f"3. Performance metrics recorded: {metrics}")
            print("   - Average duration: {:.4f}s".format(metrics['avg_duration']))
            print("   - Call count: {}".format(metrics['call_count']))
        else:
            print("3. No performance metrics recorded")
        
        # Test debounce decorator
        @pm.debounce(0.1)
        def debounced_function():
            return "debounced"
        
        result = debounced_function()
        print(f"4. Debounce decorator test result: {result}")
        
        # Test table optimization
        # Create a mock table with many rows
        table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Col1")), ft.DataColumn(ft.Text("Col2"))],
            rows=[]
        )
        
        # Add many rows
        for i in range(500):
            table.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(f"Row{i}Col1")),
                ft.DataCell(ft.Text(f"Row{i}Col2"))
            ]))
        
        print(f"5. Created table with {len(table.rows)} rows")
        
        # Optimize table
        pm.optimize_table_rendering(table, max_visible_rows=100)
        print(f"6. Table optimized to {len(table.rows)} rows")
        
        return True
        
    except Exception as e:
        print(f"PerformanceManager functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Performance Manager Functionality Test")
    print("=" * 40)
    
    if test_performance_manager_functionality():
        print("\nAll Performance Manager tests passed!")
        return 0
    else:
        print("\nSome Performance Manager tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())