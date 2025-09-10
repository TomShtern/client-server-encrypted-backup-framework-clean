# Design Patterns and Guidelines - CORRECTED FOR THREE-TIER ARCHITECTURE

## Core Design Principles - CORRECTED

### Three-Tier Architecture Pattern
- **C++ Client Layer**: Pure encryption and file transfer operations
- **Python Flask API Layer**: RESTful middleware with data transformation
- **JavaScript Web GUI Layer**: Modern web interface with TailwindCSS
- **Python Flet Desktop Layer**: Server management and monitoring interface
- **SQLite3 Database Layer**: Unified data persistence across all tiers

### Framework Harmony (CRITICAL)
- **Work WITH each framework**: Use Flet for desktop, Flask for API, vanilla JS for web
- **Avoid over-engineering**: Don't reinvent functionality that each framework provides
- **Performance First**: Use appropriate update mechanisms for each technology
- **Simple Communication**: REST API between web GUI and Flask server
- **Binary Protocol**: Efficient communication between C++ client and Flask server

## Component Design Patterns - CORRECTED

#### Flask API Endpoint Pattern
```python
@app.route('/api/files', methods=['GET'])
def get_files():
    \"\"\"Get list of backed up files.\"\"\"
    try:
        # Get data from C++ client or database
        files = server_bridge.get_file_list()
        return jsonify({
            'status': 'success',
            'data': files
        })
    except Exception as e:
        logger.error(f\"Failed to get files: {e}\")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
```

#### JavaScript API Client Pattern
```javascript
class BackupAPI {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }
    
    async getFiles() {
        try {
            const response = await fetch(`${this.baseURL}/files`);
            if (!response.ok) throw new Error('API request failed');
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }
}
```

#### C++ to Flask Communication Pattern
```cpp
// C++ client sending data to Flask API
void send_file_info(const FileInfo& file) {
    try {
        // Serialize to binary protocol
        std::vector<char> buffer = serialize_file_info(file);
        
        // Send to Flask server
        boost::asio::io_service io_service;
        tcp::socket socket(io_service);
        // ... connection and send logic
        
    } catch (const std::exception& e) {
        logger.error("Failed to send file info: " + std::string(e.what()));
    }
}
```

## Architectural Patterns - CORRECTED

### API Layer Patterns
- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Communication**: Web GUI ↔ Flask API
- **Binary Protocol**: C++ Client ↔ Flask API
- **Error Handling**: Consistent error responses across all endpoints
- **Authentication**: Secure API key or token-based auth

### Database Patterns
- **SQLite3 Integration**: Single database file for all components
- **Connection Pooling**: Efficient database connections in Flask
- **Migration System**: Version-controlled database schema changes
- **Transaction Management**: ACID compliance for critical operations
- **Backup Strategy**: Automated database backups

### Web GUI Patterns
- **Component-Based**: Reusable JavaScript components
- **TailwindCSS**: Utility-first CSS framework
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: WebSocket or polling for live data
- **Progressive Enhancement**: Works without JavaScript

### Desktop GUI Patterns (Flet)
- **Material Design 3**: Modern UI components and theming
- **State Management**: Reactive UI updates
- **Navigation Rail**: Consistent navigation pattern
- **Performance**: Efficient rendering and updates
- **Cross-platform**: Windows, macOS, Linux support

## Code Quality Guidelines - CORRECTED

### API Development Guidelines
- **OpenAPI Documentation**: Document all endpoints with Swagger/OpenAPI
- **Input Validation**: Validate all request data with schemas
- **Rate Limiting**: Prevent API abuse
- **CORS Configuration**: Proper cross-origin resource sharing
- **Logging**: Comprehensive API request/response logging

### Web Development Guidelines
- **ES6+ Features**: Modern JavaScript with async/await
- **Error Boundaries**: Graceful error handling in UI
- **Accessibility**: WCAG compliance for web interface
- **Performance**: Code splitting and lazy loading
- **Security**: XSS prevention and secure API calls

### Database Guidelines
- **Schema Design**: Normalized database design
- **Indexing**: Proper indexes for query performance
- **Backup**: Regular automated backups
- **Migration**: Safe schema migration scripts
- **Monitoring**: Database performance monitoring

## Development Workflow Patterns - CORRECTED

### Full-Stack Development
1. **Design API First**: Define Flask API endpoints
2. **Implement Backend**: Build Flask API and C++ client integration
3. **Create Web GUI**: Build JavaScript/HTML interface
4. **Add Desktop GUI**: Implement Flet management interface
5. **Test Integration**: End-to-end testing across all tiers
6. **Deploy**: Coordinated deployment of all components

### Component-Specific Workflows
- **API Changes**: Update Flask routes, test with Postman, update web client
- **Web GUI Changes**: Update JavaScript, test in browser, verify API integration
- **C++ Changes**: Update client code, rebuild, test with Flask API
- **Flet Changes**: Update desktop GUI, test Material Design compliance
- **Database Changes**: Create migration scripts, test data integrity

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: API to database testing
- **End-to-End Tests**: Complete user workflow testing
- **Performance Tests**: Load testing for all tiers
- **Security Tests**: Penetration testing and vulnerability assessment