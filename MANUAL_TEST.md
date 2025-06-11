# Manual Testing Instructions

## 🎯 **VERIFY SCREEN HELPER ACTUALLY WORKS**

The automated tests confirm the code works, but to see **real screen recording and AI analysis**, follow these steps:

### **Step 1: Start the App**
```bash
source ~/.env/ee.sh
uv run python run_screen_helper.py
```

### **Step 2: Test the Full Workflow**

1. **Open the app** at `http://127.0.0.1:7860`
2. **Enter your Gemini API key** (or it should be pre-filled from environment)
3. **Click "Connect"** - the main interface should appear
4. **Set capture mode** to "snapshots" for faster response
5. **Click "Start Recording"**
6. **Grant screen share permission** when browser prompts
7. **Select your screen/window** to share
8. **Wait 2-3 seconds** - AI analysis should appear in the chat!

### **Step 3: Verify AI is Working**

You should see:
- ✅ Real-time descriptions of what's on your screen
- ✅ Updates every 2 seconds showing current screen content  
- ✅ Deduplication working (similar content filtered out)
- ✅ Mode switching between snapshots/video and raw/processed views

### **Step 4: Test Different Content**

Try displaying different content on your screen:
- Open a website
- Display an image
- Show text documents
- The AI should describe what it sees!

## 🚀 **Expected Results**

If working correctly, you'll see chat messages like:
```
🤖 "I can see a web browser displaying a GitHub repository page with code..."
🤖 "The screen shows a text editor with Python code visible..."
🤖 "I see a desktop with various application icons and a taskbar..."
```

## 🎉 **Success Criteria**

- ✅ **UI loads and connects**: Interface appears after entering API key
- ✅ **Screen sharing works**: Browser requests and grants screen permission  
- ✅ **AI analysis appears**: Chat shows descriptions of screen content
- ✅ **Real-time updates**: Content updates as screen changes
- ✅ **Mode switching**: Can toggle between different capture/view modes

## 🛠 **If Something Doesn't Work**

1. **Check API key**: Make sure `GEMINI_API_KEY` is valid
2. **Grant permissions**: Ensure browser has screen sharing permission
3. **Check console**: Look for WebRTC or network errors in browser dev tools
4. **Try different browser**: Chrome/Edge work best for WebRTC

---

**The Playwright tests verified the UI works correctly. This manual test verifies the end-to-end screen capture and AI analysis functionality!**