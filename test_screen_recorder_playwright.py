#!/usr/bin/env python3
"""Test the screen recorder with Playwright to ensure it's working."""

import asyncio
import tempfile
import time
import subprocess
import sys
from pathlib import Path

import pytest
from playwright.async_api import async_playwright


async def start_gradio_server():
    """Start the Gradio server in the background."""
    import sys
    import os
    
    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    from newdotfiles.screen_helper_fixed import create_app
    
    app = create_app()
    
    # Start server in a separate process
    process = subprocess.Popen([
        sys.executable, "-c",
        """
import sys
from pathlib import Path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
from newdotfiles.screen_helper_fixed import create_app
app = create_app()
app.launch(server_name="0.0.0.0", server_port=7860, share=False, debug=False)
"""
    ])
    
    # Wait for server to start
    await asyncio.sleep(3)
    return process


class TestScreenRecorder:
    """Test the screen recording functionality."""
    
    @pytest.mark.asyncio
    async def test_screen_recorder_interface(self):
        """Test that the screen recorder interface loads correctly."""
        # Start the Gradio server
        server_process = await start_gradio_server()
        
        try:
            async with async_playwright() as p:
                # Launch browser with screen capture permissions
                browser = await p.chromium.launch(
                    headless=False,  # Need headed mode for screen capture
                    args=[
                        "--use-fake-ui-for-media-stream",
                        "--use-fake-device-for-media-stream",
                        "--allow-running-insecure-content",
                        "--disable-web-security",
                        "--autoplay-policy=no-user-gesture-required"
                    ]
                )
                
                context = await browser.new_context(
                    permissions=["camera", "microphone"],
                    viewport={"width": 1280, "height": 720}
                )
                
                page = await context.new_page()
                
                # Navigate to the local Gradio app
                await page.goto("http://localhost:7860")
                
                # Wait for the page to load
                await page.wait_for_selector("h1", timeout=10000)
                
                # Check if main elements are present
                assert "Professional Screen Recorder" in await page.locator("h1").text_content()
                
                # Check for API key input
                api_key_input = page.locator('input[type="password"]')
                assert await api_key_input.is_visible()
                
                # Check for screen recorder HTML
                screen_recorder = page.locator("#screen-video")
                assert await screen_recorder.is_visible()
                
                # Check for start button
                start_btn = page.locator("#startBtn")
                assert await start_btn.is_visible()
                assert "Start Screen Recording" in await start_btn.text_content()
                
                await browser.close()
                
        finally:
            server_process.terminate()
            server_process.wait()
    
    @pytest.mark.asyncio
    async def test_screen_recorder_functionality(self):
        """Test screen recording functionality."""
        server_process = await start_gradio_server()
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False,
                    args=[
                        "--use-fake-ui-for-media-stream",
                        "--use-fake-device-for-media-stream",
                        "--allow-running-insecure-content",
                        "--disable-web-security",
                        "--autoplay-policy=no-user-gesture-required",
                        "--enable-features=VaapiVideoDecoder",
                        "--use-gl=desktop"
                    ]
                )
                
                context = await browser.new_context(
                    permissions=["camera", "microphone"],
                    viewport={"width": 1280, "height": 720}
                )
                
                page = await context.new_page()
                
                # Set up fake screen capture
                await page.add_init_script("""
                    // Mock getDisplayMedia for testing
                    navigator.mediaDevices.getDisplayMedia = async (constraints) => {
                        // Create a fake video stream
                        const canvas = document.createElement('canvas');
                        canvas.width = 1280;
                        canvas.height = 720;
                        const ctx = canvas.getContext('2d');
                        
                        // Draw a test pattern
                        ctx.fillStyle = '#4CAF50';
                        ctx.fillRect(0, 0, canvas.width, canvas.height);
                        ctx.fillStyle = '#fff';
                        ctx.font = '48px Arial';
                        ctx.textAlign = 'center';
                        ctx.fillText('TEST SCREEN RECORDING', canvas.width/2, canvas.height/2);
                        
                        const stream = canvas.captureStream(30);
                        
                        // Add fake ended event
                        stream.getVideoTracks()[0].onended = null;
                        
                        return stream;
                    };
                """)
                
                await page.goto("http://localhost:7860")
                
                # Wait for page to load
                await page.wait_for_selector("#startBtn", timeout=10000)
                
                # Click start recording button
                await page.click("#startBtn")
                
                # Wait for recording to start
                await page.wait_for_selector("#recordingIndicator", state="visible", timeout=5000)
                
                # Check status
                status_text = await page.locator("#status").text_content()
                assert "Recording" in status_text
                
                # Wait a bit for recording
                await asyncio.sleep(2)
                
                # Stop recording
                await page.click("#stopBtn")
                
                # Check that recording stopped
                await page.wait_for_selector("#recordingIndicator", state="hidden", timeout=5000)
                
                final_status = await page.locator("#status").text_content()
                assert "stopped" in final_status.lower()
                
                await browser.close()
                
        finally:
            server_process.terminate()
            server_process.wait()
    
    @pytest.mark.asyncio 
    async def test_gemini_integration(self):
        """Test Gemini API integration UI."""
        server_process = await start_gradio_server()
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()
                
                await page.goto("http://localhost:7860")
                
                # Wait for page to load
                await page.wait_for_selector('input[type="password"]', timeout=10000)
                
                # Enter a fake API key for testing UI
                await page.fill('input[type="password"]', "fake-api-key-for-testing")
                
                # Click connect button
                await page.click("text=Connect to AI")
                
                # Wait for response (should show error for fake key)
                await asyncio.sleep(2)
                
                # Check that some response appears
                analysis_result = page.locator('textarea[label="AI Analysis Result"]')
                await analysis_result.wait_for(timeout=5000)
                
                await browser.close()
                
        finally:
            server_process.terminate()
            server_process.wait()


if __name__ == "__main__":
    # Run a simple test manually
    async def main():
        test = TestScreenRecorder()
        print("Testing interface loading...")
        await test.test_screen_recorder_interface()
        print("✅ Interface test passed!")
        
        print("Testing recording functionality...")
        await test.test_screen_recorder_functionality()
        print("✅ Recording functionality test passed!")
        
        print("Testing Gemini integration...")
        await test.test_gemini_integration()
        print("✅ Gemini integration test passed!")
        
        print("🎉 All tests passed!")
    
    asyncio.run(main())
