# 1. Basic Project Setup: Define the project name and require a modern CMake version.
cmake_minimum_required(VERSION 3.15)
project(EncryptedBackupClient VERSION 1.0)

# 2. Use Local Crypto++ Sources: Instead of vcpkg, use local crypto++ sources
# This makes the project portable and avoids vcpkg dependency issues
file(GLOB CRYPTOPP_SOURCES "third_party/crypto++/*.cpp")
# Remove test and example files that we don't need
list(FILTER CRYPTOPP_SOURCES EXCLUDE REGEX ".*/(test|bench|valid|dll|adhoc|fips|regtest|datatest).*\\.(cpp|c)$")

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
    ${CRYPTOPP_SOURCES}
)
 
# 4. Configure Include Directories: Tell our code where to find header files.
# It needs our project's "include" folder and the local Crypto++ headers.
target_include_directories(EncryptedBackupClient PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/crypto++
)

# 5. Link Libraries: Connect our executable to the required Windows libraries.
# Since we're using local crypto++ sources, we only need Windows libraries.
target_link_libraries(EncryptedBackupClient PRIVATE 
    ws2_32      # Windows Sockets for networking
    crypt32     # Windows Cryptography API
)

# 6. Set C++ Standard: Enforce C++17 for compatibility.
set_property(TARGET EncryptedBackupClient PROPERTY CXX_STANDARD 17)
set_property(TARGET EncryptedBackupClient PROPERTY CXX_STANDARD_REQUIRED ON)
