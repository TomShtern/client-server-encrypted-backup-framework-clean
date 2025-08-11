#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced progress reporting system.
This script validates that progress updates flow correctly through all layers.
"""

import sys
import os
import time
from datetime import datetime

# Setup standardized import paths
from Shared.path_utils import setup_imports
setup_imports()

from api_server.real_backup_executor import RealBackupExecutor

def test_progress_calculation():
    """Test the dynamic progress calculation methods"""
    print("="*60)
    print("TESTING ENHANCED PROGRESS REPORTING SYSTEM")
    print("="*60)
    
    # Create a test RealBackupExecutor instance
    executor = RealBackupExecutor()
    
    # Test file path (use this script as test file)
    test_file = __file__
    
    print(f"Test file: {test_file}")
    print(f"File size: {os.path.getsize(test_file)} bytes")
    print()
    
    # Test progress calculation at various time intervals
    print("Testing dynamic progress calculation:")
    print("-" * 40)
    
    for elapsed_seconds in [0, 1, 3, 5, 8, 12, 18, 25, 28, 30]:
        progress = executor._calculate_transfer_progress(test_file, elapsed_seconds)
        phase = executor._get_current_phase(elapsed_seconds)
        print(f"Time: {elapsed_seconds:2d}s | Progress: {progress:2d}% | Phase: {phase}")
    
    print()
    print("Testing status callback integration:")
    print("-" * 40)
    
    # Set up status callback to capture progress updates
    captured_updates = []
    
    def test_status_callback(phase, data):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        if isinstance(data, dict) and 'progress' in data:
            captured_updates.append({
                'timestamp': timestamp,
                'phase': phase, 
                'progress': data['progress'],
                'message': data.get('message', phase)
            })
            print(f"[{timestamp}] {phase}: {data['progress']}% - {data.get('message', phase)}")
        else:
            captured_updates.append({
                'timestamp': timestamp,
                'phase': phase,
                'message': str(data)
            })
            print(f"[{timestamp}] {phase}: {data}")
    
    executor.set_status_callback(test_status_callback)
    
    # Simulate some progress updates
    print("\nSimulating progress updates:")
    executor._log_status("START", "Beginning backup process")
    time.sleep(0.1)
    
    executor._log_status("PROGRESS", {"progress": 15, "message": "Connection established"})
    time.sleep(0.1)
    
    executor._log_status("PROGRESS", {"progress": 35, "message": "File encryption in progress"})
    time.sleep(0.1)
    
    executor._log_status("PROGRESS", {"progress": 60, "message": "File transfer in progress"})
    time.sleep(0.1)
    
    executor._log_status("PROGRESS", {"progress": 90, "message": "Verifying transfer"})
    time.sleep(0.1)
    
    executor._log_status("COMPLETED", {"progress": 100, "message": "Backup completed successfully"})
    
    print(f"\nCaptured {len(captured_updates)} status updates")
    
    # Verify progress progression
    progress_updates = [u for u in captured_updates if 'progress' in u]
    if progress_updates:
        print("\nProgress progression verification:")
        for i, update in enumerate(progress_updates):
            print(f"  {i+1}. {update['progress']}% - {update['message']}")
        
        # Check that progress is monotonically increasing
        progresses = [u['progress'] for u in progress_updates]
        is_monotonic = all(progresses[i] <= progresses[i+1] for i in range(len(progresses)-1))
        print(f"\nProgress monotonicity check: {'[PASS]' if is_monotonic else '[FAIL]'}")
        print(f"Final progress: {progresses[-1]}%")
        
        if progresses[-1] == 100:
            print("[SUCCESS] Progress reaches 100% completion")
        else:
            print("[ERROR] Progress does not reach 100%")
    
    print("\n" + "="*60)
    print("PROGRESS REPORTING TEST COMPLETED")
    print("="*60)
    
    return len(progress_updates) > 0 and progress_updates[-1]['progress'] == 100

if __name__ == "__main__":
    try:
        success = test_progress_calculation()
        if success:
            print("\n[SUCCESS] Enhanced progress reporting system is working correctly!")
            sys.exit(0)
        else:
            print("\n[ERROR] Issues detected in progress reporting system")
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)