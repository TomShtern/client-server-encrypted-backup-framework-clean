# Flet GUI Terminal Debugging Setup

This guide provides a simple, effective approach to centralize all Flet GUI debugging output to the terminal.

## Core Solution
- to centralize Flet GUI debugging output, including errors currently only visible in the GUI, to the terminal. The best approach combines Python's `logging` module with a `global exception handler` (`sys.excepthook`).
  
  - Here's the setup:
  
  ---
  
  ### 1. Configure Python's `logging` Module
  
  Set up `logging.basicConfig` to output `DEBUG` level messages to `sys.stdout` (the terminal).
  
  ```python
  import logging
  import sys
  
  logging.basicConfig(
      level=logging.DEBUG,
      format='%(asctime)s - %(levelname)s - %(message)s',
      stream=sys.stdout
  )
  logger = logging.getLogger(__name__)
  ```
  
  ### 2. Implement a Global Exception Hook (`sys.excepthook`)
  
  This is crucial for catching all uncaught Python exceptions, ensuring they are logged to the terminal, even if Flet's event loop might otherwise suppress them.
  
  ```python
  def custom_exception_hook(exc_type, exc_value, exc_traceback):
      if issubclass(exc_type, KeyboardInterrupt):
          sys.__excepthook__(exc_type, exc_value, exc_traceback)
          return
      logger.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
  
  sys.excepthook = custom_exception_hook
  ```
  
  ### 3. Use `logger` in Your Flet Application
  
  Replace `print()` statements with `logger.debug()`, `logger.info()`, `logger.error()`, etc., for consistent, structured output.
  
  ```python
  import flet as ft
  # ... (logging setup from above) ...
  
  def main(page: ft.Page):
      logger.info("Flet application started.")
  
      def button_clicked(e):
          logger.debug("Button clicked event received.")
          try:
              result = 1 / 0  # Simulate an error
              logger.info(f"Result: {result}")
          except Exception as ex:
              logger.error(f"Error in button_clicked: {ex}", exc_info=True)
  
      def on_page_resized(e):
          logger.info(f"Page resized to: {page.width}x{page.height}")
  
      page.on_resized = on_page_resized
      page.add(
          ft.Text("Hello, Debugging!"),
          ft.ElevatedButton("Click Me", on_click=button_clicked)
      )
      logger.info("UI elements added.")
  
  if __name__ == "__main__":
      ft.app(target=main)
  ```
  
  This approach provides centralized, structured logging, and critically, catches all uncaught exceptions, ensuring comprehensive debugging information appears in the terminal.
  
  While Flet offers visual debugging tools like `page.show_semantics_debugger` and internal logging methods like `page.log()`/`page.debug()`, there isn't a single built-in Flet solution that replaces Python's `logging` module and `sys.excepthook` for comprehensive terminal debugging of Python errors. The Python-level approach remains the most robust and reliable method for catching all errors and displaying them in the terminal.
  
  ### Why this is the most robust solution for terminal debugging:
  
  - **Centralized Logging:** All your messages (`info`, `debug`, `errors`) go to one place.
  - **Catch All Exceptions:** The `sys.excepthook` ensures that even exceptions that occur in Flet's internal event processing, which might otherwise be silent, are caught and logged to your terminal with full tracebacks. This directly addresses the problem of errors not appearing in the terminal.
  - **Structured Output:** `logging` allows for consistent formatting, timestamps, and log levels, making it easier to parse and filter debug information.
  - **Flexibility:** You can easily change the log level (e.g., to `INFO` for production) or add more handlers (e.g., to write logs to a file) without changing your application code.
  
  This setup will provide a much more comprehensive and reliable stream of debugging information directly to your terminal, helping you catch errors that are currently only visible within the GUI.