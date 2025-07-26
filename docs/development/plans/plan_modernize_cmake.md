
# Plan: Modernize the CMake Build System

**Objective:** Refactor the `CMakeLists.txt` and associated build scripts to use modern, target-centric CMake practices. This will improve portability, maintainability, and integration with tools like `vcpkg`.

**Strategy:** The current `CMakeLists.txt` uses older, directory-based commands (`target_include_directories`, `link_libraries`) and has some platform-specific logic that can be improved. This plan will refactor it to use `target_*` commands, which associate properties directly with build targets, making the project structure clearer and more robust.

**Pre-computation/Analysis:**

*   **Files to Modify:** `CMakeLists.txt`, `scripts/configure_cmake.bat`
*   **Key Concepts:**
    *   **Target-centric CMake:** Instead of telling CMake what to do in a directory, we define properties on specific targets (e.g., the `EncryptedBackupClient` executable).
    *   **`vcpkg` Integration:** Modern CMake can automatically find and use the `vcpkg` toolchain file, removing the need for hardcoded paths in build scripts.

**Step-by-Step Plan:**

1.  **Update `CMakeLists.txt` to be Target-Centric:**
    *   **Action:** Modify `CMakeLists.txt` to use `target_link_libraries` to manage both public and private dependencies. This command can also specify include directories for dependencies.
    *   **Example (Before):**
        ```cmake
        target_include_directories(EncryptedBackupClient PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
        find_package(Boost REQUIRED COMPONENTS asio system)
        target_link_libraries(EncryptedBackupClient PRIVATE Boost::asio Boost::system)
        ```
    *   **Example (After):**
        ```cmake
        # No need for target_include_directories for dependencies
        find_package(Boost REQUIRED COMPONENTS asio system)
        target_link_libraries(EncryptedBackupClient PRIVATE
            Boost::asio
            Boost::system
        )
        ```
    *   **Action:** Use `target_compile_features` to specify the C++ standard required by the target.
        ```cmake
        # Replace set(CMAKE_CXX_STANDARD 17)
        target_compile_features(EncryptedBackupClient PRIVATE cxx_std_17)
        ```

2.  **Automate `vcpkg` Toolchain Discovery:**
    *   **Action:** Remove the hardcoded `-DCMAKE_TOOLCHAIN_FILE` argument from `scripts/configure_cmake.bat`.
    *   **Action:** Add the following to the top of `CMakeLists.txt` to allow CMake to automatically find the `vcpkg` toolchain:
        ```cmake
        if(DEFINED ENV{VCPKG_ROOT} AND NOT DEFINED CMAKE_TOOLCHAIN_FILE)
            set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" CACHE STRING "vcpkg toolchain file")
        endif()
        ```
    *   **Verification:** The user can now run `cmake -B build` without the `configure_cmake.bat` script, as long as the `VCPKG_ROOT` environment variable is set.

3.  **Create a Unified Build Script:**
    *   **Action:** Create a new script named `build.bat` that combines the steps of configuring CMake and building the project.
    *   **Content of `build.bat`:**
        ```batch
        @echo off
        echo [INFO] Configuring CMake...
        cmake -B build -S .
        echo [INFO] Building project...
        cmake --build build
        ```
    *   **Verification:** Running `build.bat` should successfully configure and build the entire project.

4.  **Add a `tests` Subdirectory to the Build:**
    *   **Action:** Create a `CMakeLists.txt` file in the `tests` directory.
    *   **Action:** Add `add_subdirectory(tests)` to the main `CMakeLists.txt` file.
    *   **Action:** In `tests/CMakeLists.txt`, define a new executable target for the tests and link it against Google Test.
    *   **Verification:** The `run_tests` executable should be built along with the main client application.
