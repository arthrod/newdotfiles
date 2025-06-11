# Screen Streaming Gradio App
# -------------------------------------------------------------
# Requirements (install with pip):
#   gradio>=4.34.0
#   fastrtc>=0.0.31            # real‑time WebRTC helpers for Gradio
#   google-generativeai>=0.3.2 # Gemini SDK
#   opencv-python              # video encoding for 2‑second clips
#   numpy
# -------------------------------------------------------------
# The only configuration needed is to expose your Google Gemini
# API key.  You can either export it as an environment variable:
#   export GEMINI_API_KEY="<your‑key>"
# or paste it into the textbox that appears when the demo starts.

import os
import time
import uuid
import cv2
import tempfile
import asyncio
from pathlib import Path
from typing import List, Dict, Any

import gradio as gr
import numpy as np

# FastRTC/Gradio‑WebRTC
from fastrtc import (
    WebRTC,
    StreamHandler,
    get_cloudflare_turn_credentials_async,
)

# Google Gemini SDK
import google.genai as genai
from google.genai import types

# ---------------------------------------------------------------------------
#  Gemini helper functions – lifted directly from the user’s specification
# ---------------------------------------------------------------------------
USER_SCREEN_ANALYSIS_MODEL = "gemini-2.0-flash"
IMAGE_ANALYSIS_MODEL = "gemini-2.0-flash"
DEDUP_MODEL = "gemini-2.0-flash"


def _get_client(api_key: str | None = None) -> genai.Client:
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Please supply a Google Gemini API key – either export GEMINI_API_KEY or paste it in the UI.")
    return genai.Client(api_key=api_key)


# --- video (2‑s chunk) ------------------------------------------------------

def User_Screen_analysis_tool(question: str, folder: str, api_key: str | None = None) -> str:
    """Call Gemini on a short screen‑recording clip saved inside *folder*."""
    try:
        client = _get_client(api_key)
        # pick *any* file in the folder – we only ever write one clip
        video_files = list(Path(folder).glob("*.mp4"))
        if not video_files:
            raise RuntimeError("No video file found to upload.")
        file_ref = client.files.upload(file=str(video_files[0]))
        resp = client.models.generate_content(
            model=USER_SCREEN_ANALYSIS_MODEL,
            contents=[file_ref, question],
        )
        return resp.text if hasattr(resp, "text") else str(resp)
    except Exception as e:
        raise RuntimeError(f"Processing failed: {e}")


# --- snapshot (single image) ------------------------------------------------

def image_analysis_tool(question: str, file_path: str, api_key: str | None = None) -> str:
    try:
        client = _get_client(api_key)
        file_ref = client.files.upload(file=file_path)
        resp = client.models.generate_content(
            model=IMAGE_ANALYSIS_MODEL,
            contents=[file_ref, question],
        )
        return resp.text if hasattr(resp, "text") else str(resp)
    except Exception as e:
        raise RuntimeError(f"Processing failed: {e}")


# --- deduplication ----------------------------------------------------------

def deduplication_tool(sentence: str, previous_sentence: str, api_key: str | None = None) -> bool:
    try:
        client = _get_client(api_key)
        contents = (
            "This is the current sentence: "
            f"{sentence}.\nThis is the previous sentence: {previous_sentence}.\n"
            "If they are substantially the same, respond with True, if they are not, respond False."
        )
        resp = client.models.generate_content(model=DEDUP_MODEL, contents=contents)
        response_text = resp.text if hasattr(resp, "text") else str(resp)
        return "true" in response_text.lower()
    except Exception as e:
        raise RuntimeError(f"Processing failed: {e}")


# ---------------------------------------------------------------------------
#  Gradio / FastRTC stream handler
# ---------------------------------------------------------------------------
class ScreenStreamHandler(StreamHandler):
    """Receive video frames, batch them into 2‑second chunks, analyse with Gemini, and
    push messages into two shared chat histories (raw & processed)."""

    def __init__(self):
        super().__init__()
        self.buffer: List[np.ndarray] = []
        self.last_chunk_time: float = time.time()
        self.prev_answer: str = ""

    # FastRTC will call *copy()* so that each user gets an independent handler
    def copy(self):
        return ScreenStreamHandler()

    # ---------------------------------------------------------------------
    def receive(self, frame: np.ndarray):  # called for every inbound frame
        self.buffer.append(frame)

        # Access the latest UI arguments (they appear after the WebRTC component)
        # layout: [webrtc, api_key, capture_mode, stream_mode, recording_state,
        #          raw_messages, processed_messages]
        (
            _webrtc,
            api_key,
            capture_mode,
            stream_mode,
            recording_state,
            raw_msgs,
            proc_msgs,
        ) = self.latest_args  # type: ignore[attr-defined]

        if not recording_state:
            # Not recording – ignore frames
            self.buffer.clear()
            return

        now = time.time()
        if now - self.last_chunk_time < 2:
            return  # wait until 2 s have elapsed

        self.last_chunk_time = now
        frames_to_process = self.buffer.copy()
        self.buffer.clear()

        try:
            answer: str
            if capture_mode == "Only snapshots":
                # use last frame as JPEG
                img_path = tempfile.mktemp(prefix="snapshot_", suffix=".jpg")
                cv2.imwrite(img_path, cv2.cvtColor(frames_to_process[-1], cv2.COLOR_RGB2BGR))
                answer = image_analysis_tool("Describe this screen", img_path, api_key)
            else:  # 2‑second video
                folder = tempfile.mkdtemp(prefix="clip_")
                vid_path = Path(folder) / "screen.mp4"
                h, w, _ = frames_to_process[0].shape
                writer = cv2.VideoWriter(
                    str(vid_path), cv2.VideoWriter_fourcc(*"mp4v"), 10, (w, h)
                )
                for frm in frames_to_process:
                    writer.write(cv2.cvtColor(frm, cv2.COLOR_RGB2BGR))
                writer.release()
                answer = User_Screen_analysis_tool("Describe this screen", folder, api_key)
        except Exception as e:
            answer = f"⚠️ Gemini processing failed: {e}"

        # Update raw chat
        raw_msgs.append({"role": "assistant", "content": answer})

        # Deduplicate for processed chat
        if not self.prev_answer:
            is_dup = False
        else:
            try:
                is_dup = deduplication_tool(answer, self.prev_answer, api_key)
            except Exception:
                is_dup = False  # fail open
        if not is_dup:
            proc_msgs.append({"role": "assistant", "content": answer})
            self.prev_answer = answer

    # ---------------------------------------------------------------------
    def emit(self):
        """Return the most recent frame so users can see their own screen."""
        if self.buffer:
            return self.buffer[-1]
        return None


# ---------------------------------------------------------------------------
#  Shared chat‑history containers (per user, via gr.State)
# ---------------------------------------------------------------------------

def _init_chat() -> List[Dict[str, Any]]:
    return []


# ---------------------------------------------------------------------------
#  Gradio UI
# ---------------------------------------------------------------------------
css = """
#video-source {max-width: 700px !important; max-height: 500px !important;}
.chatbot {height: 320px; overflow: auto}
"""

demo = gr.Blocks(css=css, theme=gr.themes.Soft())

with demo:
    gr.Markdown(
        """
        # 🖥️  Live Screen Describer
        Share your screen and every **2 seconds** Gemini will describe what's visible.
        Toggle between *raw* descriptions (all answers) and *processed* (deduplicated).
        """,
    )

    # --- API Key & Connect -------------------------------------------------
    with gr.Row() as api_row:
        api_box = gr.Textbox(
            label="Gemini API Key (kept only in‑browser)",
            type="password",
            placeholder="Paste your key or export GEMINI_API_KEY",
            value=os.environ.get("GEMINI_API_KEY", ""),
        )
        connect_btn = gr.Button("Connect to FastRTC", variant="primary")

    # --- Main controls (hidden until connect) -----------------------------
    with gr.Row(visible=False) as main_row:
        with gr.Column(scale=1):
            # WebRTC component (client screen share)
            webrtc = WebRTC(
                label="Screen Share",
                mode="send-receive",
                modality="video",
                elem_id="video-source",
                rtc_configuration=get_cloudflare_turn_credentials_async,
            )
            # recording toggles
            start_btn = gr.Button("Start Recording", variant="primary")
            stop_btn = gr.Button("Stop Recording", variant="stop")
        with gr.Column(scale=1):
            capture_mode = gr.Radio(
                ["Only snapshots", "2‑second videos"],
                label="Capture Mode",
                value="Only snapshots",
            )
            stream_mode = gr.Radio(
                ["Stream to Gemini every 2 s", "Save locally & send"],
                label="Streaming Mode",
                value="Stream to Gemini every 2 s",
            )
            show_toggle = gr.Radio(
                ["processed", "raw"],
                label="Chat View",
                value="processed",
            )
            chat = gr.Chatbot(label="Descriptions", elem_classes=["chatbot"], type="messages")

    # --- States -----------------------------------------------------------
    recording_state = gr.State(False)
    raw_state = gr.State(_init_chat())
    proc_state = gr.State(_init_chat())

    # --- Stream binding ----------------------------------------------------
    webrtc.stream(
        ScreenStreamHandler(),
        inputs=[
            webrtc,          # must be first
            api_box,         # Gemini key
            capture_mode,    # snapshots vs video
            stream_mode,     # streaming vs save
            recording_state, # bool
            raw_state,
            proc_state,
        ],
        outputs=[webrtc],
        time_limit=None,  # run as long as the user wants
        concurrency_limit=2,
    )

    # --- Display logic -----------------------------------------------------
    def _merge_chat(raw, proc, mode):
        return proc if mode == "processed" else raw

    # Poll every 0.7 s to update the chat box
    poller = gr.Timer(value=0.7, active=True)
    poller.then(_merge_chat, inputs=[raw_state, proc_state, show_toggle], outputs=chat, show_progress="hidden")

    # --- Button Actions ----------------------------------------------------
    connect_btn.click(lambda: (gr.update(visible=False), gr.update(visible=True)), None, [api_row, main_row])

    start_btn.click(lambda: True, None, recording_state, queue=False)
    stop_btn.click(lambda: False, None, recording_state, queue=False)

if __name__ == "__main__":
    demo.launch(strict_cors=False)
