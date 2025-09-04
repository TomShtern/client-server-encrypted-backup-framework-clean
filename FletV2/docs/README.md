# FletV2 Documentation

## Overview

This directory contains comprehensive documentation for the FletV2 application.

## Documentation Files

- [`server_bridge_api.md`](server_bridge_api.md) - Server bridge API documentation
- [`views_api.md`](views_api.md) - View creation functions and patterns
- [`theme_system.md`](theme_system.md) - Theme system architecture and usage
- [`utilities.md`](utilities.md) - Utility modules and their APIs

## Architecture Overview

FletV2 follows a clean architecture pattern with the following layers:

1. **Views** - UI components created with Flet
2. **Theme System** - Styling and theming
3. **Server Bridge** - Backend communication
4. **Utilities** - Common functionality

## Development Guidelines

### Code Style

- Follow Flet best practices
- Use function-based view creation instead of class inheritance
- Leverage Flet's built-in components
- Maintain consistent error handling
- Use appropriate logging levels

### Testing

- Write unit tests for core functionality
- Test both success and failure cases
- Use mocking for external dependencies
- Maintain test coverage

### Documentation

- Keep documentation up to date with code changes
- Provide clear examples for APIs
- Document best practices
- Include usage guidelines