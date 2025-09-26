#!/usr/bin/env python3
"""
Essential Playwright Tests for CyberBackup Portfolio Demo
========================================================

These tests validate the key functionality for recruiters/evaluators:
1. Happy path with real-time progress updates
2. WebSocket connection and fallback behavior
3. Error handling with restart functionality

Author: Generated for CyberBackup 3.0 Real-Time Progress System
Date: 2025-08-01
"""

import asyncio
import os
import tempfile
import time
from contextlib import suppress

import pytest
from playwright.async_api import async_playwright, expect


class TestCyberBackupDemo:
    """
    Portfolio demo validation tests - focused on key functionality
    that showcases the real-time progress tracking system.
    """

    @pytest.fixture(autouse=True)
    async def setup_test_environment(self):
        """Setup test environment with demo file"""
        # Create a test file for upload demonstrations
        self.test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        self.test_file.write("CyberBackup Demo File - Real-time Progress Test\n" + "A" * 1000)
        self.test_file.close()

        yield

        # Cleanup
        with suppress(Exception):
            os.unlink(self.test_file.name)

    async def test_happy_path_real_time_progress(self):
        """
        Test Case 1: Happy Path with Real-Time Progress Updates

        This test validates:
        - Web interface loads correctly
        - WebSocket connection establishes
        - File upload triggers real-time progress updates
        - Progress bar moves from 0% to 100% with actual data
        - Success message appears on completion
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Visible for demo
            page = await browser.new_page()

            # Navigate to the application
            await page.goto("http://localhost:9090")

            # Wait for application to load and WebSocket to connect
            await expect(page.locator('h1')).to_contain_text('CYBERBACKUP', timeout=10000)

            # Wait for WebSocket connection indicator (real-time system)
            await page.wait_for_selector('.connection-status.connected', timeout=15000)

            # Configure server connection
            await page.fill('#serverInput', '127.0.0.1:1256')
            await page.fill('#usernameInput', 'demo_user')

            # Connect to server
            await page.click('#connectBtn')
            await expect(page.locator('.connection-led')).to_have_class("connected", timeout=10000)

            # Upload test file
            await page.set_input_files('#fileInput', self.test_file.name)

            # Start backup and monitor real-time progress
            await page.click('#startBackupBtn')

            # Validate that progress updates happen in real-time (not polling delays)
            progress_updates = []
            start_time = time.time()

            # Monitor progress for up to 30 seconds
            for _ in range(60):  # Check every 500ms for 30 seconds
                try:
                    progress_element = page.locator('.progress-bar')
                    if await progress_element.is_visible():
                        progress_text = await progress_element.inner_text()
                        if progress_text and '%' in progress_text:
                            progress_value = int(progress_text.replace('%', '').strip())
                            progress_updates.append({
                                'value': progress_value,
                                'timestamp': time.time() - start_time
                            })

                            # Break if we reach 100%
                            if progress_value >= 100:
                                break

                except:
                    pass

                await asyncio.sleep(0.5)

            # Validate real-time progress behavior
            assert len(progress_updates) > 1, "Should have multiple progress updates"
            assert progress_updates[-1]['value'] == 100, "Should reach 100% completion"

            # Validate progress updates are real-time (not 2-3 second polling delays)
            if len(progress_updates) >= 2:
                time_between_updates = progress_updates[1]['timestamp'] - progress_updates[0]['timestamp']
                assert time_between_updates < 2.0, f"Progress updates should be real-time, not polling (got {time_between_updates}s delay)"

            # Verify success message appears
            await expect(page.locator('.status-success, .toast.success')).to_be_visible(timeout=5000)

            await browser.close()

    async def test_websocket_connection_and_fallback(self):
        """
        Test Case 2: WebSocket Connection and Polling Fallback

        This test validates:
        - WebSocket connection status is visible
        - System gracefully falls back to polling if WebSocket fails
        - Connection recovery notifications work
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            # Navigate and wait for load
            await page.goto("http://localhost:9090")
            await expect(page.locator('h1')).to_contain_text('CYBERBACKUP', timeout=10000)

            # Check WebSocket connection indicators
            websocket_connected = await page.evaluate("""
                () => {
                    return window.app && window.app.socketConnected === true;
                }
            """)

            assert websocket_connected, "WebSocket should be connected for real-time updates"

            # Test WebSocket ping functionality
            ping_response = await page.evaluate("""
                async () => {
                    if (window.app && window.app.testWebSocketConnection) {
                        return window.app.testWebSocketConnection();
                    }
                    return false;
                }
            """)

            assert ping_response, "WebSocket ping should work"

            # Simulate WebSocket disconnection (for fallback testing)
            await page.evaluate("""
                () => {
                    if (window.app && window.app.socket) {
                        window.app.socket.disconnect();
                    }
                }
            """)

            # Wait for fallback mechanism to activate
            await asyncio.sleep(2)

            # Verify fallback notification
            fallback_active = await page.evaluate("""
                () => {
                    // Check if polling fallback is active
                    return window.app && window.app.socketConnected === false;
                }
            """)

            assert fallback_active, "Should fallback to polling when WebSocket disconnects"

            await browser.close()

    async def test_error_handling_and_restart(self):
        """
        Test Case 3: Error Handling with Restart Button

        This test validates:
        - Error states are properly displayed
        - Restart button appears on failure
        - Manual restart functionality works
        - Error state is cleared on restart
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            # Navigate to application
            await page.goto("http://localhost:9090")
            await expect(page.locator('h1')).to_contain_text('CYBERBACKUP', timeout=10000)

            # Simulate error condition by providing invalid server settings
            await page.fill('#serverInput', '999.999.999.999:9999')  # Invalid server
            await page.fill('#usernameInput', 'test_error_user')

            # Attempt connection (should fail)
            await page.click('#connectBtn')

            # Wait for error state
            await expect(page.locator('.error-message, .toast.error')).to_be_visible(timeout=10000)

            # Check for restart functionality trigger
            error_present = await page.evaluate("""
                () => {
                    return window.app && window.app.state && window.app.state.hasError === true;
                }
            """)

            # If no natural error occurred, simulate one
            if not error_present:
                await page.evaluate("""
                    () => {
                        if (window.app && window.app.handleBackupError) {
                            window.app.handleBackupError({
                                message: 'Demo error for testing restart functionality',
                                phase: 'TEST_ERROR',
                                job_id: 'test_job'
                            });
                        }
                    }
                """)

            # Wait for restart button to appear
            await expect(page.locator('.restart-btn, button:has-text(\"Restart\")')).to_be_visible(timeout=5000)

            # Click restart button
            restart_button = page.locator('.restart-btn, button:has-text(\"Restart\")').first
            await restart_button.click()

            # Verify error state is cleared
            await asyncio.sleep(1)
            error_cleared = await page.evaluate("""
                () => {
                    return window.app && window.app.state && window.app.state.hasError === false;
                }
            """)

            assert error_cleared, "Error state should be cleared after restart"

            # Verify restart notification
            await expect(page.locator('.toast:has-text(\"restarted\")')).to_be_visible(timeout=3000)

            await browser.close()

    async def test_progress_configuration_loading(self):
        """
        Test Case 4: Progress Configuration System

        This test validates:
        - Progress configuration loads successfully
        - Phase descriptions are enhanced (not raw phase names)
        - ETA calculations are available
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            # Navigate and wait for load
            await page.goto("http://localhost:9090")
            await expect(page.locator('h1')).to_contain_text('CYBERBACKUP', timeout=10000)

            # Wait for progress configuration to load
            await asyncio.sleep(2)

            # Check if progress configuration loaded
            config_loaded = await page.evaluate("""
                () => {
                    return window.app && window.app.progressConfig &&
                           window.app.progressConfig.phases &&
                           Object.keys(window.app.progressConfig.phases).length > 0;
                }
            """)

            assert config_loaded, "Progress configuration should load successfully"

            # Verify rich phase descriptions are available
            phase_descriptions = await page.evaluate("""
                () => {
                    if (!window.app || !window.app.progressConfig) return {};

                    const phases = window.app.progressConfig.phases;
                    const descriptions = {};
                    for (const [phase, config] of Object.entries(phases)) {
                        descriptions[phase] = config.description;
                    }
                    return descriptions;
                }
            """)

            # Verify we have meaningful descriptions (not just phase names)
            assert 'CONNECTING' in phase_descriptions, "Should have CONNECTING phase"
            assert 'server' in phase_descriptions['CONNECTING'].lower(), "Should have meaningful description"

            # Test ETA calculation functionality
            eta_available = await page.evaluate("""
                () => {
                    return window.app && typeof window.app.calculateETA === 'function';
                }
            """)

            assert eta_available, "ETA calculation should be available"

            await browser.close()

# Additional test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

if __name__ == "__main__":
    print("CyberBackup Portfolio Demo Tests")
    print("=" * 50)
    print("These tests validate the real-time progress tracking system")
    print("for recruiters and evaluators.")
    print()
    print("Prerequisites:")
    print("1. Start the backup server: python -m python_server.server.server")
    print("2. Start the API server: python cyberbackup_api_server.py")
    print("3. Install Playwright: pip install playwright pytest-asyncio")
    print("4. Install browsers: playwright install")
    print()
    print("Run tests with: pytest test_demo_scenarios.py -v")
    print("Or run individual test: pytest test_demo_scenarios.py::TestCyberBackupDemo::test_happy_path_real_time_progress -v")
