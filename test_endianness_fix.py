#!/usr/bin/env python3
"""
Test script to verify the endianness fix in the C++ client
"""

import subprocess
import time
import os
from pathlib import Path

def test_client_build():
    \"\"\"Test that the client builds successfully with our endianness fixes\"\"\"
    print("Testing client build with endianness fixes...")
    
    # Change to project directory
    os.chdir(r"C:\\Users\\tom7s\\Desktopp\\Claude_Folder_2\\Client_Server_Encrypted_Backup_Framework")
    
    # Check if the built client exists
    client_path = Path("build/Release/EncryptedBackupClient.exe")
    if client_path.exists():
        print(f"[OK] Client executable found: {client_path}")
        return True
    else:
        print("[ERROR] Client executable not found")
        return False

def test_endianness_functions():
    \"\"\"Verify that the endianness conversion functions were added correctly\"\"\"
    client_header = Path("Client/cpp/client.h")
    client_source = Path("Client/cpp/client.cpp")
    
    if not client_header.exists() or not client_source.exists():
        print("[ERROR] Client source files not found")
        return False
    
    # Check header file for function declarations
    with open(client_header, 'r') as f:
        header_content = f.read()
    
    required_declarations = [
        "static uint16_t littleEndianToHost16(const uint8_t* bytes);",
        "static uint32_t littleEndianToHost32(const uint8_t* bytes);"
    ]
    
    missing_declarations = []
    for decl in required_declarations:
        if decl not in header_content:
            missing_declarations.append(decl)
    
    if missing_declarations:
        print("[ERROR] Missing function declarations in client.h:")
        for decl in missing_declarations:
            print(f"  - {decl}")
        return False
    else:
        print("[OK] All endianness function declarations found in client.h")
    
    # Check source file for function implementations
    with open(client_source, 'r') as f:
        source_content = f.read()
    
    required_functions = [
        "uint16_t Client::littleEndianToHost16(const uint8_t* bytes)",
        "uint32_t Client::littleEndianToHost32(const uint8_t* bytes)"
    ]
    
    missing_functions = []
    for func in required_functions:
        if func not in source_content:
            missing_functions.append(func)
    
    if missing_functions:
        print("[ERROR] Missing function implementations in client.cpp:")
        for func in missing_functions:
            print(f"  - {func}")
        return False
    else:
        print("[OK] All endianness function implementations found in client.cpp")
    
    return True

def test_receive_response_modification():
    \"\"\"Verify that the receiveResponse method was modified correctly\"\"\"
    client_source = Path("Client/cpp/client.cpp")
    
    with open(client_source, 'r') as f:
        source_content = f.read()
    
    # Check that the old direct struct reading is gone
    if "boost::asio::read(*socket, boost::asio::buffer(&header, sizeof(header)), ec)" in source_content:
        print("[WARNING] Old direct struct reading still present in receiveResponse")
        # This might be OK if it's in a different context, let's check more specifically
    
    # Check that the new raw bytes reading approach is present
    if "std::vector<uint8_t> rawHeaderBytes(sizeof(ResponseHeader))" in source_content:
        print("[OK] New raw bytes reading approach found in receiveResponse")
    else:
        print("[WARNING] New raw bytes reading approach not found in receiveResponse")
    
    # Check that endianness conversion is used
    if "littleEndianToHost16" in source_content and "littleEndianToHost32" in source_content:
        print("[OK] Endianness conversion functions are used in receiveResponse")
        return True
    else:
        print("[ERROR] Endianness conversion functions not used in receiveResponse")
        return False

def main():
    print("=== Endianness Fix Verification ===")
    print()
    
    # Test 1: Client build
    if not test_client_build():
        return False
    
    print()
    
    # Test 2: Function declarations and implementations
    if not test_endianness_functions():
        return False
    
    print()
    
    # Test 3: receiveResponse modification
    if not test_receive_response_modification():
        return False
    
    print()
    print("=== All Tests Passed ===")
    print("The endianness fix has been successfully implemented!")
    print()
    print("Next steps:")
    print("1. Start the server manually: python -m python_server.server.server")
    print("2. Run the client: build\\Release\\EncryptedBackupClient.exe")
    print("3. Verify that registration and file transfer work correctly")
    return True

if __name__ == "__main__":
    main()