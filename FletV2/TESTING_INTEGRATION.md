Integration Tests for FletV2
================================

What’s included
- Headless integration tests for the five core views: Dashboard, Clients, Files, Database, Logs
- Tests execute against the ServerBridge in mock mode (no real server required)
- A tiny FakePage to satisfy Flet Page APIs used in views (open/close dialogs, overlay, run_task)

How to run
1) Ensure dependencies are installed in your virtualenv from FletV2/requirements.txt
2) From the FletV2 folder, run the test runner:

    python -m unittest discover -s tests -p "test_*.py"

or to run only the integration suite:

    python -m unittest discover -s tests/integration -p "test_*.py"

Notes on environment
- Tests default to mock mode by setting FLET_V2_DEBUG=true
- To exercise a real HTTP server via RealServerClient, set REAL_SERVER_URL and BACKUP_SERVER_TOKEN; the bridge will attempt a health check and switch automatically if available.

What’s covered
- View creation succeeds and initial setup subscriptions run
- ServerBridge calls succeed in mock mode and return well-shaped data
- Critical operations flow through the bridge:
  - Clients: listing, delete, disconnect
  - Files: listing, delete, verify (verify path is exercised at bridge level)
  - Database: fetch clients table data
  - Logs: load and basic filter/update path (implicitly via setup)

Known limitations / follow-ups
- UI interactions that require a real Flet runtime (dialogs, FilePicker) are not fully simulated; tests validate data flows and do not click popup menu items.
- Dashboard view has rich async background tasks; the integration test validates creation and basic status retrieval rather than long-running loops.
- Real server flows are not executed in CI unless REAL_SERVER_URL is provided; consider adding a separate job with secrets to run against a staging server.
- If Flet APIs change, FakePage may require small adjustments.

Troubleshooting
- If Python reports an event loop already running during run_task, the helper falls back to a new loop per call.
- If imports fail, ensure the working directory is FletV2/ and sys.path includes it.
