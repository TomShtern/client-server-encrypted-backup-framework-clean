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

# 3. Vcpkg Integration Check
# To configure with vcpkg, use: cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg\scripts\buildsystems\vcpkg.cmake"
if(DEFINED CMAKE_TOOLCHAIN_FILE)
    message(STATUS "Using vcpkg toolchain: ${CMAKE_TOOLCHAIN_FILE}")
else()
    message(WARNING "No vcpkg toolchain detected. Make sure to use: cmake -DCMAKE_TOOLCHAIN_FILE=\"vcpkg\\scripts\\buildsystems\\vcpkg.cmake\"")
endif()

# 4. Define the Executable: List all of our application's source files.
add_executable(EncryptedBackupClient
    src/client/main.cpp
    src/client/client.cpp  # Consolidated client implementation (1.6K lines, complete with CRC)
    src/client/WebServerBackend.cpp  # HTTP API server for HTML GUI
    src/utils/CompressionWrapper.cpp
    src/wrappers/RSAWrapper.cpp  # Using Crypto++ implementation
    src/wrappers/AESWrapper.cpp
    src/wrappers/Base64Wrapper.cpp
)
 
# 5. Configure Include Directories: Tell our code where to find header files.
target_include_directories(EncryptedBackupClient PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# 6. Find and Link Libraries: Use vcpkg packages with fallback
# Try modern config-based discovery first (vcpkg style)
find_package(Boost CONFIG QUIET COMPONENTS asio beast)

if(NOT Boost_FOUND)
    # Fallback to traditional FindBoost module
    message(STATUS "Config-based Boost discovery failed, trying traditional FindBoost...")
    find_package(Boost REQUIRED COMPONENTS system thread)
    
    if(NOT Boost_FOUND)
        message(FATAL_ERROR 
            "Boost not found! Please install Boost using vcpkg:\n"
            "  vcpkg install boost-asio boost-beast\n"
            "Or ensure Boost is installed and CMAKE_PREFIX_PATH includes the Boost installation directory."
        )
    endif()
endif()

find_package(cryptopp CONFIG REQUIRED)
find_package(ZLIB REQUIRED)

# 7. Link Libraries: Include both external and Windows system libraries
target_link_libraries(EncryptedBackupClient PRIVATE 
    Boost::asio
    Boost::beast
    cryptopp::cryptopp
    ZLIB::ZLIB
)

# 8. Windows-specific libraries (minimal set for networking)
if(WIN32)
    target_link_libraries(EncryptedBackupClient PRIVATE 
        ws2_32      # Windows Sockets - required for networking
    )
endif()

# 9. Compiler-specific optimizations
if(MSVC)
    target_compile_options(EncryptedBackupClient PRIVATE /W4)
else()
    target_compile_options(EncryptedBackupClient PRIVATE -Wall -Wextra -pedantic)
endif()
