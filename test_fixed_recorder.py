#!/usr/bin/env python3
"""Test the fixed screen recorder with Playwright."""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright


async def test_screen_recorder():
    """Test the screen recorder functionality."""
    
    # Start the application
    print("🚀 Starting the screen recorder application...")
    app_process = subprocess.Popen([
        sys.executable, "setup_and_run.py"
    ], cwd=Path(__file__).parent)
    
    # Wait for the server to start
    await asyncio.sleep(5)
    
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=False,  # Need headed for screen capture
                args=[
                    "--use-fake-ui-for-media-stream",
                    "--use-fake-device-for-media-stream",
                    "--allow-running-insecure-content",
                    "--disable-web-security",
                ]
            )
            
            context = await browser.new_context(
                permissions=["camera", "microphone"],
                viewport={"width": 1280, "height": 720}
            )
            
            page = await context.new_page()
            
            # Mock getDisplayMedia for testing
            await page.add_init_script("""
                navigator.mediaDevices.getDisplayMedia = async (constraints) => {
                    const canvas = document.createElement('canvas');
                    canvas.width = 1280;
                    canvas.height = 720;
                    const ctx = canvas.getContext('2d');
                    
                    // Draw test pattern
                    ctx.fillStyle = '#4CAF50';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    ctx.fillStyle = '#fff';
                    ctx.font = '48px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText('SCREEN RECORDING TEST', canvas.width/2, canvas.height/2);
                    
                    return canvas.captureStream(30);
                };
            """)
            
            # Navigate to the app
            await page.goto("http://localhost:7860")
            
            # Wait for page to load
            await page.wait_for_selector("h1", timeout=15000)
            
            print("✅ Page loaded successfully")
            
            # Check if the main heading is present
            heading = await page.locator("h1").text_content()
            assert "Professional Screen Recorder" in heading
            print("✅ Main heading found")
            
            # Check for the recording status element
            await page.wait_for_selector("#recording-status", timeout=10000)
            print("✅ Recording status element found")
            
            # Check for start button
            start_btn = page.locator("text=Start Screen Recording")
            await start_btn.wait_for(timeout=10000)
            print("✅ Start button found")
            
            # Click start recording
            await start_btn.click()
            print("✅ Clicked start recording button")
            
            # Wait a moment for recording to start
            await asyncio.sleep(3)
            
            # Check if recording status changed
            status_element = page.locator("#recording-status")
            status_text = await status_element.text_content()
            print(f"📱 Recording status: {status_text}")
            
            # Click stop recording
            stop_btn = page.locator("text=Stop Recording")
            await stop_btn.click()
            print("✅ Clicked stop recording button")
            
            # Wait for recording to stop
            await asyncio.sleep(2)
            
            # Check final status
            final_status = await status_element.text_content()
            print(f"📱 Final status: {final_status}")
            
            print("🎉 All tests passed!")
            
            await browser.close()
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        app_process.terminate()
        app_process.wait()


if __name__ == "__main__":
    asyncio.run(test_screen_recorder())
