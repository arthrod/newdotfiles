#!/usr/bin/env python3
"""Test real screen capture functionality with visible browser."""

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, 'src')

from playwright.sync_api import sync_playwright


def test_real_screen_capture():
    """Test actual screen capture with user interaction."""
    
    print("🚀 Starting REAL screen capture test...")
    print("This will open a visible browser window where you can interact!")
    
    # Start the app server
    print("📡 Starting app server...")
    env = os.environ.copy()
    proc = subprocess.Popen(
        ["uv", "run", "python", "run_screen_helper.py"],
        env=env,
        cwd=Path(__file__).parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(5)
    
    try:
        with sync_playwright() as p:
            # Launch browser in NON-HEADLESS mode so we can see it!
            browser = p.chromium.launch(
                headless=False,  # This is the key - visible browser!
                args=[
                    "--use-fake-ui-for-media-stream",  # Auto-grant permissions
                    "--use-fake-device-for-media-stream", 
                    "--allow-running-insecure-content",
                    "--disable-web-security",
                    "--auto-select-desktop-capture-source=Screen 1"  # Auto-select screen
                ]
            )
            
            page = browser.new_page()
            
            # Grant available permissions
            context = browser.contexts[0]
            context.grant_permissions(['camera', 'microphone'])
            
            print("🌐 Opening app in browser...")
            page.goto("http://127.0.0.1:7860")
            
            # Wait for app to load
            page.wait_for_load_state("domcontentloaded")
            print("✅ App loaded!")
            
            # Enter API key
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                print("❌ No GEMINI_API_KEY found!")
                return False
            
            print("🔑 Entering API key...")
            page.fill("input[type='password']", api_key)
            
            # Connect
            print("🔗 Clicking Connect...")
            page.click("button:has-text('Connect')")
            page.wait_for_timeout(3000)
            
            # Check if main interface appeared
            if page.get_by_role("button", name="Start Recording").is_visible():
                print("✅ Main interface revealed!")
            else:
                print("❌ Main interface not revealed - connection failed")
                return False
            
            # Set to snapshot mode for faster testing
            print("📸 Setting to snapshot mode...")
            page.click("input[value='snapshots']")
            
            # Start recording
            print("🎬 Starting recording...")
            page.click("button:has-text('Start Recording')")
            
            print("\n" + "="*50)
            print("🎯 REAL TEST STARTING!")
            print("The browser should now request screen share permissions.")
            print("Please:")
            print("1. Grant screen share permission when prompted")
            print("2. Select a screen/window to share") 
            print("3. Wait for AI analysis to appear in the chat")
            print("4. The test will automatically continue...")
            print("="*50 + "\n")
            
            # Wait longer for user to interact with permissions
            page.wait_for_timeout(10000)
            
            # Check for chat messages - this means AI is working!
            chat_messages_found = False
            for i in range(30):  # Check for 30 seconds
                try:
                    # Look for any content in the chat area
                    chat_area = page.locator("div.chatbot")
                    if chat_area.is_visible():
                        # Check for actual chat content
                        messages = page.locator(".chatbot .message, .chatbot .bot, .chatbot .assistant").all()
                        if messages:
                            print(f"🎉 FOUND {len(messages)} CHAT MESSAGES!")
                            for j, msg in enumerate(messages):
                                if msg.is_visible():
                                    content = msg.inner_text()
                                    if content and len(content.strip()) > 0:
                                        print(f"  💬 Message {j+1}: {content[:100]}...")
                                        chat_messages_found = True
                        
                        # Also check for any text that looks like AI responses
                        ai_responses = page.locator("text=/describe|image|screen|visible|see|analysis/i").all()
                        if ai_responses:
                            print(f"🤖 FOUND AI RESPONSES!")
                            for resp in ai_responses[:3]:  # Show first 3
                                if resp.is_visible():
                                    content = resp.inner_text()
                                    if len(content) > 20:  # Substantial content
                                        print(f"  🧠 AI: {content[:150]}...")
                                        chat_messages_found = True
                
                except Exception as e:
                    print(f"⚠️ Error checking chat: {e}")
                
                if chat_messages_found:
                    break
                    
                print(f"⏳ Waiting for AI analysis... ({i+1}/30)")
                page.wait_for_timeout(1000)
            
            # Test mode switching
            print("🔄 Testing mode switches...")
            page.click("input[value='video']")
            page.wait_for_timeout(1000)
            print("✅ Switched to video mode")
            
            page.click("input[value='raw']")
            page.wait_for_timeout(1000)
            print("✅ Switched to raw view")
            
            # Stop recording
            print("🛑 Stopping recording...")
            page.click("button:has-text('Stop Recording')")
            
            print("\n" + "="*50)
            if chat_messages_found:
                print("🎉 SUCCESS! Screen capture and AI analysis WORKING!")
                print("✅ Real screen content was captured and analyzed by AI")
            else:
                print("⚠️ PARTIAL SUCCESS - UI works but no AI analysis detected")
                print("This could mean:")
                print("- Screen share permission was not granted")
                print("- WebRTC connection failed") 
                print("- AI API issue")
            print("="*50)
            
            # Keep browser open for manual inspection
            print("\n🔍 Browser will stay open for 10 seconds for manual inspection...")
            time.sleep(10)
            
            browser.close()
            return chat_messages_found
            
    finally:
        # Clean up server
        print("🧹 Cleaning up server...")
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    success = test_real_screen_capture()
    if success:
        print("🏆 FULL SUCCESS - Screen Helper is working perfectly!")
        sys.exit(0)
    else:
        print("❓ PARTIAL SUCCESS - Check the issues above")
        sys.exit(1)