#!/usr/bin/env python3
"""Manual test script for the screen helper app."""

import os
import sys
sys.path.insert(0, 'src')

from newdotfiles.screen_helper import create_app

def test_app_creation():
    """Test that the app can be created."""
    print("Creating app...")
    app = create_app()
    print(f"✓ App created: {type(app)}")
    
    print("Creating interface...")
    interface = app.create_interface()
    print(f"✓ Interface created: {type(interface)}")
    
    return app, interface

def test_app_launch(app):
    """Test launching the app (without blocking)."""
    print("Testing app launch...")
    try:
        # Launch with share=False and debug=False to avoid blocking
        result = app.launch(share=False, debug=False, server_name="127.0.0.1", server_port=7860, prevent_thread_lock=True)
        print("✓ App launched successfully")
        return True
    except Exception as e:
        print(f"✗ App launch failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Manual Screen Helper App Test ===")
    
    # Test creation
    try:
        app, interface = test_app_creation()
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        sys.exit(1)
    
    # Test launch
    try:
        launch_success = test_app_launch(app)
        if launch_success:
            print("\n✓ All tests passed!")
            print("App is running at http://127.0.0.1:7860")
            print("Press Ctrl+C to stop")
            
            # Keep running for manual testing
            try:
                input("Press Enter to stop the app...")
            except KeyboardInterrupt:
                pass
        else:
            print("\n✗ Launch test failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Launch test error: {e}")
        sys.exit(1)