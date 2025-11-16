"""Playwright script to capture scrolled views of the CyberBackup web GUI.

Usage:
    python test_web_gui_scroll.py [TARGET_URL]

Captures screenshots at different scroll positions.
"""
import sys
from playwright.sync_api import sync_playwright


def main():
    target_url = (
        sys.argv[1]
        if len(sys.argv) > 1 and isinstance(sys.argv[1], str)
        else "http://localhost:9091/NewGUIforClient.html"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1400, 'height': 900})

        # Navigate to the web GUI
        print(f"Navigating to {target_url}...")
        try:
            response = page.goto(target_url, wait_until='networkidle', timeout=30000)
            if response:
                print(f"Page loaded with status: {response.status}")
        except Exception as e:
            print(f"ERROR navigating to page: {e}")
            browser.close()
            return

        # Wait for JS to execute
        page.wait_for_timeout(2000)

        # Take screenshots at different scroll positions
        print("\nCapturing top view...")
        page.screenshot(path='web_gui_top.png', full_page=False)
        print("Saved: web_gui_top.png")

        # Scroll down to see action buttons
        print("\nScrolling to action buttons...")
        page.evaluate("window.scrollTo(0, 600)")
        page.wait_for_timeout(500)
        page.screenshot(path='web_gui_middle.png', full_page=False)
        print("Saved: web_gui_middle.png")

        # Scroll to bottom to see stats grid
        print("\nScrolling to bottom...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(500)
        page.screenshot(path='web_gui_bottom.png', full_page=False)
        print("Saved: web_gui_bottom.png")

        # Full page screenshot
        print("\nCapturing full page...")
        page.screenshot(path='web_gui_full.png', full_page=True)
        print("Saved: web_gui_full.png")

        print("\n✅ All screenshots captured!")

        browser.close()


if __name__ == "__main__":
    main()
