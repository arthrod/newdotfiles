"""Screen helper functionality for capturing and analyzing screen content."""

import os
import tempfile
import time
from pathlib import Path

import cv2
from google import  genai
import gradio as gr
import numpy as np
from fastrtc import StreamHandler, WebRTC, get_cloudflare_turn_credentials_async
from pydantic_ai import Agent, BinaryContent

class ScreenAnalyzer:

    """Handles Gemini API interactions for screen analysis."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize with Gemini API key."""
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key required")

        self.agent = Agent('google-gla:gemini-2.0-flash')

    def analyze_video_clip(self, video_path: str, question: str = "Describe what's happening on this screen") -> str:
        """Analyze a video clip with Gemini."""
        try:
            # Upload video file to Gemini
            video_file = genai.upload_file(path=video_path)

            # Generate content
            response = agent.run([Describe precisely what you see, AudioUrl
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

    def check_duplicate(self, current: str, previous: str) -> bool:
        """Check if current response is duplicate of previous."""
        if not previous:
            return False

        try:
            prompt = f"""
            Compare these two responses:
            Current: {current}
            Previous: {previous}

            Are they substantially the same? Respond with only 'true' or 'false'.
            """
            response = self.model.generate_content(prompt)
            return "true" in response.text.lower()
        except Exception:
            return False


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
        if not self.recording:
            self.buffer.clear()
            return

        self.buffer.append(frame)

        # Process every 2 seconds
        now = time.time()
        if now - self.last_chunk_time < 2.0:
            return

        self.last_chunk_time = now
        frames_to_process = self.buffer.copy()
        self.buffer.clear()

        if not frames_to_process or not self.analyzer:
            return

        # Get latest UI state from args
        if hasattr(self, "latest_args") and self.latest_args:
            args = self.latest_args
            if len(args) >= 5:
                capture_mode = args[2]  # "snapshots" or "video"
                raw_messages = args[3]
                processed_messages = args[4]

                try:
                    # Analyze based on capture mode
                    if capture_mode == "snapshots":
                        response = self._analyze_snapshot(frames_to_process[-1])
                    else:
                        response = self._analyze_video_clip(frames_to_process)

                    # Update raw messages
                    raw_messages.append({"role": "assistant", "content": response})

                    # Check for duplicates and update processed messages
                    if not self.analyzer.check_duplicate(response, self.prev_response):
                        processed_messages.append({"role": "assistant", "content": response})
                        self.prev_response = response

                except Exception as e:
                    error_msg = f"⚠️ Processing failed: {e}"
                    raw_messages.append({"role": "assistant", "content": error_msg})

    def _analyze_snapshot(self, frame: np.ndarray) -> str:
        """Analyze a single frame as snapshot."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            # Convert RGB to BGR for OpenCV
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(tmp.name, bgr_frame)

            result = self.analyzer.analyze_image(tmp.name)
            Path(tmp.name).unlink()  # Clean up
            return result

    def _analyze_video_clip(self, frames: list[np.ndarray]) -> str:
        """Analyze frames as a video clip."""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            if not frames:
                return "No frames to process"

            # Get frame dimensions
            h, w, _ = frames[0].shape

            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(tmp.name, fourcc, 10.0, (w, h))

            # Write frames
            for frame in frames:
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                writer.write(bgr_frame)

            writer.release()

            result = self.analyzer.analyze_video_clip(tmp.name)
            Path(tmp.name).unlink()  # Clean up
            return result

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


class ScreenHelperApp:
    """Main screen helper application."""

    def __init__(self):
        """Initialize the application."""
        self.analyzer = None
        self.handler = None

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        css = """
        #video-source {max-width: 700px !important; max-height: 500px !important;}
        .chatbot {height: 320px; overflow: auto;}
        """

        with gr.Blocks(css=css, theme=gr.themes.Soft(), title="Screen Helper") as interface:
            gr.Markdown("""
            # 🖥️ Screen Helper

            Share your screen and get AI analysis every 2 seconds using Google's Gemini model.
            Switch between raw responses and deduplicated responses.
            """)

            # API key input
            with gr.Row() as api_row:
                api_key = gr.Textbox(
                    label="Gemini API Key",
                    type="password",
                    placeholder="Enter your Gemini API key",
                    value=os.environ.get("GEMINI_API_KEY", ""),
                )
                connect_btn = gr.Button("Connect", variant="primary")

            # Main interface (hidden initially)
            with gr.Row(visible=False) as main_row:
                with gr.Column(scale=1):
                    # WebRTC component
                    webrtc = WebRTC(
                        label="Screen Share",
                        mode="send-receive",
                        modality="video",
                        elem_id="video-source",
                        rtc_configuration={
                            "iceServers": [
                                {"urls": ["stun:stun.l.google.com:19302"]},
                                {"urls": ["stun:stun1.l.google.com:19302"]},
                            ]
                        },
                    )

                    # Recording controls
                    with gr.Row():
                        start_btn = gr.Button("Start Recording", variant="primary")
                        stop_btn = gr.Button("Stop Recording", variant="stop")

                with gr.Column(scale=1):
                    # Mode controls
                    capture_mode = gr.Radio(
                        ["snapshots", "video"],
                        label="Capture Mode",
                        value="snapshots",
                        info="Snapshots: analyze single frames. Video: analyze 2-second clips",
                    )

                    view_mode = gr.Radio(
                        ["processed", "raw"],
                        label="View Mode",
                        value="processed",
                        info="Processed: deduplicated responses. Raw: all responses",
                    )

                    # Chat display
                    chat = gr.Chatbot(label="AI Analysis", elem_classes=["chatbot"], type="messages")

            # State variables
            raw_messages = gr.State(list)
            processed_messages = gr.State(list)
            recording_state = gr.State(False)

            # Event handlers
            def setup_connection(api_key_val):
                """Setup the analyzer and handler with API key."""
                if not api_key_val or not api_key_val.strip():
                    gr.Warning("Please enter a Gemini API key")
                    return gr.update(visible=True), gr.update(visible=False)

                try:
                    self.analyzer = ScreenAnalyzer(api_key_val.strip())
                    self.handler = ScreenStreamHandler(self.analyzer)
                    return gr.update(visible=False), gr.update(visible=True)
                except Exception as e:
                    gr.Error(f"Failed to connect: {e}")
                    return gr.update(visible=True), gr.update(visible=False)

            def start_recording():
                """Start recording."""
                if self.handler:
                    self.handler.start_recording()
                return True

            def stop_recording():
                """Stop recording."""
                if self.handler:
                    self.handler.stop_recording()
                return False

            def update_chat(raw_msgs, proc_msgs, view):
                """Update chat display based on view mode."""
                return proc_msgs if view == "processed" else raw_msgs

            # Wire up events
            connect_btn.click(setup_connection, inputs=[api_key], outputs=[api_row, main_row])

            start_btn.click(start_recording, outputs=[recording_state])

            stop_btn.click(stop_recording, outputs=[recording_state])

            # Set up WebRTC stream
            if hasattr(webrtc, "stream"):
                webrtc.stream(
                    lambda: self.handler if self.handler else ScreenStreamHandler(),
                    inputs=[webrtc, api_key, capture_mode, raw_messages, processed_messages],
                    outputs=[webrtc],
                    time_limit=None,
                    concurrency_limit=2,
                )

            # Update chat periodically
            timer = gr.Timer(1.0)
            timer.tick(update_chat, inputs=[raw_messages, processed_messages, view_mode], outputs=[chat], show_progress=False)

        return interface

    def launch(self, **kwargs):
        """Launch the application."""
        interface = self.create_interface()
        return interface.launch(**kwargs)


def create_app() -> ScreenHelperApp:
    """Create a new screen helper application."""
    return ScreenHelperApp()


if __name__ == "__main__":
    app = create_app()
    app.launch(share=False, debug=True,strict_cors=False)
