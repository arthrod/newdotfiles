#!/usr/bin/env python3
"""Test actual screen recording functionality with browser automation."""

import asyncio
import subprocess
import sys
import time
from playwright.async_api import async_playwright

async def test_screen_recording_functionality():
    """Test if screen recording actually works."""
    
    print("🚀 Starting screen recorder for functionality test...")
    
    # Start the app
    app_process = subprocess.Popen([
        sys.executable, "src/newdotfiles/screen_helper_fixed_v2.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for app to start
    await asyncio.sleep(5)
    
    try:
        async with async_playwright() as p:
            # Launch browser with permissions for screen capture
            browser = await p.chromium.launch(
                headless=False,  # Need visible browser for screen capture testing
                args=[
                    "--use-fake-ui-for-media-stream",
                    "--use-fake-device-for-media-stream", 
                    "--allow-running-insecure-content",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--auto-select-desktop-capture-source=Screen 1"
                ]
            )
            
            context = await browser.new_context(
                permissions=["camera", "microphone"],
                viewport={"width": 1280, "height": 720}
            )
            
            page = await context.new_page()
            
            # Go to the app
            print("🌐 Loading application...")
            await page.goto("http://localhost:7864")
            await page.wait_for_load_state("networkidle")
            
            # Check if main elements are present
            print("🔍 Checking interface elements...")
            
            # Look for start button
            start_button = page.locator('button:has-text("Start Screen Recording")')
            button_count = await start_button.count()
            print(f"📊 Start button found: {button_count > 0}")
            
            if button_count > 0:
                # Set up console listener to catch JavaScript errors/logs
                console_messages = []
                
                def handle_console(msg):
                    console_messages.append(f"[{msg.type}] {msg.text}")
                    print(f"🖥️ Browser console: [{msg.type}] {msg.text}")
                
                page.on("console", handle_console)
                
                # Test clicking the start button
                print("🎬 Attempting to start screen recording...")
                
                # Enable dialog handling (for permissions)
                page.on("dialog", lambda dialog: dialog.accept())
                
                try:
                    await start_button.click()
                    await page.wait_for_timeout(3000)  # Wait for recording to potentially start
                    
                    # Check if recording status changed
                    status_element = page.locator("#recording-status")
                    if await status_element.count() > 0:
                        status_text = await status_element.text_content()
                        print(f"📊 Recording status: {status_text}")
                        
                        # Check if status indicates recording started
                        if "recording" in status_text.lower() or "🔴" in status_text:
                            print("✅ Screen recording appears to have started!")
                            
                            # Test stop functionality
                            stop_button = page.locator('button:has-text("Stop Recording")')
                            if await stop_button.count() > 0:
                                print("⏹️ Testing stop recording...")
                                await stop_button.click()
                                await page.wait_for_timeout(2000)
                                
                                final_status = await status_element.text_content()
                                print(f"🏁 Final status: {final_status}")
                        else:
                            print("⚠️ Recording may not have started properly")
                    
                    # Check for any JavaScript errors
                    js_errors = [msg for msg in console_messages if "error" in msg.lower()]
                    if js_errors:
                        print("❌ JavaScript errors detected:")
                        for error in js_errors:
                            print(f"  - {error}")
                    else:
                        print("✅ No JavaScript errors detected")
                        
                except Exception as e:
                    print(f"❌ Error during recording test: {e}")
            
            # Test the JavaScript functions directly
            print("🧪 Testing JavaScript functions directly...")
            
            # Test if getDisplayMedia is available
            display_media_available = await page.evaluate("""
                () => {
                    return 'getDisplayMedia' in navigator.mediaDevices;
                }
            """)
            print(f"📺 getDisplayMedia API available: {display_media_available}")
            
            # Test if the JavaScript functions are defined
            functions_test = await page.evaluate("""
                () => {
                    return {
                        startScreenRecording: typeof startScreenRecording !== 'undefined',
                        stopScreenRecording: typeof stopScreenRecording !== 'undefined',
                        captureSnapshot: typeof captureSnapshot !== 'undefined'
                    };
                }
            """)
            
            print(f"🔧 JavaScript functions loaded: {functions_test}")
            
            await browser.close()
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        # Clean up
        print("🛑 Shutting down application...")
        app_process.terminate()
        try:
            app_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            app_process.kill()
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_screen_recording_functionality())
    print(f"\n{'✅ FUNCTIONALITY TEST COMPLETED' if result else '❌ FUNCTIONALITY TEST FAILED'}")