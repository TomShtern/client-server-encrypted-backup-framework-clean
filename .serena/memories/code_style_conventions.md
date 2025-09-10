# Code Style and Conventions - CORRECTED FOR THREE-TIER ARCHITECTURE

## Python Code Style (Flask API & Flet GUI)
- **Imports**: Grouped by standard library, third-party, local modules
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Docstrings**: Google-style docstrings with description, args, returns
- **Type Hints**: Used throughout for better code maintainability
- **Error Handling**: Try-except blocks with specific exception types
- **Logging**: Structured logging with appropriate levels (DEBUG, INFO, WARNING, ERROR)
- **Async/Await**: Used for non-blocking operations in Flask and Flet
- **Framework-Specific**: Flask blueprints for API organization, Flet controls for UI

## JavaScript/HTML Code Style (Web GUI)
- **ES6+ Syntax**: Arrow functions, async/await, destructuring, template literals
- **Naming**: camelCase for variables/functions, PascalCase for components/classes
- **Code Organization**: Modules with clear exports, component-based architecture
- **Error Handling**: Try-catch blocks with proper error propagation
- **Styling**: TailwindCSS utility classes, consistent spacing and colors
- **Accessibility**: ARIA attributes, semantic HTML, keyboard navigation
- **Performance**: Code splitting, lazy loading, efficient re-renders

## C++ Code Style (Client)
- **Naming**: snake_case for variables/functions, PascalCase for classes/types
- **Memory Management**: RAII pattern, smart pointers, no raw pointers when possible
- **Error Handling**: Exceptions with descriptive messages, proper cleanup
- **Documentation**: Doxygen-style comments for classes and functions
- **Performance**: Efficient algorithms, minimal copies, optimized data structures
- **Threading**: Proper synchronization, thread-safe operations
- **Build System**: CMake configuration, proper dependency management

## Key Conventions - CORRECTED

### UTF-8 Support (All Components)
```python
# Python: Always import this in any Python file that deals with subprocess or console I/O
import Shared.utils.utf8_solution
```
```cpp
// C++: Use UTF-8 aware string handling
std::string utf8_string = "UTF-8 encoded string";
```
```javascript
// JavaScript: Proper Unicode handling
const utf8String = "UTF-8 encoded string";
```

### Framework Harmony (Technology-Specific)
- **Flask API**: Use Flask-RESTful or blueprints for API organization
- **Flet GUI**: Use Material Design 3, control.update() for performance
- **Web GUI**: Use modern JavaScript, TailwindCSS for styling
- **C++ Client**: Use Boost.Asio for networking, Crypto++ for encryption

## File Organization - CORRECTED

### Flask API Server Structure
```
server/
├── main.py              # Flask application entry point
├── config.py            # Configuration settings
├── models/              # Database models
│   └── __init__.py
├── routes/              # API route handlers
│   ├── files.py         # File-related endpoints
│   ├── clients.py       # Client management endpoints
│   └── __init__.py
├── utils/               # Server utilities
│   ├── database.py      # Database connection helpers
│   └── auth.py          # Authentication utilities
└── __init__.py
```

### Web GUI Structure
```
gui/
├── static/
│   ├── css/             # Custom CSS (minimal, prefer Tailwind)
│   ├── js/              # JavaScript modules
│   └── img/             # Images and icons
├── templates/
│   ├── base.html        # Base HTML template
│   ├── dashboard.html   # Dashboard page
│   └── settings.html    # Settings page
├── js/
│   ├── api.js           # API client functions
│   ├── components.js    # Reusable UI components
│   └── app.js           # Main application logic
├── package.json         # JavaScript dependencies
└── tailwind.config.js   # TailwindCSS configuration
```

### Flet Desktop GUI Structure
```
FletV2/
├── main.py              # Desktop application entry point
├── views/               # GUI view components
│   ├── dashboard.py     # Dashboard view
│   ├── clients.py       # Clients management view
│   └── settings.py      # Settings view
├── utils/               # Utility modules
│   ├── server_bridge.py # Communication with Flask API
│   └── state_manager.py # State management system
└── theme/               # Theme configuration
```

### C++ Client Structure
```
src/
├── client/
│   ├── main.cpp         # Client entry point
│   ├── network.cpp      # Network communication
│   ├── crypto.cpp       # Encryption/decryption
│   └── file_ops.cpp     # File operations
├── wrappers/
│   └── crypto_wrapper.cpp # Crypto++ wrapper
└── include/
    ├── network.h        # Network headers
    ├── crypto.h         # Crypto headers
    └── types.h          # Common type definitions
```

## Development Workflow - CORRECTED

### Component-Specific Workflows
1. **Flask API Changes**: Update routes, test with API client, update web GUI
2. **Web GUI Changes**: Update JavaScript/HTML, test in browser, verify API integration
3. **Flet GUI Changes**: Update desktop interface, test Material Design compliance
4. **C++ Client Changes**: Update client code, rebuild, test protocol compatibility
5. **Database Changes**: Update schema, create migrations, test across all components

### Cross-Component Coordination
- **API Contracts**: Define clear interfaces between components
- **Data Formats**: Consistent JSON/binary protocols
- **Error Handling**: Unified error reporting across tiers
- **Logging**: Coordinated logging with correlation IDs
- **Testing**: Integration tests for component interactions

## Build and Development - CORRECTED

### Python Components (Flask API, Flet GUI)
- **Version**: 3.13.5 (based on requirements.txt)
- **Virtual Environment**: Use `flet_venv` for both Flask and Flet
- **Dependencies**: `requirements.txt` for both components
- **Testing**: pytest for unit tests, integration tests

### JavaScript Web GUI
- **Node.js**: Version specified in `package.json`
- **Package Manager**: npm for dependency management
- **Build Tool**: Webpack/Vite for bundling
- **Development Server**: Hot reload for development

### C++ Client
- **Compiler**: MSVC Build Tools
- **Build System**: Custom batch files
- **Dependencies**: Boost.Asio, Crypto++
- **Testing**: Unit testing framework integration

### Database
- **Engine**: SQLite3
- **Schema**: Version-controlled migrations
- **Backup**: Automated backup procedures
- **Performance**: Proper indexing and query optimization