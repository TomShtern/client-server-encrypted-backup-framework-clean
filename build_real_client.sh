#!/bin/bash
# Build the real client with proper crypto implementations

echo "Building Real Encrypted Backup Client with Crypto++"
echo "=================================================="

# Create build directory
mkdir -p build

# Set compiler flags
CXX="g++"
CXXFLAGS="-std=c++17 -Wall -O2"
INCLUDES="-Iinclude/client -Iinclude/wrappers -Ithird_party/crypto++ -I/usr/include/boost"
LIBS="-lboost_system -pthread"

# Source files for the client
CLIENT_SOURCES="
src/client/main.cpp
src/client/client.cpp
src/client/protocol.cpp
src/client/cksum.cpp
src/client/ClientGUI.cpp
src/wrappers/AESWrapper.cpp
src/wrappers/Base64Wrapper.cpp
src/wrappers/RSAWrapper.cpp
"

# Crypto++ source files (only what we need)
CRYPTO_SOURCES="
third_party/crypto++/aes.cpp
third_party/crypto++/modes.cpp
third_party/crypto++/filters.cpp
third_party/crypto++/osrng.cpp
third_party/crypto++/rsa.cpp
third_party/crypto++/integer.cpp
third_party/crypto++/nbtheory.cpp
third_party/crypto++/oaep.cpp
third_party/crypto++/sha.cpp
third_party/crypto++/algparam.cpp
third_party/crypto++/asn.cpp
third_party/crypto++/base64.cpp
third_party/crypto++/files.cpp
third_party/crypto++/misc.cpp
third_party/crypto++/cryptlib.cpp
third_party/crypto++/algebra.cpp
third_party/crypto++/eprecomp.cpp
third_party/crypto++/modarith.cpp
third_party/crypto++/pubkey.cpp
third_party/crypto++/randpool.cpp
"

echo "Compiling client with real crypto implementations..."

# Build command
$CXX $CXXFLAGS $INCLUDES \
    $CLIENT_SOURCES \
    $CRYPTO_SOURCES \
    $LIBS \
    -o client/EncryptedBackupClient

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "Executable: client/EncryptedBackupClient"
    echo ""
    echo "🔧 Features:"
    echo "  ✅ Real RSA-1024 with Crypto++"
    echo "  ✅ Real AES-256-CBC with static zero IV"
    echo "  ✅ PKCS7 padding"
    echo "  ✅ Protocol Version 3 compliance"
    echo ""
    echo "Ready to connect to the server!"
else
    echo "❌ Build failed!"
    exit 1
fi