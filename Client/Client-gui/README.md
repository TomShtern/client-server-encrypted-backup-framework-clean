# CyberBackup 3.0 Web GUI

A modern, responsive web interface for the CyberBackup encrypted file backup system.

## Features

- **Modern Web Interface**: Clean, Material Design-inspired UI with dark/light themes
- **Real-time Updates**: WebSocket communication with Socket.IO for live progress updates
- **File Management**: Drag-and-drop file selection with validation and metadata display
- **Progress Tracking**: Visual progress indicators with ETA calculations and speed monitoring
- **Connection Monitoring**: Real-time connection health and latency tracking
- **Error Handling**: Comprehensive error boundaries with user-friendly messages
- **Accessibility**: ARIA support and screen reader compatibility
- **Logging System**: Real-time logs with filtering and export capabilities
- **Responsive Design**: Works on desktop and mobile devices

## Architecture

- **Pure Vanilla JavaScript**: No framework dependencies, modern ES6 modules
- **Modular Design**: Clean separation of concerns with service layer architecture
- **Error Boundaries**: Robust error handling and recovery mechanisms
- **Performance Optimized**: Efficient DOM updates and memory management
- **Security**: Input validation and XSS protection

## Quick Start

### Prerequisites

- Node.js 16.0.0 or higher
- A compatible web browser (Chrome 90+, Firefox 88+, Safari 14+)

### Installation

```bash
# Clone or navigate to the project directory
cd Client/Client-gui

# Install dependencies
npm install

# Start the development server
npm run dev
```

The application will be available at `http://localhost:8080`

### Alternative Setup (without Node.js)

If you don't have Node.js installed, you can use any HTTP server:

```bash
# Using Python
python -m http.server 8080

# Using PHP
php -S localhost:8080

# Or use any static file server
```

## Usage

1. **Configure Connection**: Enter the server address and username
2. **Select File**: Drag and drop a file or click "Choose File"
3. **Start Backup**: Click "Connect / Start" to begin the backup process
4. **Monitor Progress**: View real-time progress, logs, and statistics

## Development

### Project Structure

```
Client-gui/
├── scripts/           # JavaScript modules
│   ├── app.js        # Main application entry point
│   ├── services/     # Business logic services
│   ├── state/        # State management
│   ├── ui/           # UI components
│   └── utils/        # Utility functions
├── styles/           # CSS stylesheets
├── *.html           # HTML templates
├── package.json     # Project configuration
└── README.md        # This file
```

### Available Scripts

```bash
# Development
npm run dev          # Start development server with hot reload
npm start            # Start production server

# Validation and Quality
npm run validate     # Validate all modules and dependencies
npm run check        # Run all quality checks
npm run clean        # Clean temporary files

# Build
npm run build        # Validate and lint the project
```

### Code Style

- **ES6 Modules**: All code uses ES6 import/export syntax
- **Error Boundaries**: All async operations wrapped in error handling
- **Clean Architecture**: Separation of concerns with clear module boundaries
- **Documentation**: Functions and classes should have JSDoc comments
- **Accessibility**: All interactive elements have proper ARIA attributes

## API Integration

The web GUI communicates with the CyberBackup server via:

1. **HTTP API**: REST endpoints for control operations
2. **WebSocket**: Real-time updates and progress notifications
3. **File Upload**: Chunked file transfer with progress tracking

### Server Configuration

The GUI expects a CyberBackup server running on the configured port (default: 1256).

## Error Handling

The application includes comprehensive error handling:

- **Network Errors**: Automatic retry with exponential backoff
- **UI Errors**: Graceful degradation with fallback functionality
- **File Errors**: Detailed error messages for validation failures
- **Connection Errors**: Real-time connection monitoring and recovery

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Security Considerations

- All user inputs are validated and sanitized
- File uploads are checked for size and type restrictions
- WebSocket connections use secure protocols when available
- No sensitive data is stored in browser localStorage

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure the CyberBackup server is running and accessible
2. **File Upload Fails**: Check file size limits and server permissions
3. **WebSocket Errors**: Verify firewall settings and port availability
4. **Module Loading Errors**: Ensure all files are present and HTTP headers are correct

### Debug Mode

Enable debug logging by opening browser developer tools and checking the console output.

## Contributing

1. Follow the existing code style and architecture patterns
2. Add error boundaries for any new async operations
3. Include proper accessibility attributes for new UI elements
4. Test with both light and dark themes
5. Validate all changes with `npm run validate`

## License

MIT License - see LICENSE file for details.

## Support

For issues and support, please refer to the main CyberBackup project documentation.