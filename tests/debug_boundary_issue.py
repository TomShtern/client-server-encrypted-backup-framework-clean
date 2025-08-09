#!/usr/bin/env python3
"""
Debug script to precisely trace the 64KB vs 66KB boundary issue.
This creates the exact files and traces through the encryption logic.
"""

def calculate_aes_encrypted_size(original_size):
    """Calculate the exact AES-CBC encrypted size with PKCS7 padding"""
    # AES block size is 16 bytes
    block_size = 16
    
    # PKCS7 padding: always adds at least 1 byte, up to 16 bytes
    # If data is exactly aligned to block boundary, adds full 16-byte block
    if original_size % block_size == 0:
        # Perfectly aligned - PKCS7 adds full block
        padding_bytes = block_size
    else:
        # Not aligned - pad to next boundary
        padding_bytes = block_size - (original_size % block_size)
    
    encrypted_size = original_size + padding_bytes
    return encrypted_size, padding_bytes

def analyze_packet_breakdown(file_size, buffer_size=65536):
    """Analyze how a file gets broken into packets"""
    encrypted_size, padding = calculate_aes_encrypted_size(file_size)
    
    # Calculate packet count (same logic as client)
    packet_count = (encrypted_size + buffer_size - 1) // buffer_size
    
    packets = []
    data_offset = 0
    
    for i in range(packet_count):
        chunk_size = min(buffer_size, encrypted_size - data_offset)
        packets.append({
            'packet_num': i + 1,
            'size': chunk_size,
            'offset': data_offset
        })
        data_offset += chunk_size
    
    return {
        'original_size': file_size,
        'encrypted_size': encrypted_size,
        'padding_bytes': padding,
        'packet_count': packet_count,
        'packets': packets
    }

def main():
    print("=== 64KB vs 66KB Boundary Analysis ===\n")
    
    # Test the exact sizes mentioned in the issue
    test_sizes = [
        (64 * 1024, "64KB"),
        (66 * 1024, "66KB")
    ]
    
    for size_bytes, size_name in test_sizes:
        print(f"--- {size_name} File ({size_bytes:,} bytes) ---")
        analysis = analyze_packet_breakdown(size_bytes)
        
        print(f"Original size:  {analysis['original_size']:,} bytes")
        print(f"Encrypted size: {analysis['encrypted_size']:,} bytes (+{analysis['padding_bytes']} padding)")
        print(f"Packet count:   {analysis['packet_count']}")
        print("Packet breakdown:")
        
        for packet in analysis['packets']:
            print(f"  Packet {packet['packet_num']}: {packet['size']:,} bytes")
        
        # Key analysis
        if analysis['packet_count'] == 1:
            print("✓ Single-packet transfer")
        else:
            print(f"✓ Multi-packet transfer")
            last_packet_size = analysis['packets'][-1]['size']
            if last_packet_size < 100:
                print(f"  ⚠️  Last packet is very small: {last_packet_size} bytes")
            elif last_packet_size > 2000:
                print(f"  ⚠️  Last packet is medium size: {last_packet_size} bytes")
        
        print()
    
    print("=== Key Differences ===")
    print("64KB: Last packet = 16 bytes (tiny)")
    print("66KB: Last packet = 2,064 bytes (medium)")
    print("\nHypothesis: The issue may be related to how the server handles")
    print("different second packet sizes in multi-packet transfers.")

if __name__ == "__main__":
    main()