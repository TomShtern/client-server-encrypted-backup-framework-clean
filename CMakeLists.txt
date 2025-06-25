# 1. Basic Project Setup: Define the project name and require a modern CMake version.
cmake_minimum_required(VERSION 3.15)
project(EncryptedBackupClient VERSION 1.0)

# 2. Find Dependencies: This finds the Crypto++ library that vcpkg installed.
# The name "cryptopp" is the correct name vcpkg uses for this package.
find_package(cryptopp CONFIG REQUIRED)

# 3. Define the Executable: List all of our application's source files.
add_executable(EncryptedBackupClient
    src/client/main.cpp
    src/client/client.cpp
    src/client/protocol.cpp
    src/client/cksum.cpp
    src/client/ClientGUIHelpers.cpp
    src/wrappers/RSAWrapper.cpp
    src/wrappers/AESWrapper.cpp
    src/wrappers/Base64Wrapper.cpp
)

# 4. Configure Include Directories: Tell our code where to find header files.
# It needs our project's "include" folder and the Crypto++ headers (found automatically by vcpkg).
target_include_directories(EncryptedBackupClient PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# 5. Link Libraries: Connect our executable to the Crypto++ library and required Windows libraries.
# `cryptopp::cryptopp` is the correct target name for the library provided by vcpkg.
target_link_libraries(EncryptedBackupClient PRIVATE 
    cryptopp::cryptopp
    ws2_32      # Windows Sockets for networking
    crypt32     # Windows Cryptography API
)

# 6. Set C++ Standard: Enforce C++17 for compatibility.
set_property(TARGET EncryptedBackupClient PROPERTY CXX_STANDARD 17)
set_property(TARGET EncryptedBackupClient PROPERTY CXX_STANDARD_REQUIRED ON)
