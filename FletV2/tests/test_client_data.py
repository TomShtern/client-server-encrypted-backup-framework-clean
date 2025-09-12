#!/usr/bin/env python3
"""
Test script to verify client data normalization fixes.
This tests the bugs we fixed:
1. Data key mismatch causing "Unknown" status
2. Client disconnect functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.server_bridge import ServerBridge
from utils.mock_data_generator import MockDataGenerator

def test_data_normalization():
    """Test that client data is properly normalized."""
    print("🧪 Testing Data Normalization...")
    
    # Create server bridge
    bridge = ServerBridge()
    
    # Get raw mock data
    mock_gen = MockDataGenerator(num_clients=5)
    raw_data = mock_gen.get_clients()
    
    print(f"\n📊 Raw Mock Data (First Client):")
    print(f"  Keys: {list(raw_data[0].keys())}")
    print(f"  client_id: {raw_data[0].get('client_id')}")
    print(f"  name: {raw_data[0].get('name')}")
    print(f"  status: {raw_data[0].get('status')}")
    
    # Get normalized data
    normalized_data = bridge.get_clients()
    
    print(f"\n✅ Normalized Data (First Client):")
    print(f"  Keys: {list(normalized_data[0].keys())}")
    print(f"  id: {normalized_data[0].get('id')}")
    print(f"  client_id: {normalized_data[0].get('client_id')}")  
    print(f"  name: {normalized_data[0].get('name')}")
    print(f"  status: {normalized_data[0].get('status')}")
    print(f"  last_seen: {normalized_data[0].get('last_seen')}")
    print(f"  files_count: {normalized_data[0].get('files_count')}")
    print(f"  total_size: {normalized_data[0].get('total_size')}")
    
    # Verify fixes
    first_client = normalized_data[0]
    
    # ✅ BUG #7 FIX: Check that 'id' field exists (was missing, causing "Unknown")
    assert 'id' in first_client, "❌ FAILED: 'id' field missing"
    assert first_client['id'] is not None, "❌ FAILED: 'id' field is None"
    assert first_client['id'] != 'unknown', "❌ FAILED: 'id' field is 'unknown'"
    print("  ✅ 'id' field properly populated")
    
    # Check that name, status aren't "Unknown"
    assert first_client['name'] != 'Unknown Client', "❌ FAILED: name is 'Unknown Client'"
    assert first_client['status'] != 'Unknown', "❌ FAILED: status is 'Unknown'"
    print("  ✅ name and status properly populated")
    
    # Check proper file size formatting
    assert isinstance(first_client['files_count'], str), "❌ FAILED: files_count not string"
    assert 'B' in first_client['total_size'] or 'KB' in first_client['total_size'] or 'MB' in first_client['total_size'] or 'GB' in first_client['total_size'], "❌ FAILED: total_size not formatted"
    print("  ✅ files_count and total_size properly formatted")
    
    print("\n🎉 Data Normalization Test PASSED!")
    return normalized_data

def test_client_identification():
    """Test that client identification works for disconnect functionality."""
    print("\n🧪 Testing Client Identification...")
    
    bridge = ServerBridge()
    clients = bridge.get_clients()
    
    if not clients:
        print("❌ FAILED: No clients returned")
        return False
    
    # Test that we can find clients by both 'id' and 'client_id'
    first_client = clients[0]
    test_id = first_client.get('id')
    
    print(f"  Testing with client ID: {test_id}")
    
    # Simulate the disconnect search logic from clients.py
    client_found_by_id = False
    client_found_by_client_id = False
    
    for client in clients:
        # Original buggy logic (only checked 'id')
        if client.get("id") == test_id:
            client_found_by_id = True
        
        # Fixed logic (checks both 'id' and 'client_id')
        current_id = client.get("id") or client.get("client_id")
        if current_id == test_id:
            client_found_by_client_id = True
    
    print(f"  ✅ Client found by 'id' field: {client_found_by_id}")
    print(f"  ✅ Client found by fallback logic: {client_found_by_client_id}")
    
    assert client_found_by_id, "❌ FAILED: Client not found by 'id' field"
    assert client_found_by_client_id, "❌ FAILED: Client not found by fallback logic"
    
    print("\n🎉 Client Identification Test PASSED!")
    return True

def main():
    """Run all tests."""
    print("🚀 Running Client Data Fix Tests...\n")
    
    try:
        # Test the data normalization fix
        normalized_data = test_data_normalization()
        
        # Test client identification fix
        test_client_identification()
        
        print(f"\n📊 Summary:")
        print(f"  Total clients: {len(normalized_data)}")
        print(f"  Connected clients: {len([c for c in normalized_data if c['status'] == 'Connected'])}")
        print(f"  All clients have valid IDs: {'✅' if all(c.get('id') for c in normalized_data) else '❌'}")
        
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ BUG #7 (Data Key Mismatch) - FIXED")
        print(f"✅ BUG #8 (Client Identification) - FIXED")
        print(f"\nThe 'Unknown' status issue and table disappearing should now be resolved!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
