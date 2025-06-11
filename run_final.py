#!/usr/bin/env python3
"""Final setup script that avoids all Gradio JavaScript integration issues."""

import os
import sys
import webbrowser
from pathlib import Path


def load_environment():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent / ".env"
    
    if env_file.exists():
        print(f"📝 Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    try:
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value.strip('"').strip("'")
                    except ValueError:
                        continue
    else:
        print(f"📝 Creating .env file at {env_file}")
        with open(env_file, "w") as f:
            f.write("""# Environment variables for Screen Helper
# Get your Gemini API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: Hugging Face token for advanced features
# HF_TOKEN=your-hf-token-here
""")
        print("✅ Please edit the .env file with your actual API keys")


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'gradio',
        'google-generativeai',
        'opencv-python'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print(f"\nInstall them with: pip install {' '.join(missing_packages)}")
        return False
    
    return True


def main():
    """Main setup and launcher."""
    print("🚀 Screen Helper - Final Setup")
    print("=" * 50)
    
    # Load environment
    load_environment()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment variables
    gemini_key = os.environ.get("GEMINI_API_KEY")
    hf_token = os.environ.get("HF_TOKEN")
    
    print(f"\n🔧 Environment Status:")
    print(f"   GEMINI_API_KEY: {'✅ Loaded' if gemini_key and gemini_key != 'your-gemini-api-key-here' else '❌ Not configured'}")
    print(f"   HF_TOKEN: {'✅ Loaded' if hf_token else '⚠️ Not found (optional)'}")
    
    # Show instructions
    print(f"\n📋 How to Use:")
    print(f"   1. 🎬 Screen Recording: Open screen_recorder.html in your browser")
    print(f"   2. 🤖 AI Analysis: Run python ai_analyzer.py")
    print(f"   3. 🔄 Both Together: This script will start both for you")
    
    # Ask user what they want to do
    print(f"\n🎯 What would you like to do?")
    print(f"   1. Open HTML screen recorder only")
    print(f"   2. Start AI analyzer only") 
    print(f"   3. Open both (recommended)")
    print(f"   4. Exit")
    
    try:
        choice = input(f"\nEnter your choice (1-4): ").strip()
        
        html_file = Path(__file__).parent / "screen_recorder.html"
        
        if choice == "1":
            print(f"🎬 Opening screen recorder...")
            webbrowser.open(f"file://{html_file.absolute()}")
            
        elif choice == "2":
            print(f"🤖 Starting AI analyzer...")
            os.system(f"{sys.executable} ai_analyzer.py")
            
        elif choice == "3":
            print(f"🎬 Opening screen recorder...")
            webbrowser.open(f"file://{html_file.absolute()}")
            
            print(f"🤖 Starting AI analyzer...")
            print(f"   • Screen recorder: file://{html_file.absolute()}")
            print(f"   • AI analyzer: http://localhost:7860")
            print(f"   • Record your screen, then upload to the analyzer!")
            
            os.system(f"{sys.executable} ai_analyzer.py")
            
        elif choice == "4":
            print(f"👋 Goodbye!")
            
        else:
            print(f"❌ Invalid choice")
            
    except KeyboardInterrupt:
        print(f"\n👋 Goodbye!")


if __name__ == "__main__":
    main()
