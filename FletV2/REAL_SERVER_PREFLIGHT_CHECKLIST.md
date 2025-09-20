# Real Server Preflight Checklist

This checklist must pass before connecting the Flet GUI to the real server.

1) Requirements & Dependencies
- [ ] httpx pinned in `requirements.txt` (>=0.27.2,<0.28)
- [ ] python-dotenv present for local env
- [ ] aiofiles present for streaming downloads

2) Configuration and Secrets
- [ ] Define `REAL_SERVER_URL` (https://host[:port]/api) in environment
- [ ] Define `BACKUP_SERVER_TOKEN` (or `BACKUP_SERVER_API_KEY`) in environment
- [ ] Optionals: `REQUEST_TIMEOUT` (seconds), `VERIFY_TLS` (true/false), `FLET_V2_DEBUG`
- [ ] No secrets committed to repo; use .env locally only

3) Bridge Auto-Detection
- [ ] `utils/server_bridge.create_server_bridge()` checks `REAL_SERVER_URL`
- [ ] Health check at `/health` succeeds; otherwise fallback to mock mode
- [ ] Bridge exposes same API in both modes (normalized `{success, data, error}`)

4) HTTP Client Behavior
- [ ] Authentication header `Authorization: Bearer <token>` applied globally
- [ ] Reasonable timeouts and TLS verification
- [ ] Errors normalized to `{success: False, error: str}`; never raise into UI

5) Endpoints Mapping (example paths; adjust to your server)
- GET  /clients → get_clients_async
- GET  /clients/{id} → get_client_details
- POST /clients → add_client_async
- DEL  /clients/{id} → delete_client_async
- POST /clients/{id}/disconnect → disconnect_client_async
- GET  /clients/{id}/files → get_client_files_async
- GET  /files → get_files_async
- POST /files/{id}/verify → verify_file_async
- GET  /files/{id}/download → download_file_async (stream)
- DEL  /files/{id} → delete_file_async
- GET  /database/info → get_database_info_async
- GET  /database/tables/{table} → get_table_data_async
- PATCH /database/tables/{table}/{id} → update_row
- DEL  /database/tables/{table}/{id} → delete_row
- GET  /logs → get_logs_async
- DELETE /logs → clear_logs_async
- POST /logs/export → export_logs_async
- GET  /logs/stats → get_log_statistics_async
- GET  /status → get_server_status_async
- GET  /system → get_system_status_async
- GET  /analytics → get_analytics_data_async
- GET  /dashboard/summary → get_dashboard_summary_async
- GET  /status/stats → get_server_statistics_async
- POST /server/start → start_server_async
- POST /server/stop → stop_server_async
- GET  /settings → load_settings_async
- POST /settings → save_settings_async
- POST /settings/validate → validate_settings_async
- POST /settings/backup → backup_settings_async
- POST /settings/restore → restore_settings_async
- GET  /settings/defaults → get_default_settings_async

6) Security & Compliance
- [ ] Use HTTPS in production
- [ ] Validate certificates; allow `VERIFY_TLS=false` only for dev
- [ ] Do not log secrets; redact Authorization headers
- [ ] Sanitize download paths and write to safe directory

7) UI/UX Readiness
- [ ] Long requests run via `page.run_task()`; UI remains responsive
- [ ] Progress reporting wired to `StateManager` for downloads/exports
- [ ] Error messages surfaced via `utils/user_feedback.py`
- [ ] Views implement `dispose()` and clean subscriptions/overlays

8) Validation
- [ ] Run `scripts/quick_syntax_check.py`
- [ ] Manual smoke: Dashboard, Clients, Files, Database, Logs, Settings
- [ ] If env vars set, app should use real mode; otherwise mock mode

9) Logging & Diagnostics
- [ ] Enable `FLET_V2_DEBUG=true` for verbose logs during integration
- [ ] Record network durations and failures without leaking secrets
