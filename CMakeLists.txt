cmake_minimum_required(VERSION 3.15)
project(EncryptedBackupClient VERSION 1.0)

find_package(cryptopp CONFIG REQUIRED)

add_executable(EncryptedBackupClient
    src/client/main.cpp
    src/client/client.cpp
    src/client/protocol.cpp
    src/client/cksum.cpp
    src/wrappers/RSAWrapper.cpp
    src/wrappers/AESWrapper.cpp
    src/wrappers/Base64Wrapper.cpp
    src/client/ClientGUIHelpers.cpp
)

target_include_directories(EncryptedBackupClient PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    C:/Users/tom7s/vcpkg/installed/x64-windows/include/cryptopp
)

target_link_libraries(EncryptedBackupClient PRIVATE 
    cryptopp::cryptopp
    ws2_32
    crypt32
)

set_property(TARGET EncryptedBackupClient PROPERTY CXX_STANDARD 17)
set_property(TARGET EncryptedBackupClient PROPERTY CXX_STANDARD_REQUIRED ON)
