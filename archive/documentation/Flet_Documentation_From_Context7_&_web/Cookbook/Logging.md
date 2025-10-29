# Logging

The Flet documentation provides guidance on controlling the logging level for the Flet library and its underlying components. To enable detailed logging for all Flet modules (flet_core and flet), you can add `logging.basicConfig(level=logging.DEBUG)` before calling `ft.app()`.

If you need to reduce verbosity, you can suppress messages from the `flet_core` module by setting its level to `INFO` using `logging.getLogger("flet_core").setLevel(logging.INFO)`.

For the Fletd server (the built-in Flet web server), its logging level is implicitly set by the Python Flet logger. However, you can override this using the `FLET_LOG_LEVEL` environment variable, with options like `debug`, `info`, `warning`, `panic`, or `fatal`.

Additionally, to redirect Flet logs to a file, set the `FLET_LOG_TO_FILE` environment variable to `true`. Logs will be saved to `/tmp/flet-server.log` on macOS and Linux, and to `%TEMP%\flet-server.log` on Windows.
