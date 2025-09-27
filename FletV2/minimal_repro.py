#!/usr/bin/env python3
"""Minimal reproduction harness to detect why process exits with code 1.
Launches a trivial Flet app WITHOUT importing the heavy main/dashboard code.
If this also exits code 1, issue is environment / flet install. If it stays
running, issue is in main application code path.
"""
import flet as ft
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def main(page: ft.Page):
    page.title = "Minimal Repro"
    page.add(ft.Text("Minimal Flet app running"))
    # Keep something alive and log heartbeat
    async def heartbeat():
        n = 0
        while True:
            n += 1
            logging.info("heartbeat %s", n)
            await asyncio.sleep(2)
    page.run_task(heartbeat)

if __name__ == "__main__":
    import asyncio
    asyncio.run(ft.app_async(target=main, view=ft.AppView.WEB_BROWSER, port=8558))  # type: ignore[attr-defined]
