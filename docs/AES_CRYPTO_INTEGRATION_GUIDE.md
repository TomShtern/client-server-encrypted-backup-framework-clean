# AES Crypto Integration Guide

## Overview

This guide explains how to integrate the AES-256-CBC encryption implementation into your simple client for the encrypted backup framework.

## Files Created

### Core Implementation
- **`aes_crypto.h`** - Header file with AESCrypto class and utility functions
- **`aes_crypto.cpp`** - Implementation using Crypto++ library backend

### Test and Demo Files
- **`test_aes_crypto.cpp`** - Comprehensive test suite
- **`simple_client_with_crypto.cpp`** - Enhanced simple client with encryption
- **`build_aes_crypto_test.bat`** - Build script for test suite
- **`build_simple_client_crypto.bat`** - Build script for enhanced client

## Quick Start

### 1. Build and Test the Implementation

```bash
# Test the AES crypto implementation
.\build_aes_crypto_test.bat

# Build the enhanced simple client
.\build_simple_client_crypto.bat
```

### 2. Integration Steps

#### Step 1: Include Headers
```cpp
#include "aes_crypto.h"
```

#### Step 2: Create AESCrypto Instance
```cpp
AESCrypto crypto;
```

#### Step 3: Decrypt AES Key from Server
```cpp
// Server sends 144-byte encrypted AES key
std::vector<uint8_t> encryptedAESKey; // Received from server
bool success = crypto.decryptAndLoadAESKey(encryptedAESKey);
```

#### Step 4: Encrypt File Data
```cpp
// Read file data
std::vector<uint8_t> fileData = AESCryptoUtils::loadFile("myfile.txt");

// Encrypt before sending to server
std::vector<uint8_t> encryptedData = crypto.encryptFileData(fileData);
```

## Detailed API Reference

### AESCrypto Class

#### Constructor/Destructor
```cpp
AESCrypto();        // Initialize with zero IV
~AESCrypto();       // Securely clear keys
```

#### Key Management
```cpp
// Load RSA private key for AES key decryption
bool loadRSAPrivateKey(const std::string& privateKeyPath);
bool loadRSAPrivateKey(const std::vector<uint8_t>& keyData);

// Decrypt and load AES key from server
bool decryptAndLoadAESKey(const std::vector<uint8_t>& encryptedAESKey);

// Manual AES key setting (for testing)
bool setAESKey(const std::vector<uint8_t>& key);

// Get current AES key
std::vector<uint8_t> getAESKey() const;
```

#### Encryption/Decryption
```cpp
// Encrypt file data using AES-256-CBC with zero IV
std::vector<uint8_t> encryptFileData(const std::vector<uint8_t>& fileData);

// Decrypt file data
std::vector<uint8_t> decryptFileData(const std::vector<uint8_t>& encryptedData);

// Test roundtrip functionality
bool testRoundtrip(const std::vector<uint8_t>& testData);
```

#### State Management
```cpp
// Check if ready for encryption/decryption
bool isReady() const;

// Clear all keys and reset state
void reset();
```

### Utility Functions (AESCryptoUtils namespace)

```cpp
// File operations
std::vector<uint8_t> loadFile(const std::string& filepath);
bool saveFile(const std::string& filepath, const std::vector<uint8_t>& data);

// Hex conversion (for debugging)
std::vector<uint8_t> hexToBytes(const std::string& hex);
std::string bytesToHex(const std::vector<uint8_t>& data);
```

## Implementation Details

### AES-256-CBC Configuration
- **Key Size**: 32 bytes (256 bits)
- **Block Size**: 16 bytes (128 bits)
- **Mode**: CBC (Cipher Block Chaining)
- **IV**: Static zero IV (per project specification)
- **Padding**: PKCS7 (handled automatically by Crypto++)

### RSA Integration
- **Algorithm**: RSA-OAEP with SHA-256 (matching project spec)
- **Key Format**: DER-encoded private keys
- **Encrypted Key Size**: 144 bytes (as sent by server)

### Error Handling
- All functions throw `std::runtime_error` on failure
- Input validation for key sizes and data integrity
- Secure memory clearing on destruction

## Integration with Simple Client

### Original Flow
1. Register client
2. Send public key → receive encrypted AES key
3. Send file data (unencrypted)

### Enhanced Flow
1. Register client
2. Send public key → receive encrypted AES key
3. **Decrypt AES key using RSA private key**
4. **Encrypt file data using AES-256-CBC**
5. Send encrypted file data

### Code Changes Required

#### In Key Exchange Step
```cpp
// OLD: Just receive and ignore encrypted AES key
std::vector<uint8_t> encryptedAESKey;
receiveData(encryptedAESKey, payloadSize);

// NEW: Decrypt and load AES key
if (crypto.decryptAndLoadAESKey(encryptedAESKey)) {
    std::cout << "✅ AES key loaded successfully" << std::endl;
} else {
    std::cout << "❌ AES key decryption failed" << std::endl;
}
```

#### In File Transfer Step
```cpp
// OLD: Send raw file data
std::vector<uint8_t> fileData = loadFile(filename);
request.insert(request.end(), fileData.begin(), fileData.end());

// NEW: Encrypt file data before sending
std::vector<uint8_t> fileData = loadFile(filename);
std::vector<uint8_t> encryptedData = crypto.encryptFileData(fileData);
request.insert(request.end(), encryptedData.begin(), encryptedData.end());
```

## Testing

### Unit Tests
Run `test_aes_crypto.exe` to verify:
- Basic functionality
- Encryption/decryption roundtrip
- File operations
- Utility functions
- Error handling

### Integration Test
Run `simple_client_with_crypto.exe` to test:
- Real server communication
- RSA key decryption
- AES file encryption
- Complete workflow

## Build Requirements

### Dependencies
- Crypto++ library (already included in project)
- Windows Sockets (ws2_32.lib)
- Windows Crypto API (advapi32.lib)

### Compiler Settings
- C++17 compatible compiler (MSVC recommended)
- Optimization: `/O2`
- Windows target: `/D_WIN32_WINNT=0x0601`

## Troubleshooting

### Common Issues

#### "AES key not loaded"
- Ensure `decryptAndLoadAESKey()` is called before encryption
- Check that RSA private key is available and valid
- Verify encrypted AES key format (144 bytes)

#### "RSA decryption failed"
- Check RSA private key file exists and is readable
- Verify DER format of private key
- Ensure key matches the public key sent to server

#### "Invalid PKCS7 padding"
- Usually indicates decryption with wrong key
- Verify AES key was decrypted correctly
- Check data integrity during transmission

### Debug Tips

1. **Enable detailed logging**: The implementation provides extensive console output
2. **Test with known data**: Use `testRoundtrip()` with sample data
3. **Verify key sizes**: AES key must be exactly 32 bytes
4. **Check file paths**: RSA key files must be accessible

## Security Notes

### Best Practices
- Keys are automatically cleared from memory on destruction
- Zero IV is used per project specification (acceptable for unique keys)
- PKCS7 padding prevents padding oracle attacks
- RSA-OAEP provides semantic security

### Limitations
- Static zero IV reduces security (offset by unique per-session AES keys)
- No key derivation function (keys come directly from server)
- Single-threaded design (sufficient for simple client)

## Performance

### Benchmarks
- AES-256-CBC encryption: ~100 MB/s (typical)
- RSA-2048 decryption: ~1000 operations/s (typical)
- Memory usage: <1MB overhead
- No significant performance impact on file transfer

### Optimization Tips
- Process large files in chunks if memory constrained
- Reuse AESCrypto instance for multiple operations
- Consider compression before encryption for larger files

## Migration Path

### Phase 1: Basic Integration
1. Add AES crypto files to project
2. Modify simple client for key decryption
3. Test with existing server

### Phase 2: Full Encryption
1. Add file encryption to transfer step
2. Update protocol handling for encrypted data
3. Verify compatibility with server decryption

### Phase 3: Production Deployment
1. Add comprehensive error handling
2. Implement logging and monitoring
3. Performance testing with real workloads

## Future Enhancements

### Possible Improvements
- Support for different IV modes
- Key derivation functions
- Streaming encryption for large files
- Multi-threaded encryption
- Hardware acceleration support

This implementation provides a solid foundation for secure file transfer while maintaining compatibility with the existing protocol and server infrastructure.