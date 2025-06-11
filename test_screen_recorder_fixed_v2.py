#!/usr/bin/env python3
"""Playwright test for screen_helper_fixed_v2.py with screen recording authorization."""

import asyncio
import time
import subprocess
import signal
from playwright.async_api import async_playwright

async def test_screen_recorder():
    """Test the screen recorder application with Playwright."""
    
    # Start the screen recorder app
    print("🚀 Starting screen recorder application...")
    app_process = subprocess.Popen([
        "python", "src/newdotfiles/screen_helper_fixed_v2.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for app to start
    await asyncio.sleep(5)
    
    try:
        async with async_playwright() as p:
            # Launch browser with screen share permissions
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    "--use-fake-ui-for-media-stream",
                    "--use-fake-device-for-media-stream",
                    "--allow-running-insecure-content",
                    "--disable-web-security",
                    "--auto-accept-camera-and-microphone-capture",
                    "--auto-select-desktop-capture-source=Entire screen"
                ]
            )
            
            # Create context with permissions
            context = await browser.new_context(
                permissions=["camera", "microphone"],
                viewport={"width": 1280, "height": 720}
            )
            
            page = await context.new_page()
            
            print("🌐 Navigating to application...")
            await page.goto("http://localhost:7864")
            
            # Wait for page to load
            await page.wait_for_timeout(3000)
            
            print("✅ Application loaded successfully!")
            
            # Check if the main elements are present
            title = await page.locator("h1").text_content()
            print(f"📋 Page title: {title}")
            
            # Look for the start recording button
            start_button = page.locator('button:has-text("Start Screen Recording")')
            if await start_button.count() > 0:
                print("🎬 Found Start Screen Recording button")
                
                # Click the start recording button
                print("🔴 Clicking Start Recording...")
                await start_button.click()
                
                # Wait a moment for the recording to potentially start
                await page.wait_for_timeout(2000)
                
                # Check recording status
                status_element = page.locator("#recording-status")
                if await status_element.count() > 0:
                    status_text = await status_element.text_content()
                    print(f"📊 Recording status: {status_text}")
                
                # Look for stop button and click it
                stop_button = page.locator('button:has-text("Stop Recording")')
                if await stop_button.count() > 0:
                    print("⏹️ Clicking Stop Recording...")
                    await stop_button.click()
                    await page.wait_for_timeout(1000)
                    
                    # Check final status
                    if await status_element.count() > 0:
                        final_status = await status_element.text_content()
                        print(f"🏁 Final status: {final_status}")
            
            # Test snapshot functionality
            snapshot_button = page.locator('button:has-text("Capture Snapshot")')
            if await snapshot_button.count() > 0:
                print("📸 Testing snapshot functionality...")
                await snapshot_button.click()
                await page.wait_for_timeout(1000)
            
            print("✅ Test completed successfully!")
            
            await browser.close()
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        # Clean up: terminate the app process
        print("🛑 Shutting down application...")
        app_process.terminate()
        try:
            app_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            app_process.kill()
        
        print("✅ Test cleanup completed")

if __name__ == "__main__":
    asyncio.run(test_screen_recorder())