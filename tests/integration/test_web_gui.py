"""Playwright script to inspect the CyberBackup web GUI and capture console errors.

Usage:
    python test_web_gui.py [TARGET_URL] [--width 1600] [--height 1000] [--headed]

Notes:
    - Playwright uses a fixed *viewport* (default 1280x720) which can make the UI look like it has
      less usable screen when running in a Playwright-controlled browser.
    - This script sets a larger deterministic viewport by default to reduce confusion.

This script saves a full-page screenshot and writes console logs to console_logs.json.
"""

from __future__ import annotations

import argparse
import json
import os
from urllib.parse import urlparse, urlunparse

from playwright.sync_api import sync_playwright


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "target_url",
        nargs="?",
        default="http://localhost:9090",
        help="Target URL to open (default: http://localhost:9090)",
    )
    parser.add_argument(
        "--width", type=int, default=int(os.getenv("PLAYWRIGHT_VIEWPORT_W", 1600))
    )
    parser.add_argument(
        "--height", type=int, default=int(os.getenv("PLAYWRIGHT_VIEWPORT_H", 1000))
    )
    parser.add_argument(
        "--headed", action="store_true", help="Launch browser in headed mode"
    )
    parser.add_argument("--headless", action="store_true", help="Force headless mode")
    parser.add_argument(
        "--maximize",
        action="store_true",
        help=(
            "Headed mode only: start maximized and let the viewport follow the window size. "
            "Useful for manual inspection."
        ),
    )
    return parser.parse_args()


def _resolve_playwright_launch(
    args: argparse.Namespace,
) -> tuple[bool, list[str], dict | None]:
    """Resolve headless/headed, window args, and viewport for Playwright.

    Returns:
        (headless, launch_args, viewport)
    """
    headless = True
    if args.headed:
        headless = False
    if args.headless:
        headless = True

    launch_args: list[str] = []
    viewport: dict | None = {"width": args.width, "height": args.height}

    if not headless and args.maximize:
        launch_args.append("--start-maximized")
        viewport = None

    return headless, launch_args, viewport


def main() -> None:
    args = _parse_args()
    target_url: str = args.target_url

    console_logs: list[dict] = []
    errors: list[dict] = []

    with sync_playwright() as p:
        headless, launch_args, viewport = _resolve_playwright_launch(args)
        browser = p.chromium.launch(headless=headless, args=launch_args)
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        # Capture console messages
        def handle_console(msg):
            log_entry = {"type": msg.type, "text": msg.text, "location": msg.location}
            console_logs.append(log_entry)
            print(f"[CONSOLE {msg.type.upper()}] {msg.text}")
            if msg.type in ["error", "warning"]:
                errors.append(log_entry)

        page.on("console", handle_console)

        # Capture page errors
        def handle_page_error(error):
            error_msg = f"Page error: {error}"
            errors.append({"type": "page_error", "text": error_msg})
            print(f"[PAGE ERROR] {error}")

        page.on("pageerror", handle_page_error)

        def _swap_host(url: str, new_host: str) -> str:
            parsed = urlparse(url)
            if not parsed.scheme:
                return url
            port_part = f":{parsed.port}" if parsed.port else ""
            return urlunparse(parsed._replace(netloc=f"{new_host}{port_part}"))

        def _goto_with_fallback(url: str):
            print(f"Navigating to {url}...")
            return page.goto(url, wait_until="networkidle", timeout=30000)

        # Navigate to the web GUI
        try:
            response = _goto_with_fallback(target_url)
        except Exception as e:
            # Windows environments sometimes resolve localhost to IPv6 (::1), while local dev servers
            # may only listen on IPv4. In that case, fall back to 127.0.0.1 for convenience.
            should_fallback = (
                "localhost" in target_url and "ERR_CONNECTION_REFUSED" in str(e)
            )
            if should_fallback:
                fallback_url = _swap_host(target_url, "127.0.0.1")
                print(f"Retrying with IPv4 loopback: {fallback_url}")
                try:
                    response = _goto_with_fallback(fallback_url)
                    target_url = fallback_url
                except Exception as e2:
                    print(f"ERROR navigating to page: {e2}")
                    return
            else:
                print(f"ERROR navigating to page: {e}")
                return

        if response:
            print(f"Page loaded with status: {response.status}")
        else:
            print("Page navigation failed: No response received.")

        # Wait a bit for JS to execute
        page.wait_for_timeout(2000)

        # Take screenshot
        screenshot_path = "web_gui_screenshot.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\nScreenshot saved to: {screenshot_path}")

        # Get page title
        title = page.title()
        print(f"Page title: {title}")

        # Get page HTML to inspect structure
        content = page.content()
        with open("web_gui_content.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Page HTML saved to: web_gui_content.html")

        # Check for specific elements
        print("\n=== Element Check ===")
        try:
            # Check for common elements that should be present
            elements_to_check = [
                ("body", "Body element"),
                ("#app", "App container"),
                (".container", "Container div"),
                ("script", "Script tags"),
                ('link[rel="stylesheet"]', "Stylesheets"),
            ]

            for selector, name in elements_to_check:
                count = page.locator(selector).count()
                print(f"{name} ({selector}): {count} found")
        except Exception as e:
            print(f"Error checking elements: {e}")

        # Print summary
        print("\n=== Summary ===")
        print(f"Total console messages: {len(console_logs)}")
        print(f"Errors/Warnings: {len(errors)}")

        if errors:
            print("\n=== Errors and Warnings ===")
            for error in errors:
                print(
                    f"[{error.get('type', 'unknown').upper()}] {error.get('text', 'No message')}"
                )
                if error.get("location"):
                    loc = error["location"]
                    print(
                        f"  Location: {loc.get('url', 'unknown')}:{loc.get('lineNumber', '?')}"
                    )

        # Save detailed log
        with open("console_logs.json", "w", encoding="utf-8") as f:
            json.dump(console_logs, f, indent=2)
        print("\nDetailed console logs saved to: console_logs.json")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
