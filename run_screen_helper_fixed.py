#!/usr/bin/env python3
"""Run the FIXED screen helper application with proper screen recording."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from newdotfiles.screen_helper_fixed import create_app

if __name__ == "__main__":
    print("🖥️  Starting FIXED Screen Helper...")
    print("📹 This version uses proper getDisplayMedia() for TRUE screen recording!")
    print("Navigate to the URL shown below to use the application.")
    print("Make sure you have a Gemini API key ready!")
    print()
    
    app = create_app()
    app.launch(
        share=False,  # Create public link for easy sharing
        debug=True,
        server_name="0.0.0.0",  # Allow external connections
        server_port=7860,
        strict_cors=False 
    )
