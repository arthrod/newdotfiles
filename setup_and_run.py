#!/usr/bin/env python3
"""Setup environment variables and test the screen recorder."""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup environment variables for the screen recorder."""
    
    print("🔧 Setting up environment for Screen Recorder...")
    
    # Check for existing environment variables
    gemini_key = os.environ.get("GEMINI_API_KEY")
    hf_token = os.environ.get("HF_TOKEN")
    
    # If not found, try to load from .env file
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"📝 Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value.strip('"').strip("'")
    
    # Check again after loading .env
    gemini_key = os.environ.get("GEMINI_API_KEY")
    hf_token = os.environ.get("HF_TOKEN")
    
    print(f"✅ GEMINI_API_KEY: {'Found' if gemini_key else 'Not found'}")
    print(f"✅ HF_TOKEN: {'Found' if hf_token else 'Not found'}")
    
    if not gemini_key:
        print("\n⚠️  GEMINI_API_KEY not found!")
        print("Please either:")
        print("1. Set environment variable: export GEMINI_API_KEY='your-key-here'")
        print("2. Create a .env file with: GEMINI_API_KEY=your-key-here")
        print("3. Enter it manually in the web interface")
    
    # Create example .env file if it doesn't exist
    if not env_file.exists():
        print(f"\n📝 Creating example .env file at {env_file}")
        with open(env_file, "w") as f:
            f.write("""# Environment variables for Screen Recorder
# Get your Gemini API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: Hugging Face token for advanced features
# HF_TOKEN=your-hf-token-here
""")
        print("✅ Please edit the .env file with your actual API keys")

if __name__ == "__main__":
    setup_environment()
    
    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from newdotfiles.screen_helper_fixed_v2 import create_app
        
        print("\n🚀 Starting Screen Recorder Pro...")
        print("Navigate to http://localhost:7860 to use the application")
        print()
        
        app = create_app()
        app.launch(
            share=False,
            debug=True,
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True
        )
        
    except ImportError:
        print("❌ Could not import the screen recorder module")
        print("Please make sure the fixed version is saved as:")
        print("src/newdotfiles/screen_helper_fixed_v2.py")
