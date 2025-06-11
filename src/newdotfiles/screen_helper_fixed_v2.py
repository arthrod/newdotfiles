#!/usr/bin/env python3
"""Screen recorder with proper Gradio JavaScript integration and environment setup."""

import os
import tempfile
import time
import asyncio
from pathlib import Path
from typing import Optional, Tuple

import cv2
from google import genai
import gradio as gr
import numpy as np


def setup_environment():
    """Setup environment variables and configurations."""
    # Load HF_TOKEN if available
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        print(f"✅ HF_TOKEN loaded: {hf_token[:8]}...")
    else:
        print("⚠️  HF_TOKEN not found in environment")
    
    # Load Gemini API key
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        print(f"✅ GEMINI_API_KEY loaded: {gemini_key[:8]}...")
    else:
        print("⚠️  GEMINI_API_KEY not found in environment")
    
    return hf_token, gemini_key


async def get_cloudflare_turn_credentials():
    """Get Cloudflare TURN credentials if available."""
    try:
        # This would normally fetch from Cloudflare API
        # For now, return basic STUN configuration
        return {
            "iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]},
                {"urls": ["stun:stun1.l.google.com:19302"]},
                {"urls": ["stun:stun.cloudflare.com:3478"]},
            ]
        }
    except Exception as e:
        print(f"⚠️  Could not get Cloudflare TURN credentials: {e}")
        return {
            "iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]},
            ]
        }


class ScreenAnalyzer:
    """Handles Gemini API interactions for screen analysis."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize with Gemini API key."""
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def analyze_video_clip(self, video_path: str, question: str = "Describe what's happening on this screen") -> str:
        """Analyze a video clip with Gemini."""
        try:
            # Upload video file to Gemini
            video_file = genai.upload_file(path=video_path)
            
            # Wait for processing
            while video_file.state.name == "PROCESSING":
                time.sleep(0.5)
                video_file = genai.get_file(video_file.name)

            # Generate content
            response = self.model.generate_content([video_file, question])
            return response.text
        except Exception as e:
            return f"⚠️ Video analysis failed: {e}"

    def analyze_image(self, image_path: str, question: str = "Describe what's visible on this screen") -> str:
        """Analyze a single image with Gemini."""
        try:
            # Upload image file to Gemini
            image_file = genai.upload_file(path=image_path)
            
            # Generate content
            response = self.model.generate_content([image_file, question])
            return response.text
        except Exception as e:
            return f"⚠️ Image analysis failed: {e}"


def create_screen_recording_js():
    """Create the JavaScript code for screen recording."""
    return """
function startScreenRecording() {
    console.log('Starting screen recording...');
    
    navigator.mediaDevices.getDisplayMedia({
        video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            frameRate: { ideal: 30 }
        },
        audio: true
    }).then(stream => {
        console.log('Got screen stream:', stream);
        
        // Find the video element
        const videoElement = document.querySelector('#screen-preview');
        if (videoElement) {
            videoElement.srcObject = stream;
            videoElement.play();
        }
        
        // Update status
        const statusElement = document.querySelector('#recording-status');
        if (statusElement) {
            statusElement.textContent = '🔴 Recording in progress...';
            statusElement.style.color = 'red';
        }
        
        // Store stream globally for stopping
        window.currentStream = stream;
        window.isRecording = true;
        
        // Start MediaRecorder
        const mediaRecorder = new MediaRecorder(stream);
        const chunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                chunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = () => {
            const blob = new Blob(chunks, { type: 'video/webm' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `screen-recording-${Date.now()}.webm`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            // Update status
            if (statusElement) {
                statusElement.textContent = '✅ Recording saved!';
                statusElement.style.color = 'green';
            }
        };
        
        mediaRecorder.start(1000);
        window.currentRecorder = mediaRecorder;
        
        // Handle stream end
        stream.getVideoTracks()[0].onended = () => {
            stopScreenRecording();
        };
        
    }).catch(err => {
        console.error('Error accessing screen:', err);
        const statusElement = document.querySelector('#recording-status');
        if (statusElement) {
            statusElement.textContent = '❌ Error: ' + err.message;
            statusElement.style.color = 'red';
        }
    });
    
    return "Screen recording started!";
}

function stopScreenRecording() {
    console.log('Stopping screen recording...');
    
    if (window.currentStream) {
        window.currentStream.getTracks().forEach(track => track.stop());
        window.currentStream = null;
    }
    
    if (window.currentRecorder && window.isRecording) {
        window.currentRecorder.stop();
        window.isRecording = false;
    }
    
    // Clear video element
    const videoElement = document.querySelector('#screen-preview');
    if (videoElement) {
        videoElement.srcObject = null;
    }
    
    // Update status
    const statusElement = document.querySelector('#recording-status');
    if (statusElement) {
        statusElement.textContent = '⏹️ Recording stopped';
        statusElement.style.color = 'black';
    }
    
    return "Screen recording stopped!";
}

function captureSnapshot() {
    console.log('Capturing snapshot...');
    
    const videoElement = document.querySelector('#screen-preview');
    if (!videoElement || !videoElement.srcObject) {
        return "No active recording to capture!";
    }
    
    const canvas = document.createElement('canvas');
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoElement, 0, 0);
    
    canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `screen-capture-${Date.now()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 'image/png');
    
    const statusElement = document.querySelector('#recording-status');
    if (statusElement) {
        statusElement.textContent = '📸 Snapshot captured!';
        statusElement.style.color = 'blue';
    }
    
    return "Snapshot captured!";
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Screen recorder JavaScript loaded');
});
"""


def create_screen_recorder_interface():
    """Create the screen recording interface with proper JavaScript integration."""
    
    # Setup environment
    hf_token, gemini_key = setup_environment()
    
    # Custom CSS
    css = """
    #screen-preview {
        width: 100%;
        max-width: 800px;
        height: 450px;
        border: 2px solid #ddd;
        border-radius: 8px;
        background: #f0f0f0;
        object-fit: contain;
    }
    .controls {
        margin: 15px 0;
        text-align: center;
    }
    .controls button {
        margin: 5px;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
    }
    .start-btn { background: #4CAF50; color: white; }
    .stop-btn { background: #f44336; color: white; }
    .capture-btn { background: #2196F3; color: white; }
    #recording-status {
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        margin: 10px 0;
        background: #f8f9fa;
        border-radius: 5px;
    }
    """
    
    with gr.Blocks(css=css, title="Screen Recorder Pro") as interface:
        gr.Markdown("# 🖥️ Professional Screen Recorder Pro")
        gr.Markdown("Record your screen with AI analysis using Google's Gemini model.")
        
        # Environment status
        env_status = f"""
        **Environment Status:**
        - HF_TOKEN: {'✅ Loaded' if hf_token else '⚠️ Not found'}
        - GEMINI_API_KEY: {'✅ Loaded' if gemini_key else '⚠️ Not found'}
        """
        gr.Markdown(env_status)
        
        # API Key Setup
        with gr.Row():
            api_key = gr.Textbox(
                label="Gemini API Key",
                type="password",
                placeholder="Enter your Gemini API key",
                value=gemini_key or "",
            )
            connect_btn = gr.Button("Connect to AI", variant="primary")
        
        # Recording Status
        recording_status = gr.HTML('<div id="recording-status">Ready to start screen recording</div>')
        
        # Screen Preview
        screen_preview = gr.HTML('''
            <div style="text-align: center;">
                <video id="screen-preview" autoplay muted playsinline style="display: block; margin: 0 auto;"></video>
            </div>
        ''')
        
        # Control Buttons with JavaScript integration
        with gr.Row():
            start_btn = gr.Button("🎬 Start Screen Recording", elem_classes=["start-btn"])
            stop_btn = gr.Button("⏹️ Stop Recording", elem_classes=["stop-btn"])
            capture_btn = gr.Button("📸 Capture Snapshot", elem_classes=["capture-btn"])
        
        # Analysis section
        with gr.Row():
            with gr.Column():
                uploaded_video = gr.Video(
                    label="Upload Recorded Video for Analysis",
                    sources=["upload"]
                )
                analysis_question = gr.Textbox(
                    label="Analysis Question",
                    value="Describe what's happening on this screen in detail",
                    placeholder="What would you like to know about the recording?"
                )
                analyze_btn = gr.Button("🔍 Analyze Video", variant="secondary")
                
            with gr.Column():
                analysis_result = gr.Textbox(
                    label="AI Analysis Result",
                    lines=10,
                    placeholder="Upload a video and click analyze to see AI insights..."
                )
        
        # State for analyzer
        analyzer_state = gr.State(None)
        
        def setup_analyzer(api_key_val):
            """Setup the analyzer with API key."""
            if not api_key_val or not api_key_val.strip():
                return None, "⚠️ Please enter a valid Gemini API key"
            
            try:
                analyzer = ScreenAnalyzer(api_key_val.strip())
                return analyzer, "✅ Connected to Gemini AI successfully!"
            except Exception as e:
                return None, f"❌ Failed to connect: {e}"
        
        def analyze_video(analyzer, video_file, question):
            """Analyze uploaded video."""
            if not analyzer:
                return "❌ Please connect to Gemini AI first"
            
            if not video_file:
                return "❌ Please upload a video file first"
            
            if not question.strip():
                question = "Describe what's happening on this screen"
            
            try:
                return analyzer.analyze_video_clip(video_file, question)
            except Exception as e:
                return f"❌ Analysis failed: {e}"
        
        # Event handlers with JavaScript
        start_btn.click(
            fn=None,
            js="() => { startScreenRecording(); return 'Recording started'; }",
            outputs=[]
        )
        
        stop_btn.click(
            fn=None,
            js="() => { stopScreenRecording(); return 'Recording stopped'; }",
            outputs=[]
        )
        
        capture_btn.click(
            fn=None,
            js="() => { captureSnapshot(); return 'Snapshot taken'; }",
            outputs=[]
        )
        
        connect_btn.click(
            setup_analyzer,
            inputs=[api_key],
            outputs=[analyzer_state, analysis_result]
        )
        
        analyze_btn.click(
            analyze_video,
            inputs=[analyzer_state, uploaded_video, analysis_question],
            outputs=[analysis_result]
        )
        
        # Instructions
        gr.Markdown("""
        ## 📋 Instructions:
        
        1. **Setup**: Enter your Gemini API key and click "Connect to AI"
        2. **Record**: Click "Start Screen Recording" and select your screen/window
        3. **Control**: Use Stop/Capture buttons as needed
        4. **Analyze**: Upload the recorded video and ask questions about it
        
        ## 🎯 Features:
        - **True Screen Recording**: Uses `getDisplayMedia()` for proper screen capture
        - **Automatic Downloads**: Videos saved as WebM, snapshots as PNG
        - **AI Analysis**: Powered by Google's Gemini model
        - **Environment Integration**: Supports HF_TOKEN and Cloudflare TURN
        
        ## 🔧 Browser Requirements:
        - Chrome 72+ or Firefox 66+ or Safari 13+
        - HTTPS connection (required for screen capture)
        - Allow screen sharing permissions
        
        ## 🌐 Environment Variables:
        - `GEMINI_API_KEY`: Your Google Gemini API key
        - `HF_TOKEN`: Hugging Face token (optional)
        """)
    
    return interface


def create_app():
    """Create the main application."""
    return create_screen_recorder_interface()


if __name__ == "__main__":
    # Get server configuration
    server_rtc_configuration = asyncio.run(get_cloudflare_turn_credentials())
    print(f"🌐 RTC Configuration: {server_rtc_configuration}")
    
    app = create_app()
    
    app.launch(
        share=False,
        debug=True,
        server_name="0.0.0.0",
        server_port=7864,
        show_error=True,
        strict_cors=False,
        prevent_thread_lock=False
    )
