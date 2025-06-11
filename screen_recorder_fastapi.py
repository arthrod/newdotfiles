#!/usr/bin/env python3
"""FastAPI-based screen recorder with WebRTC and plain JavaScript."""

import os
import asyncio
import tempfile
import base64
from pathlib import Path
from typing import Optional
from PIL import Image
from loguru import logger
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.messages import BinaryContent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup environment
def setup_environment():
    """Setup environment variables and configurations."""
    hf_token = os.environ.get("HF_TOKEN")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if hf_token:
        print(f"✅ HF_TOKEN loaded: {hf_token[:8]}...")
    else:
        print("⚠️  HF_TOKEN not found in environment")

    if gemini_key:
        print(f"✅ GEMINI_API_KEY loaded: {gemini_key[:8]}...")
    else:
        print("⚠️  GEMINI_API_KEY not found in environment")

    return hf_token, gemini_key

async def analyze_image_with_ai(image_data: bytes, question: str, api_key: str) -> str:
    """Analyze image using pydantic_ai with BinaryContent."""
    try:
        # Set the API key in environment for Gemini
        os.environ['GEMINI_API_KEY'] = api_key

        # Get model name from environment
        model_name = os.environ.get('GEMINI_MODEL', 'google-2.0-flash')

        # Create Gemini model
        model = GeminiModel(model_name)

        # Create agent
        agent = Agent('google-gla:gemini-2.0-flash')
        logger.info(f"Agent created: {agent}")

        # Create binary content for the image
        image_content = BinaryContent(
            data=image_data,
            media_type='image/png'
        )

        # Run the agent with image and question
        result = await agent.run(
            [question, image_content]
        )
        logger.info(f"Analysis completed: {result.output}")
        return result.output

    except Exception as e:
        return f"Analysis failed: {str(e)}"

# Initialize FastAPI app
app = FastAPI(title="Screen Recorder Pro", description="Professional screen recording with AI analysis")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup environment
hf_token, gemini_key = setup_environment()

# Global analyzer instance
analyzer = None

@app.get("/", response_class=HTMLResponse)
async def get_main_page():
    """Serve the main HTML page with screen recording interface."""

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Screen Recorder Pro</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .status {{
                text-align: center;
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
                background: #f8f9fa;
                border-left: 4px solid #007bff;
                font-weight: bold;
            }}
            .controls {{
                text-align: center;
                margin: 30px 0;
            }}
            .btn {{
                padding: 12px 24px;
                margin: 0 10px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                min-width: 160px;
            }}
            .btn-primary {{ background: #007bff; color: white; }}
            .btn-success {{ background: #28a745; color: white; }}
            .btn-danger {{ background: #dc3545; color: white; }}
            .btn-info {{ background: #17a2b8; color: white; }}
            .btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }}
            .btn:disabled {{ opacity: 0.5; cursor: not-allowed; transform: none; }}

            #videoPreview {{
                width: 100%;
                max-width: 800px;
                height: 450px;
                border: 2px solid #ddd;
                border-radius: 8px;
                background: #000;
                display: block;
                margin: 20px auto;
            }}
            .analysis-section {{
                margin-top: 40px;
                padding-top: 30px;
                border-top: 2px solid #eee;
            }}
            .form-group {{
                margin: 20px 0;
            }}
            .form-group label {{
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
            }}
            .form-group input, .form-group textarea {{
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }}
            .form-group textarea {{
                height: 120px;
                resize: vertical;
            }}
            .env-status {{
                background: #e9ecef;
                padding: 15px;
                border-radius: 6px;
                margin: 20px 0;
                font-family: monospace;
                font-size: 14px;
            }}
            .result-box {{
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 20px;
                margin: 20px 0;
                min-height: 100px;
                white-space: pre-wrap;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🖥️ Screen Recorder Pro</h1>
                <p>Professional screen recording with AI analysis powered by Google Gemini</p>
            </div>

            <div class="env-status">
                <strong>Environment Status:</strong><br>
                HF_TOKEN: {'✅ Loaded' if hf_token else '⚠️ Not found'}<br>
                GEMINI_API_KEY: {'✅ Loaded' if gemini_key else '⚠️ Not found'}
            </div>

            <div class="status" id="status">
                Ready to start screen recording
            </div>

            <video id="videoPreview" autoplay muted playsinline style="display: none;"></video>

            <div class="controls">
                <button class="btn btn-success" id="startBtn" onclick="startRecording()">
                    🎬 Start Screen Recording
                </button>
                <button class="btn btn-danger" id="stopBtn" onclick="stopRecording()" disabled>
                    ⏹️ Stop Recording
                </button>
                <button class="btn btn-info" id="snapshotBtn" onclick="captureSnapshot()" disabled>
                    📸 Capture Snapshot
                </button>
            </div>

            <div class="analysis-section">
                <h3>🤖 AI Analysis</h3>

                <div class="form-group">
                    <label for="apiKey">Gemini API Key:</label>
                    <input type="password" id="apiKey" placeholder="Enter your Gemini API key"
                           value="{gemini_key or ''}" />
                    <small style="color: #666; font-size: 12px;">Required for snapshot analysis and video analysis</small>
                </div>

                <div class="result-box" id="analysisResult">
                    📸 <strong>Smart Snapshot:</strong> Click "Capture Snapshot" during recording to automatically save and analyze the current frame!<br><br>
                    🎥 <strong>image Analysis:</strong> Upload a recorded video below for detailed analysis...
                </div>

                <div style="border-top: 1px solid #ddd; margin-top: 20px; padding-top: 20px;">
                    <h4>📹 Manual image Analysis</h4>

                    <div class="form-group">
                        <label for="imageFile">Upload Recorded image:</label>
                        <input type="file" id="imageFile" accept="image/*" />
                    </div>

                    <div class="form-group">
                        <label for="question">Analysis Question:</label>
                        <textarea id="question" placeholder="What would you like to know about the recording?">Describe what's happening on this screen in detail</textarea>
                    </div>

                    <button class="btn btn-primary" onclick="analyzeImage()">
                        🔍 Analyze Uploaded image
                    </button>
                </div>
            </div>
        </div>

        <script>
            let mediaRecorder = null;
            let recordedChunks = [];
            let stream = null;

            function updateStatus(message, color = '#007bff') {{
                const status = document.getElementById('status');
                status.textContent = message;
                status.style.borderLeftColor = color;
            }}

            async function startRecording() {{
                try {{
                    updateStatus('🔄 Requesting screen access...', '#ffc107');

                    stream = await navigator.mediaDevices.getDisplayMedia({{
                        video: {{
                            width: {{ ideal: 1280 }},
                            height: {{ ideal: 720 }},
                            frameRate: {{ ideal: 30 }}
                        }},
                        audio: true
                    }});

                    const video = document.getElementById('videoPreview');
                    video.srcObject = stream;
                    video.style.display = 'block';

                    recordedChunks = [];

                    // Try different codec options for maximum compatibility
                    let options = [
                        {{ mimeType: 'video/webm; codecs=vp8,opus' }},
                        {{ mimeType: 'video/webm; codecs=vp8' }},
                        {{ mimeType: 'video/webm' }},
                        {{ mimeType: 'video/mp4; codecs=h264' }},
                        {{ mimeType: 'video/mp4' }},
                        {{}} // No options - use browser default
                    ];

                    let selectedOption = null;
                    for (let option of options) {{
                        if (MediaRecorder.isTypeSupported(option.mimeType || '')) {{
                            selectedOption = option;
                            console.log('Using codec:', option.mimeType || 'default');
                            break;
                        }}
                    }}

                    mediaRecorder = new MediaRecorder(stream, selectedOption || {{}});

                    mediaRecorder.ondataavailable = (event) => {{
                        if (event.data.size > 0) {{
                            recordedChunks.push(event.data);
                        }}
                    }};

                    mediaRecorder.onstop = () => {{
                        // Determine file extension and blob type based on selected codec
                        let fileExtension = 'webm';
                        let blobType = selectedOption?.mimeType || 'video/webm';

                        if (blobType.includes('mp4')) {{
                            fileExtension = 'mp4';
                        }}

                        const blob = new Blob(recordedChunks, {{ type: blobType }});
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `screen-recording-${{Date.now()}}.$${{fileExtension}}`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);

                        updateStatus('✅ Recording saved!', '#28a745');
                    }};

                    mediaRecorder.start(1000);

                    updateStatus('🔴 Recording in progress...', '#dc3545');
                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                    document.getElementById('snapshotBtn').disabled = false;

                    // Handle stream end (user stops sharing)
                    stream.getVideoTracks()[0].onended = () => {{
                        stopRecording();
                    }};

                }} catch (err) {{
                    console.error('Error starting recording:', err);
                    updateStatus('❌ Error: ' + err.message, '#dc3545');
                }}
            }}

            function stopRecording() {{
                if (mediaRecorder && mediaRecorder.state === 'recording') {{
                    mediaRecorder.stop();
                }}

                if (stream) {{
                    stream.getTracks().forEach(track => track.stop());
                    stream = null;
                }}

                const video = document.getElementById('videoPreview');
                video.srcObject = null;
                video.style.display = 'none';

                updateStatus('⏹️ Recording stopped', '#6c757d');
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                document.getElementById('snapshotBtn').disabled = true;
            }}

            async function captureSnapshot() {{
                const video = document.getElementById('videoPreview');
                if (!video || !video.srcObject) {{
                    updateStatus('❌ No active recording to capture', '#dc3545');
                    return;
                }}

                const apiKey = document.getElementById('apiKey').value.trim();
                if (!apiKey) {{
                    updateStatus('❌ Please enter Gemini API key for snapshot analysis', '#dc3545');
                    return;
                }}

                updateStatus('📸 Capturing and analyzing snapshot...', '#17a2b8');

                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0);

                canvas.toBlob(async (blob) => {{
                    try {{
                        // Save snapshot locally
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `screen-capture-${{Date.now()}}.png`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);

                        // Send to AI for analysis
                        const formData = new FormData();
                        formData.append('image', blob, 'snapshot.png');
                        formData.append('question', 'Reason about the question in the screen under <thinking>. Then provide your answer, extremely carefully.');
                        formData.append('api_key', apiKey);

                        updateStatus('🤖 Analyzing snapshot with AI...', '#ffc107');

                        const response = await fetch('/analyze-image', {{
                            method: 'POST',
                            body: formData
                        }});

                        const result = await response.json();
                        const resultDiv = document.getElementById('analysisResult');

                        if (response.ok) {{
                            resultDiv.innerHTML = `
                                <strong>📸 Snapshot Analysis:</strong><br><br>
                                ${{result.analysis}}
                                <br><br>
                                <em>Captured at: ${{new Date().toLocaleString()}}</em>
                            `;
                            updateStatus('✅ Snapshot captured and analyzed!', '#28a745');
                        }} else {{
                            resultDiv.textContent = '❌ Analysis failed: ' + result.error;
                            updateStatus('⚠️ Snapshot saved, but analysis failed', '#ffc107');
                        }}

                    }} catch (error) {{
                        console.error('Error analyzing snapshot:', error);
                        updateStatus('⚠️ Snapshot saved, but analysis failed', '#ffc107');
                        document.getElementById('analysisResult').textContent = '❌ Network error: ' + error.message;
                    }}
                }}, 'image/png');
            }}

            async function analyzeImage() {{
                const apiKey = document.getElementById('apiKey').value.trim();
                const imageFile = document.getElementById('imageFile').files[0];
                const question = document.getElementById('question').value.trim();
                const resultDiv = document.getElementById('analysisResult');

                if (!apiKey) {{
                    resultDiv.textContent = '❌ Please enter a Gemini API key';
                    return;
                }}

                if (!imageFile) {{
                    resultDiv.textContent = '❌ Please select a image file';
                    return;
                }}

                resultDiv.textContent = '🔄 Analyzing image with Gemini AI...';

                const formData = new FormData();
                formData.append('image', imageFile);
                formData.append('question', question || 'Describe what is happening on this screen');
                formData.append('api_key', apiKey);

                try {{
                    const response = await fetch('/analyze-image', {{
                        method: 'POST',
                        body: formData
                    }});

                    const result = await response.json();

                    if (response.ok) {{
                        resultDiv.textContent = result.analysis;
                    }} else {{
                        resultDiv.textContent = '❌ ' + result.error;
                    }}
                }} catch (error) {{
                    resultDiv.textContent = '❌ Network error: ' + error.message;
                }}
            }}

            // Check browser capabilities and supported codecs
            function checkBrowserSupport() {{
                if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {{
                    updateStatus('❌ Screen recording not supported in this browser', '#dc3545');
                    document.getElementById('startBtn').disabled = true;
                    return;
                }}

                // Check supported codecs
                const codecs = [
                    'video/webm; codecs=vp8,opus',
                    'video/webm; codecs=vp8',
                    'video/webm',
                    'video/mp4; codecs=h264',
                    'video/mp4'
                ];

                const supportedCodecs = codecs.filter(codec => MediaRecorder.isTypeSupported(codec));
                console.log('Supported codecs:', supportedCodecs);

                if (supportedCodecs.length === 0) {{
                    updateStatus('⚠️ No supported video codecs found, using browser default', '#ffc107');
                }} else {{
                    updateStatus('✅ Ready to record (codec: ' + supportedCodecs[0] + ')', '#28a745');
                }}
            }}

            // Initialize on page load
            checkBrowserSupport();
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)

@app.post("/analyze-video")
async def analyze_video(
    video: UploadFile = File(...),
    question: str = Form(...),
    api_key: str = Form(...)
):
    """Analyze uploaded video with Gemini AI."""

    try:
        # For now, return a simple message since we're focusing on image analysis
        # Video analysis with pydantic_ai would need additional setup
        return JSONResponse(content={
            "analysis": "Video analysis not yet implemented with pydantic_ai. Please use snapshot feature for instant image analysis!"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-image")
async def analyze_image(
    image: UploadFile = File(...),
    question: str = Form(...),
    api_key: str = Form(...)
):
    """Analyze uploaded image with Gemini AI using pydantic_ai.

    Handles both:
    - File uploads from form input
    - Snapshot blob data from canvas capture
    """

    try:
        # Read image data directly from UploadFile (works for both file uploads and blob data)
        image_data = await image.read()

        # Validate we have image data
        if not image_data:
            raise HTTPException(status_code=400, detail="No image data received")

        # Validate content type - only accept PNG images
        if image.content_type and not image.content_type == 'image/png':
            raise HTTPException(status_code=400, detail=f"Only PNG images are supported, got: {image.content_type}")

        # Use PNG as media type
        content_type = 'image/png'

        # Analyze with pydantic_ai
        result = await analyze_image_with_ai(image_data, question, api_key)

        return JSONResponse(content={"analysis": result})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Screen Recorder Pro is running"}

if __name__ == "__main__":
    print("🚀 Starting Screen Recorder Pro with FastAPI...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7864,
        reload=False,
        access_log=True
    )
