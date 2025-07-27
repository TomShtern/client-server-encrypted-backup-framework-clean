# Project Instructions for Gemini

This file contains project-specific instructions and context for the Gemini assistant.

## Project Overview

This project is a client-server encrypted backup framework. The client is a C++ application with a web-based GUI, and the server is a Python application. The system uses RSA-1024 for key exchange and AES-256-CBC for file encryption.

## Key Components

*   **C++ Client:** The client is responsible for reading files, encrypting them, and sending them to the server. It also provides a web-based GUI for user interaction.
*   **Python Server:** The server is responsible for receiving encrypted files from the client, storing them, and managing client information.
*   **Cryptography:** The system uses a combination of RSA and AES encryption to ensure the security of the backups. The client and server use a custom binary protocol with CRC verification to ensure the integrity of the data.

## Development and Testing

The project has a comprehensive set of development and testing tools, including:

*   A build system based on CMake and custom batch scripts
*   A master test suite that combines tests from various other files
*   A variety of scripts for generating keys, testing individual components, and validating the system

## Challenges and Current Status

The project has faced several challenges, particularly with the integration of the Crypto++ library and the development of the GUI. The developers have tried several different approaches to address these challenges, and the project is now in a mostly functional state. However, there are still some issues that need to be addressed, particularly with the cryptography and the GUI.

## Future Development

The project has a detailed roadmap for future development, which includes plans for adding new features, such as incremental backups, smart compression, and a web interface. It also includes a list of advanced ideas for making the project more impressive to potential employers.