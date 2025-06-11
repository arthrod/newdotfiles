#!/usr/bin/env python3
"""Run the screen helper application."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from newdotfiles.screen_helper import create_app

if __name__ == "__main__":
    print("🖥️  Starting Screen Helper...")
    print("Navigate to the URL shown below to use the application.")
    print("Make sure you have a Gemini API key ready!")
    print()
    
    app = create_app()
    app.launch(
        share=False,  # Create public link for easy sharing
        debug=False,
        server_name="0.0.0.0",  # Allow external connections
        server_port=7860,
        strict_cors=False 
    )
