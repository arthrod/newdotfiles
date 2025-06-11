#!/usr/bin/env python3
"""Simple Gradio interface for AI video analysis - no complex JavaScript integration."""

import os
import tempfile
import time
from pathlib import Path
from typing import Optional

import google.generativeai as genai
import gradio as gr


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
            print(f"📹 Uploading video: {video_path}")
            
            # Upload video file to Gemini
            video_file = genai.upload_file(path=video_path)
            
            # Wait for processing
            while video_file.state.name == "PROCESSING":
                print("⏳ Processing video...")
                time.sleep(1)
                video_file = genai.get_file(video_file.name)

            print("✅ Video processed, generating analysis...")
            
            # Generate content
            response = self.model.generate_content([video_file, question])
            return response.text
            
        except Exception as e:
            error_msg = f"⚠️ Video analysis failed: {str(e)}"
            print(error_msg)
            return error_msg

    def analyze_image(self, image_path: str, question: str = "Describe what's visible on this screen") -> str:
        """Analyze a single image with Gemini."""
        try:
            print(f"🖼️ Uploading image: {image_path}")
            
            # Upload image file to Gemini
            image_file = genai.upload_file(path=image_path)
            
            print("✅ Image uploaded, generating analysis...")
            
            # Generate content
            response = self.model.generate_content([image_file, question])
            return response.text
            
        except Exception as e:
            error_msg = f"⚠️ Image analysis failed: {str(e)}"
            print(error_msg)
            return error_msg


def create_analyzer_interface():
    """Create a simple Gradio interface for AI analysis."""
    
    # Check environment
    gemini_key = os.environ.get("GEMINI_API_KEY")
    hf_token = os.environ.get("HF_TOKEN")
    
    # Simple CSS
    css = """
    .container {
        max-width: 1200px;
        margin: 0 auto;
    }
    .status-box {
        background: #f0f8ff;
        border: 2px solid #0066cc;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .error-box {
        background: #fff0f0;
        border: 2px solid #cc0000;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .success-box {
        background: #f0fff0;
        border: 2px solid #00cc00;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    """
    
    with gr.Blocks(css=css, title="AI Screen Analyzer", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🤖 AI Screen Analyzer")
        gr.Markdown("Analyze your screen recordings and screenshots with Google's Gemini AI.")
        
        # Environment status
        with gr.Row():
            env_info = f"""
            ### 🔧 Environment Status
            - **GEMINI_API_KEY**: {'✅ Loaded' if gemini_key else '❌ Not found'}
            - **HF_TOKEN**: {'✅ Loaded' if hf_token else '⚠️ Not found (optional)'}
            """
            gr.Markdown(env_info)
        
        # API Key Setup
        with gr.Row():
            with gr.Column(scale=3):
                api_key = gr.Textbox(
                    label="🔑 Gemini API Key",
                    type="password",
                    placeholder="Enter your Gemini API key (or set GEMINI_API_KEY environment variable)",
                    value=gemini_key or "",
                    info="Get your API key from: https://makersuite.google.com/app/apikey"
                )
            with gr.Column(scale=1):
                connect_btn = gr.Button("🔗 Connect to AI", variant="primary", size="lg")
        
        # Connection status
        connection_status = gr.Markdown("", visible=False)
        
        # Analysis section
        with gr.Tab("📹 Video Analysis"):
            with gr.Row():
                with gr.Column():
                    video_upload = gr.Video(
                        label="📁 Upload Screen Recording",
                        sources=["upload"],
                        height=400
                    )
                    
                    video_question = gr.Textbox(
                        label="❓ Analysis Question",
                        value="Describe what's happening on this screen in detail. What actions are being performed?",
                        placeholder="What would you like to know about the recording?",
                        lines=3
                    )
                    
                    analyze_video_btn = gr.Button("🔍 Analyze Video", variant="secondary", size="lg")
                    
                with gr.Column():
                    video_result = gr.Textbox(
                        label="🎯 AI Analysis Result",
                        lines=15,
                        placeholder="Upload a video and click 'Analyze Video' to see AI insights...",
                        show_copy_button=True
                    )
        
        with gr.Tab("🖼️ Image Analysis"):
            with gr.Row():
                with gr.Column():
                    image_upload = gr.Image(
                        label="📁 Upload Screenshot",
                        type="filepath",
                        height=400
                    )
                    
                    image_question = gr.Textbox(
                        label="❓ Analysis Question",
                        value="Describe what's visible on this screen. What elements and content can you see?",
                        placeholder="What would you like to know about the image?",
                        lines=3
                    )
                    
                    analyze_image_btn = gr.Button("🔍 Analyze Image", variant="secondary", size="lg")
                    
                with gr.Column():
                    image_result = gr.Textbox(
                        label="🎯 AI Analysis Result",
                        lines=15,
                        placeholder="Upload an image and click 'Analyze Image' to see AI insights...",
                        show_copy_button=True
                    )
        
        # State
        analyzer_state = gr.State(None)
        
        # Functions
        def setup_analyzer(api_key_val):
            """Setup the analyzer with API key."""
            if not api_key_val or not api_key_val.strip():
                return None, gr.Markdown("⚠️ Please enter a valid Gemini API key", visible=True)
            
            try:
                analyzer = ScreenAnalyzer(api_key_val.strip())
                return analyzer, gr.Markdown("✅ Successfully connected to Gemini AI!", visible=True)
            except Exception as e:
                return None, gr.Markdown(f"❌ Failed to connect: {e}", visible=True)
        
        def analyze_video(analyzer, video_file, question):
            """Analyze uploaded video."""
            if not analyzer:
                return "❌ Please connect to Gemini AI first by entering your API key and clicking 'Connect to AI'"
            
            if not video_file:
                return "❌ Please upload a video file first"
            
            if not question.strip():
                question = "Describe what's happening on this screen"
            
            try:
                result = analyzer.analyze_video_clip(video_file, question)
                return result
            except Exception as e:
                return f"❌ Analysis failed: {e}"
        
        def analyze_image(analyzer, image_file, question):
            """Analyze uploaded image."""
            if not analyzer:
                return "❌ Please connect to Gemini AI first by entering your API key and clicking 'Connect to AI'"
            
            if not image_file:
                return "❌ Please upload an image file first"
            
            if not question.strip():
                question = "Describe what's visible on this screen"
            
            try:
                result = analyzer.analyze_image(image_file, question)
                return result
            except Exception as e:
                return f"❌ Analysis failed: {e}"
        
        # Event handlers
        connect_btn.click(
            setup_analyzer,
            inputs=[api_key],
            outputs=[analyzer_state, connection_status]
        )
        
        analyze_video_btn.click(
            analyze_video,
            inputs=[analyzer_state, video_upload, video_question],
            outputs=[video_result]
        )
        
        analyze_image_btn.click(
            analyze_image,
            inputs=[analyzer_state, image_upload, image_question],
            outputs=[image_result]
        )
        
        # Instructions
        with gr.Tab("📖 Instructions"):
            gr.Markdown("""
            ## 🎯 How to Use This AI Analyzer
            
            ### 1. Setup (First Time Only)
            - **Get API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your free Gemini API key
            - **Enter Key**: Paste your API key in the field above and click "Connect to AI"
            - **Environment Variable** (Optional): Set `GEMINI_API_KEY` in your environment to avoid entering it each time
            
            ### 2. Recording Your Screen
            - **Use the HTML Recorder**: Open `screen_recorder.html` in your browser for high-quality screen recording
            - **Alternative**: Use any screen recording software (OBS, QuickTime, etc.)
            - **Supported Formats**: WebM, MP4, MOV, AVI for videos; PNG, JPG, GIF for images
            
            ### 3. AI Analysis
            - **Upload**: Choose your video or image file
            - **Ask Questions**: Customize the analysis prompt or use the defaults
            - **Analyze**: Click the analyze button and wait for AI insights
            - **Copy Results**: Use the copy button to save the analysis
            
            ### 🎬 Recording Tips
            - **Quality**: Use 1080p for best AI analysis results
            - **Duration**: Keep videos under 10 minutes for faster processing
            - **Content**: Ensure important elements are clearly visible
            - **Audio**: Include audio if you want voice/sound analysis
            
            ### 🤖 Analysis Tips
            - **Be Specific**: Ask detailed questions for better insights
            - **Context**: Provide context in your questions (e.g., "This is a coding tutorial...")
            - **Multiple Questions**: Run the same content with different questions for comprehensive analysis
            - **Screenshots**: For static content, images often work better than videos
            
            ### 🔧 Troubleshooting
            - **API Errors**: Check your API key and internet connection
            - **Large Files**: Compress videos if upload fails
            - **Processing Time**: Complex videos may take 30-60 seconds to analyze
            - **Browser Support**: Use Chrome, Firefox, or Safari for best compatibility
            
            ### 🔗 Companion Tools
            - **Screen Recorder**: Use the included HTML screen recorder for best results
            - **Environment Setup**: Run `setup_and_run.py` to configure environment variables
            - **Local Analysis**: All processing happens through Google's secure API
            """)
    
    return interface


def main():
    """Main function to run the analyzer."""
    print("🤖 Starting AI Screen Analyzer...")
    
    # Load environment
    gemini_key = os.environ.get("GEMINI_API_KEY")
    hf_token = os.environ.get("HF_TOKEN")
    
    if gemini_key:
        print(f"✅ GEMINI_API_KEY loaded: {gemini_key[:8]}...")
    else:
        print("⚠️ GEMINI_API_KEY not found in environment")
    
    if hf_token:
        print(f"✅ HF_TOKEN loaded: {hf_token[:8]}...")
    else:
        print("⚠️ HF_TOKEN not found (optional)")
    
    print()
    print("🌐 Starting Gradio interface...")
    print("📁 Use the companion screen_recorder.html for recording")
    print()
    
    app = create_analyzer_interface()
    app.launch(
        share=False,
        debug=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        show_api=False
    )


if __name__ == "__main__":
    main()
