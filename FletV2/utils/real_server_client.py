"""
RealServerClient - thin HTTP client for the real backup server API.

Implements a subset of methods used by ServerBridge, normalizing IO to match
the simplified bridge contract. Uses httpx for async requests.
"""

from __future__ import annotations

import httpx
from typing import Any, Dict, List, Optional

import config


class RealServerClient:
    def __init__(self, base_url: str, token: Optional[str] = None, verify_tls: bool = True, timeout: float = 10.0):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.verify_tls = verify_tls
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._default_headers(),
            timeout=self.timeout,
            verify=self.verify_tls,
        )

    def _default_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def close(self):
        await self._client.aclose()

    # Health / connectivity -------------------------------------------------
    async def test_connection_async(self) -> Dict[str, Any]:
        try:
            resp = await self._client.get("/health")
            resp.raise_for_status()
            data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"status": resp.text}
            return {"success": True, "data": data}
        except httpx.HTTPError as e:
            return {"success": False, "error": str(e)}

    def is_connected(self) -> bool:
        # Optimistic; real check is via test_connection_async
        return True

    # Clients ---------------------------------------------------------------
    async def get_clients_async(self) -> List[Dict[str, Any]]:
        resp = await self._client.get("/clients")
        resp.raise_for_status()
        return resp.json()

    def get_clients(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("Use async variant get_clients_async()")

    def get_client_details(self, client_id: str) -> Dict[str, Any]:
        # Provide a sync shim via httpx.Client for rare sync paths
        with httpx.Client(base_url=self.base_url, headers=self._default_headers(), timeout=self.timeout, verify=self.verify_tls) as c:
            resp = c.get(f"/clients/{client_id}")
            resp.raise_for_status()
            return resp.json()

    async def add_client_async(self, client_data: Dict[str, Any]):
        resp = await self._client.post("/clients", json=client_data)
        resp.raise_for_status()
        return resp.json().get("id")

    async def delete_client_async(self, client_id: str):
        resp = await self._client.delete(f"/clients/{client_id}")
        resp.raise_for_status()
        return True

    async def disconnect_client_async(self, client_id: str):
        resp = await self._client.post(f"/clients/{client_id}/disconnect")
        resp.raise_for_status()
        return True

    def resolve_client(self, client_identifier: str):
        with httpx.Client(base_url=self.base_url, headers=self._default_headers(), timeout=self.timeout, verify=self.verify_tls) as c:
            resp = c.get(f"/clients/resolve", params={"q": client_identifier})
            resp.raise_for_status()
            return resp.json()

    # Files -----------------------------------------------------------------
    async def get_files_async(self):
        resp = await self._client.get("/files")
        resp.raise_for_status()
        return resp.json()

    async def get_client_files_async(self, client_id: str):
        resp = await self._client.get(f"/clients/{client_id}/files")
        resp.raise_for_status()
        return resp.json()

    async def verify_file_async(self, file_id: str):
        resp = await self._client.post(f"/files/{file_id}/verify")
        resp.raise_for_status()
        return resp.json()

    async def download_file_async(self, file_id: str, destination_path: str):
        # Streaming download
        async with self._client.stream("GET", f"/files/{file_id}/download") as r:
            r.raise_for_status()
            import aiofiles
            import os
            os.makedirs(destination_path, exist_ok=True)
            filename = r.headers.get("x-filename", f"{file_id}.bin")
            full_path = os.path.join(destination_path, filename)
            async with aiofiles.open(full_path, "wb") as f:
                async for chunk in r.aiter_bytes():
                    if chunk:
                        await f.write(chunk)
        return {"path": full_path}

    async def delete_file_async(self, file_id: str):
        resp = await self._client.delete(f"/files/{file_id}")
        resp.raise_for_status()
        return True

    # Database --------------------------------------------------------------
    async def get_database_info_async(self):
        resp = await self._client.get("/database/info")
        resp.raise_for_status()
        return resp.json()

    async def get_table_data_async(self, table_name: str):
        resp = await self._client.get(f"/database/tables/{table_name}")
        resp.raise_for_status()
        return resp.json()

    def update_row(self, table_name: str, row_id: str, updated_data: Dict[str, Any]):
        with httpx.Client(base_url=self.base_url, headers=self._default_headers(), timeout=self.timeout, verify=self.verify_tls) as c:
            resp = c.patch(f"/database/tables/{table_name}/{row_id}", json=updated_data)
            resp.raise_for_status()
            return True

    def delete_row(self, table_name: str, row_id: str):
        with httpx.Client(base_url=self.base_url, headers=self._default_headers(), timeout=self.timeout, verify=self.verify_tls) as c:
            resp = c.delete(f"/database/tables/{table_name}/{row_id}")
            resp.raise_for_status()
            return True

    # Logs ------------------------------------------------------------------
    async def get_logs_async(self):
        resp = await self._client.get("/logs")
        resp.raise_for_status()
        return resp.json()

    async def clear_logs_async(self):
        resp = await self._client.delete("/logs")
        resp.raise_for_status()
        return True

    async def export_logs_async(self, export_format: str, filters: Optional[Dict[str, Any]] = None):
        resp = await self._client.post("/logs/export", json={"format": export_format, "filters": filters or {}})
        resp.raise_for_status()
        return resp.json()

    async def get_log_statistics_async(self):
        resp = await self._client.get("/logs/stats")
        resp.raise_for_status()
        return resp.json()

    async def stream_logs_async(self, callback):
        # Placeholder: implement SSE/WebSocket if server supports
        raise NotImplementedError

    async def stop_log_stream_async(self, streaming_task):
        raise NotImplementedError

    # Status / analytics ----------------------------------------------------
    async def get_server_status_async(self):
        resp = await self._client.get("/status")
        resp.raise_for_status()
        return resp.json()

    async def get_system_status_async(self):
        resp = await self._client.get("/system")
        resp.raise_for_status()
        return resp.json()

    async def get_analytics_data_async(self):
        resp = await self._client.get("/analytics")
        resp.raise_for_status()
        return resp.json()

    async def get_dashboard_summary_async(self):
        resp = await self._client.get("/dashboard/summary")
        resp.raise_for_status()
        return resp.json()

    async def get_server_statistics_async(self):
        resp = await self._client.get("/status/stats")
        resp.raise_for_status()
        return resp.json()

    async def start_server_async(self):
        resp = await self._client.post("/server/start")
        resp.raise_for_status()
        return resp.json()

    async def stop_server_async(self):
        resp = await self._client.post("/server/stop")
        resp.raise_for_status()
        return resp.json()

    # Settings --------------------------------------------------------------
    async def save_settings_async(self, settings_data: Dict[str, Any]):
        resp = await self._client.post("/settings", json=settings_data)
        resp.raise_for_status()
        return True

    async def load_settings_async(self):
        resp = await self._client.get("/settings")
        resp.raise_for_status()
        return resp.json()

    async def validate_settings_async(self, settings_data: Dict[str, Any]):
        resp = await self._client.post("/settings/validate", json=settings_data)
        resp.raise_for_status()
        return resp.json()

    async def backup_settings_async(self, backup_name: str, settings_data: Dict[str, Any]):
        resp = await self._client.post("/settings/backup", json={"name": backup_name, "data": settings_data})
        resp.raise_for_status()
        return resp.json()

    async def restore_settings_async(self, backup_file: str):
        resp = await self._client.post("/settings/restore", json={"file": backup_file})
        resp.raise_for_status()
        return resp.json()

    async def get_default_settings_async(self):
        resp = await self._client.get("/settings/defaults")
        resp.raise_for_status()
        return resp.json()
