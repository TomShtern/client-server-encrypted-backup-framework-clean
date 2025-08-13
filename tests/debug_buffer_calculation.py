#!/usr/bin/env python3
"""
Debug script to test our buffer calculation logic
"""

def calculate_enhanced_buffer_size(file_size: int) -> int:
    """Python version of our C++ buffer calculation"""
    
    if file_size <= 512:                        # ≤512B files: 512B buffer
        raw_buffer_size = 512                   # Tiny configs, small scripts
    elif file_size <= 2 * 1024:                # 512B-2KB files: 1KB buffer
        raw_buffer_size = 1024                  # Small configs, env files
    elif file_size <= 8 * 1024:                # 2KB-8KB files: 2KB buffer
        raw_buffer_size = 2 * 1024              # Code files, small docs
    elif file_size <= 32 * 1024:               # 8KB-32KB files: 4KB buffer
        raw_buffer_size = 4 * 1024              # Medium docs, small images
    elif file_size <= 128 * 1024:              # 32KB-128KB files: 8KB buffer
        raw_buffer_size = 8 * 1024              # Large docs, medium images
    elif file_size <= 1024 * 1024:             # 128KB-1MB files: 16KB buffer
        raw_buffer_size = 16 * 1024             # PDFs, large images, small videos
    elif file_size <= 10 * 1024 * 1024:        # 1MB-10MB files: 32KB buffer
        raw_buffer_size = 32 * 1024             # Large media, archives
    elif file_size <= 100 * 1024 * 1024:       # 10MB-100MB files: 64KB buffer
        raw_buffer_size = 64 * 1024             # Large videos, big archives
    elif file_size <= 500 * 1024 * 1024:       # 100MB-500MB files: 128KB buffer
        raw_buffer_size = 128 * 1024            # Very large files
    else:                                       # >500MB files: 256KB buffer
        raw_buffer_size = 256 * 1024            # Huge files (up to 1GB)
    
    return raw_buffer_size

def should_use_streaming_mode(file_size: int) -> bool:
    """Check if file should use streaming mode"""
    return file_size > 10 * 1024 * 1024  # 10MB threshold

def test_42kb_file() -> bool:
    """Test the specific case that's failing"""
    file_size = 42091  # The exact size from the log
    
    print(f"=== Testing 42KB File (size: {file_size} bytes) ===")
    print(f"File size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    
    # Test buffer calculation
    buffer_size = calculate_enhanced_buffer_size(file_size)
    print(f"Calculated buffer size: {buffer_size:,} bytes ({buffer_size / 1024:.1f} KB)")
    
    # Test streaming mode
    streaming = should_use_streaming_mode(file_size)
    print(f"Should use streaming mode: {streaming}")
    print(f"Transfer mode: {'Streaming' if streaming else 'Memory-based'}")
    
    # Calculate packet count
    # Assume AES adds some padding (worst case ~16 bytes)
    estimated_encrypted_size = file_size + 16
    packet_count = (estimated_encrypted_size + buffer_size - 1) // buffer_size
    print(f"Estimated encrypted size: {estimated_encrypted_size:,} bytes")
    print(f"Estimated packet count: {packet_count}")
    
    # Check if packet count is valid
    if packet_count > 65535:  # UINT16_MAX
        print("❌ ERROR: Packet count exceeds UINT16_MAX!")
        return False
    
    print("✅ Buffer calculation looks correct")
    return True

def compare_old_vs_new() -> bool:
    """Compare old vs new buffer calculation for 42KB"""
    file_size = 42091
    
    print(f"\n=== Old vs New Buffer Calculation ===")
    
    # OLD logic (from before our changes)
    if file_size <= 1024:
        old_buffer = 1024
    elif file_size <= 4 * 1024:
        old_buffer = 2 * 1024
    elif file_size <= 16 * 1024:
        old_buffer = 4 * 1024
    elif file_size <= 64 * 1024:
        old_buffer = 8 * 1024
    elif file_size <= 512 * 1024:
        old_buffer = 16 * 1024
    elif file_size <= 10 * 1024 * 1024:
        old_buffer = 32 * 1024
    else:
        old_buffer = 64 * 1024
    
    # NEW logic
    new_buffer = calculate_enhanced_buffer_size(file_size)
    
    print(f"File size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    print(f"OLD buffer: {old_buffer:,} bytes ({old_buffer / 1024:.1f} KB)")
    print(f"NEW buffer: {new_buffer:,} bytes ({new_buffer / 1024:.1f} KB)")
    
    if old_buffer == new_buffer:
        print("✅ Buffer sizes match - this is not the issue")
    else:
        print("⚠️ Buffer sizes differ - this might be the issue")
    
    return old_buffer == new_buffer

if __name__ == "__main__":
    print("Debugging Buffer Calculation for 42KB File Transfer Issue")
    print("=" * 60)
    
    # Test the specific failing case
    test_result = test_42kb_file()
    
    # Compare old vs new logic
    comparison_result = compare_old_vs_new()
    
    print(f"\n=== Results ===")
    print(f"Buffer calculation test: {'✅ PASS' if test_result else '❌ FAIL'}")
    print(f"Old vs new comparison: {'✅ SAME' if comparison_result else '⚠️ DIFFERENT'}")
    
    if test_result and comparison_result:
        print("\n🤔 Buffer calculation is not the issue.")
        print("The problem is likely in:")
        print("1. Retry mechanism interfering with successful transfers")
        print("2. Streaming mode check logic")
        print("3. AES encryption in the new code path")
        print("4. Protocol compatibility issue")
    else:
        print("\n💥 Found potential buffer calculation issue!")
