cmake_minimum_required(VERSION 3.20)

project(CppApiServer LANGUAGES CXX)

# Enable C++20 standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Find required packages via vcpkg
find_package(Drogon CONFIG REQUIRED)
find_package(SQLiteCpp CONFIG REQUIRED)
find_package(jsoncpp CONFIG REQUIRED)
find_package(spdlog CONFIG REQUIRED)
find_package(Boost REQUIRED COMPONENTS system filesystem)

# Source files
set(CPP_API_SERVER_SOURCES
    src/main.cpp
    src/AppServer.cpp
    src/Config.cpp
    src/DatabaseService.cpp
    src/JobService.cpp
    src/Notifier.cpp
    src/StatusWebSocketController.cpp
    src/HealthController.cpp
)

# Create executable
add_executable(cpp_api_server ${CPP_API_SERVER_SOURCES})

# Include directories
target_include_directories(cpp_api_server
    PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/include/cpp_api_server
)

# Link libraries
target_link_libraries(cpp_api_server
    PRIVATE
    Drogon::Drogon
    SQLiteCpp
    jsoncpp_lib
    spdlog::spdlog
    Boost::system
    Boost::filesystem
)

# Compiler-specific options
if(MSVC)
    target_compile_options(cpp_api_server PRIVATE
        /W4           # Warning level 4
        /permissive-  # Standards conformance
        /utf-8        # UTF-8 source and execution character sets
    )
else()
    target_compile_options(cpp_api_server PRIVATE
        -Wall         # Enable all warnings
        -Wextra       # Extra warnings
        -pedantic     # Strict ISO C++ compliance
    )
endif()

# Copy config file to build directory
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/config/default_config.json
    ${CMAKE_CURRENT_BINARY_DIR}/cpp_api_server_config.json
    COPYONLY
)
