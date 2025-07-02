# 1. Basic Project Setup: Define the project name and require a modern CMake version.
cmake_minimum_required(VERSION 3.15)
# Handle modern CMake policies for Boost
cmake_policy(SET CMP0167 NEW)
project(EncryptedBackupClient VERSION 1.0)

# 2. Set C++ Standard: Enforce C++17 for compatibility.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Fix Windows-specific compilation issues
if(WIN32)
    add_compile_definitions(
        WIN32_LEAN_AND_MEAN    # Exclude rarely-used APIs
        NOMINMAX               # Prevent Windows.h from defining min/max macros
        _WIN32_WINNT=0x0601   # Target Windows 7 and later
    )
endif()

# 3. Define the Executable: List all of our application's source files.
add_executable(EncryptedBackupClient
    src/client/main.cpp
    src/client/ClientCore.cpp
    src/client/ClientCrypto.cpp
    src/client/ClientFileOps.cpp
    src/client/protocol.cpp
    src/client/cksum.cpp
    src/client/ClientLogger.cpp
    # src/client/SimpleWebServer_Clean.cpp  # Standalone server with its own main()
    # src/client/WebServerBackend.cpp  # Temporarily disabled due to compilation issues
    src/utils/CompressionWrapper.cpp
    src/wrappers/RSAWrapper.cpp  # Using Crypto++ implementation
    src/wrappers/AESWrapper.cpp
    src/wrappers/Base64Wrapper.cpp
)
 
# 4. Configure Include Directories: Tell our code where to find header files.
target_include_directories(EncryptedBackupClient PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# 5. Find and Link Libraries: Use vcpkg packages
find_package(Boost REQUIRED COMPONENTS asio beast)
find_package(cryptopp CONFIG REQUIRED)
find_package(ZLIB REQUIRED)

# 6. Link Libraries: Include both external and Windows system libraries
target_link_libraries(EncryptedBackupClient PRIVATE 
    Boost::asio
    Boost::beast
    cryptopp::cryptopp
    ZLIB::ZLIB
)

# 7. Windows-specific libraries (minimal set for networking)
if(WIN32)
    target_link_libraries(EncryptedBackupClient PRIVATE 
        ws2_32      # Windows Sockets - required for networking
    )
endif()

# 8. Compiler-specific optimizations
if(MSVC)
    target_compile_options(EncryptedBackupClient PRIVATE /W4)
else()
    target_compile_options(EncryptedBackupClient PRIVATE -Wall -Wextra -pedantic)
endif()
