"""
Start a temporary static server for Client/Client-gui, open the client in Playwright,
collect console output, take a full-page screenshot, then shut the server down.

Usage:
  python scripts/capture_client_web_gui.py [--port 9091] [--page NewGUIforClient.html]

Outputs:
  - client_web_gui_screenshot.png
  - console_logs.json
  - web_gui_content.html
"""
from __future__ import annotations
import argparse
import contextlib
import http.server
import json
import os
import socket
import threading
import time
from pathlib import Path
import webbrowser

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CLIENT_DIR = ROOT / "Client" / "Client-gui"


class SilentHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args):  # noqa: A003 - extend parent API
        # Keep server logs quiet for cleaner CI/terminal output
        pass


def wait_for_port(host: str, port: int, timeout: float = 10.0) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(0.5)
            try:
                sock.connect((host, port))
                return True
            except OSError:
                time.sleep(0.2)
    return False


def start_server(host: str, port: int, directory: Path) -> tuple[http.server.ThreadingHTTPServer, threading.Thread]:
    os.chdir(directory)
    handler = SilentHTTPRequestHandler
    server = http.server.ThreadingHTTPServer((host, port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9091)
    parser.add_argument("--page", type=str, default="NewGUIforClient.html")
    parser.add_argument("--headless", action="store_true", help="Run browser headless (default)")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed/visible mode")
    parser.add_argument("--open-default", action="store_true", help="Also open the page in your default system browser")
    parser.add_argument("--keep-alive", type=int, default=0, help="Keep server alive N seconds (use with --open-default)")
    args = parser.parse_args()

    host = "127.0.0.1"
    port = args.port
    page_name = args.page

    if not CLIENT_DIR.is_dir():
        print(f"ERROR: Client directory not found: {CLIENT_DIR}")
        return 2

    # Start static server
    print(f"Starting static server at http://{host}:{port} serving {CLIENT_DIR} ...")
    server, thread = start_server(host, port, CLIENT_DIR)
    try:
        if not wait_for_port(host, port, timeout=10):
            print("ERROR: Server did not become ready in time")
            return 3

        url = f"http://{host}:{port}/{page_name}"
        print(f"Opening {url} with Playwright ...")

        console_logs = []
        errors = []
        with sync_playwright() as p:
            # Determine headless vs headed preference
            headless = True
            if args.headed:
                headless = False
            elif args.headless:
                headless = True
            # Allow env override PLAYWRIGHT_HEADLESS=false
            env_override = os.getenv("PLAYWRIGHT_HEADLESS")
            if env_override is not None:
                headless = env_override.lower() not in ("false", "0", "no")
            browser = p.chromium.launch(headless=headless, args=["--disable-web-security"], slow_mo=0 if headless else 50)
            if not headless:
                print("Browser launched in headed mode.")
            page = browser.new_page()
            # Improve viewport size for large progress ring visibility
            from contextlib import suppress
            with suppress(Exception):
                page.set_viewport_size({"width": 1600, "height": 1000})

            # Capture console
            def handle_console(msg):
                entry = {"type": msg.type, "text": msg.text, "location": msg.location}
                console_logs.append(entry)
                if msg.type in ("error", "warning"):
                    errors.append(entry)
                print(f"[CONSOLE {msg.type.upper()}] {msg.text}")

            page.on("console", handle_console)

            # Navigate and wait
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=30000)
                status = resp.status if resp else None
                print(f"Page loaded with status: {status}")
            except Exception as e:  # noqa: BLE001
                print(f"ERROR navigating to page: {e}")
                # Attempt a single retry after short delay (handles transient race)
                time.sleep(1.5)
                try:
                    resp = page.goto(url, wait_until="load", timeout=15000)
                    status = resp.status if resp else None
                    print(f"Retry loaded with status: {status}")
                except Exception as e2:  # noqa: BLE001
                    print(f"SECOND FAILURE navigating to page: {e2}")
                    browser.close()
                    return 4

            # A short settle time for late JS
            page.wait_for_timeout(1000)

            # Optionally open default browser for manual inspection
            if args.open_default:
                try:
                    webbrowser.open(url, new=2)
                    print("Opened in default browser.")
                    if args.keep_alive and args.keep_alive > 0:
                        print(f"Keeping server alive for {args.keep_alive}s ...")
                        time.sleep(args.keep_alive)
                except Exception as e:
                    print(f"Failed to open default browser: {e}")

            # Screenshot and dump
            screenshot_path = ROOT / "client_web_gui_screenshot.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"Screenshot saved to: {screenshot_path}")

            html_path = ROOT / "web_gui_content.html"
            html = page.content()
            html_path.write_text(html, encoding="utf-8")
            print(f"HTML saved to: {html_path}")

            logs_path = ROOT / "console_logs.json"
            logs_path.write_text(json.dumps(console_logs, indent=2), encoding="utf-8")
            print(f"Console logs saved to: {logs_path}")

            # Summary
            print("\n=== Summary ===")
            print(f"Console messages: {len(console_logs)} | Errors/Warnings: {len(errors)}")

            browser.close()

        return 0
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        print("Static server stopped.")


if __name__ == "__main__":
    raise SystemExit(main())
