#!/usr/bin/env python3
"""Simple boundary analysis without unicode issues"""

from typing import Tuple

def calculate_aes_encrypted_size(original_size: int) -> Tuple[int, int]:
    # AES block size is 16 bytes
    # PKCS7 padding: always adds full 16-byte block when perfectly aligned
    block_size = 16
    if original_size % block_size == 0:
        padding_bytes = block_size  # Full block padding
    else:
        padding_bytes = block_size - (original_size % block_size)
    
    encrypted_size = original_size + padding_bytes
    return encrypted_size, padding_bytes

def analyze_packets(file_size: int, buffer_size: int = 65536):
    encrypted_size: int
    padding: int
    encrypted_size, padding = calculate_aes_encrypted_size(file_size)
    packet_count: int = (encrypted_size + buffer_size - 1) // buffer_size
    
    print(f"File size: {file_size} bytes ({file_size//1024}KB)")
    print(f"Encrypted: {encrypted_size} bytes (+{padding} padding)")
    print(f"Packets: {packet_count}")
    
    for i in range(packet_count):
        start: int = i * buffer_size
        chunk_size: int = min(buffer_size, encrypted_size - start)
        print(f"  Packet {i+1}: {chunk_size} bytes")
    print()

# Analyze the boundary
print("=== BOUNDARY ANALYSIS ===")
analyze_packets(64 * 1024)  # 64KB
analyze_packets(66 * 1024)  # 66KB

print("KEY OBSERVATION:")
print("- 64KB file: 2 packets (65536 + 16 bytes)")  
print("- 66KB file: 2 packets (65536 + 2064 bytes)")
print("- DIFFERENCE: Second packet size (16 vs 2064 bytes)")
print()
print("HYPOTHESIS: Issue occurs when second packet > certain threshold")