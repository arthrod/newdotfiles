#!/usr/bin/env python3
"""Screen recorder with Gradio using getDisplayMedia() for proper screen capture."""

import os
import tempfile
import time
import base64
from pathlib import Path
from typing import Optional, Tuple

import cv2
import google.generativeai as genai
import gradio as gr
import numpy as np
from dotenv import load_dotenv
from fastrtc import StreamHandler, WebRTC, get_cloudflare_turn_credentials, get_cloudflare_turn_credentials_async

# Load environment variables
load_dotenv()


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


def get_cloudflare_credentials():
    """Get Cloudflare TURN credentials using HF token."""
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("⚠️ No HF_TOKEN found, using basic STUN configuration")
        return {
            "iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]},
                {"urls": ["stun:stun1.l.google.com:19302"]},
            ]
        }
    
    try:
        return get_cloudflare_turn_credentials(hf_token=hf_token, ttl=360_000)
    except Exception as e:
        print(f"⚠️ Failed to get Cloudflare credentials: {e}")
        return {
            "iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]},
                {"urls": ["stun:stun1.l.google.com:19302"]},
            ]
        }


async def get_cloudflare_credentials_async():
    """Get Cloudflare TURN credentials async."""
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        return {
            "iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]},
                {"urls": ["stun:stun1.l.google.com:19302"]},
            ]
        }
    
    try:
        return await get_cloudflare_turn_credentials_async(hf_token=hf_token)
    except Exception as e:
        print(f"⚠️ Failed to get Cloudflare credentials async: {e}")
        return {
            "iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]},
                {"urls": ["stun:stun1.l.google.com:19302"]},
            ]
        }


def create_screen_recorder_interface():
    """Create the screen recording interface using HTML/JavaScript."""
    
    # Print loaded tokens for debugging
    hf_token = os.environ.get("HF_TOKEN")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if hf_token:
        print(f"✅ HF_TOKEN loaded: {hf_token[:10]}...")
    else:
        print("⚠️ No HF_TOKEN found")
        
    if gemini_key:
        print(f"✅ GEMINI_API_KEY loaded: {gemini_key[:10]}...")
    else:
        print("⚠️ No GEMINI_API_KEY found")
    
    # Get RTC configuration
    rtc_config = get_cloudflare_credentials()
    print(f"🌐 RTC Configuration: {rtc_config}")

    # Custom CSS for better styling
    css = """
    #screen-video {
        max-width: 100%;
        height: 400px;
        border: 2px solid #ddd;
        border-radius: 8px;
        background: #f0f0f0;
    }
    .recording-indicator {
        display: none;
        color: red;
        font-weight: bold;
        animation: blink 1s linear infinite;
    }
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0; }
        100% { opacity: 1; }
    }
    .controls {
        margin: 10px 0;
    }
    .status {
        padding: 10px;
        background: #f8f9fa;
        border-radius: 4px;
        margin: 10px 0;
    }
    """

    # HTML with screen recording functionality
    html_content = """
    <div>
        <div class="status" id="status">Ready to start screen recording</div>

        <div class="controls">
            <button id="startBtn" onclick="startScreenRecording()">🎬 Start Screen Recording</button>
            <button id="stopBtn" onclick="stopRecording()" disabled>⏹️ Stop Recording</button>
            <button id="captureBtn" onclick="captureSnapshot()" disabled>📸 Capture Snapshot</button>
        </div>

        <div class="recording-indicator" id="recordingIndicator">🔴 RECORDING</div>

        <video id="screen-video" autoplay muted playsinline></video>

        <div style="margin-top: 10px;">
            <label>Recording Quality:</label>
            <select id="qualitySelect">
                <option value="1080">1080p</option>
                <option value="720" selected>720p</option>
                <option value="480">480p</option>
            </select>

            <label style="margin-left: 20px;">
                <input type="checkbox" id="audioCheckbox"> Include Audio
            </label>
        </div>
    </div>

    <script>
    let mediaRecorder = null;
    let recordedChunks = [];
    let stream = null;
    let isRecording = false;

    async function startScreenRecording() {
        try {
            const quality = document.getElementById('qualitySelect').value;
            const includeAudio = document.getElementById('audioCheckbox').checked;

            // Screen capture constraints
            const displayMediaOptions = {
                video: {
                    width: { ideal: parseInt(quality) * 16/9 },
                    height: { ideal: parseInt(quality) },
                    frameRate: { ideal: 30, max: 60 }
                },
                audio: includeAudio
            };

            // Get screen stream using getDisplayMedia
            stream = await navigator.mediaDevices.getDisplayMedia(displayMediaOptions);

            // Display the stream
            const video = document.getElementById('screen-video');
            video.srcObject = stream;

            // Update UI
            document.getElementById('status').textContent = 'Screen sharing started - ready to record';
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            document.getElementById('captureBtn').disabled = false;

            // Handle stream end (user stops sharing)
            stream.getVideoTracks()[0].onended = () => {
                stopRecording();
            };

        } catch (err) {
            console.error('Error starting screen recording:', err);
            document.getElementById('status').textContent = 'Error: ' + err.message;
        }
    }

    function startRecording() {
        if (!stream) return;

        recordedChunks = [];

        const options = {
            mimeType: 'video/webm;codecs=vp9',
            videoBitsPerSecond: 2500000
        };

        try {
            mediaRecorder = new MediaRecorder(stream, options);
        } catch (err) {
            // Fallback to default codec
            mediaRecorder = new MediaRecorder(stream);
        }

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            const blob = new Blob(recordedChunks, { type: 'video/webm' });
            downloadRecording(blob);
        };

        mediaRecorder.start(1000); // Collect data every second
        isRecording = true;

        document.getElementById('recordingIndicator').style.display = 'block';
        document.getElementById('status').textContent = '🔴 Recording in progress...';
    }

    function stopRecording() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }

        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
        }

        // Reset UI
        document.getElementById('screen-video').srcObject = null;
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('captureBtn').disabled = true;
        document.getElementById('recordingIndicator').style.display = 'none';
        document.getElementById('status').textContent = 'Recording stopped';
    }

    async function captureSnapshot() {
        if (!stream) return;

        const video = document.getElementById('screen-video');
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);

        // Convert to blob and download
        canvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `screen-capture-${Date.now()}.png`;
            a.click();
            URL.revokeObjectURL(url);
        }, 'image/png');

        document.getElementById('status').textContent = 'Snapshot captured!';
    }

    function downloadRecording(blob) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `screen-recording-${Date.now()}.webm`;
        a.click();
        URL.revokeObjectURL(url);
    }

    // Auto-start recording when screen sharing begins
    document.getElementById('startBtn').onclick = async () => {
        await startScreenRecording();
        if (stream) {
            startRecording();
        }
    };
    </script>
    """

    with gr.Blocks(css=css, title="Screen Recorder") as interface:
        gr.Markdown("# 🖥️ Professional Screen Recorder")
        gr.Markdown("Record your screen with AI analysis using Google's Gemini model.")

        # API Key Setup
        with gr.Row():
            api_key = gr.Textbox(
                label="Gemini API Key",
                type="password",
                placeholder="Enter your Gemini API key",
                value=os.environ.get("GEMINI_API_KEY", ""),
            )
            connect_btn = gr.Button("Connect to AI", variant="primary")

        # Screen recorder
        screen_recorder = gr.HTML(html_content)

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

        # Event handlers
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
        3. **Stop**: Click "Stop Recording" when done (or close the screen share dialog)
        4. **Analyze**: Upload the recorded video and ask questions about it

        ## 🎯 Features:
        - **True Screen Recording**: Uses `getDisplayMedia()` for proper screen capture
        - **Quality Options**: Choose between 480p, 720p, and 1080p
        - **Audio Support**: Option to include system/application audio
        - **Instant Snapshots**: Capture individual frames
        - **AI Analysis**: Powered by Google's Gemini model
        - **Automatic Downloads**: Videos saved as WebM, snapshots as PNG

        ## 🔧 Browser Requirements:
        - Chrome 72+ or Firefox 66+ or Safari 13+
        - HTTPS connection (required for screen capture)
        - Allow screen sharing permissions
        """)

    return interface


def create_app():
    """Create the main application."""
    return create_screen_recorder_interface()


if __name__ == "__main__":
    app = create_app()
    app.launch(
        share=False, debug=True,strict_cors=False,
        server_name="0.0.0.0",
        server_port=7860,
    )
