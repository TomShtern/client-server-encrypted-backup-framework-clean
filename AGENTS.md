# AGENTS.md - Development Guidelines for AI Coding Agents

## Build/Lint/Test Commands

### Python
- **Lint**: `ruff check .` (line-length=110, rules: E,F,W,B,I)
- **Format**: `ruff format .`
- **Type Check**: `mypy .` (strict mode, Python 3.13.5)
- **Test All**: `pytest tests/`
- **Test Single**: `pytest tests/test_specific_file.py::TestClass::test_method -v`
- **Test Integration**: `pytest tests/integration/ -v`

### C++
- **Build**: `cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake" && cmake --build build --config Release`
- **Format**: `clang-format -i file.cpp` (Google style, 100 cols, 4-space indent)

### Full System
- **One-Click Build+Run**: `python scripts/one_click_build_and_run.py`

## Code Style Guidelines

### Python
- **Imports**: Standard library first, then third-party, then local (alphabetical within groups)
- **Naming**: snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants
- **Types**: Use type hints, strict mypy compliance
- **Line Length**: 110 characters max
- **Error Handling**: Try/except with specific exceptions, log errors with context
- **Async**: Use async/await for I/O operations, avoid blocking calls

### C++
- **Style**: Google C++ style with clang-format
- **Indentation**: 4 spaces, no tabs
- **Braces**: Attach to function/class, new line for control statements
- **Pointers**: Left-aligned (*)
- **Includes**: Group by type, alphabetical within groups

### General
- **UTF-8**: Import `Shared.utils.utf8_solution` in files with subprocess/console I/O
- **Logging**: Use logger instead of print() for debugging
- **File Size**: Keep files under 650 lines, decompose larger files
- **Framework Harmony**: Prefer Flet built-ins over custom solutions

## AI Assistant Rules

### Copilot Instructions
See `.github/copilot-instructions-updated.md` for comprehensive development guidelines including:
- 5-layer encrypted backup architecture
- Flet Material Design 3 patterns
- Integration testing protocols
- Anti-patterns to avoid

### Key Principles
- **FletV2 First**: Use `FletV2/` directory exclusively (modern implementation)
- **Single Responsibility**: Components <300 lines, focused on one purpose
- **Async Patterns**: Use `page.run_task()` for background operations
- **Theme System**: Use TOKENS instead of hardcoded colors
- **Verification**: Check `received_files/` for actual transfers (not exit codes)

### Testing Strategy
- Integration tests verify end-to-end flows
- Component tests isolate Flet UI elements
- Always verify file presence in `received_files/` directory
- Test responsive layouts on 800x600 minimum window size