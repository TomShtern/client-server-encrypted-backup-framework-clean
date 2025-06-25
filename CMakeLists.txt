cmake_minimum_required(VERSION 3.15)
project(EncryptedBackupClient VERSION 1.0)

# IMPORTANT: When using vcpkg, configure CMake with:
#   cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE=C:/Users/tom7s/vcpkg/scripts/buildsystems/vcpkg.cmake -A x64
# This will ensure vcpkg dependencies are found automatically.

find_package(cryptopp CONFIG REQUIRED)

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

target_include_directories(EncryptedBackupClient PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    # vcpkg will inject cryptopp include path automatically
)

target_compile_definitions(EncryptedBackupClient PRIVATE
    _WIN32_WINNT=0x0A00  # Windows 10
    WINVER=0x0A00
)

target_link_libraries(EncryptedBackupClient PRIVATE 
    cryptopp::cryptopp
    ws2_32
    crypt32
)

set_property(TARGET EncryptedBackupClient PROPERTY CXX_STANDARD 17)
set_property(TARGET EncryptedBackupClient PROPERTY CXX_STANDARD_REQUIRED ON)
