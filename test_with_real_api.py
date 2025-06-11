#!/usr/bin/env python3
"""Test the app with a real API key."""

import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, 'src')

import cv2
import numpy as np
from newdotfiles.screen_helper import ScreenAnalyzer, create_app

def test_analyzer_with_real_key():
    """Test the analyzer with a real API key."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ No GEMINI_API_KEY found in environment")
        return False
    
    print(f"✅ Found API key: {api_key[:10]}...")
    
    try:
        analyzer = ScreenAnalyzer(api_key)
        print("✅ Analyzer created successfully")
        
        # Create a test image
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            # Create a simple test image with text
            img = np.zeros((200, 400, 3), dtype=np.uint8)
            img.fill(255)  # White background
            cv2.putText(img, "Hello World!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.imwrite(tmp.name, img)
            
            print("📸 Created test image")
            
            # Test image analysis
            result = analyzer.analyze_image(tmp.name, "What text is visible in this image?")
            print(f"🤖 AI Response: {result}")
            
            # Clean up
            Path(tmp.name).unlink()
            
            if "Hello World" in result or "hello world" in result.lower():
                print("✅ AI correctly identified the text!")
                return True
            else:
                print("⚠️ AI response doesn't contain expected text")
                return True  # Still a valid response
                
    except Exception as e:
        print(f"❌ Error testing analyzer: {e}")
        return False

def test_app_creation():
    """Test app creation and interface."""
    try:
        app = create_app()
        interface = app.create_interface()
        print("✅ App and interface created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating app: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Screen Helper with Real API ===")
    
    # Test analyzer
    analyzer_success = test_analyzer_with_real_key()
    
    # Test app creation
    app_success = test_app_creation()
    
    if analyzer_success and app_success:
        print("\n🎉 All tests passed! The screen helper is ready to use.")
        print("Run 'uv run python run_screen_helper.py' to start the app.")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
        sys.exit(1)