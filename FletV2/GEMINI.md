IMPORTANT: For extremely important AI guidance, rules, and data please consult the `#file:AI-Context` folder. Additional important documentation and design reference materials are in the `#file:important_docs` folder. Use `AI-Context` first for critical decisions.

## Project Overview

This project is a desktop backup management application named FletV2, built with Flet and Python. It provides a graphical user interface for managing a backup server, including features like viewing server status, managing clients, browsing files, and monitoring analytics. The application is designed with a clean architecture, emphasizing simplicity, maintainability, and performance by adhering to Flet's best practices.

**Main Technologies:**

*   **Flet 0.28.3:** The core framework for building the user interface.
*   **Python 3.13.5:** The programming language used for the application logic.
*   **Material Design 3:** The design system used for the application's theme and components.

**Architecture:**

The application follows a single-page application (SPA) architecture with a main `FletV2App` class that manages navigation and view switching. The UI is composed of several views, each responsible for a specific functionality (e.g., dashboard, clients, files). A `ServerBridge` class handles communication with the backup server, with a mock mode for development and testing. State management is handled by a simplified, Flet-native state manager.

## Building and Running

To build and run the application, follow these steps:

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the application:**
    ```bash
    python main.py
    ```

## Development Conventions

The project follows a set of development conventions to ensure code quality and consistency:

*   **Framework Harmony:** Use Flet's built-in components and patterns instead of creating custom solutions.
*   **Simplicity:** Avoid over-engineering and unnecessary complexity.
*   **Naming Conventions:**
    *   `create_*`: for view and component creation functions.
    *   `get_*`: for data retrieval methods.
    *   `on_*`: for event handlers.
    *   `show_*`: for user feedback functions.
    *   `update_*`: for state modification functions.
*   **Error Handling:** Use `try...except` blocks for operations that might fail and provide user feedback.
*   **Asynchronous Operations:** Use `async/await` for long-running operations to keep the UI responsive.
*   **Performance:**
    *   Use `control.update()` for targeted UI updates instead of `page.update()`.
    *   Use `ft.Ref` for robust and performant access to UI controls.

## Key Files and Directories

*   `main.py`: The main entry point of the application.
*   `config.py`: Configuration constants.
*   `theme.py`: Theme definitions and management.
*   `views/`: Directory containing the UI views for different functionalities.
*   `utils/`: Directory containing utility modules, such as the server bridge, state manager, and UI components.
*   `tests/`: Directory containing the test infrastructure.
*   `docs/`: Directory containing the project documentation.
*   `requirements.txt`: A file listing the Python dependencies for the project.
