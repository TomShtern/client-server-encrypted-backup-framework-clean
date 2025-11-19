#!/usr/bin/env python3
"""
Test script to verify the CyberBackup Client GUI layout fixes.
Uses Playwright to capture screenshots and verify the layout is correct.
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright


async def test_gui_layout():
    """Test the GUI layout and capture screenshots."""
    print("Starting Playwright browser...")

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        # Navigate to the GUI
        gui_path = Path(__file__).parent / "Client" / "Client-gui" / "NewGUIforClient.html"
        gui_url = f"file://{gui_path.as_posix()}"

        print(f"Loading GUI from: {gui_url}")
        await page.goto(gui_url)

        # Wait for page to load
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)  # Give time for CSS to apply

        # Capture full-page screenshot
        screenshot_path = Path(__file__).parent / "gui_layout_fixed.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"Screenshot saved to: {screenshot_path}")

        # Capture viewport screenshot
        viewport_screenshot = Path(__file__).parent / "gui_layout_fixed_viewport.png"
        await page.screenshot(path=str(viewport_screenshot))
        print(f"Viewport screenshot saved to: {viewport_screenshot}")

        # Check for layout issues
        print("\nChecking layout...")

        # Check if main grid is properly configured
        main_element = page.locator("main#mainContent")
        main_box = await main_element.bounding_box()
        print(f"Main element bounds: {main_box}")

        # Check configuration panel
        config_panel = page.locator("main#mainContent > aside.stack")
        config_box = await config_panel.bounding_box()
        print(f"Configuration panel bounds: {config_box}")

        # Check status panel
        status_panel = page.locator("main#mainContent > section.stack")
        status_box = await status_panel.bounding_box()
        print(f"Status panel bounds: {status_box}")

        # Check logs section
        logs_section = page.locator("section.logs")
        logs_box = await logs_section.bounding_box()
        print(f"Logs section bounds: {logs_box}")

        # Verify no overlap
        if config_box and status_box:
            # Check if panels don't overlap horizontally
            config_right = config_box['x'] + config_box['width']
            status_left = status_box['x']

            if config_right > status_left:
                print("❌ WARNING: Configuration and Status panels are overlapping!")
            else:
                print("✅ Configuration and Status panels are properly separated")

        if main_box and logs_box:
            # Check if logs is below main content
            main_bottom = main_box['y'] + main_box['height']
            logs_top = logs_box['y']

            if logs_top < main_bottom:
                print("❌ WARNING: Logs section is overlapping with main content!")
            else:
                print("✅ Logs section is properly positioned below main content")

        print("\n✅ Layout test complete!")

        # Keep browser open for manual inspection
        print("\nBrowser will remain open for manual inspection...")
        print("Press Enter to close browser and exit...")
        input()

        await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(test_gui_layout())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
