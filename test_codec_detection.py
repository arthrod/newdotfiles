#!/usr/bin/env python3
"""Test codec detection and compatibility."""

import asyncio
import subprocess
import sys
import time
from playwright.async_api import async_playwright

async def test_codec_detection():
    """Test codec detection functionality."""
    
    print("🚀 Testing codec detection...")
    
    # Start the FastAPI app
    app_process = subprocess.Popen([
        sys.executable, "screen_recorder_fastapi.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for app to start
    await asyncio.sleep(5)
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Capture console messages
            console_messages = []
            page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
            
            print("🌐 Loading application...")
            await page.goto("http://localhost:7864")
            await page.wait_for_load_state("networkidle")
            
            # Wait for codec detection
            await page.wait_for_timeout(2000)
            
            # Check initial status
            status = await page.locator("#status").text_content()
            print(f"📊 Initial status: {status}")
            
            # Look for codec-related console messages
            codec_messages = [msg for msg in console_messages if "codec" in msg.lower() or "supported" in msg.lower()]
            if codec_messages:
                print("🔧 Codec detection messages:")
                for msg in codec_messages:
                    print(f"  {msg}")
            
            # Test codec support directly
            codec_test = await page.evaluate("""
                () => {
                    const codecs = [
                        'video/webm; codecs=vp9',
                        'video/webm; codecs=vp8,opus',
                        'video/webm; codecs=vp8',
                        'video/webm',
                        'video/mp4; codecs=h264',
                        'video/mp4'
                    ];
                    
                    return codecs.map(codec => ({
                        codec: codec,
                        supported: MediaRecorder.isTypeSupported(codec)
                    }));
                }
            """)
            
            print("\n🧪 Codec support test:")
            for test in codec_test:
                support_icon = "✅" if test["supported"] else "❌"
                print(f"  {support_icon} {test['codec']}")
            
            # Test actual recording with codec fallback
            start_button = page.locator('#startBtn')
            if await start_button.count() > 0:
                print("\n🎬 Testing recording with automatic codec selection...")
                await start_button.click()
                await page.wait_for_timeout(3000)
                
                # Check for codec selection message
                new_messages = [msg for msg in console_messages if "using codec" in msg.lower()]
                if new_messages:
                    print("🎯 Codec selection:")
                    for msg in new_messages:
                        print(f"  {msg}")
                
                # Stop recording
                stop_button = page.locator('#stopBtn')
                if not await stop_button.is_disabled():
                    await stop_button.click()
                    await page.wait_for_timeout(2000)
            
            await browser.close()
            
        print("✅ Codec detection test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
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
    result = asyncio.run(test_codec_detection())
    sys.exit(0 if result else 1)