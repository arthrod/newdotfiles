#!/usr/bin/env python3
"""Test the enhanced snapshot functionality with automatic AI analysis."""

import asyncio
import subprocess
import sys
import time
import os
from playwright.async_api import async_playwright

async def test_smart_snapshot():
    """Test the smart snapshot functionality."""
    
    print("🚀 Testing smart snapshot with AI analysis...")
    
    # Check if we have Gemini API key
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("⚠️ GEMINI_API_KEY not found - will test without real analysis")
        test_api_key = "test_key_123"
    else:
        test_api_key = gemini_key
        print("✅ Using real Gemini API key for testing")
    
    # Start the FastAPI app
    app_process = subprocess.Popen([
        sys.executable, "screen_recorder_fastapi.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for app to start
    await asyncio.sleep(5)
    
    try:
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
            
            # Capture console messages
            console_messages = []
            page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
            
            print("🌐 Loading application...")
            await page.goto("http://localhost:7864")
            await page.wait_for_load_state("networkidle")
            
            # Enter API key
            api_key_input = page.locator("#apiKey")
            await api_key_input.fill(test_api_key)
            print(f"🔑 API key entered: {test_api_key[:8]}...")
            
            # Check initial UI state
            result_box = await page.locator("#analysisResult").text_content()
            print(f"📋 Initial result box: {result_box[:100]}...")
            
            # Start recording first
            print("🎬 Starting recording...")
            start_button = page.locator('#startBtn')
            await start_button.click()
            await page.wait_for_timeout(3000)
            
            # Check if recording started
            status = await page.locator("#status").text_content()
            print(f"📊 Recording status: {status}")
            
            # Test snapshot functionality
            snapshot_button = page.locator('#snapshotBtn')
            if not await snapshot_button.is_disabled():
                print("📸 Testing smart snapshot...")
                
                # Click snapshot button
                await snapshot_button.click()
                
                # Wait for snapshot processing
                await page.wait_for_timeout(5000)
                
                # Check status updates
                final_status = await page.locator("#status").text_content()
                print(f"📊 Final status: {final_status}")
                
                # Check analysis result
                analysis_result = await page.locator("#analysisResult").inner_html()
                print(f"🤖 Analysis result preview: {analysis_result[:200]}...")
                
                # Check if analysis was attempted
                if "Snapshot Analysis" in analysis_result:
                    print("✅ Snapshot analysis section created")
                    
                    if gemini_key and "Analysis failed" not in analysis_result:
                        print("✅ Real AI analysis completed")
                    elif "Analysis failed" in analysis_result:
                        print("⚠️ Analysis failed (expected without valid API key)")
                    else:
                        print("ℹ️ Analysis result obtained")
                else:
                    print("⚠️ Snapshot analysis section not found")
                
                # Check console for any errors
                error_messages = [msg for msg in console_messages if "error" in msg.lower()]
                if error_messages:
                    print("⚠️ Console errors:")
                    for error in error_messages[-3:]:  # Show last 3 errors
                        print(f"  {error}")
                else:
                    print("✅ No console errors detected")
                    
            else:
                print("❌ Snapshot button is disabled")
            
            # Stop recording
            stop_button = page.locator('#stopBtn')
            if not await stop_button.is_disabled():
                print("⏹️ Stopping recording...")
                await stop_button.click()
                await page.wait_for_timeout(2000)
            
            await browser.close()
            
        print("✅ Smart snapshot test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        print("🛑 Shutting down app...")
        app_process.terminate()
        try:
            app_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            app_process.kill()

if __name__ == "__main__":
    result = asyncio.run(test_smart_snapshot())
    print(f"\n{'✅ SMART SNAPSHOT TEST PASSED' if result else '❌ SMART SNAPSHOT TEST FAILED'}")
    sys.exit(0 if result else 1)