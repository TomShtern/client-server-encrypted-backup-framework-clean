# 1. Basic Project Setup: Define the project name and require a modern CMake version.
cmake_minimum_required(VERSION 3.15)
project(EncryptedBackupClient VERSION 1.0)

# 2. Set C++ Standard: Enforce C++17 for compatibility.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 3. Define the Executable: List all of our application's source files.
add_executable(EncryptedBackupClient
    src/client/main.cpp
    src/client/ClientCore.cpp
    src/client/ClientCrypto.cpp
    src/client/ClientFileOps.cpp
    src/client/ClientGUI.cpp
    src/client/protocol.cpp
    src/client/cksum.cpp
    src/client/ClientGUIHelpers.cpp
    src/client/ClientLogger.cpp
    src/client/SimpleWebServer_Clean.cpp
    src/client/WebServerBackend.cpp
    src/utils/CompressionWrapper.cpp
    src/wrappers/RSAWrapperCNG.cpp
    src/wrappers/AESWrapper.cpp
    src/wrappers/Base64Wrapper.cpp
)
 
# 4. Configure Include Directories: Tell our code where to find header files.
target_include_directories(EncryptedBackupClient PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# 5. Find and Link Libraries: Use vcpkg to find and link Boost and Crypto++ libraries.
find_package(Boost REQUIRED COMPONENTS asio system bind beast)
find_package(cryptopp CONFIG REQUIRED)

# 6. Link Libraries: Include both external and Windows system libraries
target_link_libraries(EncryptedBackupClient PRIVATE 
    Boost::asio
    Boost::system
    Boost::bind
    Boost::beast
    cryptopp::cryptopp
)

# 7. Windows-specific libraries for CNG RSA implementation
if(WIN32)
    target_link_libraries(EncryptedBackupClient PRIVATE 
        ws2_32      # Windows Sockets
        crypt32     # Windows Cryptography API
        bcrypt      # Windows CNG (Cryptography Next Generation)
        advapi32    # Advanced Windows API
        user32      # Windows User Interface
    )
endif()

# 8. Compiler-specific optimizations
if(MSVC)
    target_compile_options(EncryptedBackupClient PRIVATE /W4)
else()
    target_compile_options(EncryptedBackupClient PRIVATE -Wall -Wextra -pedantic)
endif()
