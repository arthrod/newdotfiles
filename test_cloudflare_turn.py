#!/usr/bin/env python3
"""Test Cloudflare TURN credentials setup."""

import os
from dotenv import load_dotenv
from fastrtc import get_cloudflare_turn_credentials, get_cloudflare_turn_credentials_async

# Load environment variables
load_dotenv()

def test_cloudflare_credentials():
    """Test getting Cloudflare TURN credentials."""
    
    hf_token = os.environ.get("HF_TOKEN")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    print("🔍 Environment Check:")
    if hf_token:
        print(f"✅ HF_TOKEN loaded: {hf_token[:10]}...")
    else:
        print("❌ No HF_TOKEN found")
        
    if gemini_key:
        print(f"✅ GEMINI_API_KEY loaded: {gemini_key[:10]}...")
    else:
        print("❌ No GEMINI_API_KEY found")
    
    print("\n🌐 Testing Cloudflare TURN credentials...")
    
    if not hf_token:
        print("⚠️ Cannot test Cloudflare TURN without HF_TOKEN")
        return False
    
    try:
        credentials = get_cloudflare_turn_credentials(hf_token=hf_token, ttl=360_000)
        print("✅ Cloudflare TURN credentials obtained successfully!")
        print(f"🔧 Configuration: {credentials}")
        return True
    except Exception as e:
        print(f"❌ Failed to get Cloudflare credentials: {e}")
        return False

if __name__ == "__main__":
    success = test_cloudflare_credentials()
    if success:
        print("\n🎉 Cloudflare TURN setup is working!")
    else:
        print("\n⚠️ Cloudflare TURN setup needs attention")
        print("Will fall back to basic STUN servers")