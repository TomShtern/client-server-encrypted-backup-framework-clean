"""Playwright script to inspect the CyberBackup web GUI and capture console errors.

Usage:
    python test_web_gui.py [TARGET_URL]

If TARGET_URL is omitted, defaults to http://localhost:9090
This script saves a full-page screenshot and writes console logs to console_logs.json.
"""
from playwright.sync_api import sync_playwright
import json
import sys

def main():
    target_url = (
        sys.argv[1]
        if len(sys.argv) > 1 and isinstance(sys.argv[1], str)
        else "http://localhost:9090"
    )
    console_logs = []
    errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console messages
        def handle_console(msg):
            log_entry = {
                'type': msg.type,
                'text': msg.text,
                'location': msg.location
            }
            console_logs.append(log_entry)
            print(f"[CONSOLE {msg.type.upper()}] {msg.text}")
            if msg.type in ['error', 'warning']:
                errors.append(log_entry)

        page.on('console', handle_console)

        # Capture page errors
        def handle_page_error(error):
            error_msg = f"Page error: {error}"
            errors.append({'type': 'page_error', 'text': error_msg})
            print(f"[PAGE ERROR] {error}")

        page.on('pageerror', handle_page_error)

        # Navigate to the web GUI
        print(f"Navigating to {target_url}...")
        try:
            response = page.goto(target_url, wait_until='networkidle', timeout=30000)
            print(f"Page loaded with status: {response.status}")
        except Exception as e:
            print(f"ERROR navigating to page: {e}")
            browser.close()
            return

        # Wait a bit for JS to execute
        page.wait_for_timeout(2000)

        # Take screenshot
        screenshot_path = 'web_gui_screenshot.png'
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\nScreenshot saved to: {screenshot_path}")

        # Get page title
        title = page.title()
        print(f"Page title: {title}")

        # Get page HTML to inspect structure
        content = page.content()
        with open('web_gui_content.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Page HTML saved to: web_gui_content.html")

        # Check for specific elements
        print("\n=== Element Check ===")
        try:
            # Check for common elements that should be present
            elements_to_check = [
                ('body', 'Body element'),
                ('#app', 'App container'),
                ('.container', 'Container div'),
                ('script', 'Script tags'),
                ('link[rel="stylesheet"]', 'Stylesheets'),
            ]

            for selector, name in elements_to_check:
                count = page.locator(selector).count()
                print(f"{name} ({selector}): {count} found")
        except Exception as e:
            print(f"Error checking elements: {e}")

        # Print summary
        print(f"\n=== Summary ===")
        print(f"Total console messages: {len(console_logs)}")
        print(f"Errors/Warnings: {len(errors)}")

        if errors:
            print("\n=== Errors and Warnings ===")
            for error in errors:
                print(f"[{error.get('type', 'unknown').upper()}] {error.get('text', 'No message')}")
                if 'location' in error and error['location']:
                    loc = error['location']
                    print(f"  Location: {loc.get('url', 'unknown')}:{loc.get('lineNumber', '?')}")

        # Save detailed log
        with open('console_logs.json', 'w', encoding='utf-8') as f:
            json.dump(console_logs, f, indent=2)
        print("\nDetailed console logs saved to: console_logs.json")

        browser.close()

if __name__ == "__main__":
    main()
