#!/usr/bin/env python3
"""Test the FastAPI screen recorder implementation."""

import asyncio
import subprocess
import sys
import time
from playwright.async_api import async_playwright
from security import safe_requests

async def test_fastapi_screen_recorder():
    """Test the FastAPI-based screen recorder."""
    
    print("🚀 Starting FastAPI screen recorder...")
    
    # Start the FastAPI app
    app_process = subprocess.Popen([
        sys.executable, "screen_recorder_fastapi.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for app to start
    await asyncio.sleep(5)
    
    try:
        # Test if the app is running
        response = safe_requests.get("http://localhost:7864/health", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI app is running")
            print(f"📊 Health check: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
        # Test the main page
        main_response = safe_requests.get("http://localhost:7864/", timeout=5)
        if main_response.status_code == 200:
            print("✅ Main page loads successfully")
            
            # Check if the HTML contains key elements
            html_content = main_response.text
            key_elements = [
                "Screen Recorder Pro",
                "startRecording()",
                "stopRecording()",
                "captureSnapshot()",
                "getDisplayMedia"
            ]
            
            missing_elements = [elem for elem in key_elements if elem not in html_content]
            if missing_elements:
                print(f"⚠️ Missing elements: {missing_elements}")
            else:
                print("✅ All key elements present in HTML")
        else:
            print(f"❌ Main page failed to load: {main_response.status_code}")
            return False
        
        # Test with browser automation
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    "--use-fake-ui-for-media-stream",
                    "--use-fake-device-for-media-stream",
                    "--allow-running-insecure-content",
                    "--disable-web-security",
                    "--auto-select-desktop-capture-source=Screen 1"
                ]
            )
            
            context = await browser.new_context(
                permissions=["camera", "microphone"],
                viewport={"width": 1280, "height": 720}
            )
            
            page = await context.new_page()
            
            print("🌐 Testing browser interface...")
            await page.goto("http://localhost:7864")
            await page.wait_for_load_state("networkidle")
            
            # Check if main elements are visible
            title = await page.locator("h1").text_content()
            print(f"📋 Page title: {title}")
            
            # Test if JavaScript functions are available
            js_test = await page.evaluate("""
                () => {
                    return {
                        startRecording: typeof startRecording === 'function',
                        stopRecording: typeof stopRecording === 'function',
                        captureSnapshot: typeof captureSnapshot === 'function',
                        getDisplayMedia: 'getDisplayMedia' in navigator.mediaDevices
                    };
                }
            """)
            
            print(f"🔧 JavaScript functions: {js_test}")
            
            # Test clicking the start button
            start_button = page.locator('#startBtn')
            if await start_button.count() > 0:
                print("🎬 Testing start recording button...")
                
                # Set up console logging
                page.on("console", lambda msg: print(f"🖥️ Console: [{msg.type}] {msg.text}"))
                
                # Click start button
                await start_button.click()
                await page.wait_for_timeout(3000)
                
                # Check status
                status = await page.locator("#status").text_content()
                print(f"📊 Recording status: {status}")
                
                # Test stop button
                stop_button = page.locator('#stopBtn')
                if not await stop_button.is_disabled():
                    print("⏹️ Testing stop recording...")
                    await stop_button.click()
                    await page.wait_for_timeout(2000)
                    
                    final_status = await page.locator("#status").text_content()
                    print(f"🏁 Final status: {final_status}")
            
            await browser.close()
            
        print("✅ FastAPI screen recorder test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Clean up
        print("🛑 Shutting down FastAPI app...")
        app_process.terminate()
        try:
            app_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            app_process.kill()

if __name__ == "__main__":
    result = asyncio.run(test_fastapi_screen_recorder())
    print(f"\n{'✅ TEST PASSED' if result else '❌ TEST FAILED'}")
    sys.exit(0 if result else 1)
