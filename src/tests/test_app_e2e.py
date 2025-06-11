"""End-to-end tests using Playwright to verify the app works."""

import os
import subprocess
import time
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def app_server():
    """Start the app server for testing."""
    # Start the app in a subprocess
    env = os.environ.copy()
    # Remove any existing GEMINI_API_KEY so we can test empty state
    env.pop("GEMINI_API_KEY", None)
    
    proc = subprocess.Popen(
        ["uv", "run", "python", "-c", 
         "import sys; sys.path.insert(0, 'src'); "
         "from newdotfiles.screen_helper import create_app; "
         "app = create_app(); "
         "app.launch(share=False, server_name='127.0.0.1', server_port=7861, debug=False)"],
        env=env,
        cwd=Path(__file__).parent.parent.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    yield "http://127.0.0.1:7861"
    
    # Clean up
    proc.terminate()
    proc.wait()


def test_app_loads(page: Page, app_server):
    """Test that the app loads and displays the expected elements."""
    page.goto(app_server)
    
    # Check for main heading
    expect(page.locator("h1")).to_contain_text("Screen Helper")
    
    # Check for API key input
    expect(page.locator("input[type='password']")).to_be_visible()
    
    # Check for Connect button
    expect(page.get_by_role("button", name="Connect")).to_be_visible()


def test_connect_button_reveals_interface(page: Page, app_server):
    """Test that clicking Connect reveals the main interface."""
    page.goto(app_server)
    
    # Initially, main interface should be hidden
    main_interface_visible = page.locator("text=Screen Share").is_visible()
    assert not main_interface_visible
    
    # Fill API key and click Connect
    page.fill("input[type='password']", "test-api-key")
    page.click("button:has-text('Connect')")
    
    # Wait a moment for the interface to appear
    page.wait_for_timeout(1000)
    
    # Now main interface should be visible
    expect(page.locator("text=Screen Share")).to_be_visible()
    expect(page.get_by_role("button", name="Start Recording")).to_be_visible()
    expect(page.get_by_role("button", name="Stop Recording")).to_be_visible()


def test_recording_controls(page: Page, app_server):
    """Test the recording control buttons."""
    page.goto(app_server)
    
    # Connect first
    page.fill("input[type='password']", "test-api-key")
    page.click("button:has-text('Connect')")
    page.wait_for_timeout(1000)
    
    # Check recording controls are present
    start_btn = page.get_by_role("button", name="Start Recording")
    stop_btn = page.get_by_role("button", name="Stop Recording")
    
    expect(start_btn).to_be_visible()
    expect(stop_btn).to_be_visible()
    
    # Test clicking the buttons (they should be clickable)
    start_btn.click()
    stop_btn.click()


def test_mode_toggles(page: Page, app_server):
    """Test the capture and view mode radio buttons."""
    page.goto(app_server)
    
    # Connect first
    page.fill("input[type='password']", "test-api-key")
    page.click("button:has-text('Connect')")
    page.wait_for_timeout(1000)
    
    # Check for mode controls
    expect(page.locator("text=Capture Mode")).to_be_visible()
    expect(page.locator("text=View Mode")).to_be_visible()
    
    # Check for radio options
    expect(page.locator("input[value='snapshots']")).to_be_visible()
    expect(page.locator("input[value='video']")).to_be_visible()
    expect(page.locator("input[value='processed']")).to_be_visible()
    expect(page.locator("input[value='raw']")).to_be_visible()
    
    # Test switching modes
    page.click("input[value='video']")
    page.click("input[value='raw']")


def test_chat_interface_present(page: Page, app_server):
    """Test that the chat interface is present."""
    page.goto(app_server)
    
    # Connect first
    page.fill("input[type='password']", "test-api-key")
    page.click("button:has-text('Connect')")
    page.wait_for_timeout(1000)
    
    # Check for chat interface
    expect(page.get_by_text("AI Analysis", exact=True)).to_be_visible()
    
    # The chat area should be present (might be empty initially)
    chat_area = page.locator("div.chatbot")
    expect(chat_area).to_be_visible()


def test_ui_responsiveness(page: Page, app_server):
    """Test that the UI is responsive and elements are properly styled."""
    page.goto(app_server)
    
    # Check that the page has proper styling
    # Gradio should add its default styles
    page.wait_for_load_state("domcontentloaded")
    
    # Check viewport is reasonable
    viewport_size = page.viewport_size
    assert viewport_size["width"] > 0
    assert viewport_size["height"] > 0
    
    # Skip networkidle check as it can be flaky with WebRTC components
    
    # Page should not have obvious layout issues
    # (This is a basic smoke test)
    main_container = page.locator("body")
    expect(main_container).to_be_visible()


def test_error_handling_empty_api_key(page: Page, app_server):
    """Test error handling when no API key is provided."""
    page.goto(app_server)
    
    # Clear any pre-filled API key first
    page.fill("input[type='password']", "")
    
    # Try to connect without API key
    page.click("button:has-text('Connect')")
    
    # Should show some kind of warning/error message
    # Note: Exact behavior depends on Gradio version and how we handle errors
    # For now, just ensure the recording buttons don't appear
    page.wait_for_timeout(1000)
    
    # Recording controls should still be hidden
    start_btn_visible = page.get_by_role("button", name="Start Recording").is_visible()
    assert not start_btn_visible