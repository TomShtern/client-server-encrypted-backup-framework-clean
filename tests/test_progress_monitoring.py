#!/usr/bin/env python3
"""
Quick test script to verify the progress monitoring fixes are working.
This script tests the FileReceiptProgressTracker and RobustProgressMonitor without
needing to run the full backup system.
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# Setup standardized import paths
from Shared.path_utils import setup_imports
setup_imports()

def test_file_receipt_tracker():
    """Test the FileReceiptProgressTracker functionality"""
    print("="*50)
    print("Testing FileReceiptProgressTracker")
    print("="*50)
    
    # Import after adding to path
    from api.real_backup_executor import FileReceiptProgressTracker, WATCHDOG_AVAILABLE
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    print(f"Test directory: {test_dir}")
    print(f"Watchdog available: {WATCHDOG_AVAILABLE}")
    
    # Initialize tracker
    tracker = FileReceiptProgressTracker(test_dir)
    
    # Start monitoring for a test file
    test_context = {
        "original_filename": "test_file.txt",
        "file_size": 1024
    }
    
    print("\n1. Starting monitoring...")
    tracker.start_monitoring(test_context)
    
    # Check initial progress
    print("\n2. Checking initial progress...")
    initial_progress = tracker.get_progress()
    print(f"Initial progress: {initial_progress}")
    
    # Create the test file
    print("\n3. Creating test file...")
    test_file = Path(test_dir) / "test_file.txt"
    with open(test_file, 'w') as f:
        f.write("Test content for file receipt monitoring")
    
    print(f"Created file: {test_file}")
    
    # Wait a moment for detection
    print("\n4. Waiting for file detection...")
    for i in range(10):  # Wait up to 5 seconds
        time.sleep(0.5)
        progress = tracker.get_progress()
        print(f"Progress check {i+1}: {progress.get('progress', 0):.1f}% - {progress.get('message', 'No message')}")
        
        if progress.get("override", False):
            print("✅ FILE RECEIPT OVERRIDE DETECTED!")
            break
    else:
        print("❌ File receipt not detected within timeout")
    
    # Stop monitoring
    print("\n5. Stopping monitoring...")
    tracker.stop_monitoring()
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    print(f"Cleaned up test directory: {test_dir}")

def test_robust_progress_monitor():
    """Test the RobustProgressMonitor with FileReceiptProgressTracker integration"""
    print("\n" + "="*50)
    print("Testing RobustProgressMonitor Integration") 
    print("="*50)
    
    # Import after adding to path
    from api.real_backup_executor import RobustProgressMonitor
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    print(f"Test directory: {test_dir}")
    
    # Initialize monitor 
    monitor = RobustProgressMonitor(test_dir)
    
    # Set up a callback to capture progress updates
    progress_updates = []
    def progress_callback(phase, data):
        progress_updates.append((phase, data))
        print(f"Progress callback: {phase} - {data}")
    
    monitor.set_status_callback(progress_callback)
    
    # Start monitoring
    test_context = {
        "original_filename": "monitor_test.txt",
        "file_size": 2048
    }
    
    print("\n1. Starting RobustProgressMonitor...")
    monitor.start_monitoring(test_context)
    
    # Check initial progress
    print("\n2. Checking initial progress...")
    initial_progress = monitor.get_progress()
    print(f"Initial progress: {initial_progress}")
    
    # Create the test file
    print("\n3. Creating test file...")
    test_file = Path(test_dir) / "monitor_test.txt"
    with open(test_file, 'w') as f:
        f.write("Test content for robust progress monitoring")
    
    print(f"Created file: {test_file}")
    
    # Poll progress multiple times
    print("\n4. Polling progress updates...")
    for i in range(10):  # Poll for up to 5 seconds
        time.sleep(0.5)
        progress = monitor.get_progress()
        print(f"Poll {i+1}: {progress.get('progress', 0):.1f}% - {progress.get('message', 'No message')} - Tracker: {progress.get('tracker', 'Unknown')}")
        
        if progress.get("override", False):
            print("✅ GROUND TRUTH OVERRIDE DETECTED!")
            break
    else:
        print("❌ Ground truth override not detected within timeout")
    
    # Stop monitoring
    print("\n5. Stopping monitoring...")
    monitor.stop_monitoring()
    
    # Show captured progress updates
    print(f"\n6. Captured {len(progress_updates)} progress updates:")
    for i, (phase, data) in enumerate(progress_updates):
        print(f"  Update {i+1}: {phase} - {data}")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    print(f"Cleaned up test directory: {test_dir}")

if __name__ == "__main__":
    try:
        print("Progress Monitoring Test Suite")
        print("Testing the fixes for file receipt detection and progress polling")
        print()
        
        test_file_receipt_tracker()
        test_robust_progress_monitor()
        
        print("\n" + "="*50)
        print("✅ All tests completed!")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)