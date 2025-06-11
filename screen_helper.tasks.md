# screen_helper.md

---

## TAREFA 1
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

Architecture and Tools for a Real-Time Screen-Streaming Gradio App

Overview: The goal is a Gradio-based web app on Hugging Face Spaces that can stream a user’s screen in 2-second chunks to Google’s Gemini API for live analysis (video or image-based), with a chat interface showing raw and deduplicated model responses. This requires a seamless integration of WebRTC streaming, screen capture, Gemini’s multimodal API, and an interactive UI. The high-level architecture involves a front-end (browser) capturing the screen and sending it via WebRTC to the Gradio backend on Spaces, which relays frames to Gemini and returns analysis results to the UI (Figure 1).  Figure 1: End-to-end system overview – the browser captures screen via getDisplayMedia and streams it to the Gradio app backend using WebRTC; a TURN server (e.g. Twilio or Cloudflare) relays data if direct peer-to-peer is blocked. The Gradio backend forwards 2s video/image chunks to Google’s Gemini API and receives analysis results, which are displayed back in the chat UI.

WebRTC Signaling: FastRTC vs. Alternatives

For low-latency streaming of screen content, FastRTC/Gradio-WebRTC is the ideal tool. FastRTC (the gradio-webrtc custom component) allows turning any Python function into a real-time video/audio stream via WebRTC, and it integrates directly with Gradio’s interface ￼ ￼. Using this, we can embed a WebRTC component in Gradio that captures the screen from the browser and streams it to the backend, achieving near-zero latency ￼. The WebRTC component can act as both input and output in Gradio’s Blocks – it receives the video feed from the client and can also send output frames back (if needed) ￼.

---

## TAREFA 2
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

However, raw WebRTC peer-to-peer connections are often blocked on cloud platforms like Spaces due to firewalls/NAT. In such cases, a TURN server is needed to relay traffic ￼. The easiest solutions are to use a managed TURN service rather than hosting your own. Two highly-recommended options are:
	•	Cloudflare Calls (with Hugging Face integration): Hugging Face and Cloudflare have partnered to provide 10 GB/month of free WebRTC relay for Spaces ￼. By using the FastRTC helper to get Cloudflare TURN credentials (with your HF API token) and passing that to the WebRTC component’s rtc_configuration, you instantly enable a TURN relay ￼ ￼. This is perhaps the simplest approach (no extra signup beyond HF). After 10GB, you can use your own Cloudflare account’s TURN token ￼.
	•	Twilio’s NAT Traversal service: Twilio provides easy-to-use TURN servers via their API. You can create a free Twilio account and use their Python SDK to fetch temporary ICE server credentials ￼ ￼. FastRTC/Gradio-WebRTC has a utility get_twilio_turn_credentials() that automates this using your Twilio SID and Auth Token ￼. In code, you call this and pass the resulting rtc_configuration dict when initializing the WebRTC component. This approach is highlighted in the Gradio-WebRTC docs as the “easiest way” to set up TURN for cloud deployments ￼.

---

## TAREFA 3
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

In summary, FastRTC (gradio-webrtc) plus a managed TURN service is the recommended signaling stack. FastRTC handles the signaling offer/answer under the hood, so you don’t need to run a separate signaling server – you just supply TURN credentials for connectivity. Use Cloudflare’s free quota first and fall back to Twilio if needed ￼ ￼. (Self-hosting a TURN server is possible but more DevOps overhead, so it’s a third option if needed.) Once configured, the WebRTC component will connect the browser and backend, streaming the screen content in real time.

Continuous Screen Recording & Buffering (2s Chunks)

On the browser side, the most straightforward way to capture the screen is the Screen Capture API. Using navigator.mediaDevices.getDisplayMedia() prompts the user to share their screen (or a specific window/tab) and returns a live MediaStream of the display ￼. This is the default approach for in-browser screen capture and does not require any installation. The captured MediaStream can then be handled in two ways:
	•	Live WebRTC Feed: The stream can be fed directly into a WebRTC peer connection (as done by the Gradio WebRTC component) for real-time transmission to the backend ￼. This is ideal for the “Streaming” mode – the browser shares the screen and the backend receives frames continuously.
	•	Buffered Recording (MediaRecorder): In cases where you want explicit 2-second buffered segments, you can use the MediaStream Recording API (MediaRecorder) on the getDisplayMedia stream. MediaRecorder can be configured to emit video blob chunks every N milliseconds. For example, a 2000ms timeslice will yield a blob roughly every 2 seconds which can be sent to the backend as a small video clip. This approach might be used for the “Saving locally” mode, where the app buffers the 2s segments first instead of sending live.

---

## TAREFA 4
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

In practice, the “Streaming” mode can be implemented simply by streaming frames via WebRTC continuously (and processing them on the fly), whereas “Save-then-send” mode could accumulate those 2-second blobs in the browser (or on the backend) before forwarding to the model. The Gradio WebRTC component is flexible enough to handle either: you could stream frames live, or you could pause the stream and send cached content in one go if needed. But a simpler design is to treat Streaming vs Saving as how the model is invoked rather than how capture is done – e.g., always capture continuously, but if in “save” mode, don’t call the Gemini API until a certain number of chunks or a user-triggered event. A toggle in the UI can control this logic.

Note: If for some reason a browser-side solution were not viable, one could consider system-level capture with FFmpeg or similar. For example, on a desktop you could run ffmpeg to grab the screen (-f x11grab or -f gdigrab) and feed it to the app. However, on Spaces (and web apps in general) this isn’t practical because the server has no access to the user’s display. So, using the browser’s getDisplayMedia API is the de-facto approach. The captured stream can be recorded or streamed as needed ￼. In summary, use the browser’s screen-share API to continuously capture the display, and buffer it in 2-second intervals via either WebRTC frames or MediaRecorder blobs.

---

## TAREFA 5
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

Integrating Google Gemini APIs for Video & Image Analysis

Google’s Gemini is a multimodal model, and by 2025 it supports real-time “live” API calls for audio, video, and images ￼ ￼. The recommended toolset is Google’s official SDK, e.g. the google-generativeai Python package ￼, which provides client libraries to interact with Gemini. This SDK can handle authentication (using your API key) and offers methods for sending different modalities.

Setting up the Gemini client: You’ll need to supply the user’s Gemini API key (for example, via a text input in the UI or as an environment variable). Using the SDK, initialize a Gemini client with this key. In the Hugging Face Spaces example by Freddy Boulton, they simply had the user enter the API key (stored in a Gradio Textbox with type="password") and used it to create the client ￼. The app then maintains a persistent connection to Gemini’s service over websockets for streaming. In the Gemini “live” API, you typically open a bidirectional streaming connection (WebSocket) where you send data (frames, audio, etc.) and receive incremental responses.

Analyzing 2s video clips: For continuous video analysis, you can utilize Gemini’s video understanding capability. In practice, since the screen video is being captured, a straightforward method (as seen in similar implementations) is to periodically sample frames from the video feed and send them to the model. The Gemini streaming API allows sending a sequence of image frames as the video progresses, and the model can respond in real-time. In Freddy’s real-time Gemini demo, for instance, the handler sent an image frame roughly every 1 second to avoid flooding the API ￼. For a 2-second buffer, you might send a frame or a short burst (or even the whole 2-second clip if the API supports video input as a file). If the API supports direct video clip input, you could send the 2s chunk as binary data; otherwise, sending a representative image frame every couple seconds can achieve a similar effect (the model will interpret the screen content from those frames).

---

## TAREFA 6
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

Analyzing image snapshots: In “image mode”, the app would capture static screenshots (e.g. using the same getDisplayMedia stream but grabbing a single frame via a canvas). These images can be sent to Gemini’s image understanding endpoint or included in the prompt. The google-generativeai SDK likely has a method to send an image and get a caption or analysis back. In a simpler approach, you can encode the image (e.g. as base64) and send it over the established WebSocket or via a REST API call to Gemini’s image analysis method.

Deduplicating responses: To avoid spammy or repetitive outputs from the model (which might happen if the screen hasn’t changed much between 2-second intervals), implement a deduplication filter. This can be as simple as keeping track of the last model response and comparing it to the new one. For example, maintain a last_response string; each time Gemini returns a result, compare it with last_response. If they are identical (or very similar), you can choose not to display the new one in the deduplicated chat view. The app can populate two parallel logs: one with raw responses (every output as it comes, for debugging or transparency), and one with deduplicated responses (only outputs that differ meaningfully from the previous). The UI toggle can switch which log is visible. This logic doesn’t require any special library – a simple Python string comparison or a similarity check can suffice. If needed, one could use more advanced text similarity (like Levenshtein distance or embedding-based similarity) to catch paraphrased duplicates, but the simplest approach is exact-match or thresholded substring match.

---

## TAREFA 7
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

In implementation, the Gemini streaming handler (likely a subclass of StreamHandler or AsyncAudioVideoStreamHandler as used in the example ￼ ￼) will handle incoming frames (receive) and send them to Gemini, and handle incoming Gemini messages (emit or an async generator) to produce model outputs. You can integrate the deduping in the part that produces or displays the output: e.g., before appending a new message to the chat, check against the previous one. This ensures the “deduplicated” chat view only shows changes. The raw log, however, would record everything for completeness.

Designing the Gradio UI and Controls

---

## TAREFA 8
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

We can create an elegant UI in Gradio Blocks to accommodate all the controls:
	•	A “Connect” button to initiate the WebRTC connection to the server. For example, you might keep the WebRTC component hidden or disabled until the user clicks Connect (especially if you want the user to enter their API key first). In Freddy’s implementation, they used the API key submission as the trigger to reveal the streaming interface ￼. Similarly, you can have a gr.Button("Connect to Server") that, when clicked, calls a function (or uses .click event) to start the stream. If using the WebRTC component, you might not need an explicit connect function (it connects when the user allows screen share), but you could use the button to simply unhide the WebRTC component or prompt the screen capture.
	•	A toggle for Image vs Video mode: This could be a gr.Radio or gr.Toggle that selects whether the app captures just periodic screenshots or a continuous video stream. Internally, this can set a flag that the streaming handler uses to decide how to treat incoming frames (or whether to use only keyframes). You might label it “Capture Mode: [Snapshots / Live Video]”.
	•	A toggle for Live Streaming vs Save-then-Send: This could be another radio or checkbox. In live mode, each 2s frame/clip is sent immediately to Gemini; in save mode, you could accumulate data (perhaps for a fixed duration or until user clicks a “Send” button) and then send a batch to Gemini. Depending on the use-case, “save locally” might mean the user can record a segment and then analyze it after stopping. This toggle will control whether the model is called continuously or only after some trigger. (If implementing the latter, you’d likely need a buffer on the backend to store the last few frames or clips, since Spaces doesn’t allow writing to the user’s local disk. You could store them in memory or /tmp on the container.)

---

## TAREFA 9
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

•	The chat display: Gradio offers a Chatbot component which nicely formats a chat conversation. You can use one for the raw output and one for the deduplicated output, or a single Chatbot and just filter messages. An easier approach is two Chatbot components (or two multi-line text boxes), one showing all responses, the other showing only unique responses. A toggle or tabs can let the user switch the view. For example, you might have a checkbox “Show deduplicated responses only” – when checked, the UI hides the raw chat component and shows the deduplicated one (or vice-versa). This can be done by manipulating the visible property of components via events (checkbox.change with a function that returns gr.update(visible=...) for each component). The example Spaces code used a similar approach for showing/hiding elements on user action ￼.

Styling and layout can be accomplished with Gradio Blocks. You have full flexibility to arrange components in rows/columns, and even inject custom HTML/CSS/JS. For instance, in the Gemini voice demo, they added a custom HTML block with inline styles to display the Gemini logo and a heading, and custom CSS to adjust component sizing ￼ ￼. You can include TailwindCSS classes or custom styles by passing a css string to gr.Blocks or using gr.HTML to add a <style> tag. In fact, as of Gradio 4.28+, Tailwind CSS is supported in custom components, meaning you can design UI elements with Tailwind utility classes if desired ￼. This opens the door to highly refined styling. If not using Tailwind, Gradio still allows themeing and custom CSS variables for styling. And for custom interactions, you can add JavaScript code via the Blocks(js=...) parameter or the *.js argument of events, enabling dynamic front-end behavior (e.g., automatically clicking the WebRTC permission dialog, etc.) ￼ ￼.

---

## TAREFA 10
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

In summary, Gradio’s UI flexibility will cover everything needed:
	•	Use Blocks layout to place a connect button, toggles, and the chat display in a clean way (perhaps the connect and toggles in a top bar, and the chat and video feed below).
	•	The WebRTC component’s own interface (which shows the video feed and a record button with an icon) can be customized with an icon and colors (as seen in the code using icon, icon_button_color, etc. for the component) ￼. This gives a polished look and clear indication of the stream status (the icon can pulse when streaming).
	•	Leverage events to handle user interactions: e.g., when “Connect” is clicked, reveal the screen share component; when “Toggle mode” is switched, update the behavior of the streaming handler or what’s displayed.

Deployment on Hugging Face Spaces: Considerations

---

## TAREFA 11
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

Deploying on Spaces introduces a few practical considerations:
	•	Networking: Since the app needs to call the external Gemini API, make sure to enable “Internet access” for the Space (in the Spaces settings or YAML, network: true). By default, Spaces run with no internet, which would block calls to Google’s API. Enabling internet (and possibly installing google-generativeai in requirements.txt) is required.
	•	Secrets: Do not hard-code sensitive keys. The Gemini API key can be input by the user (avoiding storing it on the server). Alternatively, if you have a default key, use Spaces Secrets to store it and load from os.environ. Same with any TURN credentials (HF token for Cloudflare, Twilio SID/token) – those can be set as secrets and accessed in code, so users don’t see them.
	•	TURN configuration: As discussed, a TURN server is essential on Spaces. The app should be configured to use Cloudflare or Twilio for ICE servers. This can be done by setting the rtc_configuration of the WebRTC component. For example, WebRTC(..., rtc_configuration=get_twilio_turn_credentials()) ￼ ￼ or using the Cloudflare credential helpers. Without this, users might find that the WebRTC connection fails on Spaces (since direct P2P cannot be established through the firewall) ￼. In testing, ensure that the WebRTC connects successfully from a few different networks (it will likely always work on localhost, but Spaces needs the TURN).

---

## TAREFA 12
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

•	Resource Limits: If the model is returning a lot of data or if you plan to buffer video clips, be mindful of the memory and disk limits of Spaces (especially on free tier). 2-second video chunks are small, but continuous streaming for a long time could accumulate. It’s wise to put a reasonable limit (like the time_limit=90 seconds in the example) on streaming sessions ￼ ￼. You can use Gradio’s time_limit and concurrency_limit in the webrtc.stream(...) call to cap session length and number of simultaneous users ￼ ￼. For instance, the example limited video chat to 90s and at most 2 concurrent users (due to Gemini’s limits) ￼ ￼.
	•	GPU/CPU: The app itself might not need a GPU since Gemini is accessed via API (all heavy lifting on Google’s side). So a CPU Space is fine. But if you plan on doing additional vision processing or running CV models locally, you might need a GPU and to switch the Space to GPU mode.
	•	Testing on Spaces: It’s important to test the deployed Space with the real screen-sharing – the browser will ask for permission to capture the screen. Ensure the UI flows (connect, share screen, etc.) are user-friendly and that the chat updates in real time. Using Gradio’s live reload (demo.queue()) is usually not needed for streaming events; the stream event of WebRTC handles real-time flow internally.

---

## TAREFA 13
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

By combining Gradio WebRTC for streaming, MediaDevices API for capture, and Google’s Generative AI SDK for Gemini, you can fulfill all the requirements with minimal custom plumbing. The FastRTC (gradio-webrtc) library specifically simplifies WebRTC integration – you get a high-level WebRTC component in Python and just provide a handler class to process streams ￼ ￼. The handler can incorporate the Gemini API calls (e.g., opening a websocket to Gemini and sending frames) and produce outputs. The UI is built in pure Python using Gradio Blocks, with the ability to drop down to custom HTML/JS for fine details.

Specific Tools & Libraries Recap:
	•	Gradio 5.x (Blocks API) – base framework for UI and app logic.
	•	gradio-webrtc (FastRTC) – custom component for real-time audio/video streaming in Gradio ￼.
	•	MediaDevices.getDisplayMedia (JS) – browser API for screen capture ￼.
	•	MediaRecorder API (JS) – to buffer and chunk the stream into 2s segments (if needed).
	•	Google Generative AI SDK (google-generativeai) – to interact with Gemini models (video/image analysis, etc.) ￼.
	•	TURN services: Cloudflare Calls (with HF token) ￼ or Twilio NAT Traversal API ￼ for WebRTC connectivity on Spaces.
	•	FastAPI or websockets (Python) – already handled internally by Gradio/FastRTC, but note that under the hood the Gemini handler will use Python websockets to talk to Google’s API (as seen with websockets.sync.client.connect in the example code) – ensure the environment allows outgoing wss (it should, once internet is on).
	•	UI/UX libraries: Tailwind CSS (optional, for styling) and Gradio’s theming system for a polished look. You can embed custom JS for any additional front-end control.

---

## TAREFA 14
**Progresso:** Pendente

- ☑ Pendente
- ☐ Iniciado
- ☐ Concluído

By following this architecture, the final Gradio app will “work out of the box” with only the user’s Gemini API key required, and no mock components – real screen data will flow to a real model. The WebRTC integration ensures minimal latency streaming, and the use of Gemini’s multimodal capabilities will let the app analyze both live video and static images. All of this is achievable within a single Hugging Face Space, leveraging the powerful combination of Gradio + FastRTC + Google’s Gemini API.

Sources: The solution builds on official docs and examples from Gradio and FastRTC, and Google’s Gemini API:
	•	Gradio/FastRTC streaming setup and TURN configuration ￼ ￼ ￼
	•	Use of WebRTC component in Gradio for real-time video ￼ ￼
	•	Browser Screen Capture API (getDisplayMedia) ￼
	•	Google Gemini integration and streaming example ￼ ￼
	•	Gradio UI customization (Blocks, HTML/JS injection, Tailwind support) ￼ ￼
	•	Hugging Face Spaces deployment notes ￼ ￼.

---