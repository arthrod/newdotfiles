#!/usr/bin/env python3
"""Working screen helper with Cloudflare TURN and proper error handling."""

import os
import tempfile
import time
from pathlib import Path

import cv2
from google import genai
import gradio as gr
import numpy as np
from dotenv import load_dotenv
from fastrtc import StreamHandler, WebRTC, get_cloudflare_turn_credentials

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


class ScreenStreamHandler(StreamHandler):
    """Handles real-time screen streaming and analysis."""

    def __init__(self, analyzer: ScreenAnalyzer | None = None):
        """Initialize handler with screen analyzer."""
        super().__init__()
        self.analyzer = analyzer
        self.buffer: list[np.ndarray] = []
        self.last_chunk_time = time.time()
        self.prev_response = ""
        self.recording = False

    def copy(self):
        """Create a copy for new users."""
        return ScreenStreamHandler(self.analyzer)

    def receive(self, frame: np.ndarray):
        """Process incoming video frames."""
        if not self.recording or not self.analyzer:
            self.buffer.clear()
            return

        self.buffer.append(frame)

        # Process every 3 seconds (longer interval for stability)
        now = time.time()
        if now - self.last_chunk_time < 3.0:
            return

        self.last_chunk_time = now
        frames_to_process = self.buffer.copy()
        self.buffer.clear()

        if not frames_to_process:
            return

        # Get latest UI state from args
        if hasattr(self, "latest_args") and self.latest_args and len(self.latest_args) >= 3:
            try:
                raw_messages = self.latest_args[1]
                processed_messages = self.latest_args[2]

                # Analyze the latest frame
                response = self._analyze_snapshot(frames_to_process[-1])

                # Update raw messages
                raw_messages.append({"role": "assistant", "content": response})

                # Simple deduplication - only add if different from previous
                if response != self.prev_response:
                    processed_messages.append({"role": "assistant", "content": response})
                    self.prev_response = response

            except Exception as e:
                print(f"Error in frame processing: {e}")

    def _analyze_snapshot(self, frame: np.ndarray) -> str:
        """Analyze a single frame as snapshot."""
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                # Convert RGB to BGR for OpenCV
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                cv2.imwrite(tmp.name, bgr_frame)

                result = self.analyzer.analyze_image(tmp.name)
                Path(tmp.name).unlink()  # Clean up
                return result
        except Exception as e:
            return f"⚠️ Analysis failed: {e}"

    def emit(self):
        """Return current frame for display."""
        if self.buffer:
            return self.buffer[-1]
        return None

    def start_recording(self):
        """Start recording frames."""
        self.recording = True
        self.last_chunk_time = time.time()

    def stop_recording(self):
        """Stop recording frames."""
        self.recording = False
        self.buffer.clear()


def get_rtc_configuration():
    """Get RTC configuration with Cloudflare TURN."""
    hf_token = os.environ.get("HF_TOKEN")
    
    if hf_token:
        try:
            config = get_cloudflare_turn_credentials(hf_token=hf_token, ttl=360_000)
            print(f"✅ Using Cloudflare TURN: {len(config.get('iceServers', []))} servers")
            return config
        except Exception as e:
            print(f"⚠️ Cloudflare TURN failed: {e}")
    
    # Fallback to basic STUN
    print("🔄 Using basic STUN servers")
    return {
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
        ]
    }


def create_app():
    """Create the working screen helper app."""
    
    # Print environment status
    hf_token = os.environ.get("HF_TOKEN")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    print("🔍 Environment Check:")
    print(f"  HF_TOKEN: {'✅' if hf_token else '❌'}")
    print(f"  GEMINI_API_KEY: {'✅' if gemini_key else '❌'}")
    
    # Get RTC configuration
    rtc_config = get_rtc_configuration()
    
    css = """
    .chatbot {height: 300px; overflow: auto;}
    #webrtc-video {max-width: 600px; height: 400px;}
    .status {padding: 10px; background: #f0f0f0; border-radius: 5px; margin: 10px 0;}
    """

    with gr.Blocks(css=css, title="Screen Helper", theme=gr.themes.Soft()) as app:
        # Global state
        analyzer_state = gr.State(None)
        handler_state = gr.State(None)
        raw_messages = gr.State(list)
        processed_messages = gr.State(list)
        recording_state = gr.State(False)

        gr.Markdown("# 🖥️ Working Screen Helper")
        gr.Markdown("Real-time screen analysis with Google Gemini and Cloudflare TURN")

        # Connection section
        with gr.Row():
            api_key = gr.Textbox(
                label="Gemini API Key",
                type="password",
                value=gemini_key or "",
                placeholder="Enter your Gemini API key"
            )
            connect_btn = gr.Button("Connect", variant="primary")

        status_text = gr.Markdown("**Status:** Ready to connect")

        # Main interface (hidden initially)  
        with gr.Group(visible=False) as main_interface:
            with gr.Row():
                with gr.Column():
                    # WebRTC component
                    webrtc = WebRTC(
                        label="Screen Share",
                        mode="send-receive", 
                        modality="video",
                        rtc_configuration=rtc_config,
                        elem_id="webrtc-video"
                    )
                    
                    with gr.Row():
                        start_btn = gr.Button("Start Recording", variant="primary")
                        stop_btn = gr.Button("Stop Recording", variant="stop")

                with gr.Column():
                    view_mode = gr.Radio(
                        ["processed", "raw"],
                        label="View Mode",
                        value="processed"
                    )
                    
                    chat = gr.Chatbot(
                        label="AI Analysis",
                        type="messages",
                        elem_classes=["chatbot"]
                    )

        # Event handlers
        def setup_connection(api_key_val):
            """Setup analyzer and handler."""
            if not api_key_val:
                return None, None, "❌ Please enter an API key", gr.update(visible=False)
            
            try:
                analyzer = ScreenAnalyzer(api_key_val)
                handler = ScreenStreamHandler(analyzer)
                return (
                    analyzer, 
                    handler, 
                    "✅ Connected to Gemini AI successfully!",
                    gr.update(visible=True)
                )
            except Exception as e:
                return None, None, f"❌ Connection failed: {e}", gr.update(visible=False)

        def start_recording(handler):
            """Start recording."""
            if handler:
                handler.start_recording()
                return True, "🔴 Recording started"
            return False, "❌ Not connected"

        def stop_recording(handler):
            """Stop recording."""
            if handler:
                handler.stop_recording()
                return False, "⏹️ Recording stopped"
            return False, "❌ Not connected"

        def update_chat(raw_msgs, processed_msgs, view):
            """Update chat display."""
            return processed_msgs if view == "processed" else raw_msgs

        # Wire up events
        connect_btn.click(
            setup_connection,
            inputs=[api_key],
            outputs=[analyzer_state, handler_state, status_text, main_interface]
        )

        start_btn.click(
            start_recording,
            inputs=[handler_state],
            outputs=[recording_state, status_text]
        )

        stop_btn.click(
            stop_recording, 
            inputs=[handler_state],
            outputs=[recording_state, status_text]
        )

        # Set up WebRTC stream
        try:
            webrtc.stream(
                lambda: handler_state.value if handler_state.value else ScreenStreamHandler(),
                inputs=[webrtc, raw_messages, processed_messages],
                outputs=[webrtc],
                time_limit=None,
                concurrency_limit=1
            )
        except Exception as e:
            print(f"⚠️ WebRTC stream setup failed: {e}")

        # Update chat every 2 seconds
        timer = gr.Timer(2.0)
        timer.tick(
            update_chat,
            inputs=[raw_messages, processed_messages, view_mode],
            outputs=[chat],
            show_progress=False
        )

        gr.Markdown("""
        ## 📋 Instructions:
        1. Enter your Gemini API key and click Connect
        2. Click Start Recording and share your screen
        3. AI will analyze your screen every 3 seconds
        4. Switch between processed (deduplicated) and raw views
        """)

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(
        share=False,
        debug=True,
        server_name="0.0.0.0",
        server_port=7868,  # Use different port
        strict_cors=False
    )
