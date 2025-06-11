#!/usr/bin/env python3
"""Debug UI behavior."""

import sys
from pathlib import Path

sys.path.insert(0, 'src')

from playwright.sync_api import sync_playwright

def debug_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Go to the app
        page.goto("http://127.0.0.1:7861")
        
        print("=== Initial state ===")
        print(f"Connect button visible: {page.get_by_role('button', name='Connect').is_visible()}")
        print(f"Start Recording visible: {page.get_by_role('button', name='Start Recording').is_visible()}")
        print(f"API key input visible: {page.locator('input[type=\"password\"]').is_visible()}")
        
        # Click Connect without API key
        page.click("button:has-text('Connect')")
        page.wait_for_timeout(2000)
        
        print("\n=== After clicking Connect (no API key) ===")
        print(f"Connect button visible: {page.get_by_role('button', name='Connect').is_visible()}")
        print(f"Start Recording visible: {page.get_by_role('button', name='Start Recording').is_visible()}")
        print(f"API key input visible: {page.locator('input[type=\"password\"]').is_visible()}")
        
        # Fill API key and connect
        page.fill("input[type='password']", "test-api-key")
        page.click("button:has-text('Connect')")
        page.wait_for_timeout(2000)
        
        print("\n=== After connecting with API key ===")
        print(f"Connect button visible: {page.get_by_role('button', name='Connect').is_visible()}")
        print(f"Start Recording visible: {page.get_by_role('button', name='Start Recording').is_visible()}")
        print(f"API key input visible: {page.locator('input[type=\"password\"]').is_visible()}")
        
        input("Press Enter to close browser...")
        browser.close()

if __name__ == "__main__":
    debug_ui()