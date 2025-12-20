"""
Start a temporary static server for the canonical Web UI (api_server/web_ui), open it in Playwright,
collect console output, take a full-page screenshot, then shut the server down.

Usage:
    python scripts/capture_client_web_gui.py [--dir api_server/web_ui] [--port 9091] [--page index.html]

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
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING

from playwright.sync_api import sync_playwright

if TYPE_CHECKING:
    from playwright.sync_api import Response, ViewportSize

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEB_UI_DIR = ROOT / "api_server" / "web_ui"


class SilentHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args):  # noqa: A003 - extend parent API
        # Keep server logs quiet for cleaner CI/terminal output
        pass


def wait_for_port(host: str, port: int, timeout: float = 10.0) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        with contextlib.closing(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ) as sock:
            sock.settimeout(0.5)
            try:
                sock.connect((host, port))
                return True
            except OSError:
                time.sleep(0.2)
    return False


def start_server(
    host: str, port: int, directory: Path
) -> tuple[http.server.ThreadingHTTPServer, threading.Thread]:
    os.chdir(directory)
    handler = SilentHTTPRequestHandler
    server = http.server.ThreadingHTTPServer((host, port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir",
        type=str,
        default=str(DEFAULT_WEB_UI_DIR),
        help="Directory to serve (default: api_server/web_ui)",
    )
    parser.add_argument("--port", type=int, default=9091)
    parser.add_argument("--page", type=str, default="index.html")
    parser.add_argument(
        "--headless", action="store_true", help="Run browser headless (default)"
    )
    parser.add_argument(
        "--headed", action="store_true", help="Run browser in headed/visible mode"
    )
    parser.add_argument(
        "--maximize",
        action="store_true",
        help=(
            "Headed mode only: start maximized and let the viewport follow the window size. "
            "Useful when you want the page to use the full available screen."
        ),
    )
    parser.add_argument(
        "--open-default",
        action="store_true",
        help="Also open the page in your default system browser",
    )
    parser.add_argument(
        "--keep-alive",
        type=int,
        default=0,
        help="Keep server alive N seconds (use with --open-default)",
    )
    return parser.parse_args()


def _resolve_playwright_launch(
    args: argparse.Namespace,
) -> tuple[bool, list[str], ViewportSize | None]:
    """Resolve headless/headed, Chromium args, and viewport.

    Returns:
        (headless, launch_args, viewport)
    """
    headless = True
    if args.headed:
        headless = False
    elif args.headless:
        headless = True

    # Allow env override PLAYWRIGHT_HEADLESS=false
    env_override = os.getenv("PLAYWRIGHT_HEADLESS")
    if env_override is not None:
        headless = env_override.lower() not in ("false", "0", "no")

    launch_args: list[str] = ["--disable-web-security"]
    viewport: ViewportSize | None = {"width": 1600, "height": 1000}
    if not headless and args.maximize:
        launch_args.append("--start-maximized")
        viewport = None

    return headless, launch_args, viewport


def _navigate_with_retry(page, url: str) -> tuple[Response | None, int | None]:
    """Navigate to url with a single retry.

    Returns:
        (response, error_code) where error_code is None on success.
    """
    try:
        resp = page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return resp, None
    except Exception as e:  # noqa: BLE001
        print(f"ERROR navigating to page: {e}")
        time.sleep(1.5)
        try:
            resp = page.goto(url, wait_until="load", timeout=15000)
            return resp, None
        except Exception as e2:  # noqa: BLE001
            print(f"SECOND FAILURE navigating to page: {e2}")
            return None, 4


def _maybe_open_default_browser(url: str, args: argparse.Namespace) -> None:
    if not args.open_default:
        return

    try:
        webbrowser.open(url, new=2)
        print("Opened in default browser.")
        if args.keep_alive and args.keep_alive > 0:
            print(f"Keeping server alive for {args.keep_alive}s ...")
            time.sleep(args.keep_alive)
    except Exception as e:  # noqa: BLE001
        print(f"Failed to open default browser: {e}")


def _write_outputs(page, console_logs: list[dict], errors: list[dict]) -> None:
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

    print("\n=== Summary ===")
    print(f"Console messages: {len(console_logs)} | Errors/Warnings: {len(errors)}")


def main() -> int:
    args = _parse_args()

    host = "127.0.0.1"
    port = args.port
    page_name = args.page

    serve_dir = Path(args.dir).expanduser().resolve()

    if not serve_dir.is_dir():
        print(f"ERROR: Web UI directory not found: {serve_dir}")
        return 2

    # Start static server
    print(f"Starting static server at http://{host}:{port} serving {serve_dir} ...")
    server, thread = start_server(host, port, serve_dir)
    try:
        if not wait_for_port(host, port, timeout=10):
            print("ERROR: Server did not become ready in time")
            return 3

        url = f"http://{host}:{port}/{page_name}"
        print(f"Opening {url} with Playwright ...")

        console_logs = []
        errors = []
        with sync_playwright() as p:
            headless, launch_args, viewport = _resolve_playwright_launch(args)
            browser = p.chromium.launch(
                headless=headless,
                args=launch_args,
                slow_mo=0 if headless else 50,
            )
            if not headless:
                print("Browser launched in headed mode.")
            context = browser.new_context(viewport=viewport)
            page = context.new_page()

            # Capture console
            def handle_console(msg):
                entry = {"type": msg.type, "text": msg.text, "location": msg.location}
                console_logs.append(entry)
                if msg.type in ("error", "warning"):
                    errors.append(entry)
                print(f"[CONSOLE {msg.type.upper()}] {msg.text}")

            page.on("console", handle_console)

            # Navigate and wait
            resp, nav_error = _navigate_with_retry(page, url)
            if nav_error is not None:
                browser.close()
                return nav_error

            status = resp.status if resp else None
            print(f"Page loaded with status: {status}")

            # A short settle time for late JS
            page.wait_for_timeout(1000)

            _maybe_open_default_browser(url, args)

            _write_outputs(page, console_logs, errors)

            browser.close()

        return 0
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        print("Static server stopped.")


if __name__ == "__main__":
    raise SystemExit(main())
