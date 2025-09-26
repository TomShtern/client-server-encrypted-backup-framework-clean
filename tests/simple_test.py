#!/usr/bin/env python3
"""Simple test - no fancy output, just check if it works"""

import asyncio
import os

import httpx


async def test_simple():
    # Create test file
    with open("simple_test.txt", "w") as f:
        f.write("simple test content")

    # Test API
    async with httpx.AsyncClient() as client:
        try:
            with open("simple_test.txt", "rb") as f:
                response = await client.post('http://127.0.0.1:9090/api/start_backup',
                                       files={'file': f},
                                       data={'username': 'SimpleTest'})

            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")

            # Cleanup
            if os.path.exists("simple_test.txt"):
                os.remove("simple_test.txt")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple())
