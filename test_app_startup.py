#!/usr/bin/env python3
"""Simple test to verify the screen helper app starts without AttributeError."""

import subprocess
import time
import signal
import requests
import sys

def test_app_startup():
    """Test that the app starts without the AttributeError."""
    
    print("🚀 Testing screen_helper_fixed_v2.py startup...")
    
    # Start the app
    process = subprocess.Popen([
        sys.executable, "src/newdotfiles/screen_helper_fixed_v2.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Wait for app to start
    print("⏳ Waiting for app to start...")
    time.sleep(8)
    
    # Check if process is still running (no crash)
    if process.poll() is None:
        print("✅ App is running (no immediate crash)")
        
        # Try to access the web interface
        try:
            response = requests.get("http://localhost:7864", timeout=5)
            if response.status_code == 200:
                print("🌐 Web interface is accessible")
                print("✅ No AttributeError occurred - fix successful!")
                result = True
            else:
                print(f"⚠️ Web interface returned status {response.status_code}")
                result = False
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Could not access web interface: {e}")
            result = False
            
    else:
        # Process crashed - check error output
        stdout, stderr = process.communicate()
        print("❌ App crashed on startup")
        print("STDERR:", stderr)
        if "AttributeError: 'NoneType' object has no attribute 'wait'" in stderr:
            print("💥 AttributeError still present!")
        result = False
    
    # Clean up
    if process.poll() is None:
        print("🛑 Terminating app...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    return result

if __name__ == "__main__":
    success = test_app_startup()
    print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")
    sys.exit(0 if success else 1)